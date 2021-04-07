import json
import boto3
import traceback
import sys
import os
import numpy as np
import pandas as pd
#from sagemaker.sklearn.model import SKLearnPredictor
#from sagemaker.serializers import JSONSerializer
#from sagemaker.deserializers import NumpyDeserializer

num_anomalies_rule = 50
QUERY_1 = 'SELECT * FROM "octank-america-hvac"."thermafuser_readings" WHERE time between ago(10m) and now() ORDER BY time ASC '

def lambda_handler(event, context):
    # TODO implement
    
    ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
    SNS_TOPIC = os.environ['SNS_ARN']
    aws_session = boto3.session.Session()
    
    #Timestream session
    ts_query_client = aws_session.client('timestream-query')
    
    # grab environment variables
    sagemaker_runtime = aws_session.client('runtime.sagemaker')
    
    #sns client
    sns_client = boto3.client('sns')
    
    #Firehose client
    kinesis_client = aws_session.client('firehose', region_name='us-west-2')
    stream_name = 'anomalies1-20210310'
    
    #serializer = JSONSerializer()
    #deserializer = NumpyDeserializer()
    #predictor = SKLearnPredictor(endpoint_name=endpoint, sagemaker_session=sagemaker_session, serializer=serializer, deserializer=deserializer)
    
    #Query timestream for the latest data
    paginator = ts_query_client.get_paginator('query')
    res_df = run_query(paginator, QUERY_1)
    
    res_df = res_df.rename(columns={0:'id', 1:'name', 2:'type', 3:'measure', 4:'value', 5:'time'})
    print(res_df.head())
    res_df['time'] = pd.to_datetime(res_df['time'])
    
    #Create dataframes for each component
    unique_ids = res_df['id'].unique()

    dfs = {}
    
    for identifier in unique_ids:
        id_df = res_df.loc[res_df['id'] == identifier]
        #print(id_df.head())
        componentName = id_df.iloc[0]['name']
        componentType = id_df.iloc[0]['type']
        pivoted_df = id_df.pivot(index="time", columns="measure", values="value")
        pivoted_df = pivoted_df.reset_index()
        
        payload = pivoted_df.to_json()
        
        dfs[identifier] = pivoted_df
        
        #print(pivoted_df.head())
        #print(pivoted_df.shape)
        
        #response = predictor.predict(json_df, initial_args={'ContentType': 'application/json', 'Accept': 'application/json'})
        
        response = sagemaker_runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME, ContentType='application/json', Accept='application/json', Body=json.dumps(payload))
        bresponse = response['Body'].read()
        predictions = np.array(json.loads(bresponse))
        anomalies_zero = predictions + 1
        
        predictions_start_index = pivoted_df.shape[0] - predictions.shape[0]
        predicted_df = pivoted_df[predictions_start_index:].copy()
        predicted_df['anomaly'] = predictions
        
        #print(predicted_df.head())
        
        anomalies_to_s3(kinesis_client, stream_name, predicted_df, 1, identifier, componentName, componentType)
        
        num_anomalies = predictions.shape[0] - np.count_nonzero(anomalies_zero)
        if num_anomalies > num_anomalies_rule:
            message = "More than 10 anomalies detected for component: " + str(identifier)
            #print(message)
            response = sns_client.publish(TargetArn=SNS_TOPIC, Message=json.dumps({'default': json.dumps(message)}), MessageStructure='json')
            #print(response)
        
        #print('The predictions')
        #print(predictions)
        #print(predictions.shape)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    

def anomalies_to_s3(kinesis_client, stream_name, df_anomalies, idFactory, idComponent, componentName, componentType):
    
    df_anomalies = df_anomalies.rename(columns={'time':'timestamp'})
    df_anomalies = df_anomalies.loc[df_anomalies['anomaly'] == -1].copy()
    df_anomalies['anomaly'] = df_anomalies['anomaly'] + 2 #Make anomalies 1
    df_anomalies['timestamp'] = df_anomalies['timestamp'].map(lambda x: x.strftime("%Y-%m-%d %H:%M:%S.%f"))
    df_anomalies['factoryId'] = idFactory
    df_anomalies['objectId'] = idComponent
    df_anomalies['name'] = componentName
    df_anomalies['type'] = componentType
    anomalies_dict = df_anomalies.to_dict(orient='records')
    
    try:
        fs_records = [{'Data':json.dumps(x)} for x in anomalies_dict]
        #print(records)
        #print(fs_records)
        result = kinesis_client.put_record_batch(DeliveryStreamName=stream_name, Records=fs_records)
    
        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
            print('Status: ' + str(result['ResponseMetadata']))
            print(traceback.print_exc())
    except Exception as err:
        print("Error:", err)
        print(traceback.print_exc()) 
    
    return 0


def run_query(paginator, query_string):
    
        results = None
    
        try:
            page_iterator = paginator.paginate(QueryString=query_string)
            for page in page_iterator:
                results = parse_query_result(page)
                
                res_df = pd.DataFrame(results)
                
                return res_df
        except Exception as err:
            print("Exception while running query:", err)
            traceback.print_exc(file=sys.stderr)    
    
    
def parse_query_result(query_result):
    query_status = query_result["QueryStatus"]
    column_info = query_result['ColumnInfo']
    
    results = []
    
    #print(query_status)
    
    #print("Metadata: %s" % column_info)
    #print("Data: ")
    for row in query_result['Rows']:
        results.append(parse_row(column_info, row))
        
    return results
        

def parse_row(column_info, row):
    data = row['Data']
    row_output = []
    convert_data = {'BOOLEAN':bool, 'BIGINT':int, 'VARCHAR':str, 'DOUBLE':float}
    
    idComponent = None
    measure_name = ''
    measure_value = 0
    measure_time = None
    
    for j in range(len(data)):
        info = column_info[j]
        datum = data[j]
        
        if datum.get('NullValue') != True:
            
            if info['Name'] == 'Component_Id':
                idComponent = int(datum['ScalarValue'])
            elif info['Name'] == 'Component_Type':
                componentType = datum['ScalarValue']
            elif info['Name'] == 'Component_Name':
                componentName = datum['ScalarValue']
            elif 'measure_value' in info['Name']:
                measure_value = convert_data[info['Type']['ScalarType']](datum['ScalarValue'])
            elif info['Name'] == 'measure_name':
                measure_name = str(datum['ScalarValue'])
            elif info['Name'] == 'time':
                measure_time = str(datum['ScalarValue'])
                
    return (idComponent, componentName, componentType, measure_name, measure_value, measure_time)


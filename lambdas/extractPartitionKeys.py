import json
import base64
import re

def lambda_handler(event, context):
    # TODO implement
    
    output = []
    
    for record in event['records']:
        #Kinesis data is base64 encoded so decode here
        payload=base64.b64decode(record["data"])
        payload=json.loads(payload)
        
        match = re.search('^(\d\d\d\d)-(\d\d)-(\d\d)\s(\d\d).*$', payload['timestamp'])
        
        payload['year'] = match.group(1)
        payload['month'] = match.group(2)
        payload['day'] = match.group(3)
        payload['hour'] = match.group(4)
        payload['datehour'] = payload['year'] + '/' + payload['month'] + '/' + payload['day'] + '/' + payload['hour']
        
        payload = json.dumps(payload) + '\n'
        
        print("Transformed payload: " + payload)
        
        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': base64.b64encode(payload.encode('utf-8'))
        }
        output.append(output_record)
        
    print('Successfully processed {} records.'.format(len(event['records'])))
    
    return {'records': output}

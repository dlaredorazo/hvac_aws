import logging
import time
import boto3
import uuid
import json
import sys
import datetime
from multiprocessing import Pool
import concurrent.futures

from common import auxiliary
from db import hvacDBMapping

from sqlalchemy import and_

read_objects = {
    'ahu':[hvacDBMapping.AHUReading, hvacDBMapping.AHUReading._AHUNumber, hvacDBMapping.AHUReading._timestamp, 4,
     '2018-07-11'],
    'vfd':[hvacDBMapping.VFDReading, hvacDBMapping.VFDReading._vfdId, hvacDBMapping.AHUReading._timestamp, 1,
     '2018-07-11'],
    'filter':[hvacDBMapping.FilterReading, hvacDBMapping.FilterReading._filterId, hvacDBMapping.AHUReading._timestamp, 1,
     '2018-07-11'],
    'damper':[hvacDBMapping.DamperReading, hvacDBMapping.DamperReading._damperId, hvacDBMapping.AHUReading._timestamp, 1,
     '2018-07-11'],
    'fan':[hvacDBMapping.FanReading, hvacDBMapping.FanReading._fanId, hvacDBMapping.FanReading._timestamp, 1,
     '2018-07-11'],
    'hec':[hvacDBMapping.HECReading, hvacDBMapping.HECReading._HECId, hvacDBMapping.HECReading._timestamp, 1,
     '2018-07-11'],
    'sav': [hvacDBMapping.SAVReading, hvacDBMapping.SAVReading._SAVId, hvacDBMapping.SAVReading._timestamp, 1,
    '2018-07-11'],
    'vav': [hvacDBMapping.VAVReading, hvacDBMapping.VAVReading._VAVId, hvacDBMapping.VAVReading._timestamp, 1,
    '2018-07-11'],
    'thermafuser':[hvacDBMapping.ThermafuserReading, hvacDBMapping.ThermafuserReading._thermafuserId,
     hvacDBMapping.ThermafuserReading._timestamp, 1, '2018-07-11']
}

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

def test_boto():

    # boto3 offers two different styles of API - Resource API (high-level) and
    # Client API (low-level). Client API maps directly to the underlying RPC-style
    # service operations (put_object, delete_object, etc.). Resource API provides
    # an object-oriented abstraction on top (object.delete(), object.put()).
    #
    # While Resource APIs may help simplify your code and feel more intuitive to
    # some, others may prefer the explicitness and control over network calls
    # offered by Client APIs. For new AWS customers, we recommend getting started
    # with Resource APIs, if available for the service being used. At the time of
    # writing they're available for Amazon EC2, Amazon S3, Amazon DynamoDB, Amazon
    # SQS, Amazon SNS, AWS IAM, Amazon Glacier, AWS OpsWorks, AWS CloudFormation,
    # and Amazon CloudWatch. This sample will show both styles.
    #
    # First, we'll start with Client API for Amazon S3. Let's instantiate a new
    # client object. With no parameters or configuration, boto3 will look for
    # access keys in these places:
    #
    #    1. Environment variables (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)
    #    2. Credentials file (~/.aws/credentials or
    #         C:\Users\USER_NAME\.aws\credentials)
    #    3. AWS IAM role for Amazon EC2 instance
    #       (http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)

    s3client = boto3.client('s3')

    # Everything uploaded to Amazon S3 must belong to a bucket. These buckets are
    # in the global namespace, and must have a unique name.
    #
    # For more information about bucket name restrictions, see:
    # http://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html
    bucket_name = 'python-sdk-sample-{}'.format(uuid.uuid4())
    print('Creating new bucket with name: {}'.format(bucket_name))
    s3client.create_bucket(Bucket=bucket_name)

    # Now the bucket is created, and you'll find it in your list of buckets.

    list_buckets_resp = s3client.list_buckets()
    for bucket in list_buckets_resp['Buckets']:
        if bucket['Name'] == bucket_name:
            print('(Just created) --> {} - there since {}'.format(
                bucket['Name'], bucket['CreationDate']))

    # Files in Amazon S3 are called "objects" and are stored in buckets. A
    # specific object is referred to by its key (i.e., name) and holds data. Here,
    # we create (put) a new object with the key "python_sample_key.txt" and
    # content "Hello World!".

    object_key = 'python_sample_key.txt'

    print('Uploading some data to {} with key: {}'.format(
        bucket_name, object_key))
    s3client.put_object(Bucket=bucket_name, Key=object_key, Body=b'Hello World!')

    # Using the client, you can generate a pre-signed URL that you can give
    # others to securely share the object without making it publicly accessible.
    # By default, the generated URL will expire and no longer function after one
    # hour. You can change the expiration to be from 1 second to 604800 seconds
    # (1 week).

    url = s3client.generate_presigned_url(
        'get_object', {'Bucket': bucket_name, 'Key': object_key})
    print('\nTry this URL in your browser to download the object:')
    print(url)

    input("\nPress enter to continue...")

    # As we've seen in the create_bucket, list_buckets, and put_object methods,
    # Client API requires you to explicitly specify all the input parameters for
    # each operation. Most methods in the client class map to a single underlying
    # API call to the AWS service - Amazon S3 in our case.
    #
    # Now that you got the hang of the Client API, let's take a look at Resouce
    # API, which provides resource objects that further abstract out the over-the-
    # network API calls.
    # Here, we'll instantiate and use 'bucket' or 'object' objects.

    print('\nNow using Resource API')
    # First, create the service resource object
    s3resource = boto3.resource('s3')
    # Now, the bucket object
    bucket = s3resource.Bucket(bucket_name)
    # Then, the object object
    obj = bucket.Object(object_key)
    print('Bucket name: {}'.format(bucket.name))
    print('Object key: {}'.format(obj.key))
    print('Object content length: {}'.format(obj.content_length))
    print('Object body: {}'.format(obj.get()['Body'].read()))
    print('Object last modified: {}'.format(obj.last_modified))

    # Buckets cannot be deleted unless they're empty. Let's keep using the
    # Resource API to delete everything. Here, we'll utilize the collection
    # 'objects' and its batch action 'delete'. Batch actions return a list
    # of responses, because boto3 may have to take multiple actions iteratively to
    # complete the action.

    print('\nDeleting all objects in bucket {}.'.format(bucket_name))
    delete_responses = bucket.objects.delete()
    for delete_response in delete_responses:
        for deleted in delete_response['Deleted']:
            print('\t Deleted: {}'.format(deleted['Key']))

    # Now that the bucket is empty, let's delete the bucket.

    print('\nDeleting the bucket.')
    bucket.delete()

    # For more details on what you can do with boto3 and Amazon S3, see the API
    # reference page:
    # https://boto3.readthedocs.org/en/latest/reference/services/s3.html


def test_sql():

    max_dataPoints = 10

    sqlsession, sqlengine = auxiliary.connect_to_db('localhost', 'hvac2018_04', 'dlaredo', '@Dexsys131')

    q = sqlsession.query(hvacDBMapping.ThermafuserReading).filter(hvacDBMapping.ThermafuserReading._timestamp < '2020-12-31')
    results = q.limit(max_dataPoints).all()

    #print(q)

    while True:
        for result in results:
            msg = {'timestamp':datetime.datetime.now(), 'roomOccupancy':result.roomOccupied, 'zoneTemp':result.zoneTemperature,
                   'supplyAir':result.supplyAir, 'airFwFdbck':result.airflowFeedback, 'occCoolStpn':result.occupiedCoolingSetpoint,
                   'occHeatStpn':result.occupiedHeatingSetpoint}

            time.sleep(5)

            print(msg)


def get_sql_records(object_type, object_key, object_timestamp, key, timestamp, limit=10):

    #sqlsession, sqlengine = auxiliary.connect_to_db('localhost', 'hvac2018_04', 'dlaredo', '@Dexsys13')

    sqlsession, sqlengine = auxiliary.connect_to_db('factory1.czy5c8ouxr1q.us-west-2.rds.amazonaws.com', 'hvac2018_04', 'admin', 'Dexsys131')

    q = sqlsession.query(object_type).filter(and_(object_key == key, object_timestamp >= timestamp))

    #q = sqlsession.query(hvacDBMapping.ThermafuserReading).filter(and_(hvacDBMapping.ThermafuserReading._timestamp < '2020-12-31'))
    results = q.limit(limit).all()

    return results


def stream_to_kinesis():
    # print(q)

    kinesis_client = boto3.client('kinesis', region_name='us-west-2')

    results = get_sql_records(1000)

    while True:
        for result in results:
            msg = {'timestamp': str(datetime.datetime.now()), 'roomOccupancy': result.roomOccupied,
                   'zoneTemp': result.zoneTemperature,
                   'supplyAir': result.supplyAir, 'airFwFdbck': result.airflowFeedback,
                   'occCoolStpn': result.occupiedCoolingSetpoint,
                   'occHeatStpn': result.occupiedHeatingSetpoint}

            time.sleep(5)

            print(msg)
            kinesis_client.put_record(StreamName='StockTradeStream', Data=json.dumps(msg), PartitionKey='123')


def stream_to_firehose(object_type_str):
    #print(q)

    try:
        app_logger = logging.getLogger(__name__)
        object_type, object_key, object_timestamp, key, timestamp = read_objects[object_type_str]
        start_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d')

        print(object_type_str)

        aws_session = boto3.session.Session()
        kinesis_client = aws_session.client('firehose', region_name='us-west-2')
        stream_name = object_type_str + '1-20210310'
        print(stream_name)
    except Exception as e:
        app_logger.error(e)

    while True:

        try:
            results = get_sql_records(object_type, object_key, object_timestamp, key, start_time, 1000)

            if results:

                for result in results:
                    msg = result.to_json()
                    msg['factoryId'] = 1
                    msg['objectId'] = 1
                    #app_logger.error(msg)
                    print(msg)
                    kinesis_client.put_record(DeliveryStreamName=stream_name, Record={'Data':json.dumps(msg)})
                    time.sleep(5)

                #print("se acabo")

            else:

                print(start_time)
                start_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d')

                try:
                    start_time = start_time + datetime.timedelta(seconds=1)
                    app_logger.error('Getting new batch of data \n')
                except Exception as e:
                    app_logger.error(e)
                    break

        except Exception as e:
            app_logger.error(e)
            break

    return result.timestamp


def f(x):

    for i in range(5):
        print(x)
        print("me woa dormir")
        time.sleep(1)

    return x*x


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    app_logger = logging.getLogger(__name__)
    app_logger.setLevel(logging.WARNING)
    app_fh = logging.FileHandler('LogFiles/producer.log')
    app_formatter = logging.Formatter(
        fmt='%(levelname)s:%(threadName)s:%(asctime)s:%(filename)s:%(funcName)s:%(message)s',
        datefmt='%m/%d/%Y %H:%M:%S')
    app_fh.setFormatter(app_formatter)
    app_logger.addHandler(app_fh)

    #test_boto()
    #stream_to_kinesis()

    object_types = ['thermafuser', 'ahu', 'vfd', 'filter', 'damper', 'fan', 'hec', 'sav', 'vav']
    #object_types = ['vfd', 'damper', 'hec', 'sav', 'vav']
    #object_types = ['thermafuser']

    #stream_to_firehose('thermafuser')

    """
    time_d = datetime.datetime(year=2018, month=7, day=11)
    time_plus_d = time_d + datetime.timedelta(seconds=1)
    print(time_plus_d)
    """

    """
    for component in read_objects:
        object_type, object_key, object_timestamp, key, timestamp = read_objects[component]
        results = get_sql_records(object_type, object_key, object_timestamp, key, '2018-07-11', 5)

        for result in results:
            print(result)
    """

    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(stream_to_firehose, object_types)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

    #output = [p.get() for p in results]
    #print(output)

    #stream_to_firehose()




# See PyCharm help at https://www.jetbrains.com/help/pycharm/

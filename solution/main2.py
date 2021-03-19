import logging
import time
import boto3
import uuid
import json
import sys
import datetime
from multiprocessing import Pool
import concurrent.futures
import re
import traceback

from common import auxiliary
from db import hvacDBMapping

from botocore.config import Config

from sqlalchemy import and_

read_objects = {
    'ahu':{'params': [hvacDBMapping.AHUReading, hvacDBMapping.AHUReading._AHUNumber, hvacDBMapping.AHUReading._timestamp, '2018-07-11'], 'objs':None},
    'vfd':{'params': [hvacDBMapping.VFDReading, hvacDBMapping.VFDReading._vfdId, hvacDBMapping.AHUReading._timestamp, '2018-07-11'], 'objs':None},
    'filter':{'params': [hvacDBMapping.FilterReading, hvacDBMapping.FilterReading._filterId, hvacDBMapping.FilterReading._timestamp, '2018-07-11'], 'objs':None},
    'damper':{'params': [hvacDBMapping.DamperReading, hvacDBMapping.DamperReading._damperId, hvacDBMapping.DamperReading._timestamp, '2018-07-11'], 'objs':None},
    'fan':{'params': [hvacDBMapping.FanReading, hvacDBMapping.FanReading._fanId, hvacDBMapping.FanReading._timestamp, '2018-07-11'], 'objs':None},
    'hec':{'params': [hvacDBMapping.HECReading, hvacDBMapping.HECReading._HECId, hvacDBMapping.HECReading._timestamp, '2018-07-11'], 'objs':None},
    'sav':{'params': [hvacDBMapping.SAVReading, hvacDBMapping.SAVReading._SAVId, hvacDBMapping.SAVReading._timestamp, '2018-07-11'], 'objs':None},
    'vav':{'params': [hvacDBMapping.VAVReading, hvacDBMapping.VAVReading._VAVId, hvacDBMapping.VAVReading._timestamp, '2018-07-11'], 'objs':None},
    'thermafuser':{'params': [hvacDBMapping.ThermafuserReading, hvacDBMapping.ThermafuserReading._thermafuserId,
     hvacDBMapping.ThermafuserReading._timestamp, '2018-07-11'], 'objs':None}
}

def records_to_timestream_format(record, timestream_write_client, obj_type_str):
    #print("Writing records")
    app_logger = logging.getLogger(__name__)

    d_types = {'int':'BIGINT', 'float':'DOUBLE', 'bool':'BOOLEAN'}
    records = []

    dimensions = [
        {'Name': 'Factory_Id', 'Value': record['factoryId']},
        {'Name': 'Component_Id', 'Value': record['objectId']},
        {'Name': 'Component_Type', 'Value': record['name']},
        {'Name': 'Component_Name', 'Value': record['type']},
    ]

    excludedKeys = set(['factoryId', 'objectId', 'name', 'type', 'timestamp', 'timestamp_timestream'])
    includedKeys = record.keys() - excludedKeys

    try:
        for key in includedKeys:

            d_type = str(type(record[key]))
            match = re.search('^\<class\s\'(.*)\'\>$', d_type)

            if match:
                d_type = match.group(1)
                if d_type in d_types:
                    ts_record = {'Dimensions': dimensions, 'MeasureName': key, 'MeasureValue': str(record[key]), 'MeasureValueType':d_types[d_type], 'Time': record['timestamp_timestream']}
                    records.append(ts_record)
            else:
                continue

    except Exception as err:
        print("Error:", err)
        print(traceback.print_exc())
        app_logger.error(traceback.print_exc())

    try:
        result = timestream_write_client.write_records(DatabaseName='octank-america-hvac', TableName=obj_type_str+'_readings',
                                           Records=records, CommonAttributes={})

        if result['ResponseMetadata']['HTTPStatusCode'] != 200:
            print('Status: ' + str(result['ResponseMetadata']))
            app_logger.error('Status: ' + str(result['ResponseMetadata']))

        #print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
    except Exception as err:
        print("Error:", err)
        print(traceback.print_exc())
        app_logger.error(traceback.print_exc())


def get_sql_records(object_type, object_key, object_timestamp, key, timestamp, limit=10):

    #sqlsession, sqlengine = auxiliary.connect_to_db('localhost', 'hvac2018_04', 'dlaredo', '@Dexsys13')

    sqlsession, sqlengine = auxiliary.connect_to_db('factory2.czy5c8ouxr1q.us-west-2.rds.amazonaws.com', 'hvac2018_04', 'admin', 'Dexsys131')

    q = sqlsession.query(object_type).filter(and_(object_key == key, object_timestamp >= timestamp))

    results = q.limit(limit).all()

    return results


def stream_to_firehose(object_type_str):

    sql_results = {}
    db_buffer = 1000
    time_delta_secs = 5

    print('Writing data to streams: ' + object_type_str)
    app_logger.error('Writing data to streams: ' + object_type_str)

    try:
        object_type, object_key, object_timestamp, timestamp = read_objects[object_type_str]['params']
        object_details = read_objects[object_type_str]['objs']

        objs_metadata = {obj.componentId:[obj.name, obj.componentType] for obj in object_details}

        query_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d')

        aws_session = boto3.session.Session()
        kinesis_client = aws_session.client('firehose', region_name='us-west-2')
        stream_name = object_type_str + '1-20210310'
        timestream_write_client = aws_session.client('timestream-write', config=Config(read_timeout=20, max_pool_connections=5000,
                                                                        retries={'max_attempts': 10}))

        for key in objs_metadata.keys():
            sql_results[key] = {}
            sql_results[key]['data'] = get_sql_records(object_type, object_key, object_timestamp, key, query_time, db_buffer)
            sql_results[key]['max_records'] = len(sql_results[key]['data'])
            sql_results[key]['current_record'] = 0
            sql_results[key]['start_time'] = query_time

    except Exception as e:
        app_logger.error(e)
        print(traceback.print_exc())
        app_logger.error(traceback.print_exc())

    while True:

        #print(sql_results)

        stream_results = []

        try:

            for key in sql_results.keys():

                data = []

                if sql_results[key]['current_record'] == sql_results[key]['max_records']:

                    query_time = sql_results[key]['start_time']
                    query_time = query_time + datetime.timedelta(seconds=time_delta_secs)
                    app_logger.error('Getting new batch of data for {}\n'.format(key))
                    print('Getting new batch of data for {}\n'.format(key))
                    print(query_time)
                    app_logger.error('Getting new batch of data for {}\n'.format(key))
                    app_logger.error(query_time)
                    records = get_sql_records(object_type, object_key, object_timestamp, key, query_time, db_buffer)

                    if not records:
                        app_logger.error('Resetting time for {}\n'.format(key))
                        query_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d')
                        records = get_sql_records(object_type, object_key, object_timestamp, key, query_time, db_buffer)

                    data = records[:]
                    sql_results[key]['data'] = data
                    sql_results[key]['max_records'] = len(data)
                    sql_results[key]['current_record'] = 0
                    sql_results[key]['start_time'] = data[-1].timestamp

                else:
                    data = sql_results[key]['data']
                    result = {'res':data[sql_results[key]['current_record']], 'key':key}
                    stream_results.append(result)
                    sql_results[key]['current_record'] = sql_results[key]['current_record'] + 1

            for result in stream_results:
                msg = result['res'].to_json()
                msg['timestamp'] = str(datetime.datetime.now())
                msg['timestamp_timestream'] = str(int(round(datetime.datetime.now().timestamp()*1000)))
                msg['factoryId'] = 'Octank Oregon'
                msg['objectId'] = str(result['key'])
                msg['name'] = objs_metadata[result['key']][0]
                msg['type'] = objs_metadata[result['key']][1]

                #print(msg)

                records_to_timestream_format(msg, timestream_write_client, object_type_str)
                result = kinesis_client.put_record(DeliveryStreamName=stream_name, Record={'Data':json.dumps(msg)})

                if result['ResponseMetadata']['HTTPStatusCode'] != 200:
                    print('Status: ' + str(result['ResponseMetadata']))
                    app_logger.error('Status: ' + str(result['ResponseMetadata']))
                    print(traceback.print_exc())
                    app_logger.error(traceback.print_exc())

            time.sleep(5)

        except Exception as e:
            app_logger.error(e)
            print(traceback.print_exc())
            app_logger.error(traceback.print_exc())
            break

    return None


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

    #object_types = ['thermafuser', 'ahu', 'vfd', 'filter', 'damper', 'fan', 'hec', 'sav', 'vav']
    object_types = ['thermafuser', 'ahu', 'vfd', 'filter', 'damper', 'fan', 'hec']
    #object_types = ['ahu']
    #object_types = ['vfd', 'damper', 'hec', 'sav', 'vav']
    #object_types = ['thermafuser']

    #stream_to_firehose('thermafuser')

    # Get all the components that are related to the AHU
    sqlsession, sqlengine = auxiliary.connect_to_db('factory2.czy5c8ouxr1q.us-west-2.rds.amazonaws.com', 'hvac2018_04',
                                                    'admin', 'Dexsys131')
    q = sqlsession.query(hvacDBMapping.AHU).filter(hvacDBMapping.AHU._AHUNumber == 4)
    ahu = q.first()
    all_fans = ahu.fans
    all_dampers = ahu.dampers
    all_filters = ahu.filters
    all_hecs = ahu.hecs
    all_savs = ahu.savs
    all_vavs = ahu.vavs
    all_thermafusers = ahu.thermafusers
    all_vfds = ahu.vfds

    fans = [fan for fan in all_fans if (fan._fanId == 15 or fan.fanId == 20)]
    vfds = [vfd for vfd in all_vfds if (vfd._vfdId == 9 or vfd.vfdId == 10)]
    dampers = all_dampers[:]
    filters = all_filters[:]
    hecs = all_hecs[:]
    vavs = [vav for vav in all_vavs if (vav._VAVId == 17 or vav.VAVId == 18)]
    thermafusers = [thermafuser for thermafuser in all_thermafusers if thermafuser.thermafuserId in list(range(61, 66))]

    """
    read_objects['ahu']['ids'] = [ahu.AHUNumber]
    read_objects['fan']['ids'] = [fan.fanId for fan in fans]
    read_objects['damper']['ids'] = [damper.damperId for damper in dampers]
    read_objects['filter']['ids'] = [filt.filterId for filt in filters]
    read_objects['hec']['ids'] = [hec.HECId for hec in hecs]
    read_objects['vav']['ids'] = [vav.VAVId for vav in vavs]
    read_objects['thermafuser']['ids'] = [thermafuser.thermafuserId for thermafuser in thermafusers]
    read_objects['vfd']['ids'] = [vfd.vfdId for vfd in vfds]
    """

    read_objects['ahu']['objs'] = [ahu]
    read_objects['fan']['objs'] = fans
    read_objects['damper']['objs'] = dampers
    read_objects['filter']['objs'] = filters
    read_objects['hec']['objs'] = hecs
    read_objects['vav']['objs'] = vavs
    read_objects['thermafuser']['objs'] = thermafusers
    read_objects['vfd']['objs'] = vfds


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

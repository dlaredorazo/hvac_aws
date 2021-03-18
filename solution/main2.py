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

def records_to_timestream_format(record, timestream_write_client):
    print("Writing records")
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

    #ts_record = {'Dimensions': dimensions, 'Time': record['timestamp']}

    #print(ts_record)

    try:
        for key in includedKeys:

            d_type = str(type(record[key]))
            match = re.search('^\<class\s\'(.*)\'\>$', d_type)

            if match:
                #print('it matched')
                d_type = match.group(1)
                #print(d_type)
                ts_record = {'Dimensions': dimensions, 'MeasureName': key, 'MeasureValue': str(record[key]), 'MeasureValueType':d_types[d_type], 'Time': record['timestamp_timestream']}
                #copy_record = ts_record.copy()
                #print(copy_record)
                records.append(ts_record)
            else:
                continue

        print(records)
    except Exception as err:
        print("Error:", err)
        app_logger.error(err)


    """
    cpu_utilization = {
        'Dimensions': dimensions,
        'MeasureName': 'cpu_utilization',
        'MeasureValue': '13.5',
        'MeasureValueType': 'DOUBLE',
        'Time': current_time
    }
    """

    try:
        result = timestream_write_client.write_records(DatabaseName='octank-america-hvac', TableName='thermafuser_test',
                                           Records=records, CommonAttributes={})
        print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
    except Exception as err:
        print("Error:", err)


def get_sql_records(object_type, object_key, object_timestamp, key, timestamp, limit=10):

    #sqlsession, sqlengine = auxiliary.connect_to_db('localhost', 'hvac2018_04', 'dlaredo', '@Dexsys13')

    sqlsession, sqlengine = auxiliary.connect_to_db('factory2.czy5c8ouxr1q.us-west-2.rds.amazonaws.com', 'hvac2018_04', 'admin', 'Dexsys131')

    q = sqlsession.query(object_type).filter(and_(object_key == key, object_timestamp >= timestamp))

    #print(key)
    #print(timestamp)
    #print(q)

    #q = sqlsession.query(hvacDBMapping.ThermafuserReading).filter(and_(hvacDBMapping.ThermafuserReading._timestamp < '2020-12-31'))
    results = q.limit(limit).all()

    return results


def stream_to_firehose(object_type_str):
    #print(q)

    sql_results = {}
    bd_buffer = 10

    try:
        app_logger = logging.getLogger(__name__)
        object_type, object_key, object_timestamp, timestamp = read_objects[object_type_str]['params']
        object_details = read_objects[object_type_str]['objs']

        #for obj in object_details:
        #    print(obj)

        objs_metadata = {obj.componentId:[obj.name, obj.componentType] for obj in object_details}

        #print(objs_metadata)

        #print(objs_metadata)

        #objs_id = read_objects[object_type_str]['ids']
        start_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d')

        #print(object_type_str)

        #for obj_id in objs_id:
        #    print(object_type_str + ': %d', obj_id)

        aws_session = boto3.session.Session()
        kinesis_client = aws_session.client('firehose', region_name='us-west-2')
        stream_name = object_type_str + '1-20210310'
        timestream_write_client = aws_session.client('timestream-write', config=Config(read_timeout=20, max_pool_connections=5000,
                                                                        retries={'max_attempts': 10}))
        #print(stream_name)

        #print(objs_id)

        for key in objs_metadata.keys():
            #print(object_type_str + ': {}'.format(key))
            #print(objs_metadata[key])
            sql_results[key] = {}
            sql_results[key]['data'] = get_sql_records(object_type, object_key, object_timestamp, key, start_time, bd_buffer)
            sql_results[key]['max_records'] = len(sql_results[key]['data'])
            sql_results[key]['current_record'] = 0
            #print(len(sql_results[key]['data']))

    except Exception as e:
        app_logger.error(e)

    while True:

        stream_results = []

        try:

            for key in sql_results.keys():

                data = []

                if sql_results[key]['current_record'] == sql_results[key]['max_records']:

                    start_time = start_time + datetime.timedelta(seconds=1)
                    app_logger.error('Getting new batch of data for {}\n'.format(key))
                    records = get_sql_records(object_type, object_key, object_timestamp, key, start_time, bd_buffer)

                    if not records:
                        app_logger.error('Resetting time for {}\n'.format(key))
                        start_time = datetime.datetime.strptime(timestamp, '%Y-%m-%d')
                        records = get_sql_records(object_type, object_key, object_timestamp, key, start_time, bd_buffer)

                    data = records[:]
                    sql_results[key]['data'] = records[:]
                    sql_results[key]['max_records'] = len(sql_results[key]['data'])
                    sql_results[key]['current_record'] = 0

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
                #app_logger.error(msg)
                #print(msg)
                records_to_timestream_format(msg, timestream_write_client)
                #kinesis_client.put_record(DeliveryStreamName=stream_name, Record={'Data':json.dumps(msg)})

            time.sleep(5)

        except Exception as e:
            app_logger.error(e)
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
    #object_types = ['thermafuser', 'ahu', 'vfd', 'filter', 'damper', 'fan', 'hec']
    #object_types = ['damper', 'fan']
    #object_types = ['vfd', 'damper', 'hec', 'sav', 'vav']
    object_types = ['thermafuser']

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

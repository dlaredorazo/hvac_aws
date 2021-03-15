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
    'ahu':[hvacDBMapping.AHUReading, hvacDBMapping.AHUReading._AHUNumber, hvacDBMapping.AHUReading._timestamp, 5,
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

def get_sql_records(object_type, object_key, object_timestamp, key, timestamp, limit=10):

    #sqlsession, sqlengine = auxiliary.connect_to_db('localhost', 'hvac2018_04', 'dlaredo', '@Dexsys13')

    sqlsession, sqlengine = auxiliary.connect_to_db('factory2.czy5c8ouxr1q.us-west-2.rds.amazonaws.com', 'hvac2018_04', 'admin', 'Dexsys131')

    q = sqlsession.query(object_type).filter(and_(object_key == key, object_timestamp >= timestamp))

    #q = sqlsession.query(hvacDBMapping.ThermafuserReading).filter(and_(hvacDBMapping.ThermafuserReading._timestamp < '2020-12-31'))
    results = q.limit(limit).all()

    return results


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


    fans = [fan for fan in all_fans if (fan._fanId == 15 or fan.fanId == 20)]
    dampers = all_dampers[:]
    filters = all_filters[:]
    hecs = all_hecs[:]
    vavs = [vav for vav in all_vavs if (vav._VAVId == 17 or vav.VAVId == 18)]
    thermafusers = [thermafuser for thermafuser in all_thermafusers if thermafuser.thermafuserId in list(range(61, 66))]


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

    """
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(stream_to_firehose, object_types)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    """

    #output = [p.get() for p in results]
    #print(output)

    #stream_to_firehose()




# See PyCharm help at https://www.jetbrains.com/help/pycharm/

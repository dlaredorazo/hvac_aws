import logging
import boto3
import time


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    shard_id = 'shardId-000000000000'  # we only have one shard!

    app_logger = logging.getLogger('consumer_logger')
    app_logger.setLevel(logging.WARNING)
    app_fh = logging.FileHandler('LogFiles/producer.log')
    app_formatter = logging.Formatter(
        fmt='%(levelname)s:%(threadName)s:%(asctime)s:%(filename)s:%(funcName)s:%(message)s',
        datefmt='%m/%d/%Y %H:%M:%S')
    app_fh.setFormatter(app_formatter)
    app_logger.addHandler(app_fh)

    app_logger.error("This is a test")

    #test_boto()
    kinesis_client = boto3.client('kinesis', region_name='us-west-2')
    print(kinesis_client.list_streams())

    shard_it = kinesis_client.get_shard_iterator(StreamName="StockTradeStream", ShardId=shard_id, ShardIteratorType="LATEST")["ShardIterator"]

    while True:

        out = kinesis_client.get_records(ShardIterator=shard_it, Limit=2)
        shard_it = out["NextShardIterator"]
        print(out)
        time.sleep(5)



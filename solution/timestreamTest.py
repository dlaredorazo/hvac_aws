import boto3
import argparse

from CrudAndSimpleIngestionExample import CrudAndSimpleIngestionExample
from botocore.config import Config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--kmsId", help="This will be used for updating the database")
    args = parser.parse_args()

    session = boto3.Session()

    write_client = session.client('timestream-write', config=Config(read_timeout=20, max_pool_connections=5000,
                                                                    retries={'max_attempts': 10}))

    crud_and_simple_ingestion_example = CrudAndSimpleIngestionExample(write_client)
    crud_and_simple_ingestion_example.list_databases()
    crud_and_simple_ingestion_example.describe_database()



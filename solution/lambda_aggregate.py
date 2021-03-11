"Lambda function Calculator exercise"
from __future__ import print_function
import re
import boto3
import pandas as pd
import json

def lambda_handler(event, context):
    "Process upload event"
    bucket = event['Records'][0]["s3"]["bucket"]["name"]
    key = event['Records'][0]["s3"]["object"]["key"]

    result = None

    print("Received event. Bucket: [%s], Key: [%s]" % (bucket, key))

    # construct s3 client
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    # get the object contents
    file_contents = response['Body'].read().decode("utf-8").strip().split('\n')
    file_contents_json = [json.loads(x) for x in file_contents]
    df = pd.DataFrame(file_contents_json)
    aggregated_data = df.describe().to_dict()

    #print(df)
    #print(aggregated_data)




    print("Result: %s" % result)
    return result

# This is used for debugging, it will only execute when run locally
if __name__ == "__main__":
    # local debugging, send a simulated event
    # TODO 1: Update the event bucket name
    fake_s3_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "factory1-machine1-david-laredo-test"
                    },
                    "object": {
                        "key": "2021/02/12/04/Machine1_To_S3-1-2021-02-12-04-48-46-f4d94cac-c967-4485-a5a3-23298faa878f"
                    }
                }
            }
        ]
    }

    fake_context = []
    lambda_handler(fake_s3_event, fake_context)
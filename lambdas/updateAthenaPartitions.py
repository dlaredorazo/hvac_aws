import json
import urllib.parse
import boto3
import copy

print('Loading function')

s3 = boto3.client('s3')
athena_client = boto3.client('athena')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    
    DATABASE_NAME = 'hvac'
    TABLE_NAME = 'readings_octank_america_hvac_'
    

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        print("bucket--->" + bucket)
        print("key---->" + key)
        
        component = bucket.split('-')[-1]
        
        print("component---->" + component)
        
        # Assuming object key is folder_name/YYYY/MM/DD/HH/sample.json
        partitions_values = key.split('/')[:-1] # Remove the filename at the end
        print(partitions_values) # Output: [‘YYYY’, ‘MM', ‘DD’, ‘HH']
        
        # Initialise the Glue client using Boto 3
        glue_client = boto3.client('glue')
        
        try:
            # Check if the partition already exists. If yes, skip adding it again
            get_partition_response = glue_client.get_partition(
            DatabaseName=DATABASE_NAME,
            TableName=TABLE_NAME+component,
            PartitionValues=partitions_values
            )
            print('Glue partition already exists.')

        except Exception as e:
            # Check if the exception is EntityNotFoundException. If yes, go ahead and create parition
            if type(e).__name__ == 'EntityNotFoundException':
                print('Retrieve Table Details:')
                get_table_response = glue_client.get_table(
                DatabaseName=DATABASE_NAME,
                Name=TABLE_NAME+component
                )
    
                # Extract the existing storage descriptor and Create custom storage descriptor with new partition location
                storage_descriptor = get_table_response['Table']['StorageDescriptor']
                custom_storage_descriptor = copy.deepcopy(storage_descriptor)
                custom_storage_descriptor['Location'] = storage_descriptor['Location'] + "/".join(partitions_values) + '/'
    
                # Create new Glue partition in the Glue Data Catalog
                create_partition_response = glue_client.create_partition(
                DatabaseName=DATABASE_NAME,
                TableName=TABLE_NAME+component,
                PartitionInput={
                    'Values': partitions_values,
                    'StorageDescriptor': custom_storage_descriptor
                    }
                )
                print('Glue partition created successfully.') 
            else:
                # Handle exception as per your business requirements
                print(e)   
        
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e

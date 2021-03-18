##################################################
## A multi-process and multi-threaded driver #####
## that ingests data mimicking a DevOps ##########
## application into the specified Timestream #####
## database and table. It also creates the #######
## database and table it they don't exist. #######
##################################################

import argparse
import model
import continuous_ingester as ingest
import timestreamwrite as tswrite
import pprint
import botocore.exceptions

def createDatabaseAndTable(args):
    ##
    client = tswrite.createWriteClient(args.endpoint, args.profile)
    try:
        result = tswrite.createDatabase(client, args.databaseName)
        print(result)
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ConflictException':
            print("Database {} already exists.".format(args.databaseName))
        else:
            raise error
    except Exception as e:
        pprint.pprint(e)
        raise e

    try:
        retentionProperties = {
            'MemoryStoreRetentionPeriodInHours': args.memoryStoreRetentionHours,
            'MagneticStoreRetentionPeriodInDays': args.magneticStoreRetentionDays
        }
        print("Creating table {} in database {} with retention properties: {}".format(args.databaseName, args.tableName, retentionProperties))
        result = tswrite.createTable(client, args.databaseName, args.tableName, retentionProperties)
        print(result)
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'ConflictException':
            print("Database {} already exists.".format(args.databaseName))
        else:
            raise error
    except Exception as e:
        pprint.pprint(e)
        raise e

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog = 'DevOps Ingestion Driver', description='Execute the Ingestion Driver for DevOps Workload.')

    parser.add_argument('--database-name', '-d', dest="databaseName", action = "store", required = True, help = "The database name for the workload.")
    parser.add_argument('--table-name', '-t', dest="tableName", action = "store", required = True, help = "The table name for the workload.")
    parser.add_argument('--endpoint', '-e', action = "store", required = True, help="Specify the region where the Timestream database is located.")
    parser.add_argument('--memory-store-retention-hours', dest = "memoryStoreRetentionHours", action = "store", type = int, default = 2, help = "Memory store retention period of the table (in hours) [Default 2 hours].")
    parser.add_argument('--magnetic-store-retention-days', dest = "magneticStoreRetentionDays", action = "store", type = int, default = 365, help = "Magnetic store retention period of the table (in days) [Default 365 days].")
    parser.add_argument('--concurrency', '-c', action = "store", type = int, default = 1, help = "Number of concurrent threads to use (default: 1)")
    parser.add_argument('--processes', '-p', action = "store", type = int, default = 1, help = "Number of concurrent processes to use (default: 1)")
    parser.add_argument('--host-scale', dest = "hostScale", action = "store", type = int, default = 100, help = "The scale factor that determines the number of hosts emitting events and metrics. (default: 100)")
    parser.add_argument('--interval-millis', dest = "intervalMillis", action = "store", type = int, default = 5000, help = "Interval of time between events. (default: 5000)")
    parser.add_argument('--profile', action = "store", type = str, default= None, help = "The AWS profile to use.")
    parser.add_argument('--instance-name-seed', dest="instanceNameSeed", action = "store", type = int, default = 12345, help = "Seed to use for generating instance_name dimension values")
    parser.add_argument('--print-model-summary', dest = "modelSummary", action = "store_true", help = "Only print the data model summary")

    args = parser.parse_args()
    print(args)

    dimensionsMetrics, dimensionsEvents = model.generateDimensions(args.hostScale)
    intervalSecs = int(args.intervalMillis / 1000)
    model.printModelSummary(dimensionsMetrics, dimensionsEvents, intervalSecs, intervalSecs)

    if args.modelSummary:
        exit(0)

    ## Create the database and table.
    createDatabaseAndTable(args)

    ## start ingesting data.
    ingest.ingestRecordsMultiProc(dimensionsMetrics, dimensionsEvents, args)
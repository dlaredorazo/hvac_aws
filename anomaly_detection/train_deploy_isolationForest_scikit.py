import argparse
import os
import pandas as pd
import numpy as np
import joblib
import json

from io import StringIO

from sklearn.ensemble import IsolationForest

from sagemaker_containers.beta.framework import content_types, encoders, env, modules, transformer, worker



if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    day_quarters = {0: '0-5', 1: '6-11', 2: '12-17', 3: '18-23'}

    # Hyperparameters are described here. In this simple example we are just including one hyperparameter.
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--contamination', type=float, default=0.1)
    parser.add_argument('--max_features', type=float, default=1.0)

    # Sagemaker specific arguments. Defaults are set in the environment variables.
    parser.add_argument('--output-data-dir', type=str, default=os.environ['SM_OUTPUT_DATA_DIR'])
    parser.add_argument('--model-dir', type=str, default=os.environ['SM_MODEL_DIR'])
    parser.add_argument('--train', type=str, default=os.environ['SM_CHANNEL_TRAIN'])

    args = parser.parse_args()

    print(args.train)

    input_files = [os.path.join(args.train, file) for file in os.listdir(args.train)]

    thermafuser_df = pd.read_csv(input_files[0], index_col=False, engine='python')
    thermafuser_df = thermafuser_df.drop('Unnamed: 0', axis=1)
    thermafuser_df = thermafuser_df.loc[thermafuser_df['_thermafuserId'] == 1]
    thermafuser_df.reset_index(inplace=True, drop=True)

    col_names = {'_roomOccupied': 'RoomOccupied', '_supplyAir': 'SupplyAir',
                 '_occupiedCoolingSetpoint': 'OccupiedCoolingSetpoint', '_terminalLoad': 'TerminalLoad',
                 '_zoneTemperature': 'ZoneTemperature', '_airflowFeedback': 'AirflowFeedback',
                 '_occupiedHeatingSetpoint': 'OccupiedHeatingSetpoint', '_timestamp': 'Timestamp'}

    thermafuser_df = thermafuser_df.drop('_thermafuserId', axis=1)
    thermafuser_df = thermafuser_df.rename(columns=col_names)

    thermafuser_df['Timestamp'] = pd.to_datetime(thermafuser_df['Timestamp'])

    thermafuser_df['RoomOccupied'] = thermafuser_df['RoomOccupied'].replace({True: 1, False: 0})
    thermafuser_df = thermafuser_df.drop(['OccupiedCoolingSetpoint', 'OccupiedHeatingSetpoint', 'TerminalLoad'], axis=1)

    thermafuser_df = thermafuser_df.drop('RoomOccupied', axis=1)

    thermafuser_df['Day quarter'] = thermafuser_df['Timestamp'].map(lambda x: x.hour // 6)
    dummies = pd.get_dummies(thermafuser_df['Day quarter'])
    thermafuser_df = pd.concat([thermafuser_df, dummies], axis=1)
    thermafuser_df.rename(columns=day_quarters, inplace=True)

    thermafuser_df.drop(0, axis=0, inplace=True)
    thermafuser_df.drop('Day quarter', axis=1, inplace=True)
    thermafuser_df.drop('Timestamp', axis=1, inplace=True)

    #Create time window

    thermafuser_df_windowed = thermafuser_df.copy()

    #Create rolling windows
    thermafuser_df_windowed['AirflowRoll'] = thermafuser_df['AirflowFeedback'].rolling(window=12).mean()
    thermafuser_df_windowed['SupplyAirRoll'] = thermafuser_df['SupplyAir'].rolling(window=12).mean()
    thermafuser_df_windowed['ZoneTemperatureRoll'] = thermafuser_df['ZoneTemperature'].rolling(window=12).mean()

    thermafuser_df_windowed['0-5Roll'] = thermafuser_df['0-5'].rolling(window=12).median()
    thermafuser_df_windowed['6-11Roll'] = thermafuser_df['6-11'].rolling(window=12).median()
    thermafuser_df_windowed['12-17Roll'] = thermafuser_df['12-17'].rolling(window=12).median()
    thermafuser_df_windowed['18-23Roll'] = thermafuser_df['18-23'].rolling(window=21).median()

    thermafuser_df_windowed = thermafuser_df_windowed[['AirflowRoll', 'SupplyAirRoll', 'ZoneTemperatureRoll',
                                                       '0-5Roll', '6-11Roll', '12-17Roll', '18-23Roll']]
    thermafuser_df_windowed = thermafuser_df_windowed.dropna()

    train_df = thermafuser_df_windowed[['AirflowRoll', 'SupplyAirRoll', 'ZoneTemperatureRoll', '0-5Roll', '6-11Roll', '12-17Roll', '18-23Roll']]

    clf = IsolationForest(n_estimators=args.n_estimators, max_samples='auto', contamination=args.contamination, max_features=args.max_features,
                          bootstrap=False, n_jobs=1, verbose=1)
    clf.fit(train_df)

    # Save the model to the location specified by args.model_dir
    joblib.dump(clf, os.path.join(args.model_dir, "model.joblib"))


def input_fn(input_data, content_type):
    """Parse input data payload

    We currently only take csv input. Since we need to process both labelled
    and unlabelled data we first determine whether the label column is present
    by looking at how many columns were provided.
    """

    day_quarters = {0: '0-5', 1: '6-11', 2: '12-17', 3: '18-23'}

    # To ensure that all of the quarters are created
    fake_entries = {'time': [None, None, None, None], 'airflowFeedback': [None, None, None, None],
                    'occupiedCoolingSetpoint': [None, None, None, None], 'roomOccupied': [None, None, None, None],
                    'roomOccupied': [None, None, None, None], 'supplyAir': [None, None, None, None],
                    'terminalLoad': [None, None, None, None], 'zoneTemperature': [None, None, None, None],
                    'Day quarter': [0, 1, 2, 3]
                    }
    quarters_df = pd.DataFrame(fake_entries)


    if content_type == 'text/csv':
        # Read the raw input data as CSV.
        #df = pd.read_csv(StringIO(input_data), header=None)
        #return df
        print("csv input type")
        pass

    if content_type == 'application/json':

        #print(input_data)

        payload = json.loads(input_data)
        res_df = pd.read_json(payload)
        print(res_df.head())
        res_df = res_df.reset_index()

        #Create day quarters
        res_df['time'] = pd.to_datetime(res_df['time'])
        res_df['Day quarter'] = res_df['time'].map(lambda x: x.hour // 6)
        concat_df = pd.concat([res_df, quarters_df], axis=0)
        dummies = pd.get_dummies(concat_df['Day quarter'])
        concat_df = pd.concat([concat_df, dummies], axis=1)
        concat_df.rename(columns=day_quarters, inplace=True)

        #Delete fake quarter entries
        concat_df = concat_df.dropna(axis=0, subset=['time'])

        #Create rolling windows
        concat_df['AirflowRoll'] = concat_df['airflowFeedback'].rolling(window=12).mean()
        concat_df['SupplyAirRoll'] = concat_df['supplyAir'].rolling(window=12).mean()
        concat_df['ZoneTemperatureRoll'] = concat_df['zoneTemperature'].rolling(window=12).mean()

        concat_df['0-5Roll'] = concat_df['0-5'].rolling(window=12).median()
        concat_df['6-11Roll'] = concat_df['6-11'].rolling(window=12).median()
        concat_df['12-17Roll'] = concat_df['12-17'].rolling(window=12).median()
        concat_df['18-23Roll'] = concat_df['18-23'].rolling(window=21).median()

        #Keep only the interesting columns

        predict_df = concat_df[['AirflowRoll', 'SupplyAirRoll', 'ZoneTemperatureRoll', '0-5Roll', '6-11Roll', '12-17Roll', '18-23Roll']]
        predict_df = predict_df.dropna()

        return predict_df


    else:
        raise ValueError("{} not supported by script!".format(content_type))


def output_fn(prediction, response_content_type):
    """Format prediction output

    The default accept/content-type between containers for serial inference is JSON.
    We also want to set the ContentType or mimetype as the same value as accept so the next
    container can read the response payload correctly.
    """
    if response_content_type == "application/json":

        return prediction
    elif response_content_type == 'text/csv':
        return "csv content type"
    else:
        raise Exception("{} accept type is not supported by this script.".format(response_content_type))


def predict_fn(input_data, model):
    """Preprocess input data

    We implement this because the default predict_fn uses .predict(), but our model is a preprocessor
    so we want to use .transform().
    The output is returned in the following order:

        rest of features either one hot encoded or standardized
    """
    pred = model.predict(input_data)
    return pred


def model_fn(model_dir):
    """Deserialize fitted model
    """
    clf = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clf

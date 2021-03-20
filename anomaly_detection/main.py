import pandas as pd
import numpy as np

from common import auxiliary, dataManagement
from db import hvacDBMapping


if __name__ == '__main__':

    #db_session = dataManagement.getDBSession('hvac2018_04', 'factory2.czy5c8ouxr1q.us-west-2.rds.amazonaws.com', 'admin', 'Dexsys131')
    #results = dataManagement.loadData(session=db_session, startTimestamp='2018-07-11', endTimestamp='2018-10-11', componentTypes=['Thermafuser'])
    #thermafuser_ahu = results['Thermafuser']
    #print(thermafuser_ahu.shape)
    #thermafuser_df.to_csv('thermafuser_readings.csv')

    thermafuser_df = pd.read_csv('thermafuser_readings.csv', low_memory=False, index_col=False)
    thermafuser_df = thermafuser_df.drop('Unnamed: 0', axis=1)
    thermafuser_df = thermafuser_df.loc[thermafuser_df['_thermafuserId'] == 1]

    print(thermafuser_df.head())
    print(thermafuser_df.shape)



# File containing misc. utility functions

import pandas as pd
import datetime
import constants

# Reads, loads, and cleanses space weather data CSV and returns it as a pandas dataframe.
# Space weather dat a from https://celestrak.com/SpaceData/
def readSpaceWeatherData():
    # Only read in relevant columns
    df = pd.read_csv("../data/SW-All.csv", usecols = [
        constants.DATE_FIELD,
        constants.AP1_FIELD,
        constants.AP2_FIELD,
        constants.AP3_FIELD,
        constants.AP4_FIELD,
        constants.AP5_FIELD,
        constants.AP6_FIELD,
        constants.AP7_FIELD,
        constants.AP8_FIELD,
        constants.F107_FIELD,
        constants.F107_AVG_FIELD])

    # Drop dates past the cutoff of days with all needed data
    df[constants.DATE_FIELD] = pd.to_datetime(df[constants.DATE_FIELD]).dt.date
    df = df[df[constants.DATE_FIELD] <= constants.SW_CUTOFF_DATE]

    return df

readSpaceWeatherData()

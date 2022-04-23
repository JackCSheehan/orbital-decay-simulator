# File containing constants used throughout

import datetime
from astropy import units as u

# Names of space weather data fields
DATE_FIELD = "DATE"
AP1_FIELD = "AP1"
AP2_FIELD = "AP2"
AP3_FIELD = "AP3"
AP4_FIELD = "AP4"
AP5_FIELD = "AP5"
AP6_FIELD = "AP6"
AP7_FIELD = "AP7"
AP8_FIELD = "AP8"
F107_FIELD = "F10.7_OBS"
F107_AVG_FIELD = "F10.7_OBS_LAST81"

# Date to cutoff space whether data
SW_CUTOFF_DATE = datetime.date(2022, 6, 3)

# Indexes for parsing TLE
LINE1_INDEX = 0
LINE2_INDEX = 1

EARTH_RADIUS_KM = 6378.1366 * u.km
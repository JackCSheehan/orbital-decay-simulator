# File containing class needed to maintain space whether data and 
# calculate values from NRLMSIS 2.0

import pandas as pd
import numpy as np
import constants
from pymsis import msis

# Abstraction for calculating atmospheric properties
class Atmosphere:
    # Loads space weather data
    def __init__(self):
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

        self.spaceWeather = df

        # Described in Hoot, Roehrich, 1980: https://celestrak.com/NORAD/documentation/spacetrk.pdf
        self.referenceDensity = 2.461e-5 * constants.EARTH_RADIUS_KM

    # Returns pandas row corresponding to given day from space weather dataframe
    def getDaysSpaceWeather(self, dt):
        return self.spaceWeather[self.spaceWeather[constants.DATE_FIELD] == dt.date()]

    # Returns planetary equivalent amplitude for the given datetime and date's weather row
    def getAP(self, dt, spaceWeatherToday):
        # Convert current time to an integer 24-hour format
        currentTime = int(dt.strftime("%H%M"))

        currentAP = None

        # Get AP value based on time interval. Intervals from https://celestrak.com/SpaceData/SpaceWx-format.php
        if currentTime in range(0, 300):
            currentAP = spaceWeatherToday[constants.AP1_FIELD].values[0]
        elif currentTime in range(300, 600):
            currentAP = spaceWeatherToday[constants.AP2_FIELD].values[0]
        elif currentTime in range(600, 900):
            currentAP = spaceWeatherToday[constants.AP3_FIELD].values[0]
        elif currentTime in range(900, 1200):
            currentAP = spaceWeatherToday[constants.AP4_FIELD].values[0]
        elif currentTime in range(1200, 1500):
            currentAP = spaceWeatherToday[constants.AP5_FIELD].values[0]
        elif currentTime in range(1500, 1800):
            currentAP = spaceWeatherToday[constants.AP6_FIELD].values[0]
        elif currentTime in range(1800, 2100):
            currentAP = spaceWeatherToday[constants.AP7_FIELD].values[0]
        else:
            currentAP = spaceWeatherToday[constants.AP8_FIELD].values[0]

        return currentAP

    # Returns total atmospheric density (kg / m^3) from datetime, lat (deg), lon (deg), altitude (km), f107, f07a and ap
    def getDensity(self, dt, lon, lat, alt):
        spaceWeatherToday = self.getDaysSpaceWeather(dt)

        # Gather data from this row
        f107 = spaceWeatherToday[constants.F107_FIELD].values[0]
        f107Avg = spaceWeatherToday[constants.F107_AVG_FIELD].values[0]
        ap = self.getAP(dt, spaceWeatherToday)
        
        density = msis.run(dt, lon, lat, alt, f107, f107Avg, [[ap] * 7])[0][0]

        return density

    # Returns acceleration due to drag vector given datetime, coordinates, altitude, B*, and velocity vector (as numpy array)
    def getDragAcceleration(self, dt, lon, lat, alt, bstar, vel):
        velMagnitude = np.linalg.norm(vel)
        
        # Acceleration vector should be exactly opposite of velocity vector, so normalize it and flip it
        accelerationVector = -vel / velMagnitude

        density = self.getDensity(dt, lon, lat, alt)

        accelerationMagnitude = (density * bstar * velMagnitude**2) / self.referenceDensity

        # Acceleration magnitude is in m/s, divide by 1000 to make it km/s
        accelerationMagnitude /= 1000

        return accelerationVector * accelerationMagnitude

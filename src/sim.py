from astropy import units as u
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from orbital_mechanics import *
from astropy.coordinates import SphericalRepresentation
from poliastro.earth import *
from pymsis import msis
from datetime import *
import constants
import util

EARTH_RADIUS_KM = 6378.1366 * u.km

# Class used to encapsulate simulation
class Simulator:
    def __init__(self):
        self.spaceWeatherData = util.readSpaceWeatherData()

    # Returns COPY of space weather data
    def getSpaceWeatherData(self):
        return self.spaceWeatherData.copy()

    # Returns planetary equivalent amplitude for the given time given the given day's space weather row
    def getAP(self, dt):
        spaceWeatherToday = self.spaceWeatherData[self.spaceWeatherData[constants.DATE_FIELD] == dt.date()]

        # Convert current time to an integer 24-hour format
        currentTime = int(dt.strftime("%H%M"))

        currentAP = None

        # Get AP value based on time inveral. Intervals from https://celestrak.com/SpaceData/SpaceWx-format.php
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

    # Returns total atmospheric density from datetime, lat, lon, altitude, f107, f07a and ap
    def getAtmosDensity(self, dt, lon, lat, alt):
        # Datetime reduced to date since dataset only includes data for whole day, not time
        spaceWeatherToday = self.spaceWeatherData[self.spaceWeatherData[constants.DATE_FIELD] == dt.date()]

        # Gather data from this row
        f107 = spaceWeatherToday[constants.F107_FIELD].values[0]
        f107Avg = spaceWeatherToday[constants.F107_AVG_FIELD].values[0]
        ap = self.getAP(dt)
        
        density = msis.run(dt, lon, lat, alt, f107, f107Avg, [[ap] * 7])[0][0]

        return density

    # Driver function for orbital decay simulation
    def simulate(self, startDatetime, apogee, perigee, inclination, argOfPerigee, raan, trueAnomaly, mass, dragCoefficient, averageArea, timeStep):
        semiMajorAxis = calculateSemiMajorAxis(apogee, perigee)
        eccentricity = calculateEccentricity(apogee, perigee)

        orbit = Orbit.from_classical(Earth, semiMajorAxis * u.km, eccentricity * u.one, inclination * u.deg, raan * u.deg, argOfPerigee * u.deg, trueAnomaly * u.deg)
        #while orbit.r_p - EARTH_RADIUS_KM> 0:
            #orbit = orbit.propagate(1 * u.min)
            #print(orbit.raan)

        for i in range(0, 200):
            # Get lat/lon
            spherical = orbit.represent_as(SphericalRepresentation)
            lat = spherical.lat.to(u.deg)
            lon = spherical.lon.to(u.deg)
            alt = spherical.distance - EARTH_RADIUS_KM

            print("_____________________________________")
            print(f"Lat: {lat}  Lon: {lon}")
            print(f"Altitude: {alt}")

            orbit = orbit.propagate(1 * u.min)


date = datetime(2000, 1, 1, 12, 30)
lat = 55
lon = 45
height = 100
sim = Simulator()
#density = sim.getAtmosDensity(date, lon, lat, height)
print(sim.getAP(date))
        
        
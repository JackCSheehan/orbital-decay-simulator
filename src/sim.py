from astropy import units as u
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from orbital_mechanics import *
from astropy.coordinates import SphericalRepresentation
from poliastro.earth import *
from astropy.time import Time

from datetime import *
import constants
import util

EARTH_RADIUS_KM = 6378.1366 * u.km

# Class used to encapsulate simulation
class Simulator:
    def __init__(self):
        self.atmos = Atmosphere()

    # Driver function for orbital decay simulation
    def simulate(self, startDatetime, apogee, perigee, inclination, argOfPerigee, raan, trueAnomaly, mass, dragCoefficient, averageArea, timeStep):
        semiMajorAxis = calculateSemiMajorAxis(apogee, perigee)
        eccentricity = calculateEccentricity(apogee, perigee)

        # astropy requires its own custom Time object to be used
        epoch = Time(startDatetime.strftime("%Y-%m-%dT%H:%M:%S"))

        orbit = Orbit.from_classical(Earth, semiMajorAxis * u.km, eccentricity * u.one, inclination * u.deg, raan * u.deg, argOfPerigee * u.deg, trueAnomaly * u.deg, epoch)
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
        
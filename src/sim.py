from astropy import units as u
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from orbital_mechanics import *
from astropy.coordinates import SphericalRepresentation
from poliastro.earth import *

EARTH_RADIUS_KM = 6378.1366 * u.km

# Driver function for orbital decay simulation
def simulate(apogee, perigee, inclination, argOfPerigee, raan, trueAnomaly, mass, dragCoefficient, averageArea, timeStep):
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
        
        
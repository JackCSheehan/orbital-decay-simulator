from astropy import units as u
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from orbital_mechanics import *
from poliastro.ephem import *
from poliastro.core.spheroid_location import *

EARTH_RADIUS_KM = 6378.1366 * u.km

# Driver function for orbital decay simulation
def simulate(apogee, perigee, inclination, argOfPerigee, raan, trueAnomaly, mass, dragCoefficient, averageArea, timeStep):
    semiMajorAxis = calculateSemiMajorAxis(apogee, perigee)
    semiMinorAxis = calculateSemiMinorAxis(apogee, perigee)
    eccentricity = calculateEccentricity(apogee, perigee)

    orbit = Orbit.from_classical(Earth, semiMajorAxis * u.km, eccentricity * u.one, inclination * u.deg, raan * u.deg, argOfPerigee * u.deg, trueAnomaly * u.deg)

    #while orbit.r_p - EARTH_RADIUS_KM> 0:
        #orbit = orbit.propagate(1 * u.min)
        #print(orbit.raan)

    for i in range(0, 20):
        orbit = orbit.propagate(1 * u.min)
        ephem = Ephem.from_orbit(orbit, orbit.epoch)
    
        c = ephem._coordinates[0]
        print(cartesian_to_ellipsoidal(semiMajorAxis, semiMinorAxis, c.x, c.y, c.z))
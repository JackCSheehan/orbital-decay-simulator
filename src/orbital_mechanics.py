# File containing functions used for calculating orbital elements

import math

# Standard gravitational parameter of Earth
MU = 3.98601e5

# Earth radius in km
RADIUS = 6378.14

# Returns the orbital given the semi-major axis in km
def calculateOrbitalPeriod(a):
	return 2 * math.pi * math.sqrt(a**3 / MU)

# Returns semi-major axis in km from apogee and perigee in km
def calculateSemiMajorAxis(a, p):
	return ((a + RADIUS) + (p + RADIUS)) / 2
# File containing functions used for calculating orbital elements

import numpy as np
import pandas as pd
import math
import streamlit as st
from atmosphere import *
import html
from pyorbital.orbital import Orbital
import constants
from astropy import units as u
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from astropy.time import Time
from datetime import *

# Standard gravitational parameter of Earth in km^3/s^2
MU = 3.986004e5

# Earth radius in km
RADIUS = 6371

# Max number of points that the simulation will return in a dataframe
_MAX_POINTS = 200000

# J2 constant for Earth
J2 = 1.08262668e-3

# Returns a poliastro.twobody.Orbit object and a Pyorbital OrbitElements object from given raw TLE string and an epoch datetime
def parseOrbit(rawTLE, epoch):
	# Cleanse HTML from raw TLE and strip excess whitespace
	rawTLE = html.escape(rawTLE)
	rawTLE = rawTLE.strip()
		
	# Throw error if incorrect number of lines included in TLE input
	splitTLE = rawTLE.split("\n")
	if len(splitTLE) < 3:
		raise Exception()

	# Pyorbital orbital object contains parsed orbital elements from TLE
	orbital = Orbital("Satellite", line1 = splitTLE[constants.LINE1_INDEX], line2 = splitTLE[constants.LINE2_INDEX])

	# Astropy requires its own time format to be used
	epochAstropy = Time(epoch.strftime("%Y-%m-%dT%H:%M:%S"))

	# Gets the not-normalized position and velocity vectors of the orbit
	pos, vel = orbital.get_position(epoch, normalize = False)

	# get_position returns numpy arrays. Need to convert them to astropy quantities
	pos = list(pos) * u.km
	vel = list(vel) * u.km / u.s

	# Use pos, vel to create a poliastro orbit object
	poliastroOrbit = Orbit.from_vectors(Earth, pos, vel, epoch = epochAstropy)

	elements = orbital.orbit_elements

	return (poliastroOrbit, elements)

# Throws error if given apogee is < given perigee
def _checkExtrema(a, p):
	if a < p:
		raise Exception("Apogee must be larger than or equal to perigee")

# Returns the orbital period in seconds given the apogee and perigee in km
def calculateOrbitalPeriod(a, p):
	_checkExtrema(a, p)

	semiMajorAxis = calculateSemiMajorAxis(a, p)

	return 2 * math.pi * math.sqrt(semiMajorAxis**3 / MU)

# Returns semi-major axis in km from apogee and perigee in km
def calculateSemiMajorAxis(a, p):
	_checkExtrema(a, p)
	return ((a + RADIUS) + (p + RADIUS)) / 2

def calculateSemiMinorAxis(a, p):
	return math.sqrt((a + RADIUS) + (p + RADIUS))

# Returns eccentricity of orbit from apogee and perigee in km
def calculateEccentricity(a, p):
	_checkExtrema(a, p)
	return ((a + RADIUS) - (p + RADIUS)) / (2 * calculateSemiMajorAxis(a, p))

# Returns the angular velocity given an orbital velocity and distance from body
def calculateAngularVelocity(v, r):
	return v / r

# Returns result of Kepler's first law given apogee, perigee, and the number of degrees from perigee
def calculateMainFocusDistance(a, p, theta):
	_checkExtrema(a, p)

	# Calculate other elements needed
	semiMajorAxis = calculateSemiMajorAxis(a, p)
	eccentricity = calculateEccentricity(a, p)

	# Calculate numerator and denominator separately of the equation represented by Kepler's first law
	numerator = semiMajorAxis * (1 - eccentricity**2)
	denominator = 1 + eccentricity * np.cos(np.radians(theta))

	return numerator / denominator

# Calculates orbital velocity at a given angle theta from perigee given apogee and perigee
def calculateOrbitalVelocity(a, p, theta):
	_checkExtrema(a, p)

	# Calculate other elements needed
	semiMajorAxis = calculateSemiMajorAxis(a, p)
	distance = calculateMainFocusDistance(a, p, theta)

	ratioDifference = (2 / distance) - (1 / semiMajorAxis)

	return np.sqrt(MU * ratioDifference)

# Calculates the semi-major axis from the Vis-viva equation. Used to determine how the semi-major
# axis of an orbit changes due to velocity changes caused by drag force. Takes the distance from
# the body being orbited and the instantaneous orbital velocity
def calculateSemiMajorAxisFromVisViva(r, v):
	return -(MU * r) / (v**2 * r - 2 * MU)

# Returns the acceleration experienced by the given mass at the given height with the given velocity,
# drag coefficient, and reference area. Note that this uses Newton's second law F = ma and does
# not take into account any effects of the velocity approaching the speed of light
@st.cache(show_spinner = False)
def calculateAccelerationFromDrag(m, z, v, cd, area):
	# Check for non-zero mass
	if m == 0:
		raise Exception("Mass cannot be 0")

	density = getDensity(z)

	# Calculate drag force
	dragForce = .5 * density * v**2 * cd * area

	# Return acceleration
	return dragForce / m

# Main driver for orbital decay simulation. Takes initial apogee, perigee, inclination, drag coefficient, average
# cross-sectional area in m^2, and the time step for the simulation.
@st.cache(show_spinner = False)
def simulateOrbitalDecay(a, p, i, m, cd, area, timeStep):
	# Convert area to km^2
	area *= 1e-6

	# Initial parameters
	theta = 0
	time = 0
	distance = calculateMainFocusDistance(a, p, theta)
	altitude = distance - RADIUS
	eccentricity = calculateEccentricity(a, p)
	semiMajorAxis = calculateSemiMajorAxis(a, p)

	telemetry = {"time" : [], "dragAcceleration" : [], "velocity" : [], "apogee" : [], "perigee" : []}

	# Main simulation loop
	while altitude >= 0:
		distance = calculateMainFocusDistance(a, p, theta)
		velocity = calculateOrbitalVelocity(a, p, theta)
		altitude = distance - RADIUS

		if altitude <= 0 or altitude > 1000:
			break

		# Update velocity based on the acceleration due to atmospheric drag
		dragAcceleration = calculateAccelerationFromDrag(m, altitude, velocity, cd, area)
		velocity -=  timeStep * dragAcceleration
		
		theta +=  timeStep * calculateAngularVelocity(velocity, distance)
		semiMajorAxis = calculateSemiMajorAxisFromVisViva(distance, velocity)
		
		# Recalculate apogee and perigee for next iteration
		a = semiMajorAxis * (1 + eccentricity) - RADIUS
		p = semiMajorAxis * (1 - eccentricity) - RADIUS

		if a <= 0 or p <= 0 or a < p:
			break

		telemetry["time"].append(time)
		telemetry["dragAcceleration"].append(dragAcceleration)
		telemetry["velocity"].append(velocity)
		telemetry["apogee"].append(a)
		telemetry["perigee"].append(p)

		time += timeStep

	# Make sure apogee and perigee aren't negative
	if a < 0:
		a = 0
	if p < 0:
		p = 0

	# Try to create dataframe from telemetry if there is not too much data
	telemetryDataFrame = None

	try:
		telemetryDataFrame = pd.DataFrame(telemetry)
	
		# Even if dataframe is within size limits, too many records could slow down browser
		if len(telemetryDataFrame) > _MAX_POINTS:
			telemetryDataFrame = None
	except:
		pass
	
	return (time, telemetryDataFrame)
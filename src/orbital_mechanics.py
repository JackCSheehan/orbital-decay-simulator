# File containing functions used for calculating orbital elements

import numpy as np
import pandas as pd
import streamlit as st
from atmosphere import *

# Standard gravitational parameter of Earth in km^3/s^2
MU = 3.986004e5

# Earth radius in km
RADIUS = 6371

# Number of seconds to step during simulation
_TIME_STEP = 1

# Number of degrees Earth turns in a second
_OMEGA_EARTH = .25 / 60

# J2 constant for Earth
J2 = 1.08262668e-3

# Kilometer altitude to considerentry interface
_ENTRY_INTERFACE = 120

# Throws error if given apogee is < given perigee
def _checkExtrema(a, p):
	if a < p:
		raise Exception("Apogee must be larger than or equal to perigee")

# Returns the orbital given the apogee and perigee in km
def calculateOrbitalPeriod(a, p):
	_checkExtrema(a, p)

	semiMajorAxis = calculateSemiMajorAxis(a, p)

	return 2 * np.pi * np.sqrt(semiMajorAxis**3 / MU)

# Returns semi-major axis in km from apogee and perigee in km
def calculateSemiMajorAxis(a, p):
	_checkExtrema(a, p)
	return ((a + RADIUS) + (p + RADIUS)) / 2

# Returns the semi-minor axis in km from apogee and perigee in km
def calculateSemiMinorAxis(a, p):
	_checkExtrema(a, p)

	# Calculate semi-major axis and eccentricity
	semiMajorAxis = calculateSemiMajorAxis(a, p)
	eccentricity = calculateEccentricity(a, p)

	return semiMajorAxis * np.sqrt(1 - eccentricity**2)

# Returns eccentricity of orbit from apogee and perigee in km
def calculateEccentricity(a, p):
	_checkExtrema(a, p)
	return ((a + RADIUS) - (p + RADIUS)) / (2 * calculateSemiMajorAxis(a, p))

# Returns the change in theta (the change in angle of the orbiting spacecraft's position)
# in degrees given the angular velocity omega in degrees/s and the time in seconds
def calcualteDeltaTheta(omega, t):
	return omega * t

# Returns the angular velocity given an orbital velocity and distance from body
def calculateAngularVelocity(v, r):
	return v / r

# Returns distance from center of ellipse given apogee, perigee, and the number of degrees from perigee
def calculateCenterDistance(a, p, theta):
	_checkExtrema(a, p)

	# Calculate semi-axes
	semiMajorAxis = calculateSemiMajorAxis(a, p)
	semiMinorAxis = calculateSemiMinorAxis(a, p)

	# Calculate cosine wave elements
	amplitude = np.abs((semiMajorAxis - semiMinorAxis) / 2)
	verticalOffset = (semiMajorAxis + semiMinorAxis) / 2

	return amplitude * np.cos(2 * np.radians(theta)) + verticalOffset

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

# Returns current distance from main focus of elliptical orbit given the semi-major axis,
# eccentricity, and angle theta from the perigee
def calculateMainFocusDistanceFromSemiMajorAxis(semiMajorAxis, eccentricity, theta):
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

# Returns orbital velocity in km/s from semi-major axis
def calculateVelocityFromSemiMajorAxis(semiMajorAxis, eccentricity, theta):
	distance = calculateMainFocusDistanceFromSemiMajorAxis(semiMajorAxis, eccentricity, theta)

	ratioDifference = (2 / distance) - (1 / semiMajorAxis)

	return np.sqrt(MU * ratioDifference)

# Returns the angle to be added or subtracted to the longitude to correct for Earth's rotation
def calculateNodalDisplacementAngle(nodalDisplacement, angle):
	# sin(angle / 4) is used since it reaches 0 only at angle = 0 and 360
	return np.abs((nodalDisplacement / 2) * np.sin(np.radians(angle) / 4))

# Calculates the semi-major axis from the Vis-viva equation. Used to determine how the semi-major
# axis of an orbit changes due to velocity changes caused by drag force. Takes the distance from
# the body being orbited and the instantaneous orbital velocity
def calculateSemiMajorAxisFromVisViva(r, v):
	return -(MU * r) / (v**2 * r - 2 * MU)

# Returns Pandas dataframe of latitude and longitude coordinates for the initial orbit's ground track.
# Takes the initial orbit's apogee, perigee, inclination (in degrees), and starting longitude in degrees
@st.cache(show_spinner = False)
def calculateInitialOrbitTrackCoords(a, p, i, startingLat, startingLon):
	_checkExtrema(a, p)

	# Array of degrees to calculate various elements for
	theta = np.linspace(0, 360, 360)

	# Calculate period of given orbit
	period = calculateOrbitalPeriod(a, p)

	# Calculate the displacement of the Earth in a single orbit
	nodalDisplacement = period * _OMEGA_EARTH

	# Calculate radius of orbit at each theta
	r = calculateMainFocusDistance(a, p, theta)

	# Calculate Cartesian coordinates of orbit
	x = r * np.sin(np.radians(theta))
	y = r * np.cos(np.radians(theta)) * np.cos(np.radians(i))

	positions = np.stack((x, y), axis = -1)

	# Unit vector pointing through prime meridian
	mHat = np.array([1, 0])

	# Calculate array of latitude coordinates
	lat = i * np.cos(np.radians(theta))

	# Create emptyarray to hold longitude angles
	lon = np.empty(0)

	launchSiteEquivalentLon = 0

	# Iterate over position vectors
	for i in range(0, int(positions.size / 2)):
		# Calculate angle between mHat and current position vector using cosine rule
		angle = np.degrees(np.arccos(np.dot(positions[i], mHat) / (np.linalg.norm(positions[i]))))

		# Negate coordinates after index 90
		if i >= 90 and i < 270:
			angle *= -1

		# Correct for Earth's rotation
		if angle < 0:
			angle += calculateNodalDisplacementAngle(nodalDisplacement, angle)
		elif angle > 0 :
			angle -= calculateNodalDisplacementAngle(nodalDisplacement, angle)

		lon = np.append(lon, angle)

		if np.isclose(lat[i], startingLat, rtol = 2e-2):
			launchSiteEquivalentLon = angle

	# Add correction to launch site to determine first full orbit after launch
	lon -= launchSiteEquivalentLon - startingLon + nodalDisplacement

	return pd.DataFrame({"lat" : lat, "lon" : lon})

# Returns the acceleration experienced by the given mass at the given height with the velocity,
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

# Main driver for orbital decay simulation. Takes initial apogee, perigee, inclination, average
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
	period = calculateOrbitalPeriod(a, p)

	telemetry = {"time" : [], "dragAcceleration" : [], "period" : [], "apogee" : [], "perigee" : []}

	# Main simulation loop
	while altitude >= 0:
		period = calculateOrbitalPeriod(a, p)
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
		telemetry["period"].append(period)
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
		if len(telemetryDataFrame) > 100000:
			telemetryDataFrame = None
	except:
		pass
	
	return (time, telemetryDataFrame)

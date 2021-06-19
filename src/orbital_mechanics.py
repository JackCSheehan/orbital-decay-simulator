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
def calculateNodalDisplacementAngle(dn, angle):
	# sin(angle / 4) is used since it reaches 0 only at angle = 0 and 360
	return np.abs((dn / 2) * np.sin(np.radians(angle) / 4))

# Calculates the semi-major axis from the Vis-viva equation. Used to determine how the semi-major
# axis of an orbit changes due to velocity changes caused by drag force. Takes the distance from
# the body being orbited and the instantaneous orbital velocity
def calculateSemiMajorAxisFromVisViva(r, v):
	return -(MU * r) / (v**2 * r - 2 * MU)

# Returns Pandas dataframe of latitude and longitude coordinates for the initial orbit's ground track.
# Takes the initial orbit's apogee, perigee, inclination (in degrees), and starting longitude in degrees
@st.cache
def calculateInitialOrbitTrackCoords(a, p, i, startingLat, startingLon):
	_checkExtrema(a, p)

	# Calculate period of given orbit
	period = calculateOrbitalPeriod(a, p)

	# Calculate the displacement of the Earth in a single orbit
	nodalDisplacement = period * _OMEGA_EARTH

	# Array of degrees to calculate various elements for
	theta = np.linspace(0, 360, 360)

	# Calculate array of latitude coordinates
	lat = i * np.cos(np.radians(theta))

	# Calculate radius of orbit at each theta
	r = calculateMainFocusDistance(a, p, theta)

	# Calculate Cartesian coordinates of orbit
	x = r * np.sin(np.radians(theta))
	y = r * np.cos(np.radians(theta)) * np.cos(np.radians(i))

	# Get unit position vector of satellite at any given point in orbit
	positions = np.stack((x, y), axis = -1)

	# Unit vector pointing through prime meridian on XY plane
	mHat = np.array([1, 0])

	# Flag to indicate if coordinates should be negated. Needed to correct for limited range of arccos
	shouldNegate = False

	# Create emptyarray to hold longitude angles
	lon = np.empty(0)

	# Longitude with corresponding latitude that lines up with launch site. Used to know how much
	# to shift orbit by in order to line up initial orbit with launch site
	launchSiteEquivalentLon = 0

	# Iterate over position vectors
	for i in range(0, int(positions.size / 2)):
		# Calculate angle between mHat and current position vector using cosine rule
		angle = np.degrees(np.arccos(np.dot(positions[i], mHat) / (np.linalg.norm(positions[i]))))

		# Negate coordinates after index 90
		if i == 90:
			shouldNegate = True

		# Stop negating at index 270
		if i == 270:
			shouldNegate = False

		# Negate angle if negate flag is tripped
		if shouldNegate:
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
	lon -= np.abs(launchSiteEquivalentLon - startingLon) + nodalDisplacement
	
	# Add lat and lon of launch site to mark it on the map
	lat = np.append(lat, startingLat)
	lon = np.append(lon, startingLon)

	# Insert color for normal ground track points
	colors = np.full(lat.size - 1, "red")

	# Append color for launch site
	colors = np.append(colors, "yellow")

	# Insert marker type for normal ground track points
	markers = np.full(lat.size - 1, "circle")

	# Append marker for launch site
	markers = np.append(markers, "star")

	return pd.DataFrame({"lat" : lat, "lon" : lon,  "colors" : colors, "markers" : markers})

# Returns the acceleration experienced by the given mass at the given height with the velocity,
# drag coefficient, and reference area. Note that this uses Newton's second law F = ma and does
# not take into account any effects of the velocity approaching the speed of light
def calculateAccelerationFromDrag(m, z, v, cd, area):
	# Check for non-zero mass
	if m == 0:
		raise Exception("Mass cannot be 0")

	density = getDensity(z)

	# Calculate drag force
	dragForce = .5 * density * v**2 * cd * area

	# Adjust units since Newtons use meters as distance unit and km are used everywhere else
	dragForce /= 1000

	# Return acceleration
	return dragForce / m

# Returns the nodal precession rate of an orbit. Takes the semi-major axis, period, eccentricity, and
# inclination of the orbit
def calculateNodalPrecessionRate(semiMajorAxis, period, eccentricity, i):
	# Calculate factors separately before returning
	firstFactor = RADIUS**2 / (semiMajorAxis * (1 - eccentricity**2))**2
	secondFactor = J2 * (2 * np.pi / period) * np.cos(np.radians(i))
	return (-3 / 2) * firstFactor * secondFactor	

# Main driver for orbital decay simulation. Takes initial apogee, perigee, and inclination
@st.cache
def simulateOrbitalDecay(a, p, i, m, cd, area):
	# Holds all telemetry data from simulation
	telemetry = {"time" : [], "apogee" : [], "perigee" : [], "semiMajorAxis" : [], "altitude" : [], "velocity" : []}

	# Initial parameters
	theta = 0
	time = 0
	distance = calculateMainFocusDistance(a, p, theta)
	altitude = distance - RADIUS
	eccentricity = calculateEccentricity(a, p)
	semiMajorAxis = calculateSemiMajorAxis(a, p)
	totalDragAcceleration = 0

	timeOfInterface = 0

	# Main simulation loop
	while altitude >= 0:
		#telemetry["time"].append(time)
		#telemetry["altitude"].append(altitude)

		# Calculate updated elements
		distance = calculateMainFocusDistance(a, p, theta)
		velocity = calculateOrbitalVelocity(a, p, theta)
		altitude = distance - RADIUS

		if altitude <= 0:
			break

		velocity -= calculateAccelerationFromDrag(m, altitude, velocity, cd, area)
		
		theta += calculateAngularVelocity(velocity, distance)
		semiMajorAxis = calculateSemiMajorAxisFromVisViva(distance, velocity)
		
		# Recalculate apogee and perigee for next iteration
		a = semiMajorAxis * (1 + eccentricity) - RADIUS
		p = semiMajorAxis * (1 - eccentricity) - RADIUS

		if a <= 0 or p <= 0 or a < p:
			break

		if altitude <= _ENTRY_INTERFACE:
			timeOfInterface = time

		time += 1
	return time

#simulateOrbitalDecay(200, 200, 0, 10000, 2.2, .6)

# Calculate sample altitude/time and vel/time to test function
# Check density function
# Function to calc. accel is producing numbers way too big

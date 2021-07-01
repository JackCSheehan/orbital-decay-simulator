# File containing Streamlit interface controls

import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from bokeh.io import curdoc
from enum import Enum
from plotting import *
import time
from datetime import timedelta
from datetime import datetime, time
import altair as alt

# Format string for degree inputs
_DEGREE_FORMAT = "%d°"

# Format  string for vector head inputs
_VECTOR_FORMAT = "%.2g"

# Format string for higher prece
_HIGH_PRECISION_NUMBER = "%.5f"

# Main driver for Streamlit inputs and calling of other files' functions
def main():
	# Blank string needed to ensure Streamlit recognizes first multi-line string as markdown
	""

	# Intro text
	"""
	# Orbital Decay Simulator
	Calculates and visualizes orbital decay using atmospheric drag.
	Written by [Jack Sheehan](https://github.com/JackCSheehan).

	This tool is open source. Find a bug or want to contribute? Check out the source on
	[GitHub](https://github.com/JackCSheehan/orbital-decay-simulator).

	**Disclaimer:** This tool is for educational/hobbyist purposes only. Mistakes in calculations
	will be fixed as soon as possible, but this tools uses generalized and approximated models. Real-life
	precision should not be expected.

	---
	## How it Works
	This simulator works by calculating how drag force affects orbital elements over
	time. More complicated causes of orbital decay, such as solar radiation pressure, are not included as part
	of the decay calculations. The 1976 U.S. Standard Atmosphere model is used to calculate the density at a
	particular altitude.
	"""

	"""
	---
	## Part 1: Orbital Parameters
	Enter the basic parameters of your spacecraft's starting orbit.
	"""

	# Create 2 columns for organizing orbit parameter data
	orbit_col1, orbit_col2 = st.beta_columns(2)

	# Populate column 1 inputs
	with orbit_col1:
		startingLat = st.number_input("Starting Latitude (°)", 0.0, 90.0, 0.0, help = "The latitude, in degrees, that your vehicle launched from")
		apogee = st.number_input("Apogee (km)", 0, 1000, help = "The distance the farthest part of your orbit is from Earth's surface")
		startDate = st.date_input("Orbit insertion date", help = "Date of insertion into starting orbit")

	# Populate column 2 inputs
	with orbit_col2:
		startingLon = st.number_input("Starting Longitude (°)", -180.0, 180.0, 0.0, help = "The longitude, in degrees, that your vehicle launched from")
		perigee = st.number_input("Perigee (km)", 0, 1000, help = "The distance the closest part of your orbit is from Earth's surface")
		startTime = st.time_input("Orbit insertion time (UTC)", value = time(0, 0, 0), help = "Time of insertion into starting orbit in UTC. Uses 24-hour time")

	inclination = st.slider("Inclination (°)", 0, 90, 0, format = _DEGREE_FORMAT, help = "The angle of your orbit with respect to Earth's equatorial plane")

	# Check that inclination is valid given launch site latitude
	if inclination < startingLat:
		"""
		**Orbital inclination cannot be less than starting latitude**
		"""
		return

	"""
	#### Initial Orbit Ground Track
	"""
	initialOrbitCoords = calculateInitialOrbitTrackCoords(apogee, perigee, inclination, startingLat, startingLon)
	st.plotly_chart(plotGroundTrack(initialOrbitCoords, startingLat, startingLon))

	"""
	---
	## Part 2: Spacecraft and Simulation Parameters
	"""

	"""
	#### Basic Information
	Enter in some basic information about your spacecraft.
	"""

	# Create columns to organize spacecraft parameter inputs
	craft_col1, craft_col2 = st.beta_columns(2)

	mass = craft_col1.number_input("Mass (kg)", 1, help = "The constant mass of your spacecraft")
	dragCoefficient = craft_col2.number_input("Drag Coefficient", .10, 5.00, 1.15, format = _HIGH_PRECISION_NUMBER, help = "Also know as coefficient of drag. Often approximated as 2.2 for spherical spacecraft")
	timeStep = st.number_input("Time Step (s)", 1, 3600, help = "The number of seconds skipped in simulation loop. Lower numbers are more accurate, but take much longer")

	"""
	---
	## Part 3: Simulation and Visualizations
	"""

	# Show spinner and call appropriate functions
	with st.spinner("Please wait while your simulation is being run..."):
		pass

	if st.button("Simulate"):
		totalElapsedSeconds, telemetry = simulateOrbitalDecay(apogee, perigee, inclination, mass, dragCoefficient, 105e-6, initialOrbitCoords["lon"][0], timeStep)
		startDatetime = datetime.combine(startDate, startTime)

		landingDate = startDatetime + timedelta(seconds = totalElapsedSeconds)
		landingDateStr = landingDate.strftime("%B %d, %Y at %H:%M:%S %Z")

		f"""
		#### Estimated Landing

		At `{landingDateStr}`

		The spacecraft has the possibility of landing between `{inclination}`° latitude and `-{inclination}`° latitude. The possible landing area is highlighted on the map below.
		"""

		st.plotly_chart(plotPossibleLandingArea(inclination))

if __name__ == "__main__":
	main()
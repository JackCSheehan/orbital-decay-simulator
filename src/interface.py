# File containing Streamlit interface controls
import streamlit as st
import math
from plotting import *
import time
from datetime import timedelta
from datetime import datetime, time
import altair as alt
import numpy as np

# Format string for degree inputs
_DEGREE_FORMAT = "%d°"

# Prompt text for lat and lon inputs
_LAT_PROMPT = "Starting Latitude (°)"
_LON_PROMPT = "Starting Longitude (°)"

# Help text for lat and lon inputs
_LAT_HELP = "The latitude, in degrees, that your vehicle launched from"
_LON_HELP = "The longitude, in degrees, that your vehicle launched from"

# Prompt text for inclination input
_INCLINATION_PROMPT = "Inclination (°)"

# Help text for inclination input
_INCLINATION_HELP = "The angle of your orbit with respect to Earth's equatorial plane"

st.set_page_config(page_title = "Orbital Decay Simulator", layout = "centered", page_icon = "../assets/favicon.png")

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
	will be fixed as soon as possible, but this tools uses generalized and approximated models. **Real-life
	accuracy should not be expected.**

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

	orbitCol1, orbitCol2 = st.beta_columns(2)

	with orbitCol1:
		# Placeholder for lat input
		latInput = st.empty()

		startingLat = latInput.number_input(_LAT_PROMPT, 0.0, 90.0, 0.0, help = _LAT_HELP)
		apogee = st.number_input("Apogee (km)", 150, 1000, help = "The distance the farthest part of your orbit is from Earth's surface")
		startDate = st.date_input("Orbit insertion date", help = "Date of insertion into starting orbit")
		
		# Placeholder for inclination input
		inclinationInput = st.empty()

		inclination = inclinationInput.slider(_INCLINATION_PROMPT, 0, 90, 0, format = _DEGREE_FORMAT, help = _INCLINATION_HELP)

	with orbitCol2:
		# Placeholder inputs for lon input
		lonInput = st.empty()

		startingLon = lonInput.number_input(_LON_PROMPT, -180.0, 180.0, 0.0, help = _LON_HELP)
		perigee = st.number_input("Perigee (km)", 150, 1000, help = "The distance the closest part of your orbit is from Earth's surface")
		startTime = st.time_input("Orbit insertion time (UTC)", value = time(0, 0, 0), help = "Time of insertion into starting orbit. Uses 24-hour time")
		commonSitePreset = st.selectbox("Launch site preset", list(COMMON_LAUNCH_SITES.keys()), help = "Select from a list of common launch sites")
	
	plotCommonSites = st.checkbox("Visualize common launch sites", help = "Option to plot points of common launch sites on the map")

	# If site preset isn't custom, fill in relevant details of the site
	if commonSitePreset != "Custom":
		startingLat = latInput.number_input(_LAT_PROMPT, COMMON_LAUNCH_SITES[commonSitePreset]["lat"], help = _LAT_HELP)
		startingLon = lonInput.number_input(_LON_PROMPT, -180.0, 180.0, float(COMMON_LAUNCH_SITES[commonSitePreset]["lon"]), help = _LON_HELP)

		inclination = inclinationInput.slider(_INCLINATION_PROMPT, 0, 90, math.ceil(COMMON_LAUNCH_SITES[commonSitePreset]["lat"]), format = _DEGREE_FORMAT, help = _INCLINATION_HELP)

	# Check that apogee is >= perigee
	if apogee < perigee:
		"""
		#### Apogee must be greater than or equal to perigee
		"""
		return

	# Check that inclination is valid given launch site latitude
	if inclination < startingLat:
		"""
		#### Orbital inclination cannot be less than starting latitude
		"""
		return

	"""
	#### Initial Orbit Ground Track

	Shown is the first full orbit after orbital insertion. The seam in the orbit is a visualizations of the effect of Earth's rotation.
	"""
	initialOrbitCoords = calculateInitialOrbitTrackCoords(apogee, perigee, inclination, startingLat, startingLon)
	st.plotly_chart(plotGroundTrack(initialOrbitCoords, startingLat, startingLon, plotCommonSites), use_container_width = True)

	"""
	---
	## Part 2: Spacecraft and Simulation Parameters
	"""

	"""
	#### Basic Information
	Enter in some basic information about your spacecraft.
	"""

	craftCol1, craftCol2 = st.beta_columns(2)

	with craftCol1:
		mass = st.number_input("Mass (kg)", 1, None, 1000, help = "The constant mass of your spacecraft")

	with craftCol2:
		dragCoefficient = craftCol2.number_input("Drag Coefficient", .10, 5.00, 1.15, help = "Also know as coefficient of drag. Often approximated as 2.2 for spherical spacecraft")
	
	averageArea = st.number_input("Average cross-sectional area (m²)", .10, None, 1.00, help = "The average cross-sectional area of your spacecraft perpendicular to airflow")
	timeStep = st.number_input("Time Step (s)", 1, 3600, 300, help = "The number of seconds skipped in simulation loop. Lower numbers are more accurate, but take much longer. Larger numbers are faster, but lead to less precise visualizations and predictions")

	"""
	---
	## Part 3: Simulation and Visualizations
	"""

	# Show spinner and call appropriate functions
	with st.spinner("Please wait while your simulation is being run..."):
		pass

	if st.button("Simulate"):
		with st.spinner("Running Simulation..."):
			totalElapsedSeconds, telemetry = simulateOrbitalDecay(apogee, perigee, inclination, mass, dragCoefficient, averageArea, timeStep)
			
			startDatetime = datetime.combine(startDate, startTime)

			landingDatetime = startDatetime + timedelta(seconds = totalElapsedSeconds)
			landingDateStr = landingDatetime.strftime("%B %d, %Y at %H:%M:%S %Z")

			f"""
			#### Estimated Landing

			`{landingDateStr}`

			The spacecraft has the possibility of landing between `{inclination}°` latitude and `-{inclination}°` latitude. The possible landing area is highlighted on the map below.
			"""

			st.plotly_chart(plotPossibleLandingArea(inclination), use_container_width = True)

		if telemetry is None:
			"""
			There are too many data points to generate visualizations. Please increases the time step and rerun the simulation.
			"""
		else:
			with st.spinner("Generating Visualizations..."):
				"""
				Left click and drag to pan the plots. Use your mouse wheel to zoom. Hovering your mouse over a point will show its exact values.
				"""

				# Plot telemetry
				"#### Apogee Over Time"
				st.altair_chart(plotTelemetry(telemetry, "apogee", "Apogee (km)"), use_container_width = True)

				"#### Perigee Over Time"
				st.altair_chart(plotTelemetry(telemetry, "perigee", "Perigee (km)"), use_container_width = True)

				"#### Velocity Over Time"
				st.altair_chart(plotTelemetry(telemetry, "velocity", "Velocity (km/s)"), use_container_width = True)

				"#### Acceleration Due to Drag Over Time"
				st.altair_chart(plotTelemetry(telemetry, "dragAcceleration", "Acceleration Due to Drag m/s²"), use_container_width = True)

if __name__ == "__main__":
	main()
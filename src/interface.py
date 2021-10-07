# File containing Streamlit interface controls
import streamlit as st
from plotting import *
from datetime import timedelta, datetime, time

# Format string for degree inputs
_DEGREE_FORMAT = "%d°"

st.set_page_config(page_title = "Orbital Decay Simulator", layout = "centered", page_icon = "../assets/favicon.png")

# Main driver for Streamlit inputs and calling of other files' functions
def main():
	# Blank string needed to ensure Streamlit recognizes first multi-line string as markdown
	""

	# Intro text
	"""
	# :earth_americas: Orbital Decay Simulator
	Calculates and visualizes orbital decay.
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
	of the decay calculations. The 1976 U.S. Standard Atmosphere model is used to calculate the density of the atmosphere at a
	particular altitude.

	Start by supplying a few orbital elements and viewing the accompanying visualization. Next, supply some information about your
	spacecraft. Finally, click the "Simulate" button to run the simulation. When the simulation is completed, you will be given
	an estimate of when the spacecraft will land back on Earth as well as visualizations of the vehicle's trajectory while its orbit decayed.
	"""

	"""
	---
	## Part 1: Orbital Parameters
	Enter the basic parameters of your spacecraft's starting orbit.
	
	Only the apogee, perigee, inclination, and insertion date/time need to be provided for the
	simulator to work. The remaining parameters are only needed to more precisely plot the ground track of your orbit. If you do not care about the ground track's
	accuracy, you can leave the RAAN, argument of perigee, and true anomaly fields at their default values.
	
	The launch latitude and longitude are also optional as they simply allow you to visualize the launch site on the map.
	"""

	orbitCol1, orbitCol2 = st.columns(2)

	with orbitCol1:
		# Placeholder for lat input
		latInput = st.empty()

		startingLat = latInput.number_input("Launch Site Latitude (°)", -90.0, 90.0, 0.0, help = "The latitude, in degrees, that your vehicle launched from")
		apogee = st.number_input("Apogee (km)", 150, 1000, help = "The distance the farthest part of your orbit is from Earth's surface")
		startDate = st.date_input("Orbit insertion date", help = "Date of insertion into starting orbit")
		inclination = st.slider("Inclination (°)", 0, 90, 0, format = _DEGREE_FORMAT, help = "The angle of your orbit with respect to Earth's equatorial plane")
		argOfPerigee = st.slider("Argument of Perigee (°)", 0, 360, 0, format = _DEGREE_FORMAT, help = "Angle between the ascending node and perigee")

		# Check that inclination is valid given launch site latitude
		if inclination < abs(startingLat):
			"""
			#### Orbital inclination cannot be less than starting latitude
			"""
			return

	with orbitCol2:
		# Placeholder inputs for lon input
		lonInput = st.empty()

		startingLon = lonInput.number_input("Launch Site Longitude (°)", -180.0, 180.0, 0.0, help = "The longitude, in degrees, that your vehicle launched from")
		perigee = st.number_input("Perigee (km)", 150, 1000, help = "The distance the closest part of your orbit is from Earth's surface")
		startTime = st.time_input("Orbit insertion time (UTC)", value = time(0, 0, 0), help = "Time of insertion into starting orbit. Uses 24-hour time")
		raan = st.slider("Right Ascension of the Ascending Node (°)", 0, 360, 0, format = _DEGREE_FORMAT, help = "Angle between the I unit vector and the ascending node")
		trueAnomaly = st.slider("True Anomaly (°)", 0, 360, 0, format = _DEGREE_FORMAT, help = "Angle between spacecraft's position and perigee at epoch")

	# Check that apogee is >= perigee
	if apogee < perigee:
		"""
		#### Apogee must be greater than or equal to perigee
		"""
		return

	"""
	#### Ground Track
	Shown below is the ground track of your orbit.
	"""
	proj = st.selectbox("Map Projection", PROJECTION_TYPES)
	st.plotly_chart(plotGroundTrack(apogee, perigee, inclination, raan, argOfPerigee, trueAnomaly, startingLat, startingLon, proj), use_container_width = True)

	"""
	---
	## Part 2: Spacecraft and Simulation Parameters
	"""

	"""
	#### Basic Information
	Enter in some basic information about your spacecraft.
	"""

	craftCol1, craftCol2 = st.columns(2)

	with craftCol1:
		mass = st.number_input("Mass (kg)", 1, None, 1000, help = "The constant mass of your spacecraft")

	with craftCol2:
		dragCoefficient = st.number_input("Drag Coefficient", .10, 5.00, 1.15, help = "Also know as coefficient of drag. Often approximated as 2.2 for spherical spacecraft")
	
	averageArea = st.number_input("Average cross-sectional area (m²)", .0001, None, 1.00, help = "The average cross-sectional area of your spacecraft perpendicular to airflow")
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
			"""

			if inclination == 0:
				"The spacecraft was put into an equatorial orbit and as such can only land on the Equator, which is shown on the map below."
			else:
				f"""
				The spacecraft has the possibility of landing between `{inclination}°` latitude and `-{inclination}°` latitude. The spacecraft's ground track over several orbits is shown on the map below.
				"""
				

			st.plotly_chart(plotGroundTrack(apogee, perigee, inclination, raan, argOfPerigee, trueAnomaly, startingLat, startingLon, proj, True), use_container_width = True)

		if telemetry is None:
			"""
			There are too many data points to generate visualizations. Please increases the time step and rerun the simulation.
			"""
		else:
			with st.spinner("Generating Visualizations..."):
				"""
				#### Telemetry Visualizations

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
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
from datetime import datetime
import altair as alt

# Format string for degree inputs
_DEGREE_FORMAT = "%d°"

# Format  string for vector head inputs
_VECTOR_FORMAT = "%.2g"

# Main driver for Streamlit inputs and calling of other files' functions
def main():
	# Blank string needed to ensure Streamlit recognizes first multi-line string as markdown
	""

	# Intro text
	"""
	# Orbital Decay Simulator
	Calculates and visualizes orbital decay using atmospheric drag and nodal precession.
	Written by [Jack Sheehan](https://github.com/JackCSheehan).

	This tool is open source. Find a bug or want to contribute? Check out the source on
	[GitHub](https://github.com/JackCSheehan/orbital-decay-simulator).

	**Disclaimer:** This tool is for educational/hobbyist purposes only. Mistakes in calculations
	will be fixed as soon as possible, but this tools uses generalized and approximated models. Real-life
	precision should not be expected.

	---
	## How it Works
	This simulator works by calculating the how drag force and nodal precession affect orbital elements over
	time. More complicated causes of orbital decay, such as solar radiation pressure, are not included as part
	of the decay calculations. The 1976 U.S. Standard Atmosphere model is used to calculate the density at a
	particular altitude.

	---
	## How to Use It
	This simulator works by first taking in a series of parameters and data from the user. After some
	calculations, the user will be presented with the expected entry interface time and the
	expected landing location. Directions are included as you go, so scroll down to get started!

	---
	"""

	"""
	## Part 1: Orbital Parameters
	Enter the basic parameters of your spacecraft's starting orbit.
	"""

	# Create 2 columns for organizing orbit parameter data
	orbit_col1, orbit_col2 = st.beta_columns(2)

	# Populate column 1 inputs
	with orbit_col1:
		startingLat = st.number_input("Starting Latitude (°)", -180.0, 180.0, 0.0, help = "The latitude, in degrees, that your vehicle launched from")
		apogee = st.number_input("Apogee (km)", 0, 1000, help = "The distance the farthest part of your orbit is from Earth's surface")
		startDate = st.date_input("Orbit insertion date", help = "Date of insertion into starting orbit")

	# Populate column 2 inputs
	with orbit_col2:
		startingLon = st.number_input("Starting Longitude (°)", -180.0, 180.0, 0.0, help = "The longitude, in degrees, that your vehicle launched from")
		perigee = st.number_input("Perigee (km)", 0, 1000, help = "The distance the closest part of your orbit is from Earth's surface")
		startTime = st.time_input("Orbit insertion time (UTC)", help = "Time of insertion into starting orbit in UTC. Uses 24-hour time")

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
	st.plotly_chart(plotGroundTrack(apogee, perigee, inclination, startingLat, startingLon))

	"""
	---
	## Part  2: Spacecraft Geometry
	Submit a 3D model (.obj file) that roughly approximates the size and shape of your spacecraft. This
	model will be used to calculate the area of the orthographic projects of the spacecraft normal to the
	velocity vector.

	Each unit of distance in your model is considered 1 meter.

	Note that the fewer vertices your model has, the faster the simulation will be able to run.
	"""

	# Create file picker to upload 3D object files
	objFile = st.file_uploader("3D Model of Spacecraft (.obj files only)", ".obj", help = "Help")

	# Will hold spacecraft coords parsed from .obj file
	coords = None

	# Message to show prior to 3D model upload
	if (objFile == None):
		"Please enter a 3D model before continuing."
		return
	else:
		coords = parseObj(objFile)
		st.plotly_chart(plotSpacecraft(coords))
		f"""
		Initial orthographic projection area: `{calculateOrthographicProjectionArea(coords["x"], coords["y"], coords["z"])}` cubic meters
		"""

	"""
	---
	## Part 3: Spacecraft Parameters
	"""

	"""
	#### Basic Information
	Enter in some basic information about your spacecraft.
	"""

	# Create columns to organize spacecraft parameter inputs
	craft_col1, craft_col2 = st.beta_columns(2)

	mass = craft_col1.number_input("Mass (kg)", 1, help = "The constant mass of your spacecraft")
	drag_coefficient = craft_col2.number_input("Drag Coefficient", help = "Also know as coefficient of drag. Often approximated as 2.2 for spherical spacecraft")

	"""
	#### Center of Pressure and Center of Mass
	Use the sliders to indicate roughly where the center of mass and center of pressure are on your
	spacecraft.
	"""

	# Create columns to organize centers inputs
	centers_col1, centers_col2 = st.beta_columns(2)

	# Center of mass inputs
	with centers_col1:
		"Center of Mass"
		comX = st.slider("X", float(coords["x"].min()), float(coords["x"].max()), float(coords["x"].median()), format = _VECTOR_FORMAT, help = "X coordinate of the center of mass")
		comY = st.slider("Y", float(coords["y"].min()), float(coords["y"].max()), float(coords["y"].median()), format = _VECTOR_FORMAT, help = "Y coordinate of the center of mass")
		comZ = st.slider("Z", float(coords["z"].min()), float(coords["z"].max()), float(coords["z"].median()), format = _VECTOR_FORMAT, help = "Z coordinate of the center of mass")

	# Center of pressure inputs
	with centers_col2:
		"Center of Pressure"
		copX = st.slider("X", float(coords["x"].min()), float(coords["x"].max()), float(coords["x"].median()), format = _VECTOR_FORMAT, key = "1", help = "X coordinate of the center of pressure")
		copY = st.slider("Y", float(coords["y"].min()), float(coords["y"].max()), float(coords["y"].median()), format = _VECTOR_FORMAT, key = "1", help = "Y coordinate of the center of pressure")
		copZ = st.slider("Z", float(coords["z"].min()), float(coords["z"].max()), float(coords["z"].median()), format = _VECTOR_FORMAT, key = "1", help = "Z coordinate of the center of pressure")

	# Plot center of mass/center of pressure
	st.plotly_chart(plotSpacecraft(coords,
		com = pd.DataFrame({"x" : [comX], "y" : [comY], "z" : [comZ]}),
		cop = pd.DataFrame({"x" : [copX], "y" : [copY], "z" : [copZ]})
		)
	)

	"""
	#### Tumble Axis and Rate
	Indicate the tumble axis of your spacecraft and its rotation rate. If your spacecraft isn't tumbling,
	simply leave RPM at 0.
	"""

	# Create columns to organize tumble data
	tumbleCol1, tumbleCol2 = st.beta_columns(2)

	with tumbleCol1:
		tumbleX = st.slider("X", 0.0, 1.0, 0.0, format = _VECTOR_FORMAT, help = "X component of tumble rotation vector")
		tumbleY = st.slider("Y", 0.0, 1.0, 0.0, format = _VECTOR_FORMAT, help = "Y component of tumble rotation vector")
	
	with tumbleCol2:
		tumbleZ = st.slider("Z", 0.0, 1.0, 0.0, format = _VECTOR_FORMAT, help = "Z component of tumble rotation vector")
		rpm = st.number_input("Rotations per Minute (RPM)", 0, help = "How many times per minute your spacecraft completes a full rotation")

	st.plotly_chart(plotSpacecraft(coords, True,
		tumbleVectorHead = pd.DataFrame({"x" : [tumbleX], "y" : [tumbleY], "z" : [tumbleZ]}),
		com = pd.DataFrame({"x" : [comX], "y" : [comY], "z" : [comZ]}),
		)
	)

	"""
	---
	## Part 4: Simulation and Visualizations
	"""

	# Show spinner and call appropriate functions
	with st.spinner("Please wait while your simulation is being run..."):
		pass

	if st.button("Simulate"):
		elapsedSeconds = simulateOrbitalDecay(apogee, perigee, inclination, mass, drag_coefficient, .093)

		f"""
		#### Estimated Entry Interface

		Over `lat° E`, `lon° N` at `00:00` UTC

		`map showing final orbit and location of estimated entry interface`
		"""
		startDatetime = datetime.combine(startDate, startTime)
		landingDate = startDatetime + timedelta(seconds = elapsedSeconds)
		landingDateStr = landingDate.strftime("%B %d, %Y at %H:%M:%S %Z")
		f"""
		#### Estimated Landing

		At `lat° E`, `lon° N` on `{landingDateStr}`

		`map showing location of estimated landing location`
		"""

	"""
	#### Telemetry Plots
	`vel/time plot`

	`semi-major axis/time`

	`period/time`

	`apogee/time`

	`perigee/time`

	`drag force acceleration/time`

	`eccentricity/time`

	`inclination/time`

	`latitude/time`

	`longitude/time`
	"""

	"""
	#### Telemetry Table

	`display of telemetry in table from Pandas dataframe`
	"""

if __name__ == "__main__":
	main()
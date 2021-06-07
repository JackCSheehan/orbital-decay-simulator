# File containing Streamlit interface controls

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import time
from orbital_mechanics import *

# Format string for degree inputs
_DEGREE_FORMAT = "%d°"

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
		start_date = st.date_input("Orbit insertion date", help = "Date of insertion into starting orbit")

	# Populate column 2 inputs
	with orbit_col2:
		startingLon = st.number_input("Starting Longitude (°)", -180.0, 180.0, 0.0, help = "The longitude, in degrees, that your vehicle launched from")
		perigee = st.number_input("Perigee (km)", 0, 1000, help = "The distance the closest part of your orbit is from Earth's surface")
		state_time = st.time_input("Orbit insertion time (UTC)", help = "Time of insertion into starting orbit in UTC. Uses 24-hour time")

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
	coords = calculateInitialOrbitTrackCoords(apogee, perigee, inclination, startingLat, startingLon)

	fig = go.Figure(go.Scattergeo(
		lat = coords["lat"],
		lon = coords["lon"],
		marker_color = coords["colors"],
		marker_symbol = coords["markers"],
	))

	fig.update_geos(
		projection_type = "equirectangular",
		bgcolor = "rgba(0,0,0,0)",
		showframe = False,
		showocean = True,
		oceancolor = "#7aadff",
		lakecolor = "#7aadff",
		rivercolor = "#7aadff",
		showrivers = True,
		landcolor = "#1b332a",
		coastlinecolor = "#1b332a")
	fig.update_layout(
		width = 1000,
		margin={"r":0,"t":0,"l":0,"b":0})

	st.plotly_chart(fig)

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
	obj_file = st.file_uploader("3D Model of Spacecraft (.obj files only)", ".obj", help = "Help")

	# Message to show prior to 3D model upload
	if (obj_file == None):
		"Please enter a 3D model before continuing."
		#return

	"""
	---
	## Part 3: Spacecraft Parameters
	"""
	# Render given spacecraft model
	"#### Rendering of Given Model"

	"`rendering`"

	"""
	#### Basic Information
	Enter in some basic information about your spacecraft.
	"""

	# Create columns to organize spacecraft parameter inputs
	craft_col1, craft_col2 = st.beta_columns(2)

	mass = craft_col1.number_input("Mass (kg)", help = "The constant mass of your spacecraft")
	drag_coefficient = craft_col2.number_input("Drag Coefficient", help = "Also know as coefficient of drag. Often approximated as 2.2 for spherical spacecraft")

	"""
	#### Tumble Axis and Rate
	Indicate the tumble axis of your spacecraft and its rotation rate. If your spacecraft isn't tumbling,
	simply leave RPM at 0.
	"""

	#  Create columns to organize tumble data
	tumble_col1, tumble_col2 = st.beta_columns(2)

	alpha = tumble_col1.slider("Alpha/α (°)", 0, 360, 0, format = _DEGREE_FORMAT)
	beta = tumble_col1.slider("Beta/β (°)", 0, 360, 0, format = _DEGREE_FORMAT)
	gamma = tumble_col1.slider("Gamma/γ (°)", 0, 360, 0, format = _DEGREE_FORMAT)
	rpm = tumble_col1.number_input("Rotations per Minute (RPM)", 0, help = "How many times per minute your spacecraft completes a full rotation")

	tumble_col2.write("`rendering`")

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
		com_x_offset = st.slider("X Offset", help = "Offset from X = 0 of the center of mass")
		com_y_offset = st.slider("Y Offset", help = "Offset from Y = 0 of the center of mass")
		com_z_offset = st.slider("Z Offset", help = "Offset from Y = 0 of the center of mass")

	# Center of pressure inputs
	with centers_col2:
		"Center of Pressure"
		cop_x_offset = st.slider("X Offset", key = "1", help = "Offset from X = 0 of the center of pressure")
		cop_y_offset = st.slider("Y Offset", key = "1", help = "Offset from X = 0 of the center of pressure")
		cop_z_offset = st.slider("Z Offset", key = "1", help = "Offset from X = 0 of the center of pressure")

	"`rendering`"

	"""
	---
	## Part 4: Simulation and Visualizations
	"""

	# Show spinner and call appropriate functions
	with st.spinner("Please wait while your simulation is being run..."):
		pass

	f"""
	#### Estimated Entry Interface

	Over `lat° E`, `lon° N` at `00:00` UTC

	`map showing final orbit and location of estimated entry interface`
	"""

	f"""
	#### Estimated Landing

	At `lat° E`, `lon° N` at `00:00` UTC

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
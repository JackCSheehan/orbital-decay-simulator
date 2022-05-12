# File containing functions used to plot visualizations

from turtle import showturtle
from matplotlib.pyplot import figure
from orbital_mechanics import *
import streamlit as st
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
from poliastro.earth.plotting import GroundtrackPlotter
from poliastro.earth import EarthSatellite
from poliastro.bodies import Earth
from poliastro.util import time_range
from poliastro.plotting import StaticOrbitPlotter

from poliastro.examples import iss
from poliastro.plotting import OrbitPlotter2D, OrbitPlotter3D
import sys

# Color of ground track points and orbit outlines
ORBIT_COLOR = "red"

# Map element colors
LAND_COLOR = "white"
WATER_COLOR = "#2a7bd1"	# Color used to match the poliastro Earth color
COUNTRY_COLOR = "lightgray"
	
# Returns Plotly plot of a ground track of the given Poliastro orbit
@st.cache(show_spinner = False)
def plotGroundTrack(orbit):
	fig = GroundtrackPlotter()

	sat = EarthSatellite(orbit, None)
	t_span = time_range(orbit.epoch, end = orbit.epoch + orbit.period)
	
	# Plot ground track
	fig.plot(
		sat,
		t_span,
		label = "Ground Track",
		color = ORBIT_COLOR,
		marker={"size": 0, "color": "rgba(0, 0, 0, 0)"},
	)

	# Format map
	fig.fig.update_geos(
		bgcolor = "rgba(0, 0, 0, 0)",
		showframe = False,
		lataxis = {"showgrid" : False},
		lonaxis = {"showgrid" : False},
		showlakes = True,
		showcountries = True,
		showrivers = True,
		oceancolor = WATER_COLOR,
		landcolor = LAND_COLOR,
		lakecolor = WATER_COLOR,
		rivercolor = WATER_COLOR,
		countrycolor = COUNTRY_COLOR,
		projection_type = "equirectangular"
	)

	fig.fig.update_layout(
		showlegend = False,
		margin = {"l" : 0, "r" : 0, "b" : 0, "t" : 0},
		hoverlabel = {"bgcolor": "white"}
	)

	return fig.fig

# Returns formatted 2D and 3D plot figures of the given orbit using Poliastro's plotting classes
def plotOrbit(orbit):
	fig2D = OrbitPlotter2D().plot(orbit, color = ORBIT_COLOR)
	fig2D.update_layout(showlegend = False,
		paper_bgcolor = "rgba(0, 0, 0, 0)",
		plot_bgcolor = "rgba(0, 0, 0, 0)",
		margin = {"l": 0, "r": 0, "b": 0, "t": 0, "pad": 0},
		xaxis = {"visible": False},
		yaxis = {"visible": False}
	)

	fig3D = OrbitPlotter3D().plot(orbit, color = ORBIT_COLOR)
	fig3D.update_layout(scene = {
			"xaxis": {
				"visible": False
			},
			"yaxis": {
				"visible": False
			},
			"zaxis": {
				"visible": False
			},
		},
		margin = {"l": 0, "r": 0, "b": 0, "t": 0, "pad": 0}
	)

	return (fig2D, fig3D)

# Returns Altair chart visualizing telemetry data. Takes telemetry dataframe, name of column to visualize over time, and the
# Y-axis label for the plot
def plotTelemetry(telemetry, column, label):
	# Get smallest and largest datapoints for scaling
	smallestY = telemetry[column].min()
	largestY = telemetry[column].max()

	smallestX = telemetry["time"].min()
	largestX = telemetry["time"].max()

	return alt.Chart(telemetry).mark_line().encode(
		x = alt.X("time", axis = alt.Axis(title = "Time (s)"), scale = alt.Scale(domain = (smallestX, largestX))),
		y = alt.Y(column, axis = alt.Axis(title = label), scale = alt.Scale(domain = (smallestY, largestY))),
		tooltip = ["time", column]
	).add_selection(
		alt.selection_interval(bind = "scales")
	)
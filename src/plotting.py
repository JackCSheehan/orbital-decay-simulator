# File containing functions used to plot visualizations

from orbital_mechanics import *
import streamlit as st
import altair as alt
from poliastro.earth.plotting import GroundtrackPlotter
from poliastro.earth import EarthSatellite
from poliastro.util import time_range

from poliastro.examples import iss
from poliastro.plotting import OrbitPlotter2D, OrbitPlotter3D

# Color of ground track points
_TRACK_COLOR = "darkblue"

# Map element colors
_LAND_COLOR = "white"
_WATER_COLOR = "rgb(140, 181, 245)"
_COUNTRY_COLOR = "lightgray"

# Color of launch site marker
_LAUNCH_SITE_COLOR = "red"

# Plotly projection types
PROJECTION_TYPES = [
	"Equirectangular",
	"Mercator",
	"Orthographic",
	"Natural Earth",
	"Kavrayskiy7",
	"Miller",
	"Robinson",
	"Eckert4",
	"Azimuthal Equal Area",
	"Azimuthal Equidistant",
	"Conic Equal Area",
	"Conic Conformal",
	"Conic Equidistant",
	"Gnomonic",
	"Stereographic",
	"Mollweide",
	"Hammer",
	"Transverse Mercator",
	"Winkel Tripel",
	"Aitoff",
	"Sinusoidal"
]

def plotOrbit():
	orbit = iss

	orbitPlotter2D = OrbitPlotter2D()

	orbitPlotter3D = OrbitPlotter3D()

	return (orbitPlotter2D.plot(iss), orbitPlotter3D.plot(iss))

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
		color = _TRACK_COLOR,
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
		oceancolor = _WATER_COLOR,
		landcolor = _LAND_COLOR,
		lakecolor = _WATER_COLOR,
		rivercolor = _WATER_COLOR,
		countrycolor = _COUNTRY_COLOR,
		projection_type = "equirectangular"
	)

	fig.fig.update_layout(
		showlegend = False,
		margin = {"l" : 0, "r" : 0, "b" : 0, "t" : 0},
		hoverlabel = {"bgcolor": "white"}
	)

	return fig.fig

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
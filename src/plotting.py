# File containing functions used to plot visualizations

from orbital_mechanics import *
import plotly.graph_objects as go
import streamlit as st
import altair as alt
from poliastro.earth.plotting import GroundtrackPlotter
from poliastro.earth import EarthSatellite
from poliastro.twobody import Orbit
from poliastro.bodies import Earth
from astropy import units as u
from poliastro.util import time_range
import plotly.graph_objects as go
from astropy.time import Time

from astropy import units as u
from poliastro.examples import iss
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.plotting import OrbitPlotter2D, OrbitPlotter3D

# Color of ground track points
_TRACK_COLOR = "darkblue"

# Map element colors
_LAND_COLOR = "white"
_WATER_COLOR = "rgb(140, 181, 245)"
_COUNTRY_COLOR = "lightgray"

# Color of launch site marker
_LAUNCH_SITE_COLOR = "crimson"

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

# Returns Plotly figure of scatter mapbox plot of the ground track of an orbit given: apogee, perigee,
# inclination, right ascension of the ascending node, argument of perigee, true anomaly, starting lat,
# and starting lon
@st.cache(show_spinner = False)
def plotGroundTrack(epochDateTime, a, p, i, raan, argOfPerigee, trueAnomaly, startingLat, startingLon, proj = PROJECTION_TYPES[0], showMany = False):
	fig = GroundtrackPlotter()

	# Derive orbital elements needed to plot ground track
	period = calculateOrbitalPeriod(a, p)
	semiMajoraxis = calculateSemiMajorAxis(a, p)
	eccentricity = calculateEccentricity(a, p)

	# Multiply period if many orbit tracks are to be shown
	if showMany:
		period *= 86400 / period / 2


	epoch = Time(epochDateTime.strftime("%Y-%m-%dT%H:%M:%S"))
	print(epoch)

	# Create objection needed for poliastro GroundPlotter
	orbit = Orbit.from_classical(Earth, semiMajoraxis * u.km, eccentricity * u.one, i * u.deg, raan * u.deg, argOfPerigee * u.deg, trueAnomaly * u.deg, epoch)
	sat = EarthSatellite(orbit, None)
	t_span = time_range(orbit.epoch, end = orbit.epoch + period * u.s)
	
	# Plot ground track
	fig.plot(
		sat,
		t_span,
		label = "Ground Track",
		color = _TRACK_COLOR,
		marker={"size": 0, "symbol": "triangle-right"},
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
		projection_type = proj.lower()
	)

	fig.fig.update_traces(
		marker = {"color" : "rgba(0, 0, 0, 0)"},
	)

	fig.fig.update_layout(
		showlegend = False,
		margin = {"l" : 0, "r" : 0, "b" : 0, "t" : 0}
	)

	# Add launch site point
	fig.add_trace(
		go.Scattergeo(
			lat = [startingLat],
			lon = [startingLon],
			name = "Launch Site 🚀",
			marker = {"color" : _LAUNCH_SITE_COLOR}
		)
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
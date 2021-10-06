# File containing functions used to plot visualizations
from re import M
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

# Color of ground track points
_TRACK_COLOR = "darkblue"

_LAND_COLOR = "rgb(101, 186, 103)"
_WATER_COLOR = "rgb(140, 181, 245)"

# Color of launch site marker
_LAUNCH_SITE_COLOR = "crimson"

# Color of common launch sites
_COMMON_SITES_COLOR = "mediumblue"

# Data for common launch sites
COMMON_LAUNCH_SITES = {
	"Custom" : {"lat" : None, "lon" : None},
	"[US, FL] Kennedy Space Center" : {"lat" : 28.57, "lon" : -80.65},
	"[US, FL] Cape Canaveral Space Force Station": {"lat" : 28.49, "lon" : -80.57},
	"[US, VA] Wallops Flight Facility" : {"lat" : 37.94, "lon" : -75.47},
	"[US, CA] Vandenberg Space Force Base" : {"lat" : 34.74, "lon" : -120.57},
	"[KZ] Baikonur Cosmodrome" : {"lat" : 45.96, "lon" : 63.31},
	"[RU] Plesetsk Cosmodrome" : {"lat" : 62.93, "lon" : 40.57},
	"[GF] Guiana Space Center" : {"lat" : 5.17, "lon" : -52.68},
	"[JP] Tanegashima Space Center" : {"lat" : 30.37, "lon" : 130.96}
}

# Returns Plotly figure of scatter mapbox plot of the ground track of an orbit given: apogee, perigee,
# inclination, starting lat, starting lon, and a flag indicating whether common launch sites should be plotted
def plotGroundTrack(a, p, i, startingLat, startingLon, plotCommonSites):
	fig = GroundtrackPlotter()

	period = calculateOrbitalPeriod(a, p)
	perigeeR = calculateMainFocusDistance(a, p, 0)
	perigeeV = calculateOrbitalVelocity(a, p, 0)
	rVector = np.array([np.cos(np.radians(i)) * perigeeR, 0, np.sin(np.radians(i)) * perigeeR]) * u.km
	vVector = np.array([0, perigeeV, 0]) * u.km / u.s

	orbit = Orbit.from_vectors(Earth, rVector, vVector)
	sat = EarthSatellite(orbit, None)
	t_span = time_range(orbit.epoch - period * u.s, periods = 150, end = orbit.epoch + period * u.s)
	
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
		oceancolor = _WATER_COLOR,
		landcolor = _LAND_COLOR,
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

	# Plot common launch sites if needed
	if plotCommonSites:
		# Collect data from common sites
		for site, coords in COMMON_LAUNCH_SITES.items():
			# Plot common sites
			fig.add_trace(
				go.Scattergeo(
					lat = [coords["lat"]],
					lon = [coords["lon"]],
					text = site,
					hoverinfo = "text",
					marker = {"color" : _COMMON_SITES_COLOR}
				)
			)

	return fig.fig

# Returns Plotly figure showing possible landing area. Takes inclination of orbit
def plotPossibleLandingArea(i):
	# Create plotly figure
	fig = go.Figure(go.Scattermapbox(
		mode = "lines",
		fill = "toself",
		lat = [i, i, -i, -i],
		lon = [-180, 180, 180, -180],
		marker = {"opacity" : [0, 0, 0, 0]},
		marker_color = _TRACK_COLOR,
		),
	)

	fig.update_layout(
		mapbox = {"style" : "open-street-map"},
		showlegend = False,
		margin = {"l" : 0, "r" : 0, "b" : 0, "t" : 0}
	)

	return fig

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
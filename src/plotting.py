# File containing functions used to plot visualizations
from orbital_mechanics import *
import plotly.graph_objects as go
import streamlit as st
import altair as alt

# Color of ground track points
_TRACK_COLOR = "dodgerblue"

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

# Returns Plotly figure of scatter mapbox plot of the ground track of an orbit given: a Pandas dataframe
# with the latitude and longitude, the starting latitude, starting longitude, and a flag indicating
# whether or not to plot common launch sites
@st.cache(show_spinner = False)
def plotGroundTrack(coords, startingLat, startingLon, plotCommonSites):
	# Add lat and lon of launch site to mark it on the map
	coords = coords.append(pd.DataFrame([[startingLat, startingLon]], columns = ["lat", "lon"]))

	# Ground track and launch site point colors
	colors = np.full(coords["lat"].size - 1, _TRACK_COLOR)
	colors = np.append(colors, _LAUNCH_SITE_COLOR)

	text = np.full(coords["lat"].size - 1, "lat: %{lat}°, lon: %{lon}°<extra></extra>")
	text = np.append(text, "🚀 Launch site<extra></extra>")

	# Add common sites if user wants to see them
	if plotCommonSites:
		for name, data in COMMON_LAUNCH_SITES.items():
			coords = coords.append(pd.DataFrame([[data["lat"], data["lon"]]], columns = ["lat", "lon"]))
			colors = np.append(colors, _COMMON_SITES_COLOR)
			text = np.append(text, name + "<extra></extra>")

	# Create plotly figure
	fig = go.Figure(go.Scattergeo(
		mode = "lines",
		lat = coords["lat"],
		lon = coords["lon"],
		marker_color = colors,
		hoverinfo = None,
		hovertemplate = text,
	))

	fig.update_geos(projection_type = "equirectangular")

	fig.update_layout(
		#mapbox = {"style" : "open-street-map"},
		showlegend = False,
		margin = {"l" : 0, "r" : 0, "b" : 0, "t" : 0}
	)

	return fig

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
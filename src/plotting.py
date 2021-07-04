# File containing functions used to plot visualizations
from orbital_mechanics import *
import plotly.graph_objects as go
import streamlit as st
import altair as alt
from model import *

# Color of water on Earth maps
_WATER_COLOR = "#7aadff"

# Color of land on Earth maps
_LAND_COLOR = "#1b332a"

# Color of points used to outline spacecraft model
_SPACECRAFT_COLOR = "#213ec4"

# Color of center of mass and center of pressure
_COM_COLOR = "#bf4343"
_COP_COLOR = "#2ecbff"

# Color of tumble axis
_TUMBLE_AXIS_COLOR = "#bf4343"

# Airflow vector color
_AIRFLOW_COLOR = "#b85300"

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
	fig = go.Figure(go.Scattermapbox(
		mode = "markers",
		lat = coords["lat"],
		lon = coords["lon"],
		marker_color = colors,
		hoverinfo = None,
		hovertemplate = text,
	))

	fig.update_layout(
		mapbox = {"style" : "open-street-map"},
		showlegend = False,
		margin = {"l" : 0, "r" : 0, "b" : 0, "t" : 0}
	)

	return fig

# Returns Plotly figure of the given 3D coordinates of a 3D model. showAirflow indicates whether to
# plot an airflow vector and tumbleVectorHead is a Pandas DataFrame that indicates the coordinates
# of the tip of the tumble rotation axis measured from the center of mass. com and cop are Pandas
# DataFrames representing the coordinates of the center of mass and center of pressure, respectively
@st.cache(show_spinner = False)
def plotSpacecraft(initialOrbitCoords, showAirflow = False, tumbleVectorHead = pd.DataFrame(), com = pd.DataFrame(), cop = pd.DataFrame()):
	# Largest Y value used to determine where to put airflow vector on Y axis
	largestY = coords["y"].max()

	# Median Z used to determine where to put airflow vector on Z axis
	medianZ = coords["z"].median()

	# Add vertex coords for spacecraft model
	data = [
		go.Scatter3d(
			x = coords["x"],
			y = coords["y"],
			z = coords["z"],
			mode = "markers",
			hoverinfo = "x+y+z+text",
			text = "Spacecraft",
			marker_color = _SPACECRAFT_COLOR
		)
	]

	# Add plot of airflow vector if needed
	if showAirflow:
		data.append(
			go.Cone(
				x = [0],
				y = [largestY + 1],
				z = [medianZ],
				u = [0],
				v = [-1],
				w = [0],
				hoverinfo = "text",
				text = "Airflow Direction",
				showscale = False,
			)
		)

	# Add center of mass point if needed
	if not com.empty:
		data.append(
			go.Scatter3d(
				x = com["x"],
				y = com["y"],
				z = com["z"],
				hoverinfo = "text",
				text = "Center of Mass",
				marker_color = _COM_COLOR
			)
		)

	# Add center of pressure point if needed
	if not cop.empty:
		data.append(
			go.Scatter3d(
				x = cop["x"],
				y = cop["y"],
				z = cop["z"],
				hoverinfo = "text",
				text = "Center of Pressure",
				marker_color = _COP_COLOR
			)
		)

	# Add tumble axis vector if needed
	if not tumbleVectorHead.empty:
		# Generate vector coords
		x = np.append(com["x"], com["x"] + tumbleVectorHead["x"])
		y = np.append(com["y"], com["y"] + tumbleVectorHead["y"])
		z = np.append(com["z"], com["z"] + tumbleVectorHead["z"])

		data.append(
			go.Scatter3d(
				x = x,
				y = y,
				z = z,
				hoverinfo = "text",
				text = "Tumble Vector",
				marker_color = _TUMBLE_AXIS_COLOR
			)
		)

	fig = go.Figure(data)
	fig.update_layout(
		showlegend = False,
		height = 500,
		margin={"r" : 0, "t" : 0, "l" : 0, "b" : 0},
		scene_camera = {"eye" : {"x" : -2, "y" : 1.2, "z" : 1.2}}
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
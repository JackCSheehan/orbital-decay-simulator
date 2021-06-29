# File containing functions used to plot visualizations

from orbital_mechanics import *
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
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

# Returns Plotly figure of scatter geo plot with given apogee, perigee, starting latitude, and starting
# longitude
@st.cache
def plotGroundTrack(coords):
	# Create plotly figure
	fig = go.Figure(go.Scattermapbox(
		mode = "markers",
		lat = coords["lat"],
		lon = coords["lon"],
		marker_color = coords["colors"],
	))

	fig.update_layout(
		width = 1000,
		mapbox = {"style" : "open-street-map"},
		showlegend = False,
		margin = {"l" : 0, "r" : 0, "b" : 0, "t" : 0}
	)

	return fig

# Returns Plotly figure of the given 3D coordinates of a 3D model. showAirflow indicates whether to
# plot an airflow vector and tumbleVectorHead is a Pandas DataFrame that indicates the coordinates
# of the tip of the tumble rotation axis measured from the center of mass. com and cop are Pandas
# DataFrames representing the coordinates of the center of mass and center of pressure, respectively
@st.cache
def plotSpacecraft(coords, showAirflow = False, tumbleVectorHead = pd.DataFrame(), com = pd.DataFrame(), cop = pd.DataFrame()):
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

# Returns Plotly figure showing possible landing area. Takes inclination of final orbit
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
		width = 1000,
		mapbox = {"style" : "open-street-map"},
		showlegend = False,
		margin = {"l" : 0, "r" : 0, "b" : 0, "t" : 0}
	)


	return fig
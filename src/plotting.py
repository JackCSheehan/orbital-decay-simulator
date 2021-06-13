# File containing functions used to plot visualizations

from orbital_mechanics import *
import plotly.graph_objects as go
import plotly.express as px
from model import *

# Color of water on Earth maps
_WATER_COLOR = "#7aadff"

# Color of land on Earth maps
_LAND_COLOR = "#1b332a"

# Returns Plotly figure of scatter geo plot with given apogee, perigee, starting latitude, and starting
# longitude
def plotGroundTrack(a, p, i, startingLat, startingLon):
	# Calculate ground track coordinates
	coords = calculateInitialOrbitTrackCoords(a, p, i, startingLat, startingLon)

	# Create plotly figure
	fig = go.Figure(go.Scattergeo(
		lat = coords["lat"],
		lon = coords["lon"],
		marker_color = coords["colors"],
		marker_symbol = coords["markers"],
	))

	# Set map settings
	fig.update_geos(
		projection_type = "equirectangular",
		bgcolor = "rgba(0,0,0,0)",
		showframe = False,
		showocean = True,
		oceancolor = _WATER_COLOR,
		lakecolor = _WATER_COLOR,
		rivercolor = _WATER_COLOR,
		showrivers = True,
		landcolor = _LAND_COLOR,
		coastlinecolor = _LAND_COLOR)
	fig.update_layout(
		width = 1000,
		margin={"r":0,"t":0,"l":0,"b":0})

	return fig

# Returns Plotly figure of the given 3D coordinates of a 3D model. showAirflow indicates whether to
# plot an airflow vector and tumbleAxisAngles is a Pandas DataFrame that indicates the angles to rotate
# the craft. If tumble axis angles are given, 
def plotSpacecraft(coords, showAirflow = False, tumbleAxisAngles = None):
	# Largest Y value used to determine where to put airflow vector
	largestY = coords["y"].max()

	# Add vertex coords for spacecraft model
	data = [
		go.Scatter3d(
			x = coords["x"],
			y = coords["y"],
			z = coords["z"],
			mode = "markers",
			name = "Spacecraft",
		)
	]

	# Margin for bottom of graph
	bottomMargin = 0

	# Add plot of airflow vector if needed
	if showAirflow:
		data.append(
			go.Cone(
				x = [0],
				y = [largestY + 1],
				z = [0],
				u = [0],
				v = [-1],
				w = [0],
				hoverinfo = "text",
				text = "Airflow Direction",
				showscale = False,
			)
		)

		# Adjust bottom pad for graph where airflow is shown
		if showAirflow:
			bottomMargin = 100

	fig = go.Figure(data)
	fig.update_layout(
		showlegend = False,
		height = 500,
		margin={"r" : 0, "t" : 0, "l" : 0, "b" : 0},
		scene_camera = {"eye" : {"x" : -2, "y" : 1.2, "z" : 1.2}}
	)

	return fig
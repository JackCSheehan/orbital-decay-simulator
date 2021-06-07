# File containing functions used to plot visualizations

from orbital_mechanics import *
import plotly.graph_objects as go

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
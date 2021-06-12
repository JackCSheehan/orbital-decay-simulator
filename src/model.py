# File containing functions needed to parse .obj files and deal with 3D spacecraft models

import numpy as np
import pandas as pd
from io import StringIO
from scipy.spatial import ConvexHull

# Symbol that indicates that current line represents a vertex
_VERTEX_RECORD = "v"

# Index that holds record symbol ("v", "l", etc.)
_RECORD_INDEX = 0

# Indices for vector info in a vector record
_OBJ_X = 1
_OBJ_Y = 2
_OBJ_Z = 3

# Indices for coordinate info in a set of Numpy arrays of coordinates
_ARRAY_X = 0
_ARRAY_Z = 1

# Parses .obj file given Streamlit UploadedFile object and returns a Pandas dataframe with the
# X, Y, and Z coordinates of its vertices
def parseObj(obj):
	# Create arrays to hold x, y, and z vertex coordinates
	x = np.empty(0)
	y = np.empty(0)
	z = np.empty(0)

	# Get file contents from Streamlit file uploader
	objData = StringIO(obj.getvalue().decode("UTF-8")).read().split("\n")

	# Iterate through .obj to find vertex and line info
	for line in objData:
		# Strip whitespace from line and split at inner spaces
		lineSplit = line.strip().split(" ")
		
		# If this line contains vertex info
		if lineSplit[_RECORD_INDEX] == _VERTEX_RECORD:
			x = np.append(x, float(lineSplit[_OBJ_X]))
			y = np.append(y, float(lineSplit[_OBJ_Y]))
			z = np.append(z, float(lineSplit[_OBJ_Z]))

	return pd.DataFrame({"x" : x, "y" : y, "z" : z})

# Takes a X, Y, and Z coordinates to project onto the XZ plane (the plane normal to the velocity vector).
# Returns the projected coordinates
def _projectPoints(x, y, z):
	y *= 0
	return (x, y, z)

# Takes the X, Y, and Z coordinates of a 3D object and return the area of the orthographic projection
def calculateOrthographicProjectionArea(x, y, z):
	# Find all unique outer points from the projection
	outerPoints = ConvexHull(np.stack((x, z), -1))

	return outerPoints.volume

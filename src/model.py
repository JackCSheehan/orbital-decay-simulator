# File containing functions needed to parse .obj files and deal with 3D spacecraft models

import numpy as np
import pandas as pd
from io import StringIO

# Symbol that indicates that current line represents a vertex
_VERTEX_RECORD = "v"

# Index that holds record symbol ("v", "l", etc.)
_RECORD_INDEX = 0

# Indices for vector info in a vector record
_X_INDEX = 1
_Y_INDEX = 2
_Z_INDEX = 3

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
			print(lineSplit)
			x = np.append(x, float(lineSplit[_X_INDEX]))
			y = np.append(y, float(lineSplit[_Y_INDEX]))
			z = np.append(z, float(lineSplit[_Z_INDEX]))

	return pd.DataFrame({"x" : x, "y" : y, "z" : z})
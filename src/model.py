# File containing functions needed to parse .obj files and deal with 3D spacecraft models

import numpy as np
import pandas as pd

# Symbol that indicates that current line represents a vertex
_VERTEX_RECORD = "v"

# Symbol that indicates that current line represents a line
_LINE_RECORD = "l"

# Index that holds record symbol ("v", "l", etc.)
_RECORD_INDEX = 0

# Indices for vector info in a vector record
_X_INDEX = 1
_Y_INDEX = 2
_Z_INDEX = 3

# Parses .obj file at given path and returns a Pandas dataframe with the X and Y coordinates
# of its vertices
def parseObj(path):
	f = open(path)

	# Create arrays to hold x, y, and z vertex coordinates
	x = np.empty(0)
	y = np.empty(0)
	z = np.empty(0)

	# Iterate through .obj to find vertex and line info
	for line in f:
		# Strip whitespace from line and split at inner spaces
		lineSplit = line.strip().split(" ")

		# If this line contains vertex info
		if lineSplit[_RECORD_INDEX] == _VERTEX_RECORD:
			x = np.append(x, float(lineSplit[_X_INDEX]))
			y = np.append(y, float(lineSplit[_Y_INDEX]))
			z = np.append(z, float(lineSplit[_Z_INDEX]))

	f.close()

	return pd.DataFrame({"x" : x, "y" : y, "z" : z})
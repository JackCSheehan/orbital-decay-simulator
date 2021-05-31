# File containing implementation of 1976 U.S. Standard Atmosphere

# Universal gas constant in N*m/(kmol*K)
_R = 8.31432e3

# Acceleration due to gravity at sea-level in m/s^2
_G0 = 9.80665

# Temperature at sea-level in Kelvin
_T0 = 288.15

# Molecular weight of various gasses ordered 0 - 9. Corresponds
# to Table 3 in the 1976 U.S. Standard Atmosphere paper
_MOL_WEIGHT = {
	0 : 28.0134,
	1 : 31.9988,
	2 : 39.948,
	3 : 44.00995,
	4 : 20.183,
	5 : 4.0026,
	6 : 83.8,
	7 : 131.3,
	8 : 16.04303,
	9 : 2.01594
}

# Geopotential height reference at various subscripts. Corresponds
# to Table 4 in the 1976 U.S. Standard Atmosphere paper
_GEOPOTENTIAL_HEIGHT_REF = {
	0 : 0,
	1 : 11,
	2 : 20,
	3 : 32,
	4 : 47,
	5 : 51,
	6 : 71,
	7 : 84.8520
}

# Molecular-scale temperature gradient at various subscripts. Corresponds
# to Table 4 in the 1976 U.S. Standard Atmosphere paper
_MOL_SCALE_TEMP_GRADIENT = {
	0 : -6.5,
	1 : 0.0,
	2 : 1.0,
	3 : 2.8,
	4 : 0.0,
	5 : -2.8,
	6 : -2.0,
}

# Molecular-scale temperature at various subscripts. Calculated using
# the given sea-level temperature and the molecular-scale temperature
# gradients at each height
_MOL_TEMP = {
	0 : _T0,
	1 : 216.65,
	2 : 216.65,
}

# Get T_mb for a particular subscript
def _getMolTemp(sub):
	print()
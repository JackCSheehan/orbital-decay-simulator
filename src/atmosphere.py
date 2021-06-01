# File containing implementation of 1976 U.S. Standard Atmosphere

import math

# Universal gas constant in N*km/(kmol*K)
_R = .00831432

# Acceleration due to gravity at sea level in km/s^2
_G0 = .00980665

# Temperature at sea level in K
_T0 = 288.15

# Effective radius of the Earth in km
_R0 = 6356.766

# Mean molecular weight of gasses at sea level in kg/kmol
_M0 = 28.9644

# Geopotential height reference at various subscripts. Corresponds
# to Table 4 in the 1976 U.S. Standard Atmosphere paper
_REF_GEOPOTENTIAL_HEIGHT = [0, 11, 20, 32, 47, 51, 71, 84.8520]

# Molecular-scale temperature gradient in K/km' at various subscripts. Corresponds
# to Table 4 in the 1976 U.S. Standard Atmosphere paper
_MOL_SCALE_TEMP_GRADIENT = [-6.5, 0, 1.0, 2.8, 0, -2.8, -2.0]

# Molecular-scale temperature in K at various subscripts. Calculated using
# the given sea level temperature and the molecular-scale temperature
# gradients at each height
_REF_MOL_SCALE_TEMP = [288.15, 216.65, 216.65, 228.65, 270.65, 270.65, 214.65, 186.87]

# Reference pressures for various subscripts. Calculated using the pressure equations in the U.S.
# Standard Atmosphere paper. All pressures are in Pa
_REF_PRESSURE = [101325, 22632.06, 5474.89, 868.02, 110.91, 66.94, 3.96]

# Raises exception when an input is out of bounds of the Standard Atmosphere height range
def _checkInStandardAtmosphereRange(z):
	if z < 0 or z > 1000:
		raise Exception("Geometric height must be between 0 and 1000 km")

# Raises exception when an input is not within the 0 to 86 km height range
def _checkBelow86(z):
	if z < 0 or z > 86:
		raise Exception("Geometric height must be between 0 and 86 km")

# Raises exception when an input is not within the 86 to 1000 km range
def _checkAbove86(z):
	if z < 86 or z > 1000:
		raise Exception("Geometric height must be between 86 and 1000 km")

# Converts the given geometric height in km to geopotential km'
def _geometricToGeopotentialHeight(z):
	_checkInStandardAtmosphereRange(z)

	return (_R0 * z) / (_R0 + z)

# Converts the given geometric height to a subscript between 0 and 7 as defined in Table 4 of the U.S.
# Standard Atmosphere paper
def _heightToSubscript(z):
	_checkBelow86(z)

	# Convert to km'
	h = _geometricToGeopotentialHeight(z)

	# Check various ranges and return correct subscript
	if h >= 0 and h <= 11:
		return 0
	elif h > 11 and h <= 20:
		return 1
	elif h > 20 and h <= 32:
		return 2
	elif h > 32 and h <= 47:
		return 3
	elif h > 47 and h <= 51:
		return 4
	elif h > 51 and h <= 71:
		return 5
	elif (h > 71 and h <= 84.852) or math.isclose(h, 84.852, rel_tol = 1e-6):
		return 6

# Returns pressure at given geometric height. Raises exception if z is not between 0 to 86 km
def _getPressureBelow86(z):
	# Get subscript corresponding to height
	subscript = _heightToSubscript(z)

	# Get geopotential height
	h = _geometricToGeopotentialHeight(z)

	# Get molecular scale temp gradient corresponding to this subscript
	molScaleTempGradient = _MOL_SCALE_TEMP_GRADIENT[subscript]

	# Get reference molecular scale temp corresponding to this subscript
	referenceMolScaleTemp = _REF_MOL_SCALE_TEMP[subscript]

	# Get pressure corresponding to this subscript
	referencePressure = _REF_PRESSURE[subscript]

	# Get reference geopotential altitude corresponding to this subscript
	referenceHeight = _REF_GEOPOTENTIAL_HEIGHT[subscript]

	# Decide which pressure equation to use
	if molScaleTempGradient != 0:
		# Calculate exponent
		exponent = (_G0 * _M0) / (_R * molScaleTempGradient)

		# Calculate value notated in brackets in paper
		bracketValue = referenceMolScaleTemp / (referenceMolScaleTemp + molScaleTempGradient * (h - referenceHeight))

		return referencePressure * math.pow(bracketValue, exponent)
	else:
		# Calculate value notated in brackets in paper
		bracketValue = ((-_G0 * _M0) * (h - referenceHeight)) / (_R * referenceMolScaleTemp)

		return referencePressure * math.exp(bracketValue)

# Returns molecular-scale temp below 86 km. Raises exception if z is not between 0 to 86 km
def _getMolScaleTempBelow86(z):
	_checkBelow86(z)

	# Get subscript corresponding to this altitude
	subscript = _heightToSubscript(z)

	# Convert geometric to geopotential height
	h = _geometricToGeopotentialHeight(z)

	return _REF_MOL_SCALE_TEMP[subscript] + _MOL_SCALE_TEMP_GRADIENT[subscript] * (h - _REF_GEOPOTENTIAL_HEIGHT[subscript])

# Returns density at given geometric height. Raises exception if z is not between 0 to 86 km.
# Returns in units of kh/km^3 to match distance units used everywhere else in the program
def _getDensityBelow86(z):
	_checkBelow86(z)

	# Get subscript at given altitude
	subscript = _heightToSubscript(z)

	# Get pressure at given altitude. Convert so distance units match with other values
	pressure = _getPressureBelow86(z) * 1000

	return (pressure * _M0) / (_R * _getMolScaleTempBelow86(z))


# Returns density at given geometric height. Raises exception if z is not between 86 to 1000 km
def _getDensityAbove86(z):
	pass

# Returns density at given geometric height. Raises exception if z is not between 0 to 1000 km
def getDensity(z):
	pass

print(_getDensityBelow86(0))
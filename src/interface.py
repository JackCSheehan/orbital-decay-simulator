# File containing Streamlit interface controls

import streamlit as st
from plotting import *
from datetime import datetime
from sim import *

st.set_page_config(page_title = "Orbital Decay Simulator", layout = "wide", page_icon = "../assets/favicon.png")

# Main driver for Streamlit inputs and calling of other files' functions
def main():
	# News/changelog sidebar
	with st.sidebar:
		"""
		# News
		"""

		"""
		## Welcome to v1.2!
		If you're reading this, then you are currently running the newest version of the Orbital Decay Simulator: v1.2.
		"""

		"""
		---
		# Changelog
		"""

		# Changelog expanders
		with st.expander("v1.2"):
			"""
			- *List of changes*
			"""

		with st.expander("v1.1"):
			"""
			- *List of changes*
			"""

		with st.expander("v1.0"):
			"""
			- *List of changes*
			"""

	# Blank string needed to ensure Streamlit recognizes first multi-line string as markdown
	""

	# Intro text
	"""
	# :earth_americas: Orbital Decay Simulator
	Calculates and visualizes orbital decay.
	Written by [Jack Sheehan](https://github.com/JackCSheehan).

	This tool is open source. Find a bug or want to contribute? Check out the source on
	[GitHub](https://github.com/JackCSheehan/orbital-decay-simulator).

	**Disclaimer:** This tool is for educational/hobbyist purposes only. Mistakes in calculations
	will be fixed as soon as possible, but this tools uses generalized and approximated models. **Real-life
	accuracy should not be expected.**

	---
	## How it Works
	This simulator works by calculating how drag force affects orbital elements over
	time. More complicated causes of orbital decay, such as solar radiation pressure, are not included as part
	of the decay calculations. The 1976 U.S. Standard Atmosphere model is used to calculate the density of the atmosphere at a
	particular altitude.

	Start by supplying a few orbital elements and viewing the accompanying visualization. Next, supply some information about your
	spacecraft. Finally, click the "Simulate" button to run the simulation. When the simulation is completed, you will be given
	an estimate of when the spacecraft will land back on Earth as well as visualizations of the vehicle's trajectory while its orbit decayed.
	"""

	with st.form("data-form"):
		"""
		### TLE Data
		Insert the two-line element set of the object's orbit that you want to simulate.
		"""
		rawTLE = st.text_area("")

		"""
		### Epoch Information
		Enter the date and time of the epoch corresponding to your spacecraft's orbit in the UTC time zone.
		"""
		st.info("Although two-line element sets contain epochs, they may vary in timezone depending on where they are retrieved from. To ensure consistency, the epoch information is collected in addition to the initial TLE data. Please ensure that your epoch is in the UTC timezone.")

		dateCol, hourCol, minCol, secCol = st.columns(4)

		with dateCol:
			epochDate = st.date_input("Date")

		with hourCol:
			epochHour = st.number_input("Hour (24-hour format)", min_value = 0, max_value = 23, step = 1)

		with minCol:
			epochMin = st.number_input("Minutes", min_value = 0, max_value = 59)

		with secCol:
			epochSec = st.number_input("Seconds", min_value = 0, max_value = 59)


		simulateButton = st.form_submit_button("Simulate")

		# Button to confirm entrance of TLE data
		if len(rawTLE.strip()) > 0 and simulateButton:
			with st.spinner("Parsing TLE data..."):
				epoch = datetime.combine(epochDate, time(epochHour, epochMin, epochSec))
				orbit, elements = parseOrbit(rawTLE, epoch)

			with st.spinner("Plotting ground track..."):
				groundTrackPlot = plotGroundTrack(orbit)
				elementsTable = {
					"Epoch": [epoch.strftime("%A, %B %d, %Y, at %H:%M:%S UTC")],
					"B* Drag Term": [f"{elements.bstar:.4f}"],
					"Inclination": [f"{math.degrees(elements.inclination):.4f}°"],
					"RAAN": [f"{math.degrees(elements.right_ascension):.4f}°"],
					"Eccentricity": [f"{elements.excentricity:.4f}"],
					"Argument of Perigee": [f"{math.degrees(elements.arg_perigee):.4f}°"],
				}

			"""
			#### Ground Track
			Shown below is the ground track of your orbit at the epoch. The star indicates the spacecraft's position at the epoch.
			"""
			st.plotly_chart(groundTrackPlot, use_container_width = True)
			st.table(elementsTable)

if __name__ == "__main__":
	main()
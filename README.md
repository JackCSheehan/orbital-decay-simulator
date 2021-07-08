# :earth_americas: Orbital Decay Simulator
An interactive web app that allows for approximating and visualizing a spacecraft's orbital decay and reentry.

Check the app out [here](https://orbital-decay-simulator.herokuapp.com/)

This simulator works by calculating how drag force affects orbital elements over
time. More complicated causes of orbital decay, such as solar radiation pressure, are not included as part
of the decay calculations. The 1976 U.S. Standard Atmosphere model is used to calculate the density of the atmosphere at a
particular altitude.

Start by supplying a few orbital elements and viewing the accompanying visualization. Next, supply some information about your
spacecraft. Finally, click the "Simulate" button to run the simulation. When the simulation is completed, you will be given
an estimate of when the spacecraft will land back on Earth as well as visualizations of the vehicle's telemetry while its orbit decayed.

## Technologies Used
#### [Streamlit](https://streamlit.io/)
- Front-end framework designed for data scientists and machine learning developers to quickly add interfaces to their projects

#### [Plotly](https://plotly.com/)
- A data visualization library that allows for interactive 2D and 3D plots

#### [Altair](https://altair-viz.github.io/)
- A declarative data visualization library for Python

#### [Pandas](https://pandas.pydata.org/)
- A data science library for Python used to store and transform data

#### [Numpy](https://numpy.org/)
- A data science library for Python that supplies a powerful array data structure often preferable to Python's built-in list structure

## References
- [National Oceanic and Atmospheric Administration, National Aeronautics and Space Administration, United States Air Force, *U.S. Standard Atmosphere, 1976*](https://www.ngdc.noaa.gov/stp/space-weather/online-publications/miscellaneous/us-standard-atmosphere-1976/us-standard-atmosphere_st76-1562_noaa.pdf)
- [R. A. Braeunig, *Atmospheric Models*](http://www.braeunig.us/space/atmmodel.htm)
- [USAFA Astronautics and Space Ops, *LSN 11 - Ground Tracks* [YouTube]](https://youtu.be/Q4AQT0vDV_M)

from atmosphere import *
from poliastro.core.propagation import func_twobody
from poliastro.twobody.propagation import cowell
from poliastro.core.perturbations import J2_perturbation
from poliastro.bodies import Earth
from astropy import units as u

# Class used to encapsulate simulation
class Simulator:
    def __init__(self):
        self.atmos = Atmosphere()

    # Driver function for orbital decay simulation
    def simulate(self, startDatetime, orbit, timeStep):
        # Function to propagate orbit based on J2 perturbation. Based on example code from the 
        # poliastro docs: https://docs.poliastro.space/en/stable/examples/Natural%20and%20artificial%20perturbations.html
        def j2Perturbation(t0, state, k):
            duKep = func_twobody(t0, state, k)
            ax, ay, az = J2_perturbation(t0, state, k, J2 = Earth.J2.value, R = constants.EARTH_RADIUS_KM)
            duAd = np.array([0, 0, 0, ax, ay, az])
            
            return duKep + duAd

        data = {"time": [], "raan": [], "orbit": []}
        minutes = 0

        for _ in range(0, 100):
            minutes += 1

            # Simulate nodal precession
            orbit = orbit.propagate(1 * u.min, method = cowell, f = j2Perturbation)

            # Record data
            data["time"].append(minutes)
            data["raan"].append(str(orbit.raan.to(u.deg)))
            data["orbit"].append(str(orbit))

        return data
        
        

        
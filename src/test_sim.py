from sim import *
from datetime import datetime
import pytest

# Tests retrival of planetary equivalent amplitude based on time period
def test_ap():
    date = datetime(2000, 1, 1, 1, 30)
    lat = 25
    lon = 40
    height = 150
    sim = Simulator()

    assert sim.getAP(date) == 56

    date = datetime(2000, 1, 1, 3, 30)
    assert sim.getAP(date) == 39

    date = datetime(2000, 1, 1, 6, 30)
    assert sim.getAP(date) == 27

    date = datetime(2000, 1, 1, 9, 30)
    assert sim.getAP(date) == 18

    date = datetime(2000, 1, 1, 12, 30)
    assert sim.getAP(date) == 32

    date = datetime(2000, 1, 1, 15, 30)
    assert sim.getAP(date) == 15

    date = datetime(2000, 1, 1, 18, 30)
    assert sim.getAP(date) == 32

    date = datetime(2000, 1, 1, 21, 30)
    assert sim.getAP(date) == 22

# Test total mass density of atmosphere at various times in the day
def test_density_time():
    date = datetime(2000, 1, 1, 1, 30)
    lat = 55
    lon = 45
    height = 100
    sim = Simulator()

    density = sim.getAtmosDensity(date, lon, lat, height)
    assert density == pytest.approx(5.231E-7, .01)

    date = datetime(2000, 1, 1, 3, 30)
    density = sim.getAtmosDensity(date, lon, lat, height)
    assert density == pytest.approx(4.946E-7, .01)

    date = datetime(2000, 1, 1, 6, 30)
    density = sim.getAtmosDensity(date, lon, lat, height)
    assert density == pytest.approx(4.803E-7, .01)

    date = datetime(2000, 1, 1, 9, 30)
    density = sim.getAtmosDensity(date, lon, lat, height)
    assert density == pytest.approx(5.167E-7, .01)

    date = datetime(2000, 1, 1, 12, 30)
    density = sim.getAtmosDensity(date, lon, lat, height)
    assert density == pytest.approx(5.392E-7, .01)

    date = datetime(2000, 1, 1, 15, 30)
    density = sim.getAtmosDensity(date, lon, lat, height)
    assert density == pytest.approx(5.122E-7, .01)

    date = datetime(2000, 1, 1, 18, 30)
    density = sim.getAtmosDensity(date, lon, lat, height)
    assert density == pytest.approx(4.992E-7, .01)

    date = datetime(2000, 1, 1, 21, 30)
    density = sim.getAtmosDensity(date, lon, lat, height)
    assert density == pytest.approx(5.275E-7, .01)
from sim import *
from atmosphere import *
from datetime import datetime
import pytest

# Tests retrival of planetary equivalent amplitude based on time period
def test_ap():
    date = datetime(2000, 1, 1, 1, 30)
    lat = 25
    lon = 40
    height = 150
    atmos = Atmosphere()
    spaceWeatherToday = atmos.getDaysSpaceWeather(date)

    assert atmos.getAP(date, spaceWeatherToday) == 56

    date = datetime(2000, 1, 1, 3, 30)
    assert atmos.getAP(date, spaceWeatherToday) == 39

    date = datetime(2000, 1, 1, 6, 30)
    assert atmos.getAP(date, spaceWeatherToday) == 27

    date = datetime(2000, 1, 1, 9, 30)
    assert atmos.getAP(date, spaceWeatherToday) == 18

    date = datetime(2000, 1, 1, 12, 30)
    assert atmos.getAP(date, spaceWeatherToday) == 32

    date = datetime(2000, 1, 1, 15, 30)
    assert atmos.getAP(date, spaceWeatherToday) == 15

    date = datetime(2000, 1, 1, 18, 30)
    assert atmos.getAP(date, spaceWeatherToday) == 32

    date = datetime(2000, 1, 1, 21, 30)
    assert atmos.getAP(date, spaceWeatherToday) == 22

# Test total mass density of atmosphere at various times in the day
def test_density_time():
    date = datetime(2000, 1, 1, 1, 30)
    lat = 55
    lon = 45
    height = 100
    atmos = Atmosphere()

    density = atmos.getDensity(date, lon, lat, height)
    assert density == pytest.approx(5.231E-7, .01)

    date = datetime(2000, 1, 1, 3, 30)
    density = atmos.getDensity(date, lon, lat, height)
    assert density == pytest.approx(4.946E-7, .01)

    date = datetime(2000, 1, 1, 6, 30)
    density = atmos.getDensity(date, lon, lat, height)
    assert density == pytest.approx(4.803E-7, .01)

    date = datetime(2000, 1, 1, 9, 30)
    density = atmos.getDensity(date, lon, lat, height)
    assert density == pytest.approx(5.167E-7, .01)

    date = datetime(2000, 1, 1, 12, 30)
    density = atmos.getDensity(date, lon, lat, height)
    assert density == pytest.approx(5.392E-7, .01)

    date = datetime(2000, 1, 1, 15, 30)
    density = atmos.getDensity(date, lon, lat, height)
    assert density == pytest.approx(5.122E-7, .01)

    date = datetime(2000, 1, 1, 18, 30)
    density = atmos.getDensity(date, lon, lat, height)
    assert density == pytest.approx(4.992E-7, .01)

    date = datetime(2000, 1, 1, 21, 30)
    density = atmos.getDensity(date, lon, lat, height)
    assert density == pytest.approx(5.275E-7, .01)
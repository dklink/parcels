from parcels import Grid, ParticleSet, ScipyParticle, JITParticle
from parcels import AdvectionRK4
import numpy as np
from datetime import timedelta as delta
import math
import pytest

ptype = {'scipy': ScipyParticle, 'jit': JITParticle}


def radial_rotation_grid(xdim=200, ydim=200):  # Define 2D flat, square grid for testing purposes.

    lon = np.linspace(0, 60, xdim, dtype=np.float32)
    lat = np.linspace(0, 60, ydim, dtype=np.float32)

    x0 = 30.                                   # Define the origin to be the centre of the grid.
    y0 = 30.

    U = np.zeros((xdim, ydim), dtype=np.float32)
    V = np.zeros((xdim, ydim), dtype=np.float32)

    T = delta(days=1)
    omega = 2*np.pi/T.total_seconds()          # Define the rotational period as 1 day.

    for i in range(lon.size):
        for j in range(lat.size):

            r = np.sqrt((lon[i]-x0)**2 + (lat[j]-y0)**2)  # Define radial displacement.
            assert(r >= 0.)
            assert(r <= np.sqrt(x0**2 + y0**2))

            theta = math.atan2((lat[j]-y0), (lon[i]-x0))  # Define the polar angle.
            assert(abs(theta) <= np.pi)

            U[i, j] = r * math.sin(theta) * omega
            V[i, j] = -r * math.cos(theta) * omega

    return Grid.from_data(U, lon, lat, V, lon, lat, mesh='flat')


def true_values(age):  # Calculate the expected values for particle 2 at the endtime.

    x = 20*math.sin(2*np.pi*age/(24.*60.**2)) + 30.
    y = 20*math.cos(2*np.pi*age/(24.*60.**2)) + 30.

    return [x, y]


def rotation_example(grid, mode='jit', method=AdvectionRK4):

    npart = 2          # Test two particles on the rotating grid.
    pset = ParticleSet.from_line(grid, size=npart, pclass=ptype[mode],
                                 start=(30., 30.),
                                 finish=(30., 50.))  # One particle in centre, one on periphery of grid.

    endtime = delta(hours=17)
    dt = delta(minutes=5)
    interval = delta(hours=1)

    pset.execute(method, endtime=endtime, dt=dt, interval=interval,
                 output_file=pset.ParticleFile(name="RadialParticle"), show_movie=False)

    return pset


@pytest.mark.parametrize('mode', ['scipy', 'jit'])
def test_rotation_example(mode):
    grid = radial_rotation_grid()
    pset = rotation_example(grid, mode=mode)
    assert(pset[0].lon == 30. and pset[0].lat == 30.)  # Particle at centre of grid remains stationary.
    vals = true_values(pset[1].time)
    assert(np.allclose(pset[1].lon, vals[0], 1e-5))    # Check advected values against calculated values.
    assert(np.allclose(pset[1].lat, vals[1], 1e-5))


if __name__ == "__main__":
    filename = 'radial_rotation'
    grid = radial_rotation_grid()
    grid.write(filename)

    rotation_example(grid)
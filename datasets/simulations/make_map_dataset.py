# Licensed under a 3-clause BSD style license

import numpy as np
from astropy import units as u
from astropy.coordinates import EarthLocation, SkyCoord
from gammapy.data import Observation
from gammapy.data.pointing import FixedPointingInfo
from gammapy.datasets import (
    Datasets,
    MapDataset,
)
from gammapy.irf import load_irf_dict_from_file
from gammapy.makers import MapDatasetMaker
from gammapy.maps import MapAxis, WcsGeom
from gammapy.modeling.models import (
    FoVBackgroundModel,
    GaussianSpatialModel,
    Models,
    PowerLawSpectralModel,
    SkyModel,
)

irfs = load_irf_dict_from_file(
    "$GAMMAPY_DATA/cta-1dc/caldb/data/cta/1dc/bcf/South_z20_50h/irf_file.fits"
    
)

skydir = SkyCoord("0 deg", "0 deg", frame="galactic")
pointing = FixedPointingInfo(fixed_icrs=skydir.icrs)
energy_edges = np.logspace(-1, 2, 15) * u.TeV
energy_axis = MapAxis.from_edges(edges=energy_edges, name="energy", interp="log")

geom = WcsGeom.create(
    skydir=skydir, width=(4, 4), binsz=0.1, axes=[energy_axis], frame="galactic"
)

gauss = GaussianSpatialModel(
    lon_0="0 deg", lat_0="0 deg", sigma="0.4 deg", frame="galactic"
)
pwl = PowerLawSpectralModel(amplitude="1e-11 cm-2 s-1 TeV-1")
skymodel = SkyModel(spatial_model=gauss, spectral_model=pwl, name="source")

obs = Observation.create(
    pointing=pointing,
    livetime=1 * u.h,
    irfs=irfs,
    location=EarthLocation(lon="-70d18m58.84s", lat="-24d41m0.34s", height="2000m"),
)

def simulate_map_dataset(random_state=0, name=None):
    empty = MapDataset.create(geom, name=name)
    maker = MapDatasetMaker(selection=["exposure", "background", "psf", "edisp"])
    dataset = maker.run(empty, obs)

    bkg_model = FoVBackgroundModel(dataset_name=dataset.name)
    models = Models([bkg_model, skymodel])

    dataset.models = models
    dataset.fake(random_state=random_state)

    return dataset, models

dataset, models = simulate_map_dataset()
dataset.write('simulated_map_dataset.fits', overwrite=True)
models.write('simulated_map_dataset_model.yaml', overwrite=True)

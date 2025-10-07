# Licensed under a 3-clause BSD style license

import numpy as np
from astropy import units as u
from astropy.coordinates import SkyCoord
from gammapy.datasets import SpectrumDatasetOnOff
from gammapy.irf import EffectiveAreaTable2D, EDispKernelMap
from gammapy.makers.utils import make_map_exposure_true_energy
from gammapy.maps import MapAxis, RegionGeom, RegionNDMap
from gammapy.modeling import Fit
from gammapy.modeling.models import (
    PowerLawSpectralModel,
    ExpCutoffPowerLawSpectralModel,
    SkyModel,
    Models, 
)

energy_edges = np.logspace(-0.5, 1.5, 21) * u.TeV
energy_axis = MapAxis.from_edges(energy_edges, interp="log", name="energy")
energy_axis_true = energy_axis.copy(name="energy_true")

aeff = EffectiveAreaTable2D.from_parametrization(energy_axis_true=energy_axis_true)

bkg_model = SkyModel(
    spectral_model=PowerLawSpectralModel(
        index=2.5, amplitude="1e-12 cm-2 s-1 TeV-1"
    ),
    name="background",
)
bkg_model.spectral_model.amplitude.frozen = True
bkg_model.spectral_model.index.frozen = True

geom = RegionGeom.create(region="icrs;circle(0, 0, 0.1)", axes=[energy_axis])
acceptance = RegionNDMap.from_geom(geom=geom, data=1)
edisp = EDispKernelMap.from_diagonal_response(
    energy_axis=energy_axis,
    energy_axis_true=energy_axis_true,
    geom=geom,
)

geom_true = RegionGeom.create(
    region="icrs;circle(0, 0, 0.1)", axes=[energy_axis_true]
)
exposure = make_map_exposure_true_energy(
    pointing=SkyCoord("0d", "0d"), aeff=aeff, livetime=100 * u.h, geom=geom_true
)

mask_safe = RegionNDMap.from_geom(geom=geom, dtype=bool)
mask_safe.data += True

acceptance_off = RegionNDMap.from_geom(geom=geom, data=5)
dataset = SpectrumDatasetOnOff(
    name="test_onoff",
    exposure=exposure,
    acceptance=acceptance,
    acceptance_off=acceptance_off,
    edisp=edisp,
    mask_safe=mask_safe,
)
dataset.models = bkg_model
bkg_npred = dataset.npred_signal()


def simulate_spectrum_dataset(spectral_model, random_state=0):
    model = SkyModel(spectral_model=spectral_model, name="source")
    dataset.models = model
    dataset.fake(
        random_state=random_state,
        npred_background=bkg_npred,
    )

    models = Models([model])
    return models, dataset

models, dataset = simulate_spectrum_dataset(spectral_model=PowerLawSpectralModel())
dataset.write('simulated_spectrum_dataset_PL.fits', overwrite=True)
models.write('simulated_spectrum_dataset_PL_model.yaml', overwrite=True)

models, dataset = simulate_spectrum_dataset(spectral_model=ExpCutoffPowerLawSpectralModel(lambda_="1 TeV-1"))
dataset.write('simulated_spectrum_dataset_ECPL.fits', overwrite=True)
models.write('simulated_spectrum_dataset_ECPL_model.yaml', overwrite=True)

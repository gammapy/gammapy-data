# Licensed under a 3-clause BSD style license - see LICENSE.rst
from gammapy.modeling.models import (SpatialModel, 
                                     PowerLawSpectralModel, 
                                     SkyModel)
from gammapy.modeling import Parameter
from gammapy.irf import load_irf_dict_from_file
from gammapy.datasets import MapDataset
from gammapy.data import FixedPointingInfo, Observation, observatory_locations
from gammapy.makers import MapDatasetMaker, SafeMaskMaker
from gammapy.maps import MapAxis, WcsGeom

from astropy import units as u
from astropy.coordinates import SkyCoord, angular_separation
import numpy as np

# To create an energy-dependent morphology we start by defining parameters for different energies

class MyCustomGaussianModel(SpatialModel):
    """My custom Energy Dependent Gaussian model.

    Parameters
    ----------
    lon_0, lat_0 : `~astropy.coordinates.Angle`
        Center position
    sigma_1TeV : `~astropy.coordinates.Angle`
        Width of the Gaussian at 1 TeV
    sigma_10TeV : `~astropy.coordinates.Angle`
        Width of the Gaussian at 10 TeV

    """
    tag = "MyCustomGaussianModel"
    is_energy_dependent = True
    lon_0 = Parameter("lon_0", "5.6 deg")
    lat_0 = Parameter("lat_0", "0.2 deg", min=-90, max=90)
    
    sigma_1TeV = Parameter("sigma_1TeV", "0.3 deg", min=0)
    sigma_10TeV = Parameter("sigma_10TeV", "0.15 deg", min=0)
    
    SpatialModel.frame = 'galactic'


    @staticmethod
    def evaluate(lon, lat, energy, lon_0, lat_0, sigma_1TeV, sigma_10TeV):

        sep = angular_separation(lon, lat, lon_0, lat_0)

        # Compute sigma for the given energy using linear interpolation in log energy
        sigma_nodes = u.Quantity([sigma_1TeV, sigma_10TeV])
        energy_nodes = [1, 10] * u.TeV
        log_s = np.log(sigma_nodes.to("deg").value)
        log_en = np.log(energy_nodes.to("TeV").value)
        log_e = np.log(energy.to("TeV").value)
        sigma = np.exp(np.interp(log_e, log_en, log_s)) * u.deg

        exponent = -0.5 * (sep / sigma) ** 2
        norm = 1 / (2 * np.pi * sigma**2)

        return norm * np.exp(exponent)
    
    @property
    def evaluation_radius(self):
        """Evaluation radius (`~astropy.coordinates.Angle`)."""
        return 2 * np.max([self.sigma_1TeV.value, self.sigma_10TeV.value]) * u.deg
        
# Create spatial model        
spatial_model = MyCustomGaussianModel()

# Define energy and geometry for the dataset
energy_axis = MapAxis.from_edges(np.logspace(-1.0, 2, 10), unit="TeV", name="energy", interp="log")
geom = WcsGeom.create(skydir=(5.6, 0.2), width=4*u.deg, 
                      binsz=0.02, axes=[energy_axis], frame='galactic')
                      
# Define spectral model and SkyModel
spectral_model = PowerLawSpectralModel(index=3, amplitude="6e-12 cm-2 s-1 TeV-1", reference="1 TeV")
model = SkyModel(spatial_model=spatial_model, spectral_model=spectral_model, name="model1")

# Set up IRFs for CTA dataset
irfs = load_irf_dict_from_file(
    "$GAMMAPY_DATA/cta-1dc/caldb/data/cta/1dc/bcf/South_z20_50h/irf_file.fits"
)
livetime = 10.0 * u.hr

# Simulate an observation pointing at a fixed position in the sky.
pointing = FixedPointingInfo(
    fixed_icrs=geom.center_skydir.icrs,
)

# Create an in-memory observation
location = observatory_locations["cta_south"]
obs = Observation.create(
    pointing=pointing, livetime=livetime, irfs=irfs, location=location
)

# Make the MapDataset
empty = MapDataset.create(geom, name="dataset-simu")
maker = MapDatasetMaker(selection=["exposure", "background", "psf", "edisp"])
maker_safe_mask = SafeMaskMaker(methods=["offset-max"], offset_max=2.0*u.deg)
dataset = maker.run(empty, obs)
dataset = maker_safe_mask.run(dataset, obs)

# Add the model on the dataset and Poission fluctuate
dataset.models = model
dataset.fake(random_state=42)

# Save the energy dependent mock dataset
dataset.write('dataset_energy_dependent2.fits.gz', overwrite=True)


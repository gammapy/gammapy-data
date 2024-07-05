# Licensed under a 3-clause BSD style license - see LICENSE.rst
import os
from gammapy.data import DataStore, HDUIndexTable, ObservationTable
from gammapy.datasets import MapDataset, Datasets
from gammapy.makers import MapDatasetMaker,SafeMaskMaker
import numpy as np
from astropy.coordinates import SkyCoord
from gammapy.maps import WcsGeom, MapAxis, Map
import astropy.units as u
from regions import CircleSkyRegion

# which energy estimator
which="NN"

# paths and file names
path = os.getcwd()
os.chdir("../crab_events_pass4/")
data_path = "./"
hdu_filename = 'hdu-index-table-' + which + "-Crab.fits.gz"
obs_filename = 'obs-index-table-' + which + "-Crab.fits.gz"

# there is only one observation table so we can read it now
obs_table = ObservationTable.read(data_path+obs_filename)


# create the map dataset maker
maker = MapDatasetMaker(selection = ["counts", "background", "exposure", "edisp", "psf"])
safemask_maker = SafeMaskMaker(methods=['aeff-max'], aeff_percent=10)

# create the energy reco axis
energy_axis = MapAxis.from_edges(
        [1.00,1.78,3.16,5.62,10.0,17.8,31.6,56.2,100,177,316] * u.TeV,

        name="energy",
        interp="log"
    )

# and energy true axis
energy_axis_true = MapAxis.from_energy_bounds(1e-2, 1e3, nbin=50, unit="TeV", name="energy_true")


# create a geometry around the Crab location
geom = WcsGeom.create(skydir=SkyCoord(ra=83.63,dec=22.01, unit='deg', frame="icrs"),
                     width=6*u.deg,
                     axes=[energy_axis],
                     binsz=0.05)

circle = CircleSkyRegion(center=geom.center_skydir, radius=1 * u.deg)
exclusion_mask = geom.region_mask([circle], inside=False)



# initiate empty datasets object
datasets = Datasets()

event_types = np.arange(5,10)

for idx, bin_id in enumerate(event_types): #loop over nhit bins
    
    # load the hdu index table for this event type
    hdu_table = HDUIndexTable.read(data_path+hdu_filename, hdu=bin_id)
    hdu_table[-1]['HDU_CLASS'] = "psf_map_reco"
    # make the DataStore
    data_store = DataStore( hdu_table=hdu_table, obs_table=obs_table)

    # get the observation for this datastore
    observations = data_store.get_observations()
    # create empty dataset that will contain the data
    dataset_empty = MapDataset.create(geom=geom, name="nHit-" + str(bin_id),
                                      energy_axis_true=energy_axis_true,
                                      reco_psf=True,
                                      binsz_irf = 1*u.deg,
                                      rad_axis = MapAxis.from_bounds(0,3,200, unit='deg',name='rad'))

    # run the maker
    dataset = maker.run(dataset_empty, observations[0])
    dataset.exposure.meta["livetime"] = "1 s"
    dataset = safemask_maker.run(dataset)

    # we need to correct the background and exposure by number of transits
    transit_map = Map.read('irfs/TransitsMap_Crab.fits.gz')
    transit_number = transit_map.get_by_coord(geom.center_skydir)
    #transit_number = transit_map.interp_to_geom(geom.to_image()).data[np.newaxis, :,:]
    dataset.background.data*=transit_number
    dataset.exposure.data*=transit_number

    datasets.append(dataset)

os.chdir(path)
datasets.write('HAWC_pass4_public_Crab.yaml', overwrite=True)

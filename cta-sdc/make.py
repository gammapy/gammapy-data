# Licensed under a 3-clause BSD style license
"""Create index files for selection of SDC preliminary files."""
import os
import glob
from gammapy.data import DataStore


dirs = ["North/Dark", "South/Dark"]

for dir in dirs:
    os.chdir(dir)
    paths = glob.glob("dl3-event-obs*.fits.gz")
    datastore = DataStore.from_events_files(paths)
    datastore.hdu_table.write("hdu-index.fits.gz")
    datastore.obs_table.write("obs-index.fits.gz")
    os.chdir("../..")





from gammapy.data import DataStore 

data_store = DataStore.from_dir("$GAMMAPY_DATA/hess-dl3-dr1/")

obs_id = data_store.obs_table[data_store.obs_table["OBJECT"] == "Crab Nebula"][
        "OBS_ID"]
data_store.copy_obs(obs_id=obs_id[:2], outdir="./")

datastore1 = DataStore.from_dir("./")
table1 = datastore1.obs_table
col_mandatory = ["OBS_ID", "RA_PNT", "DEC_PNT", "TSTART", "TSTOP"]
remove_cols = list(set(table1.colnames) - set(col_mandatory))
table1.remove_columns(remove_cols)
meta_mandatory = {
    "HDUDOC": "https://github.com/open-gamma-ray-astro/gamma-astro-data-formats",
    "HDUVERS": 0.2,
    "HDUCLASS": "GADF",
    "HDUCLAS1": "INDEX",
    "HDUCLAS2": "OBS",
    }
table1.meta = meta_mandatory
  
table2 = datastore1.hdu_table
table2.remove_column("SIZE")
meta_hdu_mandatory = {
    "HDUDOC": "https://github.com/open-gamma-ray-astro/gamma-astro-data-formats",
    "HDUVERS": 0.2,
    "HDUCLASS": "GADF",
    "HDUCLAS1": "INDEX",
    "HDUCLAS2": "HDU",
    }
table2.meta = meta_hdu_mandatory
table1.write("obs-index.fits.gz", overwrite=True)
table2.write("hdu-index.fits.gz", overwrite=True)
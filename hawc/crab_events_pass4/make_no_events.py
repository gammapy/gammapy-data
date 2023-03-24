# Licensed under a 3-clause BSD style license - see LICENSE.rst

from astropy.table import Table
from gammapy.data import HDUIndexTable, ObservationTable

filename = "hdu-index-table-GP-Crab.fits.gz"

obs_table = ObservationTable(names=["OBS_ID", "OBS_MODE"], dtype=["str", "str"])
ind_table = HDUIndexTable(
    names=[
        "OBS_ID",
        "HDU_TYPE",
        "HDU_CLASS",
        "FILE_DIR",
        "FILE_NAME",
        "HDU_NAME",
        "EVENT_TYPE",
        "EVENT_CLASS",
    ],
    dtype=[">i8", "S6", "S16", "S11", "S40", "S4", "S1", "S2"],
)

for k in range(1, 4):
    t = Table.read(filename, hdu=k)
    obs_table.add_row(vals=[str(t["EVENT_TYPE"]), "DRIFT"])
    for row in t:
        if row["HDU_TYPE"] not in ["events", "gti"]:
            ind_table.add_row(vals=row)
ind_table["OBS_ID"] = ind_table["EVENT_TYPE"]
obs_table.write("obs-index-table-GP-no-events.fits.gz", overwrite=True)
ind_table.write("hdu-index-table-GP-no-events.fits.gz", overwrite=True)


Example files to support independant data selection at DL3 level using both event types and observation blocks
- hdu-index.fits.gz / obs-index.fits.gz :
minimal solution for swgo adding event type to obs_table ()

- hdu-index-no-obs-id.fits.gz / obs-index.fits.gz
solution including adding `OBS_ID`, `OBS_BLOCK_ID`, `IRF_NAME` to `obs-index` but not `hdu-index`
and `OBS_TABLE_ROW` to both obs-index and hdu-index

- hdu-index-multi.fits.gz/hdu-index-no-obs-id.fits.gz)
same as prevous  but with multiple data chunk as observations (different events list but the same irfs)

# Licensed under a 3-clause BSD style license - see LICENSE.rst
from astropy.io import fits

def add_bkg_unit(filename):
    with fits.open(filename) as hdu:
        cols = hdu[1].columns
        colnames = cols.names

        # Need to find the column which contains the bkg and give it the correct unit
        try:
            bkg_index = colnames.index('BKG') + 1  # TUNIT is 1-based
            hdu[1].header[f'TUNIT{bkg_index}'] = 's-1 MeV-1 sr-1'
        except ValueError:
            raise ValueError(f"'BKG' column not found in {filename}.")

        hdu.writeto(filename, overwrite=True)


add_bkg_unit("bkg_2d_full_example.fits")
add_bkg_unit("bkg_3d_full_example.fits")
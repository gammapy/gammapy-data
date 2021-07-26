import logging
import numpy as np
from astropy.table import Table
from gammapy.estimators import FluxPoints
from astropy import units as u
from gammapy.modeling.models import LogParabolaSpectralModel


# ### HAWC flux points for Crab Nebula 
# The HAWC flux point are taken from https://arxiv.org/pdf/1905.12518.pdf
# assigned to a `FluxPoints` object, then written to FITS.

crab_model = LogParabolaSpectralModel(
    amplitude="2.31e-13 TeV-1 cm-2 s-1",
    alpha=2.73,
    beta=0.06,
    reference="7 TeV"
)

e_min = np.array([1, 1.78, 3.16, 5.62, 10.0, 17.8, 31.6, 56.2, 100, 177]) * u.TeV
e_max = np.array([1.78, 3.16, 5.62, 10.0, 17.8, 31.6, 56.2, 100, 177, 316]) * u.TeV
e_ref = np.array([1.04, 1.83, 3.24, 5.84, 10.66, 19.6, 31.6, 66.8, 118, 204]) * u.TeV
ts = np.array([2734, 4112, 4678, 3683, 2259, 1237, 572, 105, 28.8, 0.14])
is_ul = np.array([False, False, False, False, False, False, False, False, False, True])

e2dnde = np.array(
    [
        3.63e-11,
        2.67e-11,
        1.92e-11,
        1.24e-11,
        8.15e-12,
        5.23e-12,
        3.26e-12,
        1.23e-12,
        8.37e-13,
        np.nan
    ]
) * u.Unit("cm-2 s-1 TeV")

e2dnde_err = np.array(
    [
        0.08e-11,
        0.05e-11,
        0.04e-11,
        0.03e-11,
        0.31e-12,
        0.29e-12,
        0.28e-12,
        0.24e-12,
        2.91e-13,
        np.nan
    ]
) * u.Unit("cm-2 s-1 TeV")

e2dnde_ul = np.array(
    [
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        np.nan,
        8.14e-13
    ]
) * u.Unit("cm-2 s-1 TeV")

norm = crab_model(e_ref) / e2dnde * e_ref ** 2.0
norm_err = norm * e2dnde_err / e2dnde
norm_ul = crab_model(e_ref) / e2dnde_ul * e_ref ** 2.0

e_ref_new = np.sqrt(e_min * e_max)

table = Table()
table.meta["SED_TYPE"] = "dnde"
table["e_ref"] = e_ref_new
table["e_min"] = e_min
table["e_max"] = e_max
table["dnde"] = norm * crab_model(e_ref_new)
table["dnde_err"] = norm_err * crab_model(e_ref_new)
table["dnde_ul"] = norm_ul * crab_model(e_ref_new)
table["ts"] = ts
table["is_ul"] = is_ul

table.write("HAWC19_flux_points.fits", overwrite=True)
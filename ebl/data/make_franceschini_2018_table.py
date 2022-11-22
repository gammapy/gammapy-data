import numpy as np
from astropy.io import fits
from gammapy.maps import MapAxis

redshifts = []
energies = []
tau = []
redshifts_line_numbers = []

with open("franceschini_2018_opacity.dat", "r") as f:

    for i, line in enumerate(f.readlines()):
        if line.startswith(" redshift"):

            z = float(line.split("=")[1].strip())
            # we just want the first three decimals and sometimes there is a
            # trailing 1, e.g. 0.03700000000000001
            z = float(f"{z:.3f}")
            redshifts.append(z)
            redshifts_line_numbers.append(i)

# try to read the first opacities with np.loadtxt
for i, redshift_line in enumerate(redshifts_line_numbers):

    data = np.loadtxt("franceschini_2018_opacity.dat", skiprows=redshift_line + 2, max_rows=500)

    energies.append(data[:, 1])
    tau.append(data[:, 2])

spectra = np.asarray(-np.asarray(tau))


# build the table

# create the "PARAMETERS" HDU
c_0 = fits.Column(name="NAME", format="12A", array=["REDSHIFT"])
c_1 = fits.Column(name="METHOD", format="J", array=[0])
c_2 = fits.Column(name="INITIAL", format="E", array=[redshifts[0]])
c_3 = fits.Column(name="DELTA", format="E", array=[0.001])
c_4 = fits.Column(name="MINIMUM", format="E", array=[redshifts[0]])
c_5 = fits.Column(name="BOTTOM", format="E", array=[redshifts[0]])
c_6 = fits.Column(name="TOP", format="E", array=[redshifts[-1]])
c_7 = fits.Column(name="MAXIMUM", format="E", array=[redshifts[-1]])
c_8 = fits.Column(name="NUMBVALS", format="J", array=[len(redshifts)])
c_9 = fits.Column(name="VALUE", format=f"{len(redshifts)}E", array=[redshifts])

table_parameters = fits.BinTableHDU.from_columns(
    [c_0, c_1, c_2, c_3, c_4, c_5, c_6, c_7, c_8, c_9], name="PARAMETERS"
)
table_parameters.header["HDUCLASS"] = "OGIP"
table_parameters.header["HDUCLAS1"] = "XSPEC TABLE MODEL"
table_parameters.header["HDUCLAS2"] = "PARAMETERS"
table_parameters.header["HDUVERS"] = "1.0.0"

# create the "ENERGIES" HDU
energy = MapAxis.from_nodes(energies[0], interp="log")
energy_low = energy.edges[:-1] * 1e-3  # energies read in eV, to be stored in keV
energy_high = energy.edges[1:] * 1e-3  # energies read in eV, to be stored in keV

c_0 = fits.Column(name="ENERG_LO", format="E", array=energy_low)
c_1 = fits.Column(name="ENERG_HI", format="E", array=energy_high)

table_energies = fits.BinTableHDU.from_columns([c_0, c_1], name="ENERGIES")
table_energies.header["HDUCLASS"] = "OGIP"
table_energies.header["HDUCLAS2"] = "ENERGIES"
table_energies.header["HDUVERS"] = "1.0.0"

# Create table "SPECTRA" HDU
c_0 = fits.Column(name="PARAMVAL", format="1E", array=redshifts)
c_1 = fits.Column(name="INTPSPEC", format="500E", array=spectra)

table_spectra = fits.BinTableHDU.from_columns([c_0, c_1], name="SPECTRA")
table_spectra.header["HDUCLASS"] = "OGIP"
table_spectra.header["HDUCLAS1"] = "XSPEC TABLE MODEL"
table_spectra.header["HDUCLAS2"] = "MODEL SPECTRA"
table_spectra.header["HDUVERS"] = "1.0.0"

# write it
ebl_file = fits.HDUList(
    [fits.PrimaryHDU(), table_parameters, table_energies, table_spectra]
)
ebl_file.writeto("../ebl_franceschini_2018.fits.gz", overwrite=True)

# try to read and plot it
import astropy.units as u
from gammapy.modeling.models import EBLAbsorptionNormSpectralModel
import matplotlib.pyplot as plt

ebl_model = EBLAbsorptionNormSpectralModel.read(
    "../ebl_franceschini_2018.fits.gz", redshift=0.5
)

energy_bounds = [0.08, 3] * u.TeV
opts = dict(energy_bounds=energy_bounds, xunits=u.TeV)
ebl_model.plot(**opts)
plt.show()

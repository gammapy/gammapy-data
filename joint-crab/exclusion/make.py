import logging
import click
from astropy.coordinates import SkyCoord
import astropy.units as u
from gammapy.maps import WcsGeom
from regions import read_ds9

log = logging.getLogger(__name__)
#, help="Input ds9 region file",

@click.command()
@click.argument("input", nargs=1, default="Crab_exclusion.reg")
@click.argument("output", nargs=1, default="exclusion_mask_crab.fits.gz")
@click.argument("skydir", nargs=1, default="83.633d 22.014d")
@click.option("--frame", default="icrs", show_default=True)
@click.option("--binsize", default="0.02", show_default=True)
@click.option("--width", default=(5, 5), type=(float, float), show_default=True)
@click.option("--projection", default="TAN", show_default=True)
@click.option("--overwrite", default="False", show_default=True)
def make_exclusion_mask(input, output, skydir, frame, binsize, width, projection, overwrite):
    """Performs automated data reduction process."""
    exclusion_regions = read_ds9(input)
    log.info(f"Creating exclusion mask from {exclusion_regions}")

    skydir = SkyCoord(skydir, frame=frame)

    width = u.Quantity(width, unit="deg")
    binsize = u.Quantity(binsize, unit="deg")

    geom = WcsGeom.create(width=width, binsz=binsize, frame=frame, skydir=skydir, proj=projection)
    log.info(geom)

    mask = ~geom.region_mask(exclusion_regions)
    log.info(f"Writing exclusion mask in {output}.")
    mask.write(output, overwrite=overwrite)

if __name__ == '__main__':
    make_exclusion_mask()
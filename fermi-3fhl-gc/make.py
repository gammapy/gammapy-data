
from gammapy.maps import Map
from gammapy.datasets import MapDataset
from gammapy.irf import PSFMap, EDispKernelMap


def get_dataset():
    counts = Map.read(
        "$GAMMAPY_DATA/fermi-3fhl-gc/fermi-3fhl-gc-counts-cube.fits.gz"
    )
    background = Map.read(
        "$GAMMAPY_DATA/fermi-3fhl-gc/fermi-3fhl-gc-background-cube.fits.gz"
    )

    exposure = Map.read(
        "$GAMMAPY_DATA/fermi-3fhl-gc/fermi-3fhl-gc-exposure-cube.fits.gz"
    )

    # for some reason the WCS definitions are not aligned...
    exposure.geom._wcs = counts.geom.wcs

    psf = PSFMap.read(
        "$GAMMAPY_DATA/fermi-3fhl-gc/fermi-3fhl-gc-psf-cube.fits.gz", format="gtpsf"
    )

    # reduce size of the PSF
    psf = psf.slice_by_idx(slices={"rad": slice(0, 130)})

    edisp = EDispKernelMap.from_diagonal_response(
        energy_axis=counts.geom.axes["energy"],
        energy_axis_true=exposure.geom.axes["energy_true"],
        geom=psf.psf_map.geom
    )

    mask_safe = counts.geom.boundary_mask(width="0.2 deg")

    return MapDataset(
        counts=counts,
        background=background,
        exposure=exposure,
        psf=psf,
        name="fermi-3fhl-gc",
        edisp=edisp,
        mask_safe=mask_safe
    )


if __name__ == "__main__":
    dataset = get_dataset()
    dataset.write("fermi-3fhl-gc.fits.gz", overwrite=True)

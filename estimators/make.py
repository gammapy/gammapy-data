# Licensed under a 3-clause BSD style license - see LICENSE.rst
import logging
import click
import warnings
from pathlib import Path

from gammapy.analysis import Analysis, AnalysisConfig
from gammapy.modeling.models import Models

log = logging.getLogger(__name__)

AVAILABLE_ESTIMATES = ["crab_hess_fp", "pks2155_hess_lc"]

@click.group()
@click.option(
    "--log-level", default="INFO", type=click.Choice(["DEBUG", "INFO", "WARNING"])
)
@click.option("--show-warnings", is_flag=True, help="Show warnings?")
def cli(log_level, show_warnings):
    logging.basicConfig(level=log_level)

    if not show_warnings:
        warnings.simplefilter("ignore")


@cli.command("create", help="Create Estimator results for gammapy-data")
@click.argument("estimates", type=click.Choice(list(AVAILABLE_ESTIMATES) + ["all"]))
def create(estimates):
    estimates = list(AVAILABLE_ESTIMATES) if estimates == "all" else [estimates]

    for estimate in estimates:
        analysis = run_analysis(estimate)

        if estimate is "crab_hess_fp":
            analysis.get_flux_points()
            analysis.flux_points.write(f"{estimate}/{estimate}.fits", overwrite=True)

        elif estimate is "pks2155_hess_lc":
            analysis.get_light_curve()
            analysis.light_curve.write(f"{estimate}/{estimate}.fits", format="lightcurve", overwrite=True)



def run_analysis(estimate):
    """Run analysis from observation selection to model fitting."""
    config = AnalysisConfig.read(f"{estimate}/config.yaml")
    analysis = Analysis(config)
    analysis.get_observations()
    analysis.get_datasets()

    models = Models.read(f"{estimate}/models.yaml")
    analysis.set_models(models)
    analysis.run_fit()
    return analysis


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli()

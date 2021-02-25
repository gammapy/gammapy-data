from gammapy.analysis import Analysis, AnalysisConfig

def get_dataset():
    config_stacked = AnalysisConfig.read(path="config_stack.yaml")
    analysis_stacked = Analysis(config_stacked)
    analysis_stacked.get_observations()
    analysis_stacked.get_datasets()
    dataset_stacked = analysis_stacked.datasets["stacked"]
    return dataset_stacked


if __name__ == "__main__":
    dataset = get_dataset()
    dataset.write('cta-1dc-gc.fits.gz', overwrite=True)



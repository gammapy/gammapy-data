# `gammapy-data` repository

## Description
This repository is associated with and used by the Gammapy library, stored in the 
repository [gammapy/gammapy](https://github.com/gammapy/gammapy). It contains 
different types of data:
- some datasets of event list and their associated Instrument Response Files
from different gamma-ray instruments,
  - the used format is [GADF v0.3](https://gamma-astro-data-formats.readthedocs.io/en/v0.3/) 
- some datasets of binned data (e.g. exposure, counts maps - DL4 data) created by 
Gammapy,
- some VHE source catalogues from different gamma-ray experiments,
- some astrophysical models.

These data are used in tutorials, tests and for users' analyses.

## Installation
You may fetch this repo with `git`, though you may also download them as part of the Gammapy 
tutorials package with the command `gammapy download datasets`. Then you may set environment
variable `$GAMMAPY_DATA` to the local folder where you have saved `gammapy-data`.

## Licence
All these data are freely available and usable. Because they are produced by different 
authors, their associated data are licenced differently.

Please have a careful look on the chosen licence of the individual data when copying or 
referencing these data. The licences are given in each folder.
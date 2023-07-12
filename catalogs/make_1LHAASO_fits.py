#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 17:15:06 2023

@author: qremy
"""

import astropy.units as u
import numpy as np
from astropy.table import Table
from pandas import read_csv
import gammapy

df = read_csv("lhaaso_cat.csv")

table_csv = Table.from_pandas(df)


def nanfloat(str_):
    if str_.strip() == "":
        return np.nan
    else:
        return float(str_)


def get_values(array):
    n = len(array)
    value = np.ones(n) * np.nan
    error = np.ones(n) * np.nan
    ul = np.ones(n) * np.nan
    for k, v in enumerate(array):
        if "$<$" in v:
            ul[k] = nanfloat(v.split("$<$")[-1])
        elif "$\pm$" in v:
            value[k] = nanfloat(v.split("$\pm$")[0])
            error[k] = nanfloat(v.split("$\pm$")[1])
        else:
            value[k] = nanfloat(v)
    return value, error, ul


def add_entries(data, table, alternative_model=False):
    if alternative_model:
        tag = "_b"
        components = data["Model_b"]
    else:
        tag = ""
        components = data["Model_a"]

    data[f"RAJ2000{tag}"], _, _ = get_values(table["$\\alpha_{2000}$ "])
    data[f"RAJ2000{tag}"] *= u.deg
    data[f"DECJ2000{tag}"], _, _ = get_values(table["$\\delta_{2000}$ "])
    data[f"DECJ2000{tag}"] *= u.deg
    data[f"pos_err{tag}"], _, _ = get_values(table["$\\sigma_{p 95 stat}$ "])
    data[f"pos_err{tag}"] *= u.deg

    data[f"r39{tag}"], data[f"r39_err{tag}"], data[f"r39_ul{tag}"] = get_values(
        table["$r_{39}$ "]
    )
    data[f"r39{tag}"] *= u.deg
    data[f"r39_err{tag}"] *= u.deg
    data[f"r39_ul{tag}"] *= u.deg

    data[f"N0{tag}"], data[f"N0_err{tag}"], data[f"N0_ul{tag}"] = get_values(
        table["$N_0$ "]
    )
    N0unit = np.array(
        [1e-16 if "KM2A" in comp else 1e-13 for comp in components]
    ) * u.Unit("cm−2 s−1 TeV−1")
    data[f"N0{tag}"] = data[f"N0{tag}"] * N0unit
    data[f"N0_err{tag}"] = data[f"N0_err{tag}"] * N0unit
    data[f"N0_ul{tag}"] = data[f"N0_ul{tag}"] * N0unit

    data[f"gamma{tag}"], data[f"gamma_err{tag}"], data[f"gamma_ul{tag}"] = get_values(
        table["$\\Gamma$ "]
    )
    data[f"E0{tag}"] = (
        np.array([50 if "KM2A" in comp else 3 for comp in components]) * u.TeV
    )

    data[f"TS{tag}"], _, _ = get_values(table["TS "])
    data[f"TS100{tag}"], _, _ = get_values(table["TS$_{100}$"])


data = dict()
source_name = []
for name in table_csv["#Source name "][::2]:
    source_name.append(name.replace("1LHAASO", "1LHAASO ").replace("$", "").strip())
data["Source_Name"] = np.array(source_name)
data["Model_a"] = table_csv[::2]["Components"]
add_entries(data, table_csv[::2])
data["Model_b"] = table_csv[1::2]["Components"]
add_entries(data, table_csv[1::2], alternative_model=True)


asso_name = []
asso_sep = []
for asso in table_csv["Asso.(Sep.[$^{\\circ}$])"][::2]:
    asso = str(asso).split("(")
    asso_name.append(asso[0].strip().strip("--"))
    if len(asso) > 1:
        asso_sep.append(float(asso[1].strip(") ")))
    else:
        asso_sep.append(np.nan)
data["ASSO_Name"] = np.array(asso_name)
data["ASSO_Sep"] = asso_sep * u.deg

table = Table(data)

meta_dict = {
    "NAME": "1LHAASO: The First LHAASO Catalog of Gamma-Ray Sources.",
    "VERSION": "ArXiv May 29, 2023",
    "DOI": "https://doi.org/10.48550/arXiv.2305.17030",
    "CONTACT": "Corresponding authors: S.Q. Xi, S.C. Hu, S.Z. Chen, M. Zha xisq@ihep.ac.cn, hushicong@ihep.ac.cn, chensz@ihep.ac.cn, zham@ihep.ac.cn",
    "CREATOR": f"gammapy version {gammapy.__version__.split('dev')[0].split('rc')[0]}",
}
table.meta.update(meta_dict)
table.write("1LHAASO_catalog.fits", overwrite=True)

# %% Uage example
from gammapy.catalog.LHAASO import SourceCatalog1LHAASO
from gammapy.modeling.models import Models

LHAASO1 = SourceCatalog1LHAASO("1LHAASO_catalog.fits")
models = LHAASO1.to_models()
wcda = LHAASO1.to_models(which="WCDA")
km2a = LHAASO1.to_models(which="KM2A")

wcda.write(
    "1LHAASO_wcda.yaml",
    write_covariance=False,
    overwrite=True,
    overwrite_templates=True,
)
km2a.write(
    "1LHAASO_km2a.yaml",
    write_covariance=False,
    overwrite=True,
    overwrite_templates=True,
)
models.write(
    "1LHAASO_catalog.yaml",
    write_covariance=False,
    overwrite=True,
    overwrite_templates=True,
)

models = Models.read("1LHAASO_catalog.yaml")

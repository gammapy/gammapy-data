#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 14:14:44 2024

@author: qremy
"""

from fermipy.gtanalysis import GTAnalysis

gta = GTAnalysis('config_fermipy_std_5deg_qr.yaml',logging={'verbosity' : 3})
gta.setup()

gta.compute_psf(overwrite=True)
gta.compute_drm(edisp_bins=0, overwrite=True)
"""
This script converts `3HWC.yaml` to ECSV format.

3HWC is the HAWC catalog from this paper:
https://arxiv.org/abs/2007.08582

The file `3HWC.yaml` was obtained on the HAWC website
on December 8. 2020
https://data.hawc-observatory.org/datasets/3hwc-survey/3HWC.yaml
"""

import yaml
from astropy.table import Table, Column

flux_keys = ["assumed radius",
             "flux",
             "flux statistical uncertainty up",
             "flux statistical uncertainty down",
             "index",
             "index statistical uncertainty up",
             "index statistical uncertainty down",
             "flux systematic uncertainty up",
             "flux systematic uncertainty down",
             "index systematic uncertainty up",
             "index systematic uncertainty down",
]

def get_flux_measurement(entry):
    if 'flux measurements' in entry.keys():
        return entry['flux measurements'][0]
    else:
        return {key: float('nan') for key in flux_keys}


def make_3hwc():
    with open('3HWC.yaml') as fh:
        data = yaml.load(fh, Loader=yaml.Loader)

    from pprint import pprint;
    pprint(data[0])

    table = Table()
    table.meta['catalog_name'] = '3HWC'
    table.meta['reference'] = 'https://ui.adsabs.harvard.edu/abs/2020arXiv200708582A/abstract'

    table['source_name'] = Column(
        data=[_['name'] for _ in data],
        description='Source name',
    )
    table['ra'] = Column(
        data=[_['RA'] for _ in data],
        description='Right Ascension (J2000)', unit='deg', format='.3f',
    )
    table['dec'] = Column(
        data=[_['Dec'] for _ in data],
        description='Declination (J2000)', unit='deg', format='.3f',
    )
    table['glon'] = Column(
        data=[_['l'] for _ in data],
        description='Galactic longitude', unit='deg', format='.3f',
    )
    table['glat'] = Column(
        data=[_['b'] for _ in data],
        description='Galactic latitude', unit='deg', format='.3f',
    )
    table['pos_err'] = Column(
        data=[_['position uncertainty'] for _ in data],
        description='Position error (1 sigma)', unit='deg', format='.3f',
    )
    table['search_radius'] = Column(
        data=[_['search radius'] for _ in data],
        description='Search radius (see Table 2 in the paper)', unit='deg', format='.1f',
    )
    table['ts'] = Column(
        data=[_['TS'] for _ in data],
        description='Detection test statistic', format='.1f',
    )
    add_flux_measurements(table, data)

    filename = '3HWC.ecsv'
    print(f'Writing {filename}')
    table.write(filename, format='ascii.ecsv', overwrite=True)


def add_flux_measurements(table, data):      
    flux_data = [get_flux_measurement(_) for _ in data]

    idx = 0
    
    table[f'spec{idx}_dnde'] = Column(
        data=[_['flux'] for _ in flux_data],
        description='Differential flux at 7 TeV', unit='cm-2 s-1 TeV-1', format='.3g',
    )
    table[f'spec{idx}_dnde_errn'] = Column(
        data=[_['flux statistical uncertainty down'] for _ in flux_data],
        description=f'Statistical negative error on spec{idx}_dnde', unit='cm-2 s-1 TeV-1', format='.3g',
    )
    table[f'spec{idx}_dnde_errp'] = Column(
        data=[_['flux statistical uncertainty up'] for _ in flux_data],
        description=f'Statistical positive error on spec{idx}_dnde', unit='cm-2 s-1 TeV-1', format='.3g',
    )
    table[f'spec{idx}_dnde_sys_errn'] = Column(
        data=[_['flux systematic uncertainty down'] for _ in flux_data],
        description=f'Systematic negative error on spec{idx}_dnde', unit='cm-2 s-1 TeV-1', format='.3g',
    )
    table[f'spec{idx}_dnde_sys_errp'] = Column(
        data=[_['flux systematic uncertainty up'] for _ in flux_data],
        description=f'Systematic positive error on spec{idx}_dnde', unit='cm-2 s-1 TeV-1', format='.3g',
    )
    table[f'spec{idx}_index'] = Column(
        data=[_['index'] for _ in flux_data],
        description='Spectral index', format='.2f',
    )
    table[f'spec{idx}_index_errn'] = Column(
        data=[_['index statistical uncertainty down'] for _ in flux_data],
        description=f'Statistical negative error on spec{idx}_index', format='.3f',
    )
    table[f'spec{idx}_index_errp'] = Column(
        data=[_['index statistical uncertainty up'] for _ in flux_data],
        description=f'Statistical positive error on spec{idx}_index', format='.3f',
    )
    table[f'spec{idx}_index_sys_errn'] = Column(
        data=[_['index systematic uncertainty down'] for _ in flux_data],
        description=f'Systematic negative error on spec{idx}_index', format='.3f',
    )
    table[f'spec{idx}_index_sys_errp'] = Column(
        data=[_['index systematic uncertainty up'] for _ in flux_data],
        description=f'Systematic positive error on spec{idx}_index', format='.3f',
    )
    table[f'spec{idx}_radius'] = Column(
        data=[_['assumed radius'] for _ in flux_data],
        description=f'Spectrum assumed radius', unit='deg', format='.3f',
    )


if __name__ == '__main__':
    make_3hwc()

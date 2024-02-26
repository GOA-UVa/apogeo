#!/usr/bin/env python3
from typing import List
import os
from datetime import timedelta as td

import numpy as np
import pandas as pd
# needs matplotlib and scipy too

_DIR_CSVS = './out'
_DIR_CSVS = '/srv/ftpuser/data/apogees_marambio'
_N_DAYS = 3
_TARGET = './out/last_apogee_graph.png'
_TARGET = '/var/www/goacf/realtime/images/last_marambio_apogees_graph.png'
_YTICK = 10

def read_datafiles(paths: List[str]) -> pd.DataFrame:
    dfs = []
    for path in paths:
        df = pd.read_csv(path, parse_dates=['datetime'])[['datetime', 'SBTempK_Surface_Avg', 'TargTempK_Surface_Avg', 'SBTempK_Sky_Avg', 'TargTempK_Sky_Avg']]
        namemapper = {'SBTempK_Surface_Avg': 'SB_Surface', 'TargTempK_Surface_Avg': 'Surface', 'SBTempK_Sky_Avg': 'SB_Sky', 'TargTempK_Sky_Avg': 'Sky'}
        df = df.rename(columns=namemapper)
        df[list(namemapper.values())] = df[list(namemapper.values())] - 273.15
        dfs.append(df)
    df = pd.concat(dfs).reset_index(drop=True).drop_duplicates(['datetime'], keep='last').sort_values('datetime')
    df = df[df['datetime'] > df['datetime'].max() - td(_N_DAYS)]
    return df

def main():
    files = [f for f in os.listdir(_DIR_CSVS) if f.lower().endswith('.csv')]
    files = [os.path.join(_DIR_CSVS, f) for f in sorted(files)[-_N_DAYS:]]
    df = read_datafiles(files)
    miny = np.floor(min(min(df['Surface']), min(df['Sky']))/_YTICK)*_YTICK
    maxy = np.ceil(max(max(df['Surface']), max(df['Sky']))/_YTICK)*_YTICK
    yticks = np.arange(miny, maxy, _YTICK)
    df['Surface'] = df['Surface'].rolling(window=5, win_type='gaussian', center=True).mean(std=2)
    df['Sky'] = df['Sky'].rolling(window=5, win_type='gaussian', center=True).mean(std=2)
    plot = df.plot(x='datetime', y=['Surface', 'Sky'], title='Temperature Measured via Infrared', grid=True, figsize=(12,5), yticks=yticks, xlabel='Date', ylabel='Temperature °C')
    plot.get_figure().savefig(_TARGET)

if __name__ == "__main__":
    main()

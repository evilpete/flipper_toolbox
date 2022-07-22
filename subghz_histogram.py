#!/usr/bin/env python3
"""
    Peter Shipley github.com/evilpete

    Script to read Flipper SubGhz RAW File and plot 0 & 1 segment lengths using pyplot

    Inspired by jinscho's gist :
    https://gist.github.com/jinschoi/8396f25a4cb7ac7986a7d881026ae950
"""

import re
import sys
import pandas as pd
import matplotlib.pyplot as plt


LIMIT=400

filename = sys.argv[1]

psegs = []
nsegs = []
with open(filename, 'r', encoding="utf-8") as fd:
    for line in fd:
        m = re.match(r'RAW_Data:\s*([-0-9 ]+)\s*$', line)
        if m:
            nsegs.extend(abs(int(seg)) for seg in m[1].split(r' ') if int(seg) < 0 )
            psegs.extend(abs(int(seg)) for seg in m[1].split(r' ') if int(seg) > 0 )


pseries = pd.Series(data=psegs)
nseries = pd.Series(data=nsegs)

pseries = pseries[pseries < LIMIT]
nseries = nseries[nseries < LIMIT]

df = pd.DataFrame(pseries, columns = ['pos'])
df['neg'] = nseries

ax = df.plot.hist(bins=int(LIMIT/2),
            log=False,
            alpha=0.5, figsize=(6,3),
            title='Histogram of segment length' )

ax.set(xlabel='milliseconds')

ax.grid(True, which='major', axis='y' )

plt.show()

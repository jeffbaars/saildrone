#!/usr/bin/python

#for deprecation warning check: https://github.com/matplotlib/basemap/issues/382

import numpy as np
from mpl_toolkits.basemap import Basemap  # basemap package
import matplotlib.pyplot as plt

# miller projection
map = Basemap(projection='mill',lon_0=0)
# plot coastlines, draw label meridians and parallels.
map.drawcoastlines(linewidth=0.5)
map.drawparallels(np.arange(-90,90,30),labels=[1,0,0,0], linewidth=0.3)
map.drawmeridians(np.arange(map.lonmin,map.lonmax+30,60),labels=[0,0,0,1], linewidth=0.3)
# fill continents 'coral' (with zorder=0), color wet areas 'aqua'
map.drawmapboundary(fill_color='white')
map.fillcontinents(color='coral',lake_color='aqua')
plt.show()

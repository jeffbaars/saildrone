#!/usr/bin/python
import os, sys, glob, re, math
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, cm, shiftgrid
from utils_cmap import *
from utils_date import *
from utils_load_data import *
from utils_plot import *

#---------------------------------------------------------------------------
# Paths.
#---------------------------------------------------------------------------
sail_dir    = '/home/disk/spock/jbaars/saildrone'
py_dir      = sail_dir + '/python'
pickle_dir  = sail_dir + '/pickle'
data_dir    = sail_dir + '/data'
rundirs_dir = sail_dir + '/rundirs'
#plot_dir    = '/home/disk/funnel/saildrone/images/maps_obs'
plot_dir    = sail_dir + '/plots'

saildrone_data = '/home/disk/jabba/steed/data/raw/saildrone/'
rawins_data    = '/home/disk/spock2/jbaars/qc_rawins_data'

#---------------------------------------------------------------------------
# Settings.
#---------------------------------------------------------------------------
domain = 'd01'
hh     = '00'

stns_sail = ['1054', '1055', '1056', '1057', '1058', '1059']
vars_sail = ['UWND_MEAN', 'VWND_MEAN', 'GUST_WND_MEAN', 'TEMP_AIR_MEAN', \
           'RH_MEAN', 'BARO_PRES_MEAN', 'TEMP_O2_RBR_MEAN']

dtfmt = '%Y%m%d%H'
days_back = 3

#---------------------------------------------------------------------------
# Get current time; check what plots need to be made?
#---------------------------------------------------------------------------
dt = get_now(dtfmt)
dt_utc = local_to_gmt(dt, dtfmt)

#---------------------------------------------------------------------------
# Make run directory.
#---------------------------------------------------------------------------
rundir = rundirs_dir + '/map_saildrone_obs_' + dt_utc + '.' + str(os.getpid())
print 'making ', rundir
os.makedirs(rundir)

#---------------------------------------------------------------------------
# Load geo_em lats and lons, including corner lats/lons.
#---------------------------------------------------------------------------
geo_em = data_dir + '/geo_em.' + domain + '.nc'
lat, lon, hgt, clats, clons = load_geo_em(geo_em)

#---------------------------------------------------------------------------
# Determine which dates to plot.
#---------------------------------------------------------------------------
sdt = time_increment(dt_utc, -days_back, dtfmt)
dts = get_dates(sdt, dt_utc, 60, dtfmt)
dts_plot = get_plot_dates(dts, plot_dir, saildrone_data, stns_sail)

dts_plot = ['2019111512']

if len(dts_plot) == 0:
    print 'No dates need plotting'

#---------------------------------------------------------------------------
# Make plots for each dts_plot.
#---------------------------------------------------------------------------
for d in range(len(dts_plot)):
    dt_plot = dts_plot[d]
    print 'Making plot for ', dt_plot
    #-----------------------------------------------------------------------
    # Load Saildrone netcdf data files.
    #-----------------------------------------------------------------------
    dat_sail = {}
    for s in range(len(stns_sail)):
        stn = stns_sail[s]
        file_c = saildrone_data + '/' + dt_plot[0:8] + '/sd.' + stn + \
                 '.' + dt_plot + '.nc'
        print 'loading ', file_c
        if not os.path.isfile(file_c):
            print 'cannot see ', file_c
            dat_sail[stn] = np.nan
        else:
            dat_sail[stn] = load_saildrone(file_c, vars_sail)

    #-----------------------------------------------------------------------
    # Read in ship and buoy obs from QC rawins files.
    #-----------------------------------------------------------------------
    rawins_file = rawins_data + '/' + dt_plot[0:6] + '/obs.' + dt_plot
    (stns_sb, typ_sb, dat_sb) = load_qc_rawins(rawins_file, rundir)

    #-----------------------------------------------------------------------
    # Get plot title and name together.  Since we're using the last 5-min of
    # data from the data files, we're essentially making plots for the hour
    # of the data file +1.  So adjust the title accordingly, but leave the
    # plotfname to match the data file fname.
    #-----------------------------------------------------------------------
    dt_plot_p1 = time_increment(dt_plot, 1.0/24.0, dtfmt)
    dt_nice = get_nice_date(dt_plot_p1, dtfmt, '%Y-%b-%d %H:%M Z')
    dt_nice_lst = get_nice_date(gmt_to_local(dt_plot_p1), dtfmt, \
                                '%Y-%b-%d %-I:%M %p')
    titlein = 'UW Saildrone (black), ships (blue), buoys (green), ' + \
              dt_nice + ' (' + dt_nice_lst + ')'
    plotfname = plot_dir + '/' + dt_plot + '.png'

    #-----------------------------------------------------------------------
    # Make map.
    #-----------------------------------------------------------------------
    iret = mapper(stns_sail, dat_sail, stns_sb, typ_sb, dat_sb, \
                  titlein, plotfname)

    sys.exit()

#---------------------------------------------------------------------------
# Clean up.
#---------------------------------------------------------------------------
syscom = 'rm -rf ' + rundir
print syscom
os.system(syscom)

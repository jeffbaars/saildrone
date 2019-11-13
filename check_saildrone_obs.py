#!/usr/bin/python
import os, sys, glob
import numpy as np
from utils_cmap import *
from utils_date import *
from utils_load_data import *
from utils_plot import *
from utils_stats import *

#---------------------------------------------------------------------------
# Paths.
#---------------------------------------------------------------------------
sail_dir    = '/home/disk/spock/jbaars/saildrone'
py_dir      = sail_dir + '/python'
pickle_dir  = sail_dir + '/pickle'
data_dir    = sail_dir + '/data'
rundirs_dir = sail_dir + '/rundirs'
plot_dir    = sail_dir + '/plots'

saildrone_data = '/home/disk/jabba/steed/data/raw/saildrone/'

#---------------------------------------------------------------------------
# Settings.
#---------------------------------------------------------------------------
stns_sail = ['1054', '1055', '1056', '1057', '1058', '1059']
vars_sail = ['UWND_MEAN', 'VWND_MEAN', 'GUST_WND_MEAN', 'TEMP_AIR_MEAN', \
             'RH_MEAN', 'BARO_PRES_MEAN', \
             'TEMP_IR_SEA_WING_UNCOMP_MEAN', 'TEMP_O2_RBR_MEAN', \
             'TEMP_CTD_RBR_MEAN']
dtfmt = '%Y%m%d%H'
hours_back = 2

stns_sail_cols = ['indigo', 'blue', 'deepskyblue', 'darkgreen', \
                  'lime', 'orange']

#---------------------------------------------------------------------------
# Get current time and make date array.
#---------------------------------------------------------------------------
dt = get_now(dtfmt)
dt_utc = local_to_gmt(dt, dtfmt)
sdt = time_increment(dt_utc[0:8] + '00', float(-hours_back)/24.0, dtfmt)
dts = get_dates(sdt, dt_utc, 60, dtfmt)

dts = sorted(set(dts), reverse=True)

print float(-hours_back)/24.0
print dts
#sys.exit()

#--------------------------------------------------------------
# Load Saildrone netcdf data files.
#--------------------------------------------------------------
obspts_sail = {}
for d in range(len(dts)):
    dt = dts[d]
    dt_m1 = time_increment(dt, -1.0/24.0, dtfmt)
    stns_sail_avail = []
    print '-----' + dt + ' (' + dt_m1 + ' datafile date)' + '-----'
    for s in range(len(stns_sail)):
        stn = stns_sail[s]
        
        #--- Saildrone file names denote hour of data (i.e.11Z is 
        #--- 1100-1159), and load_saildrone grabs the last 5-min of
        #--- the hour so for our dt_plot, we need to use PREVIOUS
        #--- hour's Saildrone file.
        dt_m1 = time_increment(dt, -1.0/24.0, dtfmt)
        file_c = saildrone_data + '/' + dt_m1[0:8] + '/sd.' + \
                 stn + '.' + dt_m1 + '.nc'

        if not os.path.isfile(file_c):
            print stn, ' data file missing'
            obspts_sail[stn,dt] = np.nan
        else:
            obspts_sail[stn,dt] = load_saildrone(file_c, vars_sail)
            count = 0
            missing_str = ''
            for v in range(len(vars_sail)):
                var = vars_sail[v]
                if obspts_sail[stn,dt][var] == obspts_sail[stn,dt][var]:
                    count = count + 1
                else:
                    missing_str += var + ', '
            print stn, count, missing_str
            stns_sail_avail.append(stn)
    #sys.exit()
    

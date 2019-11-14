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
plot_dir    = '/home/disk/funnel/saildrone/images/ts_ocean'
#plot_dir    = sail_dir + '/plots'

saildrone_data = '/home/disk/jabba/steed/data/raw/saildrone/'
rawins_data    = '/home/disk/spock2/jbaars/qc_rawins_data'

#---------------------------------------------------------------------------
# Settings.
#---------------------------------------------------------------------------
stns_sail = ['1054', '1055', '1056', '1057', '1058', '1059']
#vars_sail = ['WAVE_DOMINANT_PERIOD', 'WAVE_SIGNIFICANT_HEIGHT', \
#             'TEMP_O2_RBR_MEAN']
vars_sail = ['WAVE_DOMINANT_PERIOD', 'WAVE_SIGNIFICANT_HEIGHT']

dtfmt = '%Y%m%d%H'
days_back = 7

stns_sail_cols = ['indigo', 'blue', 'deepskyblue', \
                  'darkgreen', 'lime', 'orange']

#---------------------------------------------------------------------------
# Get current time and make 
#---------------------------------------------------------------------------
now = get_now(dtfmt)
now_utc = local_to_gmt(now, dtfmt)
sdt = time_increment(now_utc[0:8] + '00', -days_back, dtfmt)
        
#---------------------------------------------------------------------------
# Make run directory.
#---------------------------------------------------------------------------
#rundir = rundirs_dir + '/ts_saildrone_obs_ocean_' + dt_utc + '.' + \
#         str(os.getpid())
#print 'making ', rundir
#os.makedirs(rundir)

#---------------------------------------------------------------------------
# Determine which dates to plot.
#---------------------------------------------------------------------------
sdt = time_increment(now_utc, -days_back, dtfmt)
dts = get_dates(sdt, now_utc, 60, dtfmt)

obspts_sail = {}
for d in range(len(dts)):
    dt = dts[d]
    stns_sail_avail = []
    for s in range(len(stns_sail)):
        stn = stns_sail[s]
        #--- Saildrone file names denote hour of data (i.e.11Z is 
        #--- 1100-1159), and load_saildrone grabs the last 5-min of
        #--- the hour so for our dt_plot, we need to use PREVIOUS
        #--- hour's Saildrone file.
        dt_m1 = time_increment(dt, -1.0/24.0, dtfmt)
        file_c = saildrone_data + '/' + dt_m1[0:8] + '/sd.' + \
                 stn + '.' + dt_m1 + '.nc'
        print 'loading ', file_c
        if not os.path.isfile(file_c):
            print 'cannot see ', file_c
            obspts_sail[stn,dt] = np.nan
        else:
            obspts_sail[stn,dt] = load_saildrone(file_c, vars_sail)
            stns_sail_avail.append(stn)

#stn = '1059'
#var = 'WAVE_DOMINANT_PERIOD'
#for d in range(len(dts)):
#    dt = dts[d]
#    key = (stn,dt)
#    if key in obspts_sail:
#        if obspts_sail[key] == obspts_sail[key]:
#            test = obspts_sail[key]
#            print test
#            if var in obspts_sail[key]:
#                ob_c = obspts_sail[key][var]
#                print dt, key, ob_c
#sys.exit()

#--------------------------------------------------------------
# Make time series plot.
#--------------------------------------------------------------
for vs in range(len(vars_sail)):
    var = vars_sail[vs]
    titlein = var_lab[var] + ', UW Saildrone (black), ships (blue), ' + \
              'buoys (green)'
    plotfname = plot_dir + '/' + var + '_' + str(days_back) + 'daysback.png'
#    pf_link = plot_dir + '/' + var + '_latest.png'
    iret = ts_obs_ocean(var, dts, stns_sail, obspts_sail, stns_sail_cols, \
                        titlein, plotfname)
#sys.exit()

#
#
#dts_plot = get_plot_dates(dts, plot_dir, saildrone_data, stns_sail)
#
#if len(dts_plot) == 0:
#    print 'No dates need plotting'
#print 
#
##---------------------------------------------------------------------------
## Loop over models.
##---------------------------------------------------------------------------
#for m in range(len(models)):
#    model = models[m]
#    plot_dir_c = plot_dir + '/' + model
#    print 'Plotting for model ', model
#    grid_model  = {}
#    diffs_sail  = {}
#    diffs_sb    = {}
#    modpts_sail = {}
#    modpts_sb   = {}
#
#    for f in range(len(fhrs)):
#        fhr = fhrs[f]
#
##        #--- See if any plots are needed for this model / fhr.
##        plot_needed = 0
##        for vmp in range(len(vars_model_plot)):
##            var = vars_model_plot[vmp]
##            plotfname = plot_dir + '/' + model + '_' + var + '_' + \
##                        str(days_back) + 'daysback' + '_f' + fhr + '.png'
##            if not os.path.isfile(plotfname):
##                plot_needed = 1
##        if plot_needed == 0:
##            print 'No plots needed for F', fhr, ', ', model
##            continue
#
#        model_files = sorted(glob.glob(model_data + '/' + model + '/data/*/' + \
#                    model + '.*.' + fhr + '.nc'))
#
##        pf = pickle_dir + '/' + model + '_' + sdt + '_' + \
##             str(days_back) + 'daysback' + '_f' + fhr + '.pkl'
#        pf = 'bypass_pickle'
#        if not os.path.isfile(pf):
#
#            dts_all     = []
#            diffs_sail  = {}
#            modpts_sail = {}
#            obspts_sail = {}
#            obspts_sb   = {}
#            
#            for mf in range(len(model_files)):
#                model_file = model_files[mf]
#                dt_c = re.findall(r'(\d{10})', model_file)[0]
#                print 'comparing ', dt_c, ' to ', sdt
#                if dt_c < sdt:
#                    print 'skipping!'
#                    continue
#                dts_all.append(dt_c)
#                vdt = time_increment(dt_c, float(fhr) / 24.0, dtfmt)
#                print model_files[mf], dt_c, vdt
#    
#                #--------------------------------------------------------------
#                # Load Saildrone netcdf data files.
#                #--------------------------------------------------------------
#                stns_sail_avail = []
#                stns_sb_avail = []
#                for s in range(len(stns_sail)):
#                    stn = stns_sail[s]
#                    #--- Saildrone file names denote hour of data (i.e.11Z is 
#                    #--- 1100-1159), and load_saildrone grabs the last 5-min of
#                    #--- the hour so for our dt_plot, we need to use PREVIOUS
#                    #--- hour's Saildrone file.
#                    vdt_m1 = time_increment(vdt, -1.0/24.0, dtfmt)
#                    file_c = saildrone_data + '/' + vdt_m1[0:8] + '/sd.' + \
#                             stn + '.' + vdt_m1 + '.nc'
#                    print 'loading ', file_c
#                    if not os.path.isfile(file_c):
#                        print 'cannot see ', file_c
#                        obspts_sail[stn,dt_c] = np.nan
#                    else:
#                        obspts_sail[stn,dt_c] = load_saildrone(file_c, \
#                                                               vars_sail)
#                        stns_sail_avail.append(stn)
#    
#                #--------------------------------------------------------------
#                # Load ships and buoys?  Maybe later...
#                #--------------------------------------------------------------
#                #obspts_sb = {}
#                #stns_sb_avail = []
#    
#                #--------------------------------------------------------------
#                # Load model grid, get diffs.
#                #--------------------------------------------------------------
#                grid_model, lat_model, lon_model = load_model_data(model_file, \
#                                                                   vars_model)
#                diffs_sail, modpts_sail = get_diffs_ts(stns_sail_avail, dt_c, \
#                                                       obspts_sail, grid_model,#\
#                                                       vars_model_diffs, \
#                                                       lat_model, lon_model, \
#                                                       model, 'sail', \
#                                                       diffs_sail, modpts_sail)
#
##            pickle.dump([dts_all, obspts_sail, vars_model_diffs, model, \
##                         diffs_sail, modpts_sail], open(pf, 'wb'), -1)
#        else:
#            print 'Loading ', pf
#            (dts_all, obspts_sail, vars_model_diffs, model, \
#             diffs_sail, modpts_sail) = pickle.load(open(pf, 'rb'))
#
#        #--------------------------------------------------------------
#        # Make time series plot.
#        #--------------------------------------------------------------
#        for vmp in range(len(vars_model_plot)):
#            var = vars_model_plot[vmp]
#            titlein = var_lab[var] + ' ' + model + ' - Saildrone Obs ' + \
#                      'Differences, FHR' + fhr
#            plotfname = plot_dir + '/' + model + '_' + var + '_' + \
#                        str(days_back) + 'daysback' + '_f' + fhr + '.png'
#            pf_link = plot_dir + '/' + var + '_latest.png'
#            iret = ts_diffs(var, dts_all, stns_sail, obspts_sail, \
#                            diffs_sail, modpts_sail, stns_sail_cols, \
#                            titlein, plotfname)
#            #sys.exit()
#
##---------------------------------------------------------------------------
## Clean up.
##---------------------------------------------------------------------------
#syscom = 'rm -rf ' + rundir
#print syscom
#os.system(syscom)

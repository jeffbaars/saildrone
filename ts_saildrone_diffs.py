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
plot_dir    = '/home/disk/funnel/saildrone/images/ts_diffs'
#plot_dir    = sail_dir + '/plots'

saildrone_data  = '/home/disk/jabba/steed/data/raw/saildrone/'
rawins_data     = '/home/disk/spock2/jbaars/qc_rawins_data'
model_data      = '/home/disk/tcu/grids'
model_data_arch = '/home/disk/jabba/steed/data/raw/'

#---------------------------------------------------------------------------
# Settings.
#---------------------------------------------------------------------------
models = ['gfsp25']
domain = 'd01'
#fhrs   = ['000', '003', '006', '009', '012', '015', '018', '021', '024']
#fhrs   = ['000', '012', '024']
fhrs   = ['024']

stns_sail = ['1031', '1036', '1037', '1057', '1058', '1059']
vars_sail = ['UWND_MEAN', 'VWND_MEAN', 'GUST_WND_MEAN', 'TEMP_AIR_MEAN', \
             'RH_MEAN', 'BARO_PRES_MEAN', \
             'TEMP_IR_SEA_WING_UNCOMP_MEAN', 'TEMP_O2_RBR_MEAN', \
             'TEMP_CTD_RBR_MEAN']

vars_model = ['HGT_500mb', 'DPT_2maboveground', 'PRMSL_meansealevel', \
             'UGRD_10maboveground', 'VGRD_10maboveground', \
             'TMP_2maboveground', 'TMP_surface']
vars_model_diffs = ['DPT_2maboveground', 'PRMSL_meansealevel', \
                    'TMP_2maboveground', 'UGRD_10maboveground', \
                    'VGRD_10maboveground', 'TMP_surface']
vars_model_plot = ['DPT_2maboveground', 'PRMSL_meansealevel', \
                    'TMP_2maboveground', 'TMP_surface']
#vars_model_plot = ['TMP_surface']
dtfmt = '%Y%m%d%H'
days_back = 30

#mod_cols = ['indigo', 'blue', 'deepskyblue', \
#            'darkgreen', 'lime', 'yellow', \
#            'magenta', 'red', 'salmon', 'gray', 'darkgray', 'lightblue']
stns_sail_cols = ['indigo', 'blue', 'deepskyblue', \
                  'darkgreen', 'lime', 'orange']

bypass_pickle = 1

#---------------------------------------------------------------------------
# Get current time and make 
#---------------------------------------------------------------------------
dt = get_now(dtfmt)
dt_utc = local_to_gmt(dt, dtfmt)
sdt = time_increment(dt_utc[0:8] + '00', -days_back, dtfmt)
        
#---------------------------------------------------------------------------
# Make run directory.
#---------------------------------------------------------------------------
rundir = rundirs_dir + '/ts_saildrone_diffs_' + dt_utc + '.' + str(os.getpid())
print 'making ', rundir
os.makedirs(rundir)

#---------------------------------------------------------------------------
# Loop over models.
#---------------------------------------------------------------------------
for m in range(len(models)):
    model = models[m]
    plot_dir_c = plot_dir + '/' + model
    print 'Plotting for model ', model
    grid_model  = {}
    diffs_sail  = {}
    diffs_sb    = {}
    modpts_sail = {}
    modpts_sb   = {}

    for f in range(len(fhrs)):
        fhr = fhrs[f]

#        #--- See if any plots are needed for this model / fhr.
#        plot_needed = 0
#        for vmp in range(len(vars_model_plot)):
#            var = vars_model_plot[vmp]
#            plotfname = plot_dir + '/' + model + '_' + var + '_' + \
#                        str(days_back) + 'daysback' + '_f' + fhr + '.png'
#            if not os.path.isfile(plotfname):
#                plot_needed = 1
#        if plot_needed == 0:
#            print 'No plots needed for F', fhr, ', ', model
#            continue

        #--- Gather and combine model files from both locations.
        model_files = sorted(glob.glob(model_data + '/' + model + '/data/*/' + \
                    model + '.*.' + fhr + '.nc'))
        model_files_arch = sorted(glob.glob(model_data_arch + '/' + model + \
                                            '/*/' + model + '.*.' + fhr +'.nc'))
        model_files = model_files + model_files_arch
        model_files = sorted(set(model_files))

#        pf = pickle_dir + '/' + model + '_' + sdt + '_' + \
#             str(days_back) + 'daysback' + '_f' + fhr + '.pkl'
        pf = 'bypass_pickle'
        if not os.path.isfile(pf):

            dts_all     = []
            diffs_sail  = {}
            modpts_sail = {}
            obspts_sail = {}
            obspts_sb   = {}
            
            for mf in range(len(model_files)):
                model_file = model_files[mf]
                dt_c = re.findall(r'(\d{10})', model_file)[0]
                print 'comparing ', dt_c, ' to ', sdt
                if dt_c < sdt:
                    print 'skipping!'
                    continue
                dts_all.append(dt_c)
                vdt = time_increment(dt_c, float(fhr) / 24.0, dtfmt)
                print model_files[mf], dt_c, vdt
    
                #--------------------------------------------------------------
                # Load Saildrone netcdf data files.
                #--------------------------------------------------------------
                stns_sail_avail = []
                stns_sb_avail = []
                for s in range(len(stns_sail)):
                    stn = stns_sail[s]
                    #--- Saildrone file names denote hour of data (i.e.11Z is 
                    #--- 1100-1159), and load_saildrone grabs the last 5-min of
                    #--- the hour so for our dt_plot, we need to use PREVIOUS
                    #--- hour's Saildrone file.
                    vdt_m1 = time_increment(vdt, -1.0/24.0, dtfmt)
                    file_c = saildrone_data + '/' + vdt_m1[0:8] + '/sd.' + \
                             stn + '.' + vdt_m1 + '.nc'
                    print 'loading ', file_c
                    if not os.path.isfile(file_c):
                        print 'cannot see ', file_c
                        obspts_sail[stn,dt_c] = np.nan
                    else:
                        obspts_sail[stn,dt_c] = load_saildrone(file_c, \
                                                               vars_sail)
                        stns_sail_avail.append(stn)
    
                #--------------------------------------------------------------
                # Load ships and buoys?  Maybe later...
                #--------------------------------------------------------------
                #obspts_sb = {}
                #stns_sb_avail = []
    
                #--------------------------------------------------------------
                # Load model grid, get diffs.
                #--------------------------------------------------------------
                print 'model_file = ', model_file
                grid_model, lat_model, lon_model = load_model_data(model_file,\
                                                                   vars_model)
                diffs_sail, modpts_sail = get_diffs_ts(stns_sail_avail, dt_c, \
                                                       obspts_sail, grid_model,\
                                                       vars_model_diffs, \
                                                       lat_model, lon_model, \
                                                       model, 'sail', \
                                                       diffs_sail, modpts_sail)

#            pickle.dump([dts_all, obspts_sail, vars_model_diffs, model, \
#                         diffs_sail, modpts_sail], open(pf, 'wb'), -1)
        else:
            print 'Loading ', pf
            (dts_all, obspts_sail, vars_model_diffs, model, \
             diffs_sail, modpts_sail) = pickle.load(open(pf, 'rb'))

        #--------------------------------------------------------------
        # Make time series plot.
        #--------------------------------------------------------------
        for vmp in range(len(vars_model_plot)):
            var = vars_model_plot[vmp]
            titlein = var_lab[var] + ' ' + model + ' - Saildrone Obs ' + \
                      'Differences, FHR' + fhr
            plotfname = plot_dir + '/' + model + '_' + var + '_' + \
                        str(days_back) + 'daysback' + '_f' + fhr + '.png'
            pf_link = plot_dir + '/' + var + '_latest.png'
            iret = ts_diffs(var, dts_all, stns_sail, obspts_sail, \
                            diffs_sail, modpts_sail, stns_sail_cols, \
                            titlein, plotfname)
            #sys.exit()

#---------------------------------------------------------------------------
# Clean up.
#---------------------------------------------------------------------------
syscom = 'rm -rf ' + rundir
print syscom
os.system(syscom)

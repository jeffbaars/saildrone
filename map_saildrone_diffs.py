#!/usr/bin/python
import os, sys
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
plot_dir    = '/home/disk/funnel/saildrone/images/maps_diffs'
#plot_dir    = sail_dir + '/plots'

saildrone_data = '/home/disk/jabba/steed/data/raw/saildrone/'
rawins_data    = '/home/disk/spock2/jbaars/qc_rawins_data'
model_data     = '/home/disk/tcu/grids'

#---------------------------------------------------------------------------
# Settings.
#---------------------------------------------------------------------------
models = ['gfsp25']
domain = 'd01'
#fhrs   = ['000', '003', '006', '009', '012', '015', '018', '021', '024']
fhrs   = ['000', '012', '024']

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
dtfmt = '%Y%m%d%H'
days_back = 3

#---------------------------------------------------------------------------
# Get current time.
#---------------------------------------------------------------------------
now = get_now(dtfmt)
now_utc = local_to_gmt(now, dtfmt)

#---------------------------------------------------------------------------
# Make run directory.
#---------------------------------------------------------------------------
rundir = rundirs_dir + '/map_saildrone_diffs_' + now_utc + '.'+str(os.getpid())
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

        #------------------------------------------------------------------
        # Determine which dates to plot.
        #------------------------------------------------------------------
        sdt = time_increment(now_utc, -days_back, dtfmt)
        dts = get_dates(sdt, now_utc, 60, dtfmt)
        dts_plot = get_diffs_plot_dates(dts, fhr, plot_dir_c, \
                                        saildrone_data, model_data, model, \
                                        stns_sail)
#        dts_plot = ['2019110600']    
    
        #-------------------------------------------------------------------
        # Make plots for each dts_plot.
        #-------------------------------------------------------------------
        for d in range(len(dts_plot)):
            dt_plot = dts_plot[d]
            vdt = time_increment(dt_plot, float(fhr) / 24.0, dtfmt)
            if vdt > now_utc:
                print 'verif date, ', vdt, ', is in the future'
                continue
            if vdt < sdt:
                print 'verif date, ', vdt, ', is too old'
                continue

            plotfname = get_plotfname_diffs(plot_dir_c, dt_plot, model, fhr)

            if os.path.isfile(plotfname):
                print 'file already exists for F', fhr, model, dt_plot
                continue
            else:
                print 'Making plot for date ', dt_plot
            
            #---------------------------------------------------------------
            # Load Saildrone netcdf data files.
            #---------------------------------------------------------------
            obspts_sail = {}
            stns_sail_avail = []
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
                    obspts_sail[stn] = np.nan
                else:
                    obspts_sail[stn] = load_saildrone(file_c, vars_sail)
                    stns_sail_avail.append(stn)

            #-------------------------------------------------------------------
            # Read in ship and buoy obs from QC rawins files.
            #-------------------------------------------------------------------
            rawins_file = rawins_data + '/' + vdt[0:6] + '/obs.' + vdt
            #rawins_file = 'junk'
            if os.path.isfile(rawins_file):
                print 'Reading ', rawins_file
                (stns_sb, typ_sb, obspts_sb) = load_qc_rawins(rawins_file, \
                                                              rundir)
            else:
                stns_sb = []
                typ_sb  = []
                obspts_sb = {}
                print 'Cannot see rawins obs file ', rawins_file

            #--------------------------------------------------------------
            # Load model data, get diffs for saildrone and ships and buoys.
            #--------------------------------------------------------------
            model_file = model_data + '/' + model + '/data/' + dt_plot + '/' + \
                         model + '.' + dt_plot + '.' + fhr + '.nc'
            if not os.path.isfile(model_file):
                print 'cannot see ', model_file
                continue
    
            print 'Loading ', model_file
            grid_model, lat_model, lon_model = load_model_data(model_file, \
                                                               vars_model)
            diffs_sail, modpts_sail = get_diffs(stns_sail_avail, obspts_sail, \
                                                grid_model,\
                                                vars_model_diffs, lat_model, \
                                                lon_model, model, 'sail')
            diffs_sb, modpts_sb = get_diffs(stns_sb, obspts_sb, grid_model, \
                                            vars_model_diffs, lat_model, \
                                            lon_model, model, 'sb')

            #---------------------------------------------------------------
            # Get plot title and name together. Since we're using the last 5-
            # min of data from the data files, we're essentially making plots
            # for the hour of the data file +1.  So adjust the title accord-
            # ingly, but leave the plotfname to match the data file fname.
            #---------------------------------------------------------------
            dt_nice = get_nice_date(vdt, dtfmt, '%Y-%b-%d %H:%M Z')
            dt_nice_lst = get_nice_date(gmt_to_local(vdt), dtfmt, \
                                        '%Y-%b-%d %-I:%M %p')
            titlein = model + ' minus obs, FHR-' + fhr + ', ' + \
                      dt_nice + ' (' + dt_nice_lst + ')'
            plotfname = get_plotfname_diffs(plot_dir_c, dt_plot, model, fhr)
        
            #---------------------------------------------------------------
            # Make map.
            #---------------------------------------------------------------
            iret = mapper_diffs(stns_sail_avail, obspts_sail, diffs_sail, \
                                modpts_sail, stns_sb, typ_sb,\
                                obspts_sb, diffs_sb, modpts_sb, grid_model, \
                                lat_model, lon_model, titlein, plotfname)

#---------------------------------------------------------------------------
# Clean up.
#---------------------------------------------------------------------------
syscom = 'rm -rf ' + rundir
print syscom
os.system(syscom)

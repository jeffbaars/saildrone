#!/usr/bin/python
import sys, getopt, os.path
import numpy as np
#import matplotlib.pyplot as plt
from utils_mysql import *
from utils_date import *
from utils_verify_ens import *
import pickle
from metpy.calc import wind_components

#-----------------------------------------------------------------------------
# Paths.
#-----------------------------------------------------------------------------
homedir   = '/home/disk/spock/jbaars';
workdir   = homedir + '/saildrone'
datadir   = workdir + '/data'
driverdir = workdir + '/driver'
pickledir = workdir + '/pickle'
plotdir   = workdir + '/plots'
logdir    = workdir + '/log'

#-----------------------------------------------------------------------------#
# Settings section
#-----------------------------------------------------------------------------#
models  = ['ensgefs01',  'ensgefs02', 'ensgefs03', 'ensgefs04', 'ensgefs05', \
           'ensgefs06',  'ensgefs07', 'ensgefs08', 'ensgefs09', 'ensgefs10', \
           'ensgfswrf4', 'enshrrr',   'enscmcg',   'ensgasp',   'ensjmag', \
           'ensngps',    'enstcwb',   'ensukmo']
domain = 'd1'

netid = 'bf'

variables = [ 'temp', 'dew', 'spd', 'dir', 'pres', 'pcp6' ]

#varsplot = ['temp', 'pcp6', 'dew', 'spd', 'pres']
varsplot = ['pcp6']

sdt = '2019090100'
edt = '2019102000'

#periods = [ 3, 30, 90 ]
periods = [ 7 ]

#ihrs = ['00', '12']
ihrs = ['00']

#fhrs = [6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72]
fhrs = [00]

#--- 1 = skip winds < 3 knots; 0 = use all winds.
windskip = 1

#-----------------------------------------------------------------------------
# FOR NOW, JUST DO FIRST PERIOD OF PERIODS.  EVENTUALLY LOOP OVER ALL?
#-----------------------------------------------------------------------------
p = 0

#-----------------------------------------------------------------------------
# Get db pw, current time (now), idts, vdts, etc.
#-----------------------------------------------------------------------------
#--- Get mysql d.b. password from file.
pw = get_db_pw(pwfn)

#--- Get start and end dates.
now = get_now(dtfmt)
if 'sdt' not in locals() :
    edt = now
    sdt = time_increment(edt, -periods[p], dtfmt)
    print 'Running for ', sdt, ' - ', edt

    idts = get_idts(dtfmt, ihrs, periods[p])
    vdts = get_vdts(idts, fhrs, dtfmt)
else:
    idts = get_dates(sdt, edt, 24*60, dtfmt)
    vdts = get_vdts(idts, fhrs, dtfmt)

sidt = min(idts)
eidt = max(idts)
svdt = min(vdts)
evdt = max(vdts)
sidteidt = sidt + '_' + eidt
fhrsrange = str(fhrs[0]) + '_' + str(fhrs[len(fhrs)-1])

#-----------------------------------------------------------------------------
# Get list of station refids, lats, and lons load_refids.
#-----------------------------------------------------------------------------
yyyy = edt[0:4]
refids, lats, lons = load_refids(host, user, pw, db, 'wrfgfs', domain, yyyy, \
                                 netid)
print refids, lats, lons
sys.exit()


#-----------------------------------------------------------------------------
# If pickle file exists, use that.  Otherwise load data from sql.
#-----------------------------------------------------------------------------
pf = pickledir + '/' + sidteidt + '_' + domain + '_f' + fhrsrange + '.pickle'
#pf = 'test'
if not os.path.isfile(pf):
    print 'Cannot see pickle file ', pf, ', continuing with data load...'

    #-------------------------------------------------------------------------
    # Load obs from sql database.
    #-------------------------------------------------------------------------
    print 'Filling observations dict...'
    obs = load_observations(host, user, pw, db, variables, vdts, refids, dtfmt)

    #-------------------------------------------------------------------------
    # Load forecasts from sql database.
    #-------------------------------------------------------------------------
    print 'Filling elevcors dict...'
    elevcors = load_elevcors(host, user, pw, db, models, domain, svdt, \
                             evdt, dtfmt)

    #--- Fill model data dictionary.
    print 'Filling forecasts dict...'
    forecasts = load_forecasts(host, user, pw, db, models, domain, variables, \
                               elevcors, fhrs, sidt, eidt, dtfmt)

    #--- Dump data to a pickle file.
    pickle.dump([obs, forecasts, idts, vdts], open(pf, 'wb'), -1)
else:
    print 'Loading ', pf
    (obs, forecasts, idts, vdts) = pickle.load(open(pf, 'rb'))

#-----------------------------------------------------------------------------
# Rank histogram.
#-----------------------------------------------------------------------------
for f in range(len(fhrs)):
    fhr = fhrs[f]
    for var in varsplot:
        pfadd = ''
        if var == 'spd' and windskip == 1:
            pfadd = '_gt' + str(spdmin) + 'kts'
        plotfname = plotdir + '/rankhist_' + var + pfadd + '_' + domain + \
                    '_' + sidteidt + '_f' + str(fhr) + '.png'
        rh = rank_histogram(models, domain, refids, idts, fhr, var, obs, \
                            forecasts, plotfname, windskip)

sys.exit()


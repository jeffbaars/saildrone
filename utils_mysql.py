#!/usr/bin/python
import  os, os.path, time, string
import sys, string, datetime, time
import numpy as np
import MySQLdb
from utils_qc_webpage import *

mvc  = -9999.0
host = 'sql.atmos.washington.edu'
user = 'ovens'
db   = 'verify'
pwfn = '/home/disk/sage1/mm5rt/.obsdb_password_rmm5rt'

qctests = [ 'range', 'step', 'persist', 'spatial']

qctest_dict = {
    'range':   '2', 
    'step':    '3', 
    'persist': '4',
    'spatial': '5'
}

mod_varname_dict = {
    'temp': 't2m',
    'dew' : 'dew2m',
    'rh'  : 'rh2m',
    'spd' : 'wsp10m',
    'dir' : 'dir10m',
    'pres': 'slp',
    'pcp6': 'pcp6'
    }

mod_varname_long_dict = {
    'temp': '2-m Temperature',
    'dew' : '2-m Dew Point Temperature',
    'rh'  : '2-m Relative Humidity',
    'spd' : '10-m Wind Speed',
    'dir' : '10-m Wind Direction',
    'pres': 'Sea Level Pressure',
    'pcp6': '6-h Precipitation'
    }

#-----------------------------------------------------------------------------
# Read db pw file.
#-----------------------------------------------------------------------------
def get_db_pw(pwfn):
    with open(pwfn) as f:
        pw = f.readlines()[0]
        pw = pw.strip()
    return pw

#-----------------------------------------------------------------------------
# Get an elev cor nearest sent-in date 'dt' from a elevcors dict, by
# looping up to 1000  hours forwards and backwards from 'dt'.  
#-----------------------------------------------------------------------------
def get_elevcor(elevcors, model, refid, dt, dtfmt):
    ntries = 1000
    elevcor = np.nan
    key = (model,refid,dt)
    if key in elevcors:
        elevcor = elevcors[key]
    else:
        for n in range(1,ntries):
            dt_c = time_increment(dt, n * (1./24.), dtfmt)
            key = (model,refid,dt_c)
            if key in elevcors:
                elevcor = elevcors[key]                
                break
            else:
                dt_c = time_increment(dt, -n * (1./24.), dtfmt)
                key = (model,refid,dt_c)
                if key in elevcors:
                    elevcor = elevcors[key]
                    break
    return elevcor

#-----------------------------------------------------------------------------
# Get closest date from a list of string dates.
#-----------------------------------------------------------------------------
def get_closest_date(dts, dt):
    dts_int = map(int, dts)
    dts_int[:] = [abs(x - int(dt)) for x in dts_int]
    imin = np.argmin(dts_int)
    dt_close = dts[imin]
    return dt_close

#-----------------------------------------------------------------------------
# Get elevation corrections (elevcors) for temp and dewp, between sdt and edt.
#-----------------------------------------------------------------------------
def load_elevcors(host, user, pw, db, models, domain, sdt, edt, dtfmt):

    dts_all = get_dates(sdt, edt, 60, dtfmt)
    db = MySQLdb.connect(host = host, user = user, passwd = pw, db = db)
    cur = db.cursor()
    elevcors = {}
    for m in range(len(models)):
        model = models[m] + domain

        query = 'SELECT refid, date_format(modifydate,\'%Y%m%d%H\'),' + \
                'elevcor, date_format(enddate,\'%Y%m%d%H\') ' + \
                'FROM ' + model + '_elev_YEAR ' + \
                'WHERE modifydate >= SDATE' + '0000' + ' and ' + \
                'modifydate <= EDATE' + '0000 ' + \
                'ORDER BY refid,modifydate'
        queries = get_queries(query, sdt, edt)

        for query_c in queries:
            cur.execute(query_c)
            for row in cur:
                refid = row[0]
                mdt   = row[1]
            
                #--- This taken from legacy code (d.ovens, I think): if elev
                #--- cor is null, set it to 0.
                if row[2]:
                    ecor = row[2]
                else:
                    ecor = 0
                edt   = row[3]
                elevcors[model,refid,mdt] = ecor

                #--- Fill in elevcors between modifydate and enddate,
                #--- if those dates differ.
                if mdt != edt:
                    dts = get_dates(mdt, edt, 60, dtfmt)
                    for date in dts:
                        elevcors[model,refid,date] = ecor
                else:
                    elevcors[model,refid,mdt] = ecor
    db.close()

    return elevcors

#-----------------------------------------------------------------------------
# Get forecasts from database.
#-----------------------------------------------------------------------------
def load_forecasts(host, user, pw, db, models, domain, variables, elevcors, \
                  fhrs, sdt, edt, dtfmt):

    #--- Get list of forecast variables that correspond to obs variables.
    varsf = []
    for v in range(len(variables)):
        var = variables[v]
        varsf.append(mod_varname_dict[var])
    vars_str = ','.join(varsf)
    fhrs_str = ','.join(map(str, fhrs))

    forecasts = {}

    db = MySQLdb.connect(host = host, user = user, passwd = pw, db = db)
    cur = db.cursor()

    for m in range(len(models)):
        model = models[m] + domain
        print '   loading ', model
        
        query = 'SELECT refid, fhr, date_format(initdate,\'%Y%m%d%H\'), ' + \
                'date_format(validdate,\'%Y%m%d%H\'),' + vars_str + ' ' +\
                'FROM ' + model + '_YEAR ' + \
                'WHERE initdate >= SDATE' + '0000' + ' and ' + \
                'initdate <= EDATE' + '0000 and ' + \
                'fhr in (' + fhrs_str + ') ' + \
                'ORDER BY refid, initdate'
#        print query
        queries = get_queries(query, sdt, edt)

        for query_c in queries:
            cur.execute(query_c)

            for row in cur:
                refid = row[0]
                fhr   = row[1]
                idt   = row[2]
                vdt   = row[3]
                for v in range(len(variables)):
                    var_c = variables[v]
                    data_c = row[4+v]
                    if data_c != None:
                        #--- Do elevation correction on temp and dewp.
                        if var_c == 'temp' or var_c == 'dewp':
                            ecor = get_elevcor(elevcors, model,refid,vdt,dtfmt)

                            #--- Look out for nan's.
                            if (data_c != data_c) or (ecor != ecor):
                                forecasts[model,refid,idt,fhr,var_c] = np.nan
                            else:
                                forecasts[model,refid,idt,fhr,var_c] = data_c+\
                                                                       ecor
                        else:
                            forecasts[model,refid,idt,fhr,var_c] = data_c
                    else:
                        forecasts[model,refid,idt,fhr,var_c] = np.nan
                #sys.exit()
    db.close()

    return forecasts

#-----------------------------------------------------------------------------
# Get observations from database.
#-----------------------------------------------------------------------------
def load_observations(host, user, pw, db, variables, vdts, refids, dtfmt):

    vars_str = ','.join(variables)
    refids_str = ', '.join("'{0}'".format(r) for r in refids)
    db = MySQLdb.connect(host = host, user = user, passwd = pw, db = db)
    obs = {}
    for d in range(len(vdts)):
        vdt = vdts[d]
        year = vdt[0:4]
        print 'loading obs for ', vdt
#        query = 'SELECT refid, date_format(date,\'%Y%m%d%H\'),' + \
#                vars_str + ' FROM sfc' + year + ' ' + \
#                'FORCE INDEX (datelatlon) ' + \
#                'WHERE date = ' + vdt + '0000 ' + \
#                'ORDER BY refid,date'
        query = 'SELECT refid, date_format(date,\'%Y%m%d%H\'),' + \
                vars_str + ' FROM sfc' + year + ' ' + \
                'FORCE INDEX (datelatlon) ' + \
                'WHERE date = ' + vdt + '0000 ' + \
                'and refid in (' + refids_str + ') ' + \
                'ORDER BY refid,date'
        cur = db.cursor()

        cur.execute(query)
        for row in cur:
            refid = row[0]
            dt    = row[1]
            for v in range(len(variables)):
                var_c = variables[v]
                data_c = row[2+v]
                if data_c != None:
                    obs[refid,dt,var_c] = data_c
                else:
                    obs[refid,dt,var_c] = np.nan
    db.close()

    return obs

#-----------------------------------------------------------------------------
# Get lists of refids, lats, and lons from sent-in model from database.
#-----------------------------------------------------------------------------
def load_refids(host, user, pw, db, model, domain, yyyy, netid):

    db = MySQLdb.connect(host = host, user = user, passwd = pw, db = db)
    refids = []
    query = 'SELECT distinct(refid) from ' + model + domain + '_' + yyyy + \
            ' where refid like \'' + netid + '_%\''
    print query
    
    cur = db.cursor()
    cur.execute(query)
    for row in cur:
        refids.append(row[0])

    lats = []
    lons = []
    for r in range(len(refids)):
        refid = refids[r]
        query = 'SELECT lat, lon from stations where refid = \'' + \
                refid + '\''
        cur = db.cursor()
        cur.execute(query)
        for row in cur:
            lats.append(float(row[0]))
            lons.append(float(row[1]))
    db.close()

    return refids, lats, lons

#-----------------------------------------------------------------------------
# Get list of query or queries, handling crossing year table boundary.
#-----------------------------------------------------------------------------
def get_queries(qin, sdt, edt):

    syear = sdt[0:4]
    eyear = edt[0:4]
    nyears = int(eyear) - int(syear) + 1

    queries = []
    if syear == eyear:
        query = qin
        query = query.replace('YEAR', syear)
        query = query.replace('SDATE', sdt)
        query = query.replace('EDATE', edt)                
        queries.append(query)
    else:
        for ny in range(nyears):
            year = str(int(syear) + ny)

            #--- On first year, go from original start date to end of start
            #--- date's year.
            if ny == 0:
                sdt_c = sdt
                edt_c = year + '123123'
            #--- On last year, go from Jan 1 00:00 of end date's year to end
            #--- date.
            elif ny == (nyears - 1):
                sdt_c = year + '010100'
                edt_c = edt
            #--- For intermediate years (only cases where we are crossing more
            #--- than one year boundary) go from Jan 01 - Dec 31.
            else:
                sdt_c = year + '010100'
                edt_c = year + '123123'
                
            query = qin
            query = query.replace('YEAR', year)
            query = query.replace('SDATE', sdt_c)
            query = query.replace('EDATE', edt_c)
            queries.append(query)

    return queries


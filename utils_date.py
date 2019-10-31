#!/usr/bin/python
import  os, os.path, time, glob, re, string
import sys, string, readline, datetime, time
import numpy as np
from dateutil import tz
import pytz

#dtfmt = '%Y%m%d%H'
dtfmt_nice = '%Y-%b-%d %HZ'

#-----------------------------------------------------------------------------
# Get list of dates given start date, end date, and time step in minutes.
#-----------------------------------------------------------------------------
def get_dates(sdt, edt, minute_iter, dtfmt):
    sdtnum = datetime.datetime(*(time.strptime(sdt, dtfmt)[0:6]))
    edtnum = datetime.datetime(*(time.strptime(edt, dtfmt)[0:6]))
    delta = datetime.timedelta(minutes = minute_iter)
    now = sdtnum
    dts = []
    while now <= edtnum:
        dts.append(now.strftime(dtfmt))
        now += delta
    return dts

#-----------------------------------------------------------------------------
# Convert unix time to date.
#-----------------------------------------------------------------------------
def unix_to_date(dt, dtfmt):
    dtout = datetime.datetime.fromtimestamp(dt,pytz.utc).strftime(dtfmt)
    return dtout

#-----------------------------------------------------------------------------
# Get current date/time.
#-----------------------------------------------------------------------------
def get_now(dtfmt):
    now = time.strftime(dtfmt)
    return now

#-----------------------------------------------------------------------------
# Get list of idts given ihrs.
#-----------------------------------------------------------------------------
def get_idts(dtfmt, ihrs, days_back):
    now_local = get_now(dtfmt)
    now = local_to_gmt(now_local)
    now_hh = now[8:10]
    if (int(now_hh) > 12):
        now = now[:8] + '12'
    else:
        now = now[:8] + '00'    

    sdt = time_increment(now, -days_back, dtfmt)
    idts_tmp = get_dates(sdt, now, 60*12, dtfmt)

    idts = []
    for i in range(len(idts_tmp)):
        idt_hh = idts_tmp[i][8:10]
        if (idt_hh in ihrs):
            idts.append(idts_tmp[i])

#    idts.sort(reverse=True)

    return idts

#-----------------------------------------------------------------------------
# Increment time.
#-----------------------------------------------------------------------------
def time_increment(dt, inc_days, dtfmt):
    dtnum = datetime.datetime(*(time.strptime(dt, dtfmt)[0:6]))
    delta = datetime.timedelta(days = inc_days)
    dtoutnum = dtnum + delta
    dtout = dtoutnum.strftime(dtfmt)
    return dtout

#-----------------------------------------------------------------------------
# Get vdts given idts and fhrs.
#-----------------------------------------------------------------------------
def get_vdts(idts, fhrs, dtfmt):
    vdts     = []
    vdts_all = []
    for d in range(len(idts)):
        idt_c = idts[d]
        for f in range(len(fhrs)):
            fhr_c = fhrs[f]
            idtnum = datetime.datetime(*(time.strptime(idt_c, dtfmt)[0:6]))
            delta = datetime.timedelta(minutes = fhr_c * 60)
            vdtnum = idtnum + delta
            vdt_c = vdtnum.strftime(dtfmt)
            vdts_all.append(vdt_c)
    vdts = np.unique(vdts_all)
    return vdts

#---------------------------------------------------------------------------
# Convert YYYYMMDDHH GMT date to YYYYMMDDHH local time.
#---------------------------------------------------------------------------
def gmt_to_local(dt):
    dtfmt = '%Y%m%d%H'
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.datetime.strptime(dt, dtfmt)    

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    dttmp = utc.astimezone(to_zone)
    dtout = datetime.datetime.strftime(dttmp, dtfmt)    

    return dtout

#---------------------------------------------------------------------------
# Convert YYYYMMDDHH local date to YYYYMMDDHH GMT time.
#---------------------------------------------------------------------------
def local_to_gmt(dt, dtfmt):
    to_zone = tz.tzutc()
    from_zone = tz.tzlocal()
    utc = datetime.datetime.strptime(dt, dtfmt)    

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    dttmp = utc.astimezone(to_zone)
    dtout = datetime.datetime.strftime(dttmp, dtfmt)    

    return dtout

#---------------------------------------------------------------------------
# Get date in a nice format.
# Examples:
# '%Y-%b-%d %H:%M %p': 2018-Aug-14 03:00 AM
# '%Y%m%d%H': 201808140300
# '%a %H:%M %p': Tue 12:00 PM
#---------------------------------------------------------------------------
def get_nice_date(dt, dtfmtin, dtfmtout):
    dtnum = datetime.datetime(*(time.strptime(dt, dtfmtin)[0:6]))
    dtout = dtnum.strftime(dtfmtout)
    return dtout

'''
#---------------------------------------------------------------------------
# Get date in a nice format.
#---------------------------------------------------------------------------
def get_nice_date(dt):
    yyyy = dt[0:4]
    mm   = dt[4:6]
    dd   = dt[6:8]
    hh   = dt[8:10]        
    if (len(dt) <= 10):
        mn = '00'
    else:
        mn = dt[10:12]
    if (float(hh) >= 0 and float(hh) < 12):
        ampm = 'AM'
    elif(float(hh) > 12):
        hh = '{:02d}'.format(int(float(hh) - 12))
        ampm = 'PM'
    elif(float(hh) == 12):
        ampm = 'PM'
    hhmm = hh + ':' + mn + ' ' + ampm

    if (mm == '01'): monplot = 'Jan'
    if (mm == '02'): monplot = 'Feb'
    if (mm == '03'): monplot = 'Mar'
    if (mm == '04'): monplot = 'Apr'            
    if (mm == '05'): monplot = 'May'
    if (mm == '06'): monplot = 'Jun'
    if (mm == '07'): monplot = 'Jul'
    if (mm == '08'): monplot = 'Aug'
    if (mm == '09'): monplot = 'Sep'
    if (mm == '10'): monplot = 'Oct'
    if (mm == '11'): monplot = 'Nov'
    if (mm == '12'): monplot = 'Dec'

    dtout = yyyy + '-' + monplot + '-' + dd + ' ' + hhmm
    return dtout
'''

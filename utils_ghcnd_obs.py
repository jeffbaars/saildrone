#!/usr/bin/python
import os, sys, glob, re
import numpy as np
import codecs

seasons = ['spring', 'summer', 'fall', 'winter', 'annual']
min_season_days = 85

ghcnd_dict = {
    'KSEA': 'USW00024233',
    'KSMP': 'USW00024237',
    'KYKM': 'USW00024243',
    'KGEG': 'USW00024157',
    'KPDX': 'USW00024229',
    'KMFR': 'USW00024225',
    'KHQM': 'USW00094225',
    'KNUW': 'USW00024255',
    'KUIL': 'USW00094240',
    'KBLI': 'USW00024217',
    'KELN': 'USW00024220', 
    'KOLM': 'USW00024227',
    'KALW': 'USW00024160', 
    'KPSC': 'USW00024163', 
    'KRDD': 'USW00024257',
    'KBOI': 'USW00024131', 
    'KSLC': 'USW00024127',
    'KEKO': 'USW00024121',
    'KIDA': 'USW00024145',
    'KBZN': 'USW00024132',
    'KBTM': 'USW00024135',
    'KMYL': 'USW00094182', 
    'KPIH': 'USW00024156', 
    'KEKA': 'USW00024213',
    'KAST': 'USW00094224',
    'KRBG': 'USW00024231',
    'KRDM': 'USW00024230',
    'KBNO': 'USW00094185', 
    'KDLS': 'USW00024219',
    'KOMK': 'USW00094197',
    'KEAT': 'USW00094239',
    'KSXT': 'USW00024235',
    'KOTH': 'USW00024251',
    'KPAE': 'USW00024203',
    'KCLM': 'USW00094266',
    'KAWO': 'USW00024247',
    'KEPH': 'USW00024141',
    'KMWH': 'USW00024110',
    'KBKE': 'USW00024130',
    'KRKS': 'USW00024027',
    'KENV': 'USW00024111',
    'KWMC': 'USW00024128',
    'KLMT': 'USW00024224',
    'KSLE': 'USW00024232',
    'KEUG': 'USW00024221',
    'KONP': 'USW00024285',
    'KTMK': 'USW00024254',
    'KCEC': 'USW00024286',
    'KFHR': 'USW00094276',
    'KTWF': 'USW00094178',
    'KOVE': 'USW00093210',
    'KRBL': 'USW00024216',
    'KMYV': 'USW00093205',
    'KCIC': 'US1CABT0017'
    }

station_name_dict = {
    'KSEA': 'Seattle, WA',
    'KSMP': 'Stampede Pass, WA',
    'KYKM': 'Yakima, WA',
    'KGEG': 'Spokane, WA',
    'KPDX': 'Portland, OR',
    'KMFR': 'Medford, OR',
    'KHQM': 'Hoquiam, WA',
    'KNUW': 'Whidbey Island, WA',
    'KUIL': 'Quillayute, WA',
    'KBLI': 'Bellingham, WA',
    'KELN': 'Ellensburg, WA',
    'KOLM': 'Olympia, WA',
    'KALW': 'Walla Walla, WA',
    'KPSC': 'Pasco Tri-Cities, WA',
    'KRDD': 'Redding, CA',
    'KBOI': 'Boise, ID',
    'KSLC': 'Salt Lake City, UT',
    'KEKO': 'Elko, NV',
    'KIDA': 'Idaho Falls, ID',
    'KBZN': 'Bozeman, MT',
    'KBTM': 'Butte, MT',
    'KMYL': 'McCall, ID',
    'KPIH': 'Pocatello, ID',
    'KEKA': 'Eureka, CA',
    'KAST': 'Astoria, OR',
    'KRBG': 'Roseburg, OR',
    'KRDM': 'Redmond, OR',
    'KBNO': 'Burns, OR',
    'KDLS': 'The Dalles, OR',
    'KOMK': 'Omak, WA',
    'KEAT': 'Wenatchee, WA',
    'KSXT': 'Sexton Summit, OR',
    'KOTH': 'North Bend, OR',
    'KPAE': 'Everett, WA',
    'KCLM': 'Port Angeles, WA',
    'KAWO': 'Arlington, WA',
    'KEPH': 'Ephrata, WA',
    'KMWH': 'Moses Lake, WA',
    'KBKE': 'Baker City, OR',
    'KRKS': 'Rock Springs, WY',
    'KENV': 'Wendover AFB, UT',
    'KWMC': 'Winnemucca, NV',
    'KLMT': 'Klamath Falls, OR',
    'KSLE': 'Salem, OR',
    'KEUG': 'Eugene, OR',
    'KONP': 'Newport, OR',
    'KTMK': 'Tillamook, OR',
    'KCEC': 'Crescent City, CA',
    'KFHR': 'Friday Harbor, WA',
    'KTWF': 'Twin Falls, ID',
    'KOVE': 'Oroville, CA',
    'KRBL': 'Red Bluff, CA',
    'KMYV': 'Marysville Yuba County, CA',
    'KCIC': 'Chico, CA',
    'SNO30': 'Snoqualmie Pass, WA'
    }


#---------------------------------------------------------------------------
# Read in a GHCND obs file.
#---------------------------------------------------------------------------
def read_ghcnd(stns, elements, ghcnd_dir, syyyymm, eyyyymm):

    data_out = {}
    dts_all = []

    for s in range(len(stns)):
        stn = stns[s]
        stn_ghcnd = ghcnd_dict[stn]
        file_c = ghcnd_dir + '/' + stn_ghcnd + '.dly'

        if not os.path.isfile(file_c):
            print 'cannot find file ', file_c
            continue
        else:
            print 'Reading ', stn, ' file ', file_c

        readLoc = codecs.open(file_c, "r", "utf-8")
        allLines = readLoc.readlines()
        readLoc.close
    
        for lineOfData in allLines:
            countryCode = lineOfData[0:2]
            stationID = lineOfData[0:11]
            stationMonthCode = lineOfData[0:17]
            year = lineOfData[11:15]
            month = lineOfData[15:17]
            
            #--- Skip lines not in 'elements'.
            element = lineOfData[17:21]
            if not element in elements:
                continue

            #--- Skip lines with dates falling outside sent-in date ranges.
            yyyymm = year + month
            if (yyyymm < syyyymm or yyyymm > eyyyymm):
                continue

            for x in range(0, 31):
                dayOM = x + 1
                offsetStart = (x*8)+21
                offsetEnd = offsetStart + 8
                ld = lineOfData[offsetStart:offsetEnd]
                val = ld[0:5]
                mflag = ld[5:6]
                qflag = ld[6:7]
                sflag = ld[7:8]
                
                if float(val) == -9999.0:
                    val = np.nan
        
                if element == 'TMAX' or element == 'TMIN':
                    #--- Temperatures are in tenths of degrees C.
                    valout = float(val) / 10.0
                elif element == 'PRCP':
                    #--- Precip is in tenths of a mm.  Converting to inches.
                    valout = (float(val) / 10.0) * 0.0393701

                #--- Look at qflag and set valout to nan if it's flagged.
                #--- Some of these out of range values looked legit though!
                if qflag and qflag.strip():
                    valout = np.nan            

                day_c = '{:02d}'.format(x+1)
                dt_c = year + month + day_c
                dts_all.append(dt_c)
                data_out[element,stn,dt_c] = valout

        #--- Get unique list of dates.
        dts_all = list(sorted(set(dts_all)))

    #--- If T2MEAN was requested, calculate it from T2MAX and T2MIN for
    #--- every station and date.
    if 'T2MEAN' in elements:
        for s in range(len(stns)):
            for d in range(len(dts_all)):
                keymax = ('TMAX', stns[s], dts_all[d])
                keymin = ('TMIN', stns[s], dts_all[d])
                if keymax in data_out and keymin in data_out:
                    keymean = ('T2MEAN', stns[s], dts_all[d])
                    data_out[keymean] = np.mean([data_out[keymax], \
                                                data_out[keymin]])
    return data_out, dts_all

#---------------------------------------------------------------------------
# Get seasonal stats (totals or averages currently).
#---------------------------------------------------------------------------
def get_seasonal_stats_ghcnd(data_all, dts_all, stns, var, stat):

    out_sum = {}
    out_avg = {}
    out_max = {}
    out_min = {}
    years_all = []

    for s in range(len(stns)):
        stn = stns[s]
        ndays = {}
        years_stn = []
        for d in range(len(dts_all)):
            dt_c = dts_all[d]
            yyyy = dt_c[0:4]
            mm = dt_c[4:6]
            years_stn.append(yyyy)

            if (var,stn,dt_c) in data_all:
                dat_c = data_all[var,stn,dt_c]
            else:
                continue

            #--- annual is all days so get sum/max/min for every dts_all.
            (ndays, out_sum, out_max, out_min) = \
                    get_season_summaxmin(dat_c, stn, 'annual', yyyy, mm, ndays,\
                                         out_sum, out_max, out_min)

            if (mm == '03' or mm == '04' or mm == '05'):
                season = 'spring'
            if (mm == '06' or mm == '07' or mm == '08'):
                season = 'summer'
            if (mm == '09' or mm == '10' or mm == '11'):
                season = 'fall'
            if (mm == '12' or mm == '01' or mm == '02'):
                season = 'winter'
            (ndays, out_sum, out_max, out_min) = \
                    get_season_summaxmin(dat_c, stn, season, yyyy, mm, ndays, \
                                         out_sum, out_max, out_min)

        #--- Get list of unique, sorted years found above.
        years = list(sorted(set(years_stn)))

        #--- Check number of data points per unique years and nan out
        #--- ones that do not have enough (< min_season_days).
        for y in range(len(years)):
            yyyy = years[y]
            for s in range(len(seasons)):
                season = seasons[s]
                if (season+yyyy) in ndays:
                    if ndays[season+yyyy] < min_season_days:
                        out_sum[season,stn,yyyy] = np.nan
                        out_max[season,stn,yyyy] = np.nan
                        out_min[season,stn,yyyy] = np.nan
                else:
                    ndays[season+yyyy] = np.nan
                    out_sum[season,stn,yyyy] = np.nan
                    out_max[season,stn,yyyy] = np.nan
                    out_min[season,stn,yyyy] = np.nan

        #--- if stat requested was 'avg', do averaging.
        if (stat == 'avg' or stat == 'max' or stat == 'min'):
            for y in range(len(years)):
                yyyy = years[y]
                for s in range(len(seasons)):
                    season = seasons[s]
                    out_avg[season,stn,yyyy] = out_sum[\
                        season,stn,yyyy] / ndays[season+yyyy]
            
        #--- Keep around all years found for this station.
        years_all.append(years_stn)

    #--- Final, unique, sorted list of years found.
    years = list(sorted(set(years_all[0])))            

    if (stat == 'avg'):
        return out_avg, years
    elif (stat == 'max'):
        return out_max, years
    elif (stat == 'min'):
        return out_min, years
    else:
        return out_sum, years

#----------------------------------------------------------------------------
# Add data to sums, max's and min's arrays, for any month other than December.
#----------------------------------------------------------------------------
def get_season_summaxmin(dat_c, stn, season, yyyyin, month, ndays, \
                         out_sum, out_max, out_min):

    #--- Look out for cases where data is NaN (e.g. the 31st of June) and
    #--- do nothing (return) in those cases.
    if np.isnan(dat_c):
        return ndays, out_sum, out_max, out_min
        
    #--- Put December winter data into next year's winter-- naming
    #--- winters by their Jan/Feb year rather than their Dec year.
    if month == '12':
        yyyy = str(int(yyyyin) + 1)
    else:
        yyyy = yyyyin
        
    #--- Count number of days for this season and year.
    if (season+yyyy) in ndays:
        ndays[season+yyyy] += 1
    else:
        ndays[season+yyyy] = 1

    key = (season,stn,yyyy)

    #--- Get sum of sent in data.
    if key in out_sum:
        out_sum[key] = out_sum[key] + dat_c
    else:
        out_sum[key] = dat_c

    #--- Get maximum.
    if key in out_max:
        if dat_c > out_max[key]:
            out_max[key] = dat_c
    else:
        out_max[key] = dat_c
            
    #--- Get minimum.
    if key in out_min:
        if dat_c < out_min[key]:
            out_min[key] = dat_c
    else:
        out_min[key] = dat_c

    return ndays, out_sum, out_max, out_min


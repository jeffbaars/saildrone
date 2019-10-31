#!/usr/bin/python
import  os, os.path, time, glob, re, string
import sys, string, readline, datetime, time
import numpy as np
from scipy.stats import rankdata
from utils_date import *
from utils_mysql import *
import matplotlib.pyplot as plt

fs      = 9
titlefs = 9
width   = 8
height  = 6

spdmin = 3

#-----------------------------------------------------------------------------
# Create rank histogram.
#-----------------------------------------------------------------------------
def rank_histogram(models, domain, refids, idts, fhr, var, obs, forecasts, \
                   plotfname, windskip):
    good_fract = 0.90

    obsgood    = []
    refidsgood = []
    idtsgood   = []
    vdtsgood   = []    

    for i in range(len(idts)):
        idt = idts[i]
        vdt = get_vdts([idt], [fhr], dtfmt)[0]

        #--- Find good obs and store them in list obsgood.
        for r in range(len(refids)):
            refid = refids[r]
            key = (refid, vdt, var)
            if key in obs:
                if np.isnan(float(obs[key])):
                    print 'skipping ', refid, idt, vdt, obs[key]
                    continue
                if windskip == 1:
                    if var == 'spd':
                        if float(obs[key]) < spdmin:
                            continue

                #--- If ALL member's forecasts are missing, don't
                #--- keep refid.
                allmissing = 1
                for m in range(len(models)):
                    model = models[m] + domain
                    keym = (model,refid,idt,fhr,var)
                    if keym in forecasts:
                        for_c = float(forecasts[keym])                    
                        if ~np.isnan(for_c):
                            allmissing = 0
                if allmissing == 0:
#                    if np.isnan(obs[key]):
#                        print refid, idt, vdt, obs[key]
#                        sys.exit()
                    obsgood.append(float(obs[key]))
                    refidsgood.append(refid)
                    idtsgood.append(idt)
                    vdtsgood.append(vdt)                    

#    for o in range(len(obsgood)):
#        refid = refidsgood[o]
#        idt = idtsgood[o]
#        vdt = vdtsgood[o]
#        obsg = obsgood[o]
#        print refid, idt, vdt, obsg
#        if np.isnan(obsg):
#            print 'i think nan'
#    sys.exit()

    totobs = len(refids) * len(idts)
    print 'Found ', len(obsgood), ' good obs out of ', totobs, ' total'

    #--- Keep forecasts only for good obs found above.
    ensemble = np.ones((len(models),len(refidsgood))) * np.nan
    for o in range(len(obsgood)):
        refid = refidsgood[o]
        idt = idtsgood[o]
        for m in range(len(models)):
            model = models[m] + domain
            key = (model,refid,idt,fhr,var)
            if key in forecasts:
                ensemble[m,o] = forecasts[key]

    #--- Find and remove entirely members that do not have enough
    #--- (< good_fract) non-missing forecasts.
    imods_remove = []
    for m in range(len(models)):
        mod_c = ensemble[m,:]
        bgood = ~np.isnan(mod_c)
        igood = [int(elem) for elem in bgood]
        fract_c = float(sum(igood) / len(obsgood))
        if fract_c < good_fract:
            imods_remove.append(m)
            print models[m], ' good fract: ', fract_c, ' *removing!'
        else:
            print models[m], ' good fract: ', fract_c
    if len(imods_remove) > 0:
        ensemble = np.delete(ensemble, (imods_remove), 0)

    #--- Compute rank histogram, following code from:
    #--- https://github.com/oliverangelil/rankhistogram/blob/master/ranky.py
    #--- Handles "ties" (as would be really common for precip=0.0 for example)
    #--- according to Hamill, 2000, MWR.
    combined = np.vstack((np.asarray(obsgood), ensemble))    

    print 'computing ranks'
    ranks = np.apply_along_axis(lambda x: rankdata(x,method='min'),0,combined)

    print 'computing ties'
    ties = np.sum(ranks[0]==ranks[1:], axis=0)
    ranks = ranks[0]
    tie = np.unique(ties)

    for i in range(1,len(tie)):
        index = ranks[ties == tie[i]]
        print 'randomizing tied ranks for ' + str(len(index)) + \
              ' instances where there is ' + str(tie[i]) + ' tie/s. ' + \
              str(len(tie)-i-1) + ' more to go'
        ranks[ties == tie[i]] = [np.random.randint(index[j],index[j]+tie[i]+1,tie[i])[0] for j in range(len(index))]

    rankhist = np.histogram(ranks, bins=\
                            np.linspace(0.5, combined.shape[0]+0.5, \
                                        combined.shape[0]+1))

    #--- Print out data for testing.
    for o in range(len(obsgood)):
        refid = refidsgood[o]
        idt = idtsgood[o]
        pstr = refid + ',' + var + ',' + idt + ',' + str(fhr) + ','
        for i in np.sort(ensemble[:,o]):
            pstr = pstr + str(float(i)) + ','
        pstr = pstr + str(obsgood[o])
        print pstr

    #--- Make actual bar plot.
    fig, ax = plt.subplots( figsize=(width,height) )
    ind = np.arange(len(rankhist[0]))
    norm = [float(i)/sum(rankhist[0]) for i in rankhist[0]]

    plt.bar(ind, norm)
    plt.xlabel('Rank',     fontsize=fs+1)
    plt.ylabel('Fraction', fontsize=fs+1)    

    xticks_c = range(0, len(ind))
    xlabs_c = [ str(i+1) for i in xticks_c ]
    plt.xticks(xticks_c)
    ax.set_xticklabels(xlabs_c)

    plt.ylim(0, 0.45)

    titleadd = ''
    if windskip == 1:
        if var == 'spd':
            titleadd = ' (spd > ' + str(spdmin) + ' kts)'
    
    titlein = 'Ensemble Rank Histogram, ' + \
              mod_varname_long_dict[var] + titleadd + ', ' + \
              get_nice_date(idts[0], dtfmt, dtfmt_nice) + ' - ' + \
              get_nice_date(idts[len(idts)-1], dtfmt, dtfmt_nice) + \
              ', F' + str(fhr)
    plt.title(titlein, fontsize=titlefs, fontweight='bold')

    plt.savefig(plotfname)

    return rankhist


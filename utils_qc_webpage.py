#!/usr/bin/python
import  os, os.path, time, string
import sys, string, datetime, time
import numpy as np
import csv
from utils_date import *

mvc  = -9999.0
host = 'sql.atmos.washington.edu'
user = 'ovens'
db   = 'verify'
pwfn = '/home/disk/sage1/mm5rt/.obsdb_password_rmm5rt'

varname_dict = {
    'temp':   'Temperature', 
    'dew':    'Dew Point', 
    'rh':     'Relative Humidity',
    'dir':    'Wind Direction',
    'pres':   'Surface Pressure',
    'spd':    'Wind Speed',
    'pcp6':   '6-hr Precipitation'
}

#-----------------------------------------------------------------------------
# Read netid file.
#-----------------------------------------------------------------------------
def read_netid_file(netid_file):
    nets = []
    nets_long = []
    f = open(netid_file, 'rb')
    reader = csv.reader(f)
    for line in reader:
        nets_long.append(line[0].replace("'", ""))
        nets.append(line[1].replace("'", ""))    
    return nets, nets_long

#-----------------------------------------------------------------------------
# Read db pw file.
#-----------------------------------------------------------------------------
def get_db_pw(pwfn):
    with open(pwfn) as f:
        pw = f.readlines()[0]
        pw = pw.strip()
    return pw

#-----------------------------------------------------------------------------
# Create byvarnet html page.
#-----------------------------------------------------------------------------
def write_col_headers(f, vars):
    f.write('   <tr bgcolor = \"#c0c0c0\">\n')
    f.write('      <th></th>\n')    
    for v in range(len(vars)):
        f.write('      <th>' + varname_dict[vars[v]] + '</th>')
    f.write('\n')
    f.write('   </tr>\n')

#-----------------------------------------------------------------------------
# Create byvarnet html page.
#-----------------------------------------------------------------------------
def byvarnet_html(ngood, nbad, vars, nets, nets_long, sdt, edt,
                  gf_stns_dict, gfs_dict, pg_flag, htmlfile):

    sdt_nice = get_nice_date(sdt)
    edt_nice = get_nice_date(edt)    

    f = open(htmlfile, 'w')

    f.write('<html>\n')
    f.write('<style>\n')
    f.write('.tooltip_pg {\n')
    f.write('    position: relative;\n')
    f.write('    display: inline-block;\n')
    f.write('    border-bottom: 1px dotted black;\n')
    f.write('}\n')
    
    f.write('.tooltip_pg .tooltiptext_pg {\n')
    f.write('    visibility: hidden;\n')
    f.write('    width: 120px;\n')
    f.write('    background-color: red;\n')
    f.write('    font-family: consolas;\n')
    f.write('    color: #fff;\n')        
    f.write('    text-align: center;\n')
    f.write('    border-radius: 6px;\n')
    f.write('    padding: 5px 0;\n')
        
    f.write('    /* Position the tooltip */\n')
    f.write('    position: absolute;\n')
    f.write('    z-index: 1;\n')
    f.write('}\n')
        
    f.write('.tooltip_pg:hover .tooltiptext_pg {\n')
    f.write('    visibility: visible;\n')
    f.write('}\n')
    f.write('</style>\n')
    
    f.write('<head>\n')
    f.write('<meta http-equiv=\"Content-Type\" content=\"text/html; ' + \
            '"\"charset=iso-8859-1\">\n')
    f.write('<link rel=\"stylesheet\" type=\"text/css\" ' + \
            'href=\"css/byvarnet.css\">\n')
    
    f.write('<table width=\"100%\"  border=\"0\" cellspacing=\"0\"' + \
            'cellpadding=\"0\"><!-- content area layout table -->\n')
    f.write(' <tr>\n')
    f.write('<th valign=\"top\" style=\"padding: \"' + \
            '\"20px 40px 40px 40px\"> <!-- content area -->\n')

    f.write('<span class=headline>Observations Quality Control Summary' + \
            '</span><br>\n')
    f.write('<span class=bodyheadline>By Network and Variable</span><br>\n')
    f.write('<span class=caption>' + sdt_nice + ' - ' + edt_nice + \
            '</span><br>\n')
    f.write('<span class=hilight_caption>Networks with Percent Good Obs < ' + \
            str(pg_flag) + ' in RED; rollover to see stations < ' + \
            str(pg_flag) + '</span><br>\n')
    f.write('<br>\n')

    f.write('<table class=\"grayBorder\" cellspacing=\"1\" ' + \
            'cellpadding=\"4\">\n')

    #--- Fill in rest of table, starting with row headers (network names).
    color_switch = 1
    net_count = 0
    for n in range(len(nets)):
        net = nets[n]
        #--- See if any obs exist for this network.
        found_good = 0
        for v in range(len(vars)):
            if (ngood[v,n] > 0 or nbad[v,n] > 0):
                found_good = 1
        if (found_good == 0):
            continue

        #--- Write column headers every 6 networks.
        if (net_count % 6 == 0):
            write_col_headers(f, vars)

        #--- Alternate row colors for readability.
        if (color_switch == 1):
            bgcol = '#fcfcfc'
        else:
            bgcol = '#eeeeee'

        f.write('<tr>\n')
        f.write('    <th align=\"right\" bgcolor = \"' + bgcol + \
                '\">' + nets_long[n] + ' (% good)</th>')
        for v in range(len(vars)):
            var = vars[v]
            ng = ngood[v,n]
            nb = nbad[v,n]
            if (ng == 0 and nb == 0):
                f.write('      <td bgcolor = \"' + bgcol + '\">0</td>\n')
            else:
                fract_c = float(ng / (ng+nb))                
                s = '{:6.1f}'.format(100 * fract_c)
                if (fract_c < pg_flag):
                    if ((net,var) in gf_stns_dict):
                        gf_stns_c = gf_stns_dict[net,var]
                        gfs_c = gfs_dict[net,var]                    
                        f.write('      <td class=\"hilight_bad\" bgcolor = \"'+\
                                bgcol + '\"><div class=\"tooltip_pg\">' + \
                                '<span class=\"tooltiptext_pg\">')
                        f.write('      stn:\t% good<br>\n')
                        for ng in range(len(gfs_c)):
                            gfs_print = '{:6.1f}'.format(100 * gfs_c[ng])
                            stn_print = gf_stns_c[ng].split('_', 1)[-1]
                            f.write('      ' + stn_print.upper() + ':\t' + \
                                    gfs_print + '<br>\n')
                        f.write('      </span>' + s + '</div></td>\n')
                else:
                    f.write('      <td bgcolor = \"' + bgcol + '\">' + s + \
                            '</td>')
        f.write('     <tr align=\"right\" bgcolor = ' + bgcol + \
                '><td>Number of Obs</td>')

        for v in range(len(vars)):            
            f.write('      <td align=\"right\">' + \
                    '{:d}'.format(int(ngood[v,n] + nbad[v,n])) + '</td>')
        f.write('   </tr>\n')            
        f.write('   <tr bgcolor = ' + bgcol + '><td>Number of flagged Obs</td>')
        for v in range(len(vars)):
            f.write('      <td align=\"right\">' + \
                    '{:d}'.format(int(nbad[v,n])) + '</td>')
        f.write('     </tr>\n')

        f.write('</tr>\n')

        if (color_switch == 1):
            color_switch = 0
        else:
            color_switch = 1
        net_count = net_count + 1

    f.write('   </table>\n')
    f.write('</table>\n\n')
    f.write('</html>\n')

    f.close()

    return 1

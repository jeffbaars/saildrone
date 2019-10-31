#!/usr/bin/python
import os, sys
from make_cmap import *

#--------------------------------------------------------------------------
# Rainwatch dBz and precip colors.
#--------------------------------------------------------------------------
# Color table taken from:
# http://pykl3radar.com/pykl3wiki/index.php/Color_table_customization
levs_dbz = [-5,0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75]
cmap_dbz = [(255,255,255), \
            (255,255,255), \
            (4,233,227), \
            (4,158,243), \
            (4,2,243), \
            (2,250,2), \
            (17,121,1), \
            (0,140,0), \
            (255,255,0), \
            (228,187,2), \
            (255,148,0), \
            (252,0,0), \
            (210,0,0), \
            (187,0,0), \
            (247,0,252), \
            (151,84,197), \
            (255,255,255)]

levs_swe = [ 50, 100, 200, 300, 400, 500, 600, 700, 800, 900,
             1000, 1200, 1400, 1600, 2000, 2400]
cmap_swe = [(225,225,225), \
            (192,192,192), \
            (128,128,128 ), \
            (0,255,255), \
            (32,178,170), \
            (0,255,0), \
            (0,128,0), \
            (255,0,204), \
            (199,21,133), \
            (0,0,255), \
            (0,0,128), \
            (255,255,0), \
            (255,204,17), \
            (255,69,0), \
            (0,0,0),\
            (255,255,255)]
levs_norm_c = []
for i in range(len(levs_swe)):
    x = float(levs_swe[i])
    norm_c = (x - min(levs_swe)) / (max(levs_swe) - min(levs_swe))
    levs_norm_c.append(norm_c)
cmap_swe = make_cmap(cmap_swe, bit = True, position = levs_norm_c)

levs_swe_std = [ 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
cmap_swe_std = [(225,225,225), \
            (192,192,192), \
            (128,128,128 ), \
            (0,255,255), \
            (32,178,170), \
            (0,255,0), \
            (0,128,0), \
            (255,0,204), \
            (199,21,133), \
            (0,0,255)]

levs_norm_c = []
for i in range(len(levs_swe_std)):
    x = float(levs_swe_std[i])
    norm_c = (x - min(levs_swe_std)) / (max(levs_swe_std) - min(levs_swe_std))
    levs_norm_c.append(norm_c)
cmap_swe_std = make_cmap(cmap_swe_std, bit = True, position = levs_norm_c)

levs_swe_diff = [ -1200, -800, -600, -400, -200, -100, -50, 0, \
                  50, 100, 200, 400, 800 ]
cmap_swe_diff = [ ( 63,  37,  11), \
                  ( 84,  48,   5), \
                  (140,  81,  10), \
                  (191, 129,  45), \
                  (223, 194, 125), \
                  (246, 232, 195), \
                  (245, 245, 245), \
                  (199, 234, 229), \
                  (128, 205, 193), \
                  ( 53, 151,  43), \
                  (  1, 102,  95), \
                  (  0,  60,  48), \
                  (  0, 100,  0)]

levs_norm_c = []
for i in range(len(levs_swe_diff)):
    x = float(levs_swe_diff[i])
    norm_c = (x - min(levs_swe_diff)) / (max(levs_swe_diff) - \
                                         min(levs_swe_diff))
    levs_norm_c.append(norm_c)
cmap_swe_diff = make_cmap(cmap_swe_diff, bit = True, position = levs_norm_c)


levs_swdown = [ 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, \
                600, 650, 700, 750, 800]
cmap_swdown = [(255,255,255), \
               (192,192,192), \
               (128,128,128 ), \
               (0,255,255), \
               (32,178,170), \
               (0,255,0), \
               (0,128,0), \
               (255,0,204), \
               (199,21,133), \
               (0,0,255), \
               (0,0,128), \
               (255,255,0), \
               (255,204,17), \
               (255,69,0), \
               (0,0,0),\
               (255,255,255)]

#--------------------------------------------------------------------------
# Temperature.
#--------------------------------------------------------------------------
levs_temp = [ -20, -18, -16, -14, -12, -10, -8, -6, -4, -2, 0, 2, \
              4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, \
              28, 30, 32, 34, 36, 38, 40]
cmap_temp = [ (109, 227, 255), \
              (175, 240, 255), \
              (255, 196, 226), \
              (255, 153, 204), \
              (255,   0, 255), \
              (128,   0, 128), \
              (  0,   0, 128), \
              ( 70,  70, 255), \
              ( 51, 102, 255), \
              (133, 162, 255), \
              (255, 255, 255), \
              (204, 204, 204), \
              (179, 179, 179), \
              (153, 153, 153), \
              ( 96,  96,  96), \
              (128, 128,   0), \
              (  0,  92,   0), \
              (  0, 128,   0), \
              ( 51, 153, 102), \
              (157, 213,   0), \
              (212, 255,  91), \
              (255, 255,   0), \
              (255, 184, 112), \
              (255, 153,   0), \
              (255, 102,   0), \
              (255,   0,   0), \
              (188,  75,   0), \
              (171,   0,  56), \
              (128,   0,   0), \
              (163, 112, 255), \
              (255, 255, 255)]
levs_norm_c = []
for i in range(len(levs_temp)):
    x = float(levs_temp[i])
    norm_c = (x - min(levs_temp)) / (max(levs_temp) - min(levs_temp))
    levs_norm_c.append(norm_c)
cmap_temp = make_cmap(cmap_temp, bit = True, position = levs_norm_c)

levs_temp_diff = [ -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, \
                   4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0 ]
cmap_temp_diff = [  (  0,   0,  51), \
                    (  0,   0, 204), \
                    (153, 153, 255), \
                    (255, 255, 255), \
                    (128, 128,   0), \
                    (  0,  92,   0), \
                    (  0, 128,   0), \
                    ( 51, 153, 102), \
                    (157, 213,   0), \
                    (212, 255,  91), \
                    (255, 255,   0), \
                    (255, 184, 112), \
                    (255, 153,   0), \
                    (255, 102,   0), \
                    (255,   0,   0), \
                    (188,  75,   0), \
                    (171,   0,  56), \
                    (128,   0,   0), \
                    (163, 112, 255)]
levs_norm_c = []
for i in range(len(levs_temp_diff)):
    x = float(levs_temp_diff[i])
    norm_c = (x - min(levs_temp_diff)) / \
             (max(levs_temp_diff) - min(levs_temp_diff))
    levs_norm_c.append(norm_c)
cmap_temp_diff = make_cmap(cmap_temp_diff, bit = True, position = levs_norm_c)


#levs_temp_diff_rmg = [ -10.0, -8.0, -6.0, -5.0, -4.0, -3.5, -3.0, -2.5, \
#                       -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5,\
#                       3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0, 14.0 ]
levs_temp_diff_rmg = [ -14, -12, -10, -9, -8, -7, -6, -5, \
                       -4, -3, -2, -1, 0.0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, \
                       12, 14, 16]

cmap_temp_diff_rmg = [  (  6,   0, 255), \
                        (  4,   0, 255), \
                        (  2,   0, 255), \
                        (  0,   0, 255), \
                        (  0,  18, 255), \
                        (  0,  50, 255), \
                        (  0,  84, 255), \
                        (  0, 116, 255), \
                        (  0, 148, 255), \
                        (  0, 180, 255), \
                        (  0, 212, 255), \
                        (  0, 255, 244), \
                        (255, 255, 255), \
                        (128, 128,   0), \
                        (  0,  92,   0), \
                        (  0, 128,   0), \
                        ( 51, 153, 102), \
                        (157, 213,   0), \
                        (212, 255,  91), \
                        (255, 255,   0), \
                        (255, 184, 112), \
                        (255, 153,   0), \
                        (255, 102,   0), \
                        (255,   0,   0), \
                        (188,  75,   0), \
                        (171,   0,  56)]

levs_norm_c = []
for i in range(len(levs_temp_diff_rmg)):
    x = float(levs_temp_diff_rmg[i])
    norm_c = (x - min(levs_temp_diff_rmg)) / \
             (max(levs_temp_diff_rmg) - min(levs_temp_diff_rmg))
    levs_norm_c.append(norm_c)
cmap_temp_diff_rmg = make_cmap(cmap_temp_diff_rmg, bit = True, \
                               position = levs_norm_c)



levs_temp_std = [ 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, \
                   4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0 ]
cmap_temp_std = [  (  0,   0,  51), \
                    (  0,   0, 204), \
                    (153, 153, 255), \
                    (255, 255, 255), \
                    (128, 128,   0), \
                    (  0,  92,   0), \
                    (  0, 128,   0), \
                    ( 51, 153, 102), \
                    (157, 213,   0), \
                    (212, 255,  91), \
                    (255, 255,   0), \
                    (255, 184, 112), \
                    (255, 153,   0), \
                    (255, 102,   0), \
                    (255,   0,   0), \
                    (188,  75,   0), \
                    (171,   0,  56)]

levs_norm_c = []
for i in range(len(levs_temp_std)):
    x = float(levs_temp_std[i])
    norm_c = (x - min(levs_temp_std)) / \
             (max(levs_temp_std) - min(levs_temp_std))
    levs_norm_c.append(norm_c)
cmap_temp_std = make_cmap(cmap_temp_std, bit = True, position = levs_norm_c)

#--------------------------------------------------------------------------
# Precip.
#--------------------------------------------------------------------------
levs_pcp = [ 0.0, 2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, \
             50.0, 75.0, 100.0, 150.0, 200.0]
cmap_pcp = [ (240, 255, 230), \
             (233, 255, 190), \
             (153, 255, 119), \
             (56,  224,   9), \
             (61,  204,  66), \
             (61,  184, 104), \
             (51,  166, 137), \
             (26,  147, 171), \
             (33,  110, 158), \
             (32,   75, 145), \
             (27,   46, 133), \
             (12,   16, 120), \
             (12,   16, 180), \
             ( 0,    0, 255), \
             ( 0,    0,   0)]
levs_norm_c = []
for i in range(len(levs_pcp)):
    x = float(levs_pcp[i])
    norm_c = (x - min(levs_pcp)) / (max(levs_pcp) - min(levs_pcp))
    levs_norm_c.append(norm_c)
cmap_pcp = make_cmap(cmap_pcp, bit = True, position = levs_norm_c)

levs_pcp_percdiff = [ -50, -40, -20, -15, -10, -5, 0, 5, 10, 15, 20, 40, 50 ]
cmap_pcp_percdiff = [ ( 63,  37,  11), \
                      ( 84,  48,   5), \
                      (140,  81,  10), \
                      (191, 129,  45), \
                      (223, 194, 125), \
                      (246, 232, 195), \
                      (245, 245, 245), \
                      (199, 234, 229), \
                      (128, 205, 193), \
                      ( 53, 151,  43), \
                      (  1, 102,  95), \
                      (  0,  60,  48), \
                      (  0, 100,  0)]
levs_norm_c = []
for i in range(len(levs_pcp_percdiff)):
    x = float(levs_pcp_percdiff[i])
    norm_c = (x - min(levs_pcp_percdiff)) / \
             (max(levs_pcp_percdiff) - min(levs_pcp_percdiff))
    levs_norm_c.append(norm_c)
cmap_pcp_percdiff = make_cmap(cmap_pcp_percdiff, bit=True, position=levs_norm_c)

levs_pcp_diff = [ -6, -3, -2.0, -1.5, -1.0, -0.5, 0, 0.5, 1, 1.5, 2, 3, 6 ]
cmap_pcp_diff = [ ( 63,  37,  11), \
                  ( 84,  48,   5), \
                  (140,  81,  10), \
                  (191, 129,  45), \
                  (223, 194, 125), \
                  (246, 232, 195), \
                  (245, 245, 245), \
                  (199, 234, 229), \
                  (128, 205, 193), \
                  ( 53, 151,  43), \
                  (  1, 102,  95), \
                  (  0,  60,  48), \
                  (  0, 100,  0)]
levs_norm_c = []
for i in range(len(levs_pcp_diff)):
    x = float(levs_pcp_diff[i])
    norm_c = (x - min(levs_pcp_diff)) / \
             (max(levs_pcp_diff) - min(levs_pcp_diff))
    levs_norm_c.append(norm_c)
cmap_pcp_diff = make_cmap(cmap_pcp_diff, bit=True, position=levs_norm_c)

levs_pcp_diff_annual = [ -16, -12, -8, -4, -2, -1, 0, 1, 2, 4, 8, 12, 16 ]
cmap_pcp_diff_annual = [ ( 63,  37,  11), \
                         ( 84,  48,   5), \
                         (140,  81,  10), \
                         (191, 129,  45), \
                         (223, 194, 125), \
                         (246, 232, 195), \
                         (245, 245, 245), \
                         (199, 234, 229), \
                         (128, 205, 193), \
                         ( 53, 151,  43), \
                         (  1, 102,  95), \
                         (  0,  60,  48), \
                         (  0, 100,  0)]
levs_norm_c = []
for i in range(len(levs_pcp_diff_annual)):
    x = float(levs_pcp_diff_annual[i])
    norm_c = (x - min(levs_pcp_diff_annual)) / \
             (max(levs_pcp_diff_annual) - min(levs_pcp_diff_annual))
    levs_norm_c.append(norm_c)
cmap_pcp_diff_annual = make_cmap(cmap_pcp_diff_annual, bit=True, \
                                 position=levs_norm_c)

levs_pcp_std = [ 0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, \
             20.0, 22.0, 24.0, 26.0, 28.0]
cmap_pcp_std = [ (240, 255, 230), \
             (233, 255, 190), \
             (153, 255, 119), \
             (56,  224,   9), \
             (61,  204,  66), \
             (61,  184, 104), \
             (51,  166, 137), \
             (26,  147, 171), \
             (33,  110, 158), \
             (32,   75, 145), \
             (27,   46, 133), \
             (12,   16, 120), \
             (12,   16, 180), \
             ( 0,    0, 255), \
             ( 0,    0,   0)]
levs_norm_c = []
for i in range(len(levs_pcp_std)):
    x = float(levs_pcp_std[i])
    norm_c = (x - min(levs_pcp_std)) / (max(levs_pcp_std) - min(levs_pcp_std))
    levs_norm_c.append(norm_c)
cmap_pcp_std = make_cmap(cmap_pcp_std, bit = True, position = levs_norm_c)

#--------------------------------------------------------------------------
# Wind Speed.
#--------------------------------------------------------------------------
levs_spd = [  1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 ]
cmap_spd = [  (179, 179, 179), \
              (153, 153, 153), \
              ( 96,  96,  96), \
              (128, 128,   0), \
              (  0,  92,   0), \
              (  0, 128,   0), \
              ( 51, 153, 102), \
              (157, 213,   0), \
              (212, 255,  91), \
              (255, 255,   0), \
              (255, 184, 112), \
              (255, 153,   0), \
              (255, 102,   0), \
              (255,   0,   0), \
              (188,  75,   0), \
              (171,   0,  56), \
              (128,   0,   0), \
              (163, 112, 255)]

levs_norm_c = []
for i in range(len(levs_spd)):
    x = float(levs_spd[i])
    norm_c = (x - min(levs_spd)) / (max(levs_spd) - min(levs_spd))
    levs_norm_c.append(norm_c)
cmap_spd = make_cmap(cmap_spd, bit=True, position=levs_norm_c)

levs_spd_diff = [ -12.0, -9.0, -6.0, -3.0, -2.0, -1.0, 0, 1.0, 2.0, 3.0, \
                  6.0, 9.0, 12.0 ]
cmap_spd_diff = [ ( 63,  37,  11), \
                  ( 84,  48,   5), \
                  (140,  81,  10), \
                  (191, 129,  45), \
                  (223, 194, 125), \
                  (246, 232, 195), \
                  (245, 245, 245), \
                  (199, 234, 229), \
                  (128, 205, 193), \
                  ( 53, 151,  43), \
                  (  1, 102,  95), \
                  (  0,  60,  48), \
                  (  0, 100,  0)]
levs_norm_c = []
for i in range(len(levs_spd_diff)):
    x = float(levs_spd_diff[i])
    norm_c = (x - min(levs_spd_diff)) / \
             (max(levs_spd_diff) - min(levs_spd_diff))
    levs_norm_c.append(norm_c)
cmap_spd_diff = make_cmap(cmap_spd_diff, bit=True, position=levs_norm_c)

#!/usr/local/bin/perl
use POSIX qw(ceil floor);
#use List::Util qw[min max];
use GD;

#----------------------------------------------------------------------------
# Set directories.
#----------------------------------------------------------------------------
$homedir   = "/home/disk/spock/jbaars";
$workdir   = "${homedir}/verify/rtens";
$driverdir = "${workdir}/driver";
#$matlabdir = "${workdir}/matlab";
$datadir   = "${workdir}/data";
$utildir   = "${homedir}/perlutil";

#----------------------------------------------------------------------------
# Requires.
#----------------------------------------------------------------------------
$r = "/usr/local/wx/include_files/master_path_file";
if (-e $r) { require $r } else { die "can't find require $r!";}
$r = "/usr/local/wx/include_files/master_station_numberlist";
if (-e $r) { require $r } else { die "can't find require $r!";}
$r = "$paths{wx_include_files}/date-lib.pl";
if (-e $r) { require $r } else { die "can't find require $r!";}
$r = "$paths{wx_include_files}/local-lib.pl";
if (-e $r) { require $r } else { die "can't find require $r!";}
$r = "${driverdir}/get_latlonbox_data_from_sql.pl";
if (-e $r) { require $r } else { die "can't find require $r!";}
$r = "${utildir}/unique.pl";
if (-e $r) { require $r } else { die "can't find require $r!";}

$webdir       = $paths{mm5rt_www_base};
$plotdir      = "${webdir}/images/verify/map";
$plotlinksdir = "${webdir}/images/verify/links";

#----------------------------------------------------------------------------
# Settings.
#----------------------------------------------------------------------------
$sdate = "2019040100";
$edate = "2019040500";

$maxlat = 90;
$minlat = 0;
$maxlon = -140.0;
$minlon =  -80.0;

print "\nptlat, ptlon = $ptlat, $ptlon\n";
print "maxlat = $maxlat\n";
print "minlat = $minlat\n";
print "maxlon = $maxlon\n";
print "minlon = $minlon\n";

@ihrs = qw( 00 );

@fhrs = qw( 24 36 );

#@models = qw( ensgefs01  ensgefs02  ensgefs03  ensgefs04  ensgefs05
#             ensgefs06  ensgefs07  ensgefs08  ensgefs09  ensgefs10
#             enscent  enscmcg  ensgasp2  ensjmag2  ensngps  enstcwb  ensukmo );
@models = qw( ensgefs01d3  ensgefs02d3  ensgefs03d3 );

# variables to plot with matlab.
@plotvars = qw( temp  dewp  spd  dir  slp pcp6 );
#@plotvars = qw( temp );

# leave blank for allowing un-QC'd data.  Only can handle full (no partial)!
$qc = "full";

# winds to skip for spd and dir variables.
$windskip = 0;

# missing value constant.
$mvc = "-9999.0";

# difference files coming out of &get_latlonbox_data_from_sql that are less 
# than $minsize_diff_file get ignored (no map made for any of @models).
$minsize_diff_file = 100;

#----------------------------------------------------------------------------
# Based on settings set above, determine further required settings.
#----------------------------------------------------------------------------
$dir = "$datadir/get_latlonbox_data.$$";
if (-e $dir) { system("rm -r $dir"); }
print "mkdir $dir\n";;
mkdir($dir);
chdir($dir);

@idts = &get_dates($sdate, $edate, 24);

#----------------------------------------------------------------------------
# Loop over each forecast hour and init hour making queries and gathering
# data files.
#----------------------------------------------------------------------------
undef @data_files;

foreach $fhr (@fhrs) {
    foreach $ihr (@ihrs) {
	#--- this loop's current init hour / fhr combo.
	print "\n---------------------------------------------------------\n";
	print "gathering data for ${ihr}Z, f${fhr}\n";

	#-----------------
	# Get validation init/valid YEARS into an array @valid_ivyears.
	#-----------------
	undef @ivyyyys;
	undef @valid_years;
	foreach $idt_c (@idts) {
	    $vdt_c = &time_increment("${idt_c}0000",yy,0,($fhr*3600),
				     "YYYYMMDDHH");
	    $iyyyy_c = substr($idt_c, 0, 4);
	    $vyyyy_c = substr($vdt_c, 0, 4);

	    $ivyyyy_c = "${iyyyy_c}${vyyyy_c}";
	    push @ivyyyys, $ivyyyy_c;
	}
	@valid_ivyears = unique(@ivyyyys);

	#-----------------
	# Loop through validation init/valid years, calling 
	# &get_latlonbox_data_from_sql once for each one.
	#-----------------
	foreach $valid_ivyear (@valid_ivyears) {

	    print "------------------------------------------\n";
	    print "$valid_ivyear\n";
	    $yeari = substr($valid_ivyear, 0, 4);
	    $yearv = substr($valid_ivyear, 4, 4);

	    #-----------
	    #--- Get array of all validation dates for this $valid_ivyear.
	    #-----------
	    undef @vdts_in;
	    foreach $idt_c (@idts) {
		$vdt_c = &time_increment("${idt_c}0000",yy,0,($fhr*3600),yy);
		$iyyyy_c = substr($idt_c, 0, 4);
		$vyyyy_c = substr($vdt_c, 0, 4);
		$ivyyyy_c = "${iyyyy_c}${vyyyy_c}";

		if ($ivyyyy_c == $valid_ivyear) {
		    push @vdts_in, $vdt_c;
		}
	    }

	    #-----------
	    #--- Get data file names for each model and year and build
	    #--- an array of these file names to be sent in and created by 
	    #--- &get_diffs_from_sql.  Also create daily domavg file names 
	    #--- array.
	    #-----------
	    $sdate_valid = min(@vdts_in);
	    $edate_valid = max(@vdts_in);
	    $fsuffixv = "${sdate_valid}_${edate_valid}_${ihr}z_f${fhr}";
	    undef @data_files_in;
	    $im = 0;
	    foreach $m (@models) {
		$data_files{$m}{$fhr}{$ihr} = 
		    "${dir}/data_${m}_${fsuffixv}.tmp";
		$data_files_in[$im] = $data_files{$m}{$fhr}{$ihr};
		$im++;
	    }
	    
	    print "data_files_in are @data_files_in\n";

	    #--------
	    #--- Make queries to get model and obs data for all @models.
	    #--------
	    print "calling get_maps_diffs_from_sql\n";
	    $iret = &get_latlonbox_data_from_sql($maxlat, $minlat, 
						 $maxlon, $minlon, 
						 \@vdts_in, 
						 $yearv, $yeari, 
						 $ihr, $fhr, $windskip,
						 \@models, \@data_files_in);
	    print "done calling get_diffs_from_sql_database\n";
	    if ($iret ne 0) {
		$emsg = "problem getting diffs from verify mysql database!";
		print "$emsg\n";
	    }

#	    $dir_c = "${datadir}/f${fhr}/${yyyymm}/";
	    $dir_c = "${datadir}/f${fhr}/";	    
            if (!-d $dir_c) { 
                $iret = system("mkdir -p $dir_c");
                if ($iret != 0) {
                    print "Problem trying to create $dir_c!\n";
                }
            }
            print "system(mv -f ${outfile_c} ${dir_c}\n";
            $iret = system("mv -f ${outfile_c} ${dir_c}");

            if ($iret != 0) {
                $emsg = "trouble moving verif files\n";
                $emsg = "can't move $outfile_c to $dir_c\n";
#                $iret = send_error_report_email($emsg);
            }

	    
	    die;

	} # end loop over @valid_ivyears.

    }   # end ihr loop.
}    # end fhr loop.

#----------------------------------------------------------------------------
#--- Done.
#----------------------------------------------------------------------------
exit 0;


sub clean_up {
    chdir($workdir);
    print "rm -rf $dir\n";
    system("rm -rf $dir");
}

#-----------------------------------------------------------------------------
#--- Get array of dates YYYYMMDDHH (@dts) between start ($s) and 
#--- end ($e) dates, iterating by $hours.
#-----------------------------------------------------------------------------
sub get_dates {
    my ($s, $e, $hours) = @_;
    my @dts;
    my ($i, $dt_c, $dt1, $dt_yyyymmddhh);

    $i = 0;
    $dt_c = $s;
    while ($dt_c le $e) {
        $dt_yyyymmddhh = substr($dt_c, 0, 10);
        $dt1 = "${dt_yyyymmddhh}";
        push @dts, $dt1;
        $i++;
        $dt_c = &changetime10($s, $i * $hours);
    }
    return @dts;
}



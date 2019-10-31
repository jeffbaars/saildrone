#!/usr/local/bin/perl
use DBI;

sub get_latlonbox_data_from_sql {

    my ($maxlat_in, $minlat_in, $maxlon_in, $minlon_in,  
	$dates, $year_valid, $year_init, $ihr_in, $fhr_in, $windskip, 
	$models_in, $diff_files_in) = @_;

    print "maxlat_in  = $maxlat_in\n";
    print "minlat_in  = $minlat_in\n";
    print "maxlon_in  = $maxlon_in\n";
    print "minlon_in  = $minlon_in\n";
    print "dates      = @$dates\n";
    print "year_valid = $year_valid\n";
    print "year_init  = $year_init\n";
    print "ihr_in     = $ihr_in\n";
    print "fhr_in     = $fhr_in\n";
    print "windskip   = $windskip\n";
    print "models_in  = @$models_in\n";
    print "filenames  = @$diff_files_in\n";

    #-------------------------------------------------------------------------
    # Requires.
    #-------------------------------------------------------------------------
    require "/usr/local/wx/include_files/master_path_file"; # fill %paths
    require "/usr/local/wx/include_files/master_station_numberlist";
    require ("$paths{wx_include_files}/date-lib.pl");    
    require ("$paths{wx_include_files}/local-lib.pl");   

    #------------------------------------------------------------------------
    # Open database Connection
    #------------------------------------------------------------------------
    my($dsn)="DBI:mysql:verify:sql";
    $dbh=DBI->connect ($dsn,"verify",$password,
		       {RaiseError => 0,PrintError => 1});

    #------------------------------------------------------------------------
    # For each model in @models_in, do querying and create output file.
    #------------------------------------------------------------------------
    $m = 0;
    foreach $model (@$models_in) {
	undef %hash;
	undef %elevcors;

	$model_year = "${model}_${year_init}";

	#---
	#--- Get all elevation corrections ("elevcors") for this 
	#--- model/year_init. $etable is our elevation correction data table.
	#---
	my ($refid,$modifydate,$elevcor,$enddate);
	($etable = $model_year) =~ s/_/_elev_/;
	$start = time;
	$bind = 0;
	print "starting query for elevcors ... \n";
	$query = "SELECT refid, date_format(modifydate,'%Y%m%d%H'),".
	    "elevcor, date_format(enddate,'%Y%m%d%H') ".
	    "FROM $etable " .
	    "ORDER BY refid,modifydate";

	print "query = $query\n"; 
	$sth = $dbh->prepare($query);

	$rv = $sth->execute();

	unless ($bind) {
	    # Bind Perl variables to columns:
	    $rv = $sth->bind_columns(\$refid,\$modifydate,\$elevcor,\$enddate);
	    $bind = 1;
	}
	# Column binding is the most efficient way to fetch data
	while ($sth->fetch) {
	    ##
	    ## we won't store the start and end dates, but will fill
	    ## a hash with elevcor for each intervening dates
	    $date = $modifydate;
	    $elevcor = 0 if ($elevcor eq "" || ! defined($elevcor));
#	    if (! defined( @{ $daterange{$modifydate}{$enddate} } ) ) {
	    if (!( @{ $daterange{$modifydate}{$enddate} } ) ) {

#		print "in here, date = $date\n";
		
		while ($date <= $enddate) {
		    $elevcors{$refid}{$date} = $elevcor;
		    push @{ $daterange{$modifydate}{$enddate} },$date;
		    $date = &time_increment("${date}0000","yy",0,43200,
					    "YYYYMMDDHH");
		}
	    } else {
#		print "where i would think we would be\n";
		foreach $date (@{ $daterange{$modifydate}{$enddate} }) {
		    $elevcors{$refid}{$date} = $elevcor;
		}
	    }
#	    die;
	}
	print "filling elevcors took " . (time-$start) . " seconds\n";

#	die;

	my ($refid,$fhr,$initdate,$validdate,
	    $t2m,$dew2m,$wsp10m,$dir10m,$sfp,$sfps,$slp,$pcp6);

	$outfile = @$diff_files_in[$m];

	undef %running;	    
	$start = time;
	$bind = 0;
	print "starting query for init=${ihr_in} fhr=${fhr_in} ... \n";
	$query = "SELECT refid,fhr,date_format(initdate,'%Y%m%d%H')," . 
	    "date_format(validdate,'%Y%m%d%H'),t2m,dew2m,wsp10m,dir10m," . 
	    "sfp,sfps,slp,pcp6 " .
	    "FROM $model_year " . 
	    "FORCE INDEX (valid) " .
	    "WHERE validdate=? " . 
	    "AND fhr=${fhr_in} " .
	    "AND hour(initdate) = ${ihr_in} " .
	    "ORDER BY refid, initdate";

	$sth = $dbh->prepare($query);
	print "query = $query\n";
	    
	foreach $date (@$dates) {
	    print "getting model data for $date...\n";

	    #--- place holder ('?') in $query is valid date, $date.  This
	    #--- has to be sent to the execute statement.
	    $rv = $sth->execute($date);
	    
	    unless ($bind) {
		# Bind Perl variables to columns:
		$rv = $sth->bind_columns(\$refid,\$fhr,\$initdate,
					 \$validdate,\$t2m,\$dew2m,
					 \$wsp10m,\$dir10m,\$sfp,
					 \$sfps,\$slp,\$pcp6);
		$bind = 1;
	    }

	    # Column binding is the most efficient way to fetch data
	    while ($sth->fetch) {
		if (defined($elevcors{$refid}{$initdate})) {
		    $ecor = $elevcors{$refid}{$initdate};
		} else {
		    $ecor = $mvc;
		} 
		# if no elevation correction is found, make t2m and dew2m
		# missing (mvc).
		if ($ecor == $mvc) { 
		    $hash{$refid}{$validdate} = "$initdate," . 
			"$mvc,$mvc,$wsp10m,$dir10m,$sfp,$sfps,$slp,$pcp6";
		} else {
		    $hash{$refid}{$validdate} = "$initdate," . 
			($t2m+$ecor) . "," . ($dew2m+$ecor) . 
			",$wsp10m,$dir10m,$sfp,$sfps,$slp,$pcp6";
		}

	    }
	}

	print "running execute and filling forecast data hash for " . 
	    "$model_year took " . (time-$start) . " seconds \n";
	print "rv from $query = $rv\n" if ($debug);
	
	my ($refid,$date,$lat,$lon,$elev,
	    $temp,$dew,$spd,$dir,$stnpres,$pres,$pcp6,$qcflags);
	$start = time;

	$query = "SELECT refid,date_format(date,'%Y%m%d%H'), " . 
	    "lat,lon,elev,temp,dew,spd,dir,stnpres,pres,pcp6,qcflags " . 
	    "FROM sfc${year_valid} " .
	    "FORCE INDEX (datelatlon) " .
	    "WHERE date=? " .
	    "AND (lat >= $minlat AND lat <= $maxlat AND lon >= $minlon " .
	    "AND lon <= $maxlon) " .
	    "ORDER BY refid, date";

	$sth = $dbh->prepare($query);
	print "query = $query\n";
	$bind = 0;
	    
	open(OUT,">$outfile") || die "cannot open $outfile for writing\n";
	$rows = 0;

	#--- For each date between $sdate_valid and $edate_valid query
	#--- obs and write out (f - o) differences to $outfile.
	foreach $mydate (@$dates) {
	    print "getting obs for $mydate...\n";
	    $rv = $sth->execute($mydate);
	    unless ($bind) {
		# Bind Perl variables to columns:
		$rv = $sth->bind_columns(\$refid,\$date,\$lat,\$lon,\$elev,
					 \$temp,\$dew,\$spd,\$dir,
					 \$stnpres,\$pres,\$pcp6,\$qcflags);
		$bind = 1;
	    }

	    # Column binding is the most efficient way to fetch data
	    undef %stats;
	    while ($sth->fetch) {

		if ($hash{$refid}{$date}) {

		    ($initdate,$t2m,$dew2m,$wsp10m,$dir10m,$sfp,$sfps,
		     $slp,$mpcp6) = 
			 split(',',$hash{$refid}{$date});
		    if (!$elev) {
			$elev_print = $mvc;
		    } else {
			$elev_print = $elev;
		    }


		    #--- pull out individual obs qc flags for each variable:
		    my $temp_flg    = substr($qcflags, 1, 1);
		    my $dew_flg     = substr($qcflags, 2, 1);
		    my $spd_flg     = substr($qcflags, 5, 1);
		    my $dir_flg     = substr($qcflags, 4, 1);
		    my $stnpres_flg = substr($qcflags, 8, 1);
		    my $pres_flg    = substr($qcflags, 6, 1);
		    my $pcp6_flg    = substr($qcflags, 9, 1);

		    if ($temp_flg eq 1 or $temp_flg eq 2 or $temp_flg eq 3) {
			$temp = $mvc
		    }
		    if ($dew_flg eq 1 or $dew_flg eq 2 or $dew_flg eq 3) {
			$dew = $mvc
		    }
		    if ($spd_flg eq 1 or $spd_flg eq 2 or $spd_flg eq 3) {
			$spd = $mvc
		    }
		    if ($dir_flg eq 1 or $dir_flg eq 2 or $dir_flg eq 3) {
			$dir = $mvc
		    }

		    #--- for winds, also look at $windskip...
		    if ($spd =~ (/^$/)) {
			$spd = $mvc;
		    } else {
			if ($spd > $mvc and $spd <= $windskip) {
			    $spd = $mvc;
			    $dir = $mvc;
			}
		    }

		    if ($stnpres_flg eq 1 or $stnpres_flg eq 2 or 
			$stnpres_flg eq 3) {
			$stnpres = $mvc
		    }
		    if ($pres_flg eq 1 or $pres_flg eq 2 or $pres_flg eq 3) {
			$pres = $mvc
		    }
		    if ($pcp6_flg eq 1 or $pcp6_flg eq 2 or $pcp6_flg eq 3) {
			$pcp6 = $mvc
		    }

		    $t2m      = &check_for_missing($t2m);
		    $temp     = &check_for_missing($temp);
		    $dew2m    = &check_for_missing($dew2m);
		    $dew      = &check_for_missing($dew);
		    $wsp10m   = &check_for_missing($wsp10m);
		    $spd      = &check_for_missing($spd);
		    $dir10m   = &check_for_missing($dir10m);
		    $dir      = &check_for_missing($dir);
		    $sfp      = &check_for_missing($sfp);
		    $stnpres  = &check_for_missing($stnpres);
		    $slp      = &check_for_missing($slp);
		    $pres     = &check_for_missing($pres);
		    $mpcp6    = &check_for_missing($mpcp6);
		    $pcp6     = &check_for_missing($pcp6);

		    print OUT 
			"$refid,$fhr,$date,$initdate,$lat,$lon,$elev_print,". 
			"$t2m,$temp,$dew2m,$dew,$wsp10m,$spd,$dir10m,$dir,".
			"$sfp,$stnpres,$sfps,$stnpres,$slp,$pres," .
			"$mpcp6,$pcp6\n";
		    $rows++;
		}
	    }
	}
	
	print "running execute and writing $outfile for " . 
	    "init=${ihr_in}, fhr=${fhr_in} sfc${year_valid} took " . 
	    (time-$start) . " seconds \n";
	print "rv from $query = $rv\n" if ($debug);
	
	close OUT;

	if ($rows > 0) {
	    print "wrote $rows lines to $outfile\n";
	} elsif ($rows == 0) {
	    print "ERROR:  didn't write out any rows!\n";
	    return -1;
	}

	$iret = $sth->finish();

	$m++;   # iterate model counter.
    }
    #---
    #--- Disconnect from database
    #---
    $iret = $dbh->disconnect();

    print "total rows = $rows\n";

    if ($rows == 0) {
	return -1;
    } else {
	return 0;
    }

}

sub check_for_missing {
    my($val) = @_;
    my $diff;

    if ($val =~ (/^$/)) {
	return $mvc;
    } else {
	return $val;
    }
}

1;

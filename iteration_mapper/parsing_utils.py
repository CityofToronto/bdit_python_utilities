#map_metric.py
#! python3
"""Parsing utilities for map_metric.py

Public Functions:
    parse_args(args, prog = None, usage = None):
        Parse command line argument

    get_yyyymmdd(yyyy, mm, **kwargs):
        Combine integer yyyy and mm into a string date yyyy-mm-dd. 
    
    fullmatch(regex, string, flags=0):
        Emulate python-3.4 re.fullmatch().
    
    format_fromto_hr(hour1, hour2):
        Format hour1-hour2 as a string and append AM/PM
        
    validate_multiple_yyyymm_range(years_list, agg_level):
        Validate a list of pairs of yearmonth strings
        
    get_timerange(time1, time2):
        Validate provided times and create a timerange string to be inserted into PostgreSQL
    """
import argparse
import logging
import re
from datetime import time

def fullmatch(regex, string, flags=0):
    """Emulate python-3.4 re.fullmatch().
    source: http://stackoverflow.com/a/30212799/4047679"""
    return re.match("(?:" + regex + r")\Z", string, flags=flags)

def _check_hour(parser, hour):
    if hour < 0 or hour > 24:
        raise parser.error('{} must be between 0 and 24'.format(hour))

def _check_hours(parser, hours):
    if len(hours) > 1:
        for hour in hours:
            _check_hour(parser, hour)
        if hours[0] > hours[1]:
            raise parser.error('{} must be before {}'.format(hours[0],hours[1]))
    else:
        _check_hour(parser, hours if type(hours) is int else hours[0])

def parse_args(args, prog = None, usage = None):
    """Parse command line arguments
    
    Args:
        sys.argv[1]: command line arguments
        prog: alternate program name, FOR TESTING
        usage: alternate usage message, to suppress FOR TESTING
        
    Returns:
        dictionary of parsed arguments
    """
    PARSER = argparse.ArgumentParser(description='Produce maps of congestion metrics (tti, bti) for '
                                                 'different aggregation periods, timeperiods, and '
                                                 'aggregation levels', prog=prog, usage=usage)
    
    PARSER.add_argument('Metric', choices=['b', 't'], nargs='+',
                        help="Map either Buffer Time Index, Travel"
                        "Time Index or both e.g. b, t, or 'b t'."
                        "Make sure to space arguments")
    
    PARSER.add_argument("Aggregation", choices=['year', 'quarter', 'month'],
                        help="Aggregation level to be used")
    
    PARSER.add_argument("-r", "--range", nargs=2, action='append',
                        help="Range of months (YYYYMM) to operate over"
                        "from startdate to enddate. Accepts multiple pairs",
                        metavar=('YYYYMM', 'YYYYMM'), required=True)
    
    TIMEPERIOD = PARSER.add_mutually_exclusive_group(required=True)
    TIMEPERIOD.add_argument("-p", "--timeperiod", nargs='+', type=int,
                            help="Timeperiod of aggregation, use 1 arg for 1 hour or 2 args for a range")
    TIMEPERIOD.add_argument("-i","--hours_iterate", nargs=2, type=int,
                            help="Create hourly maps from H1 to H2 with H from 0-24")
    
    PARSER.add_argument("--periodname", nargs=2,
                        help="Custom name for --timeperiod e.g. 'AM Peak'")
    
    PARSER.add_argument("-d", "--dbsetting",
                        default='default.cfg',
                        help="Filename with connection settings to the database"
                        "(default: opens %(default)s)")
    PARSER.add_argument("-t", "--tablename",
                        default='congestion.metrics',
                        help="Table containing metrics %(default)s")
    parsed_args = PARSER.parse_args(args)
    
    if parsed_args.periodname:
        parsed_args.periodname = ' '.join(parsed_args.periodname) + ' '
    if parsed_args.timeperiod and len(parsed_args.timeperiod) > 2:
        PARSER.error('--timeperiod takes one or two arguments')
    if len(parsed_args.Metric) > 2:
        PARSER.error('Extra input of metrics unsupported')
    if parsed_args.periodname and parsed_args.hours_iterate:
        PARSER.error('--periodname should only be used with --timeperiod')
    _check_hours(PARSER, parsed_args.timeperiod if parsed_args.timeperiod else parsed_args.hours_iterate)
    try:
        parsed_args.range = validate_multiple_yyyymm_range(parsed_args.range, parsed_args.Aggregation)
    except ValueError as err:
        PARSER.error(err)
    return parsed_args

def get_yyyymmdd(yyyy, mm, **kwargs):
    """Combine integer yyyy and mm into a string date yyyy-mm-dd."""
    
    if 'dd' not in kwargs:
        dd = '01'    
    elif kwargs['dd'] >= 10:
        dd = str(kwargs['dd'])
    elif kwargs['dd'] < 10:
        dd = '0'+str(kwargs['dd'])
            
    if mm < 10:
        return str(yyyy)+'-0'+str(mm)+'-'+dd
    else:
        return str(yyyy)+'-'+str(mm)+'-'+dd

def _format_hour_ampm(hr):
    """Return a string hour with no leading zero and AM/PM"""
    return '{:d} {}'.format(int(hr.strftime("%I")), hr.strftime("%p"))

def format_fromto_hr(hour1, hour2):
    """Format hour1-hour2 as a string and append AM/PM"""
    from_to_hour = '{from_hour}-{to_hour}'
    hr1 = time(hour1)
    to_hour = None
    
    if hour2 == 24:
        to_hour = '12 AM'
        from_hour =  _format_hour_ampm(hr1)
    else:
        to_hour = _format_hour_ampm(time(hour2))
        if hour1 < 12 and hour2 >= 12:
            from_hour =  _format_hour_ampm(hr1)
        else:
            from_hour = str(int(hr1.strftime("%I")))
    return from_to_hour.format(from_hour=from_hour, to_hour=to_hour)

def _validate_yyyymm_range(yyyymmrange, agg_level):
    """Validate the two yyyymm command line arguments provided

    Args:
        yyyymmrange: List containing a start and end year-month in yyyymm format
        agg_level: the aggregation level, determines number of months each 
            period spans
    
    Returns:
        A dictionary with the processed range like {'yyyy':range(mm1,mm2+1)}
    
    Raises:
        ValueError: If the values entered are incorrect
    """

    #if agg_level not in SQLS:
    #    raise ValueError('Aggregation level: {agg_level} not implemented'.format(agg_level=agg_level))
    if agg_level == 'month':
        step = 1
    elif agg_level == 'quarter':
        step = 3
    
    if len(yyyymmrange) != 2:
        raise ValueError('{yyyymmrange} should contain two YYYYMM arguments'
                         .format(yyyymmrange=yyyymmrange))
    
    regex_yyyymm = re.compile(r'20\d\d(0[1-9]|1[0-2])')
    yyyy, mm = [], []
    years = {}
    
    for yyyymm in yyyymmrange:
        if fullmatch(regex_yyyymm.pattern, yyyymm):
            if agg_level == 'year' and int(yyyymm[-2:]) != 1:
                raise ValueError('For annual aggregation, month must be 01 not {yyyymm}'
                                 .format(yyyymm=yyyymm))
            elif agg_level == 'quarter' and (int(yyyymm[-2:]) % 3) != 1:
                raise ValueError('For quarterly mapping, month must be in [1,4,7,10] not {yyyymm}'
                                 .format(yyyymm=yyyymm))
            yyyy.append(int(yyyymm[:4]))
            mm.append(int(yyyymm[-2:]))
        else:
            raise ValueError('{yyyymm} is not a valid year-month value of format YYYYMM'
                             .format(yyyymm=yyyymm))
     
    if yyyy[0] > yyyy[1] or (yyyy[0] == yyyy[1] and mm[0] > mm[1]):
        raise ValueError('Start date {yyyymm1} after end date {yyyymm2}'
                         .format(yyyymm1=yyyymmrange[0], yyyymm2=yyyymmrange[1]))
     
    if agg_level == 'year':
        #Only add January for each year to be mapped
        if yyyy[0] == yyyy[1]:
            years[yyyy[0]] = [1]
        else:
            for year in range(yyyy[0], yyyy[1]+1):
                years[year] = [1]
    else: 
        #Iterate over years and months with specified aggregation step 
        #(month or quarter)
        if yyyy[0] == yyyy[1]:
            years[yyyy[0]] = range(mm[0], mm[1]+1, step)
        else:
            for year in range(yyyy[0], yyyy[1]+1):
                if year == yyyy[0]:
                    years[year] = range(mm[0], 13, step)
                elif year == yyyy[1]:
                    years[year] = range(1, mm[1]+1, step)
                else:
                    years[year] = range(1, 13, step)
    
    return years

def validate_multiple_yyyymm_range(years_list, agg_level):
    """Validate a list of pairs of yearmonth strings
    
    Takes one or more lists like ['YYYYMM','YYYYMM'] and passes them to 
    _validate_yyyymm_range then merges them back into a dictionary of
    years[YYYY] = [month1, month2, etc]
    
    Args: 
        years_list: a list of lists of yyyymm strings
        agg_level: the aggregation level, determines number of months each 
            period spans
    
    Raises:
        ValueError: If the values entered are incorrect
    
    Returns:
        a dictionary of years[YYYY] = [month1, month2, etc]
    """
    years = {}
    if len(years_list) == 1:
        years = _validate_yyyymm_range(years_list[0], agg_level)
    else:
        for yearrange in years_list:
            years_to_add = _validate_yyyymm_range(yearrange, agg_level)
            for year_to_add in years_to_add:
                if year_to_add not in years:
                    years[year_to_add] = years_to_add[year_to_add]
                else:
                    years[year_to_add] = set.union(set(years_to_add[year_to_add]),
                                                   set(years[year_to_add]))
    return years

def get_timerange(time1, time2):
    """Validate provided times and create a timerange string to be inserted into PostgreSQL
    
    Args:
        time1: Integer first hour
        time2: Integer second hour
        
    Returns:
        String representation creating a PostgreSQL timerange object
    """
    if time1 == time2:
        raise ValueError('2nd time parameter {time2} must be at least 1 hour after first parameter {time1}'.format(time1=time1, time2=time2))
        
    starttime = time(int(time1))
    
    #If the second time is 24, aka midnight, replace with maximum possible time for the range
    if time2 == 24:
        endtime = time.max
    else:
        endtime = time(int(time2))
        
    if starttime > endtime:
        raise ValueError('start time {starttime} after end time {endtime}'.format(starttime=starttime, endtime=endtime))
    
    return 'timerange(\'{starttime}\'::time, \'{endtime}\'::time)'.format(starttime=starttime.isoformat(),
                                                                          endtime=endtime.isoformat())

import unittest
import sys
from argparse import ArgumentError
from contextlib import contextmanager
from io import StringIO
from parsing_utils import get_timerange, parse_args, validate_multiple_yyyymm_range, _validate_yyyymm_range, format_fromto_hr
''' Testing file
    Run with `python -m unittest in the root folder'''

@contextmanager
def capture_sys_output():
    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err

class TimeRangeTestCase(unittest.TestCase):
    '''Tests for timerange creation'''
    
    def test_outoforder_times(self):
        '''Test if the proper error is thrown with time1=9 and time2=8'''
        with self.assertRaises(ValueError) as cm:
            get_timerange(9,8)
        self.assertEqual('start time 09:00:00 after end time 08:00:00', str(cm.exception))
        
    def test_valid_range(self):
        '''Test if the right string is produced from time1=8 and time2=9'''
        valid_result = 'timerange(\'08:00:00\'::time, \'09:00:00\'::time)'
        self.assertEqual(valid_result, get_timerange(8,9))
        
    def test_equal_numbers(self):
        '''Test if the proper error is thrown if both parameters are equal'''
        with self.assertRaises(ValueError) as cm:
            get_timerange(8,8)
        self.assertEqual('2nd time parameter 8 must be at least 1 hour after first parameter 8', str(cm.exception))

class YearsValidationTestCase(unittest.TestCase):
    '''Test processing of yyyymm parameters'''
    
    def test_valid_yyyymm_range_month(self):
        '''Test if the range ['201206','201403'] produces the right range'''
        valid_result = {2012:range(6,13),
                        2013:range(1,13),
                        2014:range(1,4)}
        self.assertEqual(valid_result, 
                         _validate_yyyymm_range(['201206', '201403'], 'month'))

    def test_valid_yyyymm_sameyear_range_month(self):
        '''Test if the range ['201604','201606'] produces the right range'''
        valid_result = {2016:range(4,7)}
        self.assertEqual(valid_result, 
                         _validate_yyyymm_range(['201604', '201606'], 'month'))

    def test_outoforder_yyyymm_range(self):
        '''Test if the proper error is thrown with ['201403', '201206']'''
        with self.assertRaises(ValueError) as cm:
            _validate_yyyymm_range(['201403', '201206'], 'month')
        self.assertEqual('Start date 201403 after end date 201206', str(cm.exception))
        
    def test_outoforder_yyyymm_range_sameyear(self):
        '''Test if the proper error is thrown with ['201606', '201603']'''
        with self.assertRaises(ValueError) as cm:
            _validate_yyyymm_range(['201606', '201603'], 'month')
        self.assertEqual('Start date 201606 after end date 201603', str(cm.exception))

    def test_yearagg_wrongmonth(self):
        '''Test if the proper error is thrown with agg_level of
        'year' and ['201502', '201601']'''
        with self.assertRaises(ValueError) as cm:
            _validate_yyyymm_range(['201502', '201601'], 'year')
        self.assertEqual('For annual aggregation, month must be 01 not 201502', str(cm.exception))

    def test_quarteragg_wrongmonth(self):
        '''Test if the proper error is thrown with agg_level of
        'quarter' and ['201502', '201601']'''
        with self.assertRaises(ValueError) as cm:
            _validate_yyyymm_range(['201502', '201601'],
                                   'quarter')
        self.assertEqual('For quarterly mapping, month must be in [1,4,7,10] not 201502', str(cm.exception))
    
    def test_invalid_yyyymm_value(self):
        '''Test if the proper error is thrown with an invalid YYYYMM ['201206','201217']'''
        with self.assertRaises(ValueError) as cm:
            _validate_yyyymm_range(['201206', '201217'], 'month')
        self.assertEqual('201217 is not a valid year-month value of format YYYYMM', str(cm.exception))
        
    def test_multiple_yyyymm_range(self):
        '''Test if using an overlapping range produces the right result'''
        test_range = [['201203', '201301'],['201207', '201209']]
        valid_result = {2012:set(range(3,13)),
                        2013:range(1,2)}
        self.assertEqual(valid_result,validate_multiple_yyyymm_range(test_range, 'month'))

    def test_multiple_yyyymm_range_distinct(self):
        '''Test if using distinct ranges in the same year produces the right result'''
        test_range = [['201203', '201207'],['201209', '201303']]
        valid_result = {2012:set.union(set(range(3,8)), set(range(9,13))),
                        2013:range(1,4)}
        self.assertEqual(valid_result,validate_multiple_yyyymm_range(test_range, 'month'))
        
    def test_multiple_yyyymm_range_single(self):
        '''Test if a single range produces the right result'''
        test_range = [['201203', '201301']]
        valid_result = {2012:range(3,13),
                        2013:range(1,2)}
        self.assertEqual(valid_result,validate_multiple_yyyymm_range(test_range, 'month'))

    def test_valid_yyyymm_range_quarter(self):
        '''Test if the range ['201207','201404'] produces the right range with quarterly aggregation'''
        valid_result = {2012:range(7,13,3),
                        2013:range(1,13,3),
                        2014:range(1,5,3)}
        self.assertEqual(valid_result, 
                         _validate_yyyymm_range(['201207', '201404'], 'quarter'))

    def test_valid_yyyymm_sameyear_range_quarter(self):
        '''Test if the range ['201601','201607'] produces the right range with quarterly aggregation'''
        valid_result = {2016:[1, 4]}
        self.assertEqual(valid_result, 
                         _validate_yyyymm_range(['201601', '201607'], 'quarter'))

    def test_valid_yyyymm_range_year(self):
        '''Test if the range ['201201','201401'] produces the right range with annual aggregation'''
        valid_result = {2012:[1],
                        2013:[1],
                        2014:[1],
                       }
        self.assertEqual(valid_result, 
                         _validate_yyyymm_range(['201201', '201401'], 'year'))

    def test_valid_yyyymm_sameyear_range_quarter(self):
        '''Test if the range ['201501','201501'] produces the right range with annual aggregation'''
        valid_result = {2015:[1]}
        self.assertEqual(valid_result, 
                         _validate_yyyymm_range(['201501', '201501'], 'year'))

class ArgParseTestCase(unittest.TestCase):
    '''Tests for argument parsing'''

    def __init__(self, *args, **kwargs):
        self.testing_params = {'prog':'TESTING', 'usage':''}
        self.stderr_msg = 'usage: \nTESTING: error: {errmsg}\n'
        super(ArgParseTestCase, self).__init__(*args, **kwargs)
    
    def test_years_y_single(self):
        '''Test if a single pair of years produces the right values'''
        valid_result = {2016:range(4,7)}
        args = parse_args('b month -p 8 -r 201604 201606'.split())
        self.assertEqual(valid_result, args.range)

    def test_metric_both(self):
        '''Test if inputting both metrics produces right metric arguments'''
        valid_result = ['b','t']
        args = parse_args('b t year -p 8 -r 201401 201501'.split())
        self.assertEqual(valid_result, args.Metric)

    def test_metric_three(self):
        '''Test if a too many metrics throws an error'''
        with self.assertRaises(SystemExit) as cm, capture_sys_output() as (stdout, stderr):
            args = parse_args('b t t year -p 8 -r 201407 201506'.split(), **self.testing_params)
        self.assertEqual(2, cm.exception.code)
        errmsg = 'Extra input of metrics unsupported'
        self.assertEqual(self.stderr_msg.format(errmsg=errmsg), stderr.getvalue())

    def test_aggregation_level(self):
        '''Test if aggregation level years produces the right value'''
        valid_result = 'year'
        args = parse_args('b t year -p 8 -r 201401 201501'.split())
        self.assertEqual(valid_result, args.Aggregation)

    def test_years_y_multiple(self):
        '''Test if a multiple pair of years produces the right values'''
        valid_result = {2012:set.union(set(range(3,8)), set(range(9,13))),
                        2013:range(1,4)}
        
        args = parse_args('b month -p 8 -r 201203 201207 -r 201209 201303'.split())
        self.assertEqual(valid_result, args.range)

    def test_range_only_one_exception(self):
        '''Test if a single year produces the right exception'''
        with self.assertRaises(SystemExit) as cm, capture_sys_output() as (stdout, stderr):
            args = parse_args('b year -p 8 -r 201201'.split(), **self.testing_params)
        self.assertEqual(2, cm.exception.code)
        self.assertEqual('usage: \nTESTING: error: argument -r/--range: expected 2 arguments\n', stderr.getvalue())

    def test_custom_period_name_exception(self):
        '''Test if combining custom time period name with -i produces the right exception'''
        with self.assertRaises(SystemExit) as cm, capture_sys_output() as (stdout, stderr):
            args = parse_args('b month -i 8 10 --periodname AM Peak -r 201207 201506'.split(), **self.testing_params)
        self.assertEqual(2, cm.exception.code)
        self.assertEqual('usage: \nTESTING: error: --periodname should only be used with --timeperiod\n', stderr.getvalue())

    def test_timeperiod_too_many_args_exception(self):
        '''Test if a single year produces the right exception'''
        with self.assertRaises(SystemExit) as cm, capture_sys_output() as (stdout, stderr):
            args = parse_args('b month -p 8 10 12 -r 201207 201506'.split(), **self.testing_params)
        self.assertEqual(2, cm.exception.code)
        self.assertEqual('usage: \nTESTING: error: --timeperiod takes one or two arguments\n', stderr.getvalue())

    def test_period_one(self):
        '''Test if a the right value for period is parsed'''
        valid_result = [8]
        args = parse_args('b t month -p 8 -r 201407 201506'.split())
        self.assertEqual(valid_result, args.timeperiod)

    def test_periodname(self):
        '''Test if the right value for a custom timeperiod name is parsed'''
        valid_result = 'AM Peak '
        args = parse_args("b t month -p 8 --periodname AM Peak -r 201407 201506".split())
        self.assertEqual(valid_result, args.periodname)

    def test_iterate_hours(self):
        '''Test if the right value for iteration hours is parsed'''
        valid_result = [8,9]
        args = parse_args('b t month -i 8 9 -r 201407 201506'.split())
        self.assertEqual(valid_result, args.hours_iterate)

    def test_default_tablename(self):
        '''Test if the right default for tablename is returned'''
        valid_result = 'congestion.metrics'
        args = parse_args('b t month -i 8 9 -r 201407 201506'.split())
        self.assertEqual(valid_result, args.tablename)

    def test_hours_check(self):
        '''Test if a too many metrics throws an error'''
        with self.assertRaises(SystemExit) as cm, capture_sys_output() as (stdout, stderr):
            args = parse_args('b year -p 8 25 -r 201407 201506'.split(), **self.testing_params)
        self.assertEqual(2, cm.exception.code)
        errmsg = '25 must be between 0 and 24'
        self.assertEqual(self.stderr_msg.format(errmsg=errmsg), stderr.getvalue())
        with self.assertRaises(SystemExit) as cm, capture_sys_output() as (stdout, stderr):
            args = parse_args('b year -p 24 8 -r 201407 201506'.split(), **self.testing_params)
        self.assertEqual(2, cm.exception.code)
        errmsg = '24 must be before 8'
        self.assertEqual(self.stderr_msg.format(errmsg=errmsg), stderr.getvalue())
        
class FromToHourTestCase(unittest.TestCase):
    '''Tests for getting strings for the to_hour'''
        
    def test_valid(self):
        '''Test if the right string is produced from hour<12, hour=12, hour>12, hour=24'''
        valid_result = '8-10 AM'
        self.assertEqual(valid_result, format_fromto_hr(8, 10))
        valid_result = '8 AM-12 PM'
        self.assertEqual(valid_result, format_fromto_hr(8, 12))
        valid_result = '4-6 PM'
        self.assertEqual(valid_result, format_fromto_hr(16, 18))
        valid_result = '5 AM-12 AM'
        self.assertEqual(valid_result, format_fromto_hr(5, 24))

        
if __name__ == '__main__':
    unittest.main()
''' Testing file
    Run with `python -m unittest in the root folder'''
import sys
import unittest

from parsing_utilities.time_parsing import (_validate_yyyymm_range,
                                            _validate_yyyymmdd_range,
                                            format_fromto_hr, get_timerange,
                                            validate_multiple_yyyymm_range)

sys.path.append('../')



class TimeRangeTestCase(unittest.TestCase):
    '''Tests for timerange creation'''
    
    def test_outoforder_times(self):
        '''Test if the proper error is thrown with time1=9 and time2=8'''
        with self.assertRaises(ValueError) as cm:
            get_timerange(9, 8)
        self.assertEqual('start time 09:00:00 after end time 08:00:00', str(cm.exception))
        
    def test_valid_range(self):
        '''Test if the right string is produced from time1=8 and time2=9'''
        valid_result = 'timerange(\'08:00:00\'::time, \'09:00:00\'::time)'
        self.assertEqual(valid_result, get_timerange(8, 9))
        
    def test_equal_numbers(self):
        '''Test if the proper error is thrown if both parameters are equal'''
        with self.assertRaises(ValueError) as cm:
            get_timerange(8, 8)
        self.assertEqual('2nd time parameter 8 must be at least 1 hour after first parameter 8',
                         str(cm.exception))

class YearsValidationTestCase(unittest.TestCase):
    '''Test processing of yyyymm parameters'''
    
    def test_valid_yyyymm_range_month(self):
        '''Test if the range ['201206','201403'] produces the right range'''
        valid_result = {2012:range(6, 13),
                        2013:range(1, 13),
                        2014:range(1, 4)}
        self.assertEqual(valid_result, 
                         _validate_yyyymm_range(['201206', '201403'], 'month'))

    def test_valid_yyyymm_sameyear_range_month(self):
        '''Test if the range ['201604','201606'] produces the right range'''
        valid_result = {2016:range(4, 7)}
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
        self.assertEqual('For quarterly mapping, month must be in [1,4,7,10] not 201502',
                         str(cm.exception))
    
    def test_invalid_yyyymm_value(self):
        '''Test if the proper error is thrown with an invalid YYYYMM ['201206','201217']'''
        with self.assertRaises(ValueError) as cm:
            _validate_yyyymm_range(['201206', '201217'], 'month')
        self.assertEqual('201217 is not a valid year-month value of format YYYYMM',
                         str(cm.exception))
        
    def test_multiple_yyyymm_range(self):
        '''Test if using an overlapping range produces the right result'''
        test_range = [['201203', '201301'], ['201207', '201209']]
        valid_result = {2012:set(range(3, 13)),
                        2013:range(1, 2)}
        self.assertEqual(valid_result,
                         validate_multiple_yyyymm_range(test_range, 'month'))

    def test_multiple_yyyymm_range_distinct(self):
        '''Test if using distinct ranges in the same year produces the right result'''
        test_range = [['201203', '201207'], ['201209', '201303']]
        valid_result = {2012:set.union(set(range(3, 8)), set(range(9, 13))),
                        2013:range(1, 4)}
        self.assertEqual(valid_result,validate_multiple_yyyymm_range(test_range, 'month'))
        
    def test_multiple_yyyymm_range_single(self):
        '''Test if a single range produces the right result'''
        test_range = [['201203', '201301']]
        valid_result = {2012:range(3, 13),
                        2013:range(1, 2)}
        self.assertEqual(valid_result,validate_multiple_yyyymm_range(test_range, 'month'))

    def test_valid_yyyymm_range_quarter(self):
        '''Test if the range ['201207','201404'] produces the right range with quarterly aggregation'''
        valid_result = {2012:range(7, 13, 3),
                        2013:range(1, 13, 3),
                        2014:range(1, 5, 3)}
        self.assertEqual(valid_result, 
                         _validate_yyyymm_range(['201207', '201404'], 'quarter'))

    def test_valid_yyyymm_sameyear_range_quarter(self):
        '''Test if the range ['201601','201607'] produces the right range with quarterly aggregation'''
        valid_result = {2016:range(1, 8, 3)}
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

    def test_valid_yyyymm_sameyear_quarter(self):
        '''Test if the range ['201501','201501'] produces the right range with annual aggregation'''
        valid_result = {2015:[1]}
        self.assertEqual(valid_result, 
                         _validate_yyyymm_range(['201501', '201501'], 'year'))

class YyyymmddValidationTestCase(unittest.TestCase):
    '''Test processing of yyyymm parameters'''
    
    def test_valid_yyyymmdd_range(self):
        '''Test if correct ranges produce the right range'''
        test_name = 'Same month'
        with self.subTest(name=test_name):
            valid_result = {2012: {8: range(8, 13 + 1)}}
            self.assertEqual(valid_result, 
                             _validate_yyyymmdd_range(['20120808', '20120813']), test_name)
        test_name = 'Same year'
        with self.subTest(name=test_name):
            valid_result = {2012: {8: range(8, 31 + 1),
                                   9: range(1, 30 + 1),
                                   10: range(1, 10 + 1)}}
            self.assertEqual(valid_result, 
                             _validate_yyyymmdd_range(['20120808', '20121010']), test_name)
        test_name = 'Different years'
        with self.subTest(name=test_name):
            valid_result = {2012: {12: range(8, 31 + 1)},
                            2013: {1: range(1, 12 + 1)}}
            self.assertEqual(valid_result, 
                             _validate_yyyymmdd_range(['20121208', '20130112']), test_name)

    def test_invalid_yyyymmdd_value(self):
        '''Test if the proper error is thrown with an invalid yyyymmdd ['20120601','20121701']'''
        with self.assertRaises(ValueError) as cm:
            _validate_yyyymmdd_range(['20120601', '20121701'])
        self.assertEqual('20121701 is not a valid year-month value of format YYYYMMDD',
                         str(cm.exception))

    def test_outoforder_yyyymmdd_range(self):
        '''Test if the proper error is thrown with ['20140301', '20120601']'''
        with self.assertRaises(ValueError) as cm:
            _validate_yyyymmdd_range(['20140301', '20120601'])
        self.assertEqual('Start date 20140301 after end date 20120601', str(cm.exception))
        
    def test_outoforder_yyyymmdd_range_sameyear(self):
        '''Test if the proper error is thrown with ['20160601', '20160301']'''
        with self.assertRaises(ValueError) as cm:
            _validate_yyyymmdd_range(['20160601', '20160301'])
        self.assertEqual('Start date 20160601 after end date 20160301', str(cm.exception))

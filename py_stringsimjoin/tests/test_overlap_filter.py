import unittest

import pandas as pd

from py_stringsimjoin.filter.overlap_filter import OverlapFilter
from py_stringsimjoin.utils.tokenizers import create_delimiter_tokenizer


# test OverlapFilter.filter_pair method
class FilterPairTestCases(unittest.TestCase):
    def setUp(self):
        self.tokenizer = create_delimiter_tokenizer(' ')
        self.overlap_filter = OverlapFilter(self.tokenizer,
                                            overlap_size=1)

    def test_to_be_pruned_pair(self):
        self.assertTrue(self.overlap_filter.filter_pair('aa bb cc', 'xx yy'))

    def test_to_be_passed_pair(self):
        self.assertFalse(self.overlap_filter.filter_pair('aa bb cc',
                                                         'xx yy aa'))

    def test_empty_input(self):
        self.assertTrue(self.overlap_filter.filter_pair('ab', ''))


# test OverlapFilter.filter_tables method
class FilterTablesTestCases(unittest.TestCase):
    def setUp(self):
        self.tokenizer = create_delimiter_tokenizer(' ')
        self.overlap_filter = OverlapFilter(self.tokenizer,
                                            overlap_size=1)

    def test_valid_tables(self):
        A = pd.DataFrame([{'id': 1, 'attr':'ab cd ef aa bb'},
                          {'id': 2, 'attr':''},
                          {'id': 3, 'attr':'ab'},
                          {'id': 4, 'attr':'ll oo pp'},
                          {'id': 5, 'attr':'xy xx zz fg'}])
        B = pd.DataFrame([{'id': 1, 'attr':'mn'},
                          {'id': 2, 'attr':'he ll'},
                          {'id': 3, 'attr':'xy pl ou'},
                          {'id': 4, 'attr':'aa'},
                          {'id': 5, 'attr':'fg cd aa ef'}])
        expected_one_overlap_pairs = set(['1,4', '1,5', '4,2', '5,3', '5,5'])
        C = self.overlap_filter.filter_tables(A, B,
                                              'id', 'id',
                                              'attr', 'attr')
        self.assertEquals(len(C), len(expected_one_overlap_pairs))
        self.assertListEqual(list(C.columns.values),
                             ['_id', 'l_id', 'r_id'])
        actual_one_overlap_pairs = set()
        for idx, row in C.iterrows():
            actual_one_overlap_pairs.add(','.join((str(row['l_id']),
                                                   str(row['r_id']))))

        self.assertEqual(len(expected_one_overlap_pairs),
                         len(actual_one_overlap_pairs))
        common_pairs = actual_one_overlap_pairs.intersection(
                           expected_one_overlap_pairs)
        self.assertEqual(len(common_pairs),
                         len(expected_one_overlap_pairs))

    def test_empty_tables(self):
        A = pd.DataFrame(columns=['id', 'attr'])
        B = pd.DataFrame(columns=['id', 'attr'])
        C = self.overlap_filter.filter_tables(A, B,
                                              'id', 'id',
                                              'attr', 'attr')
        self.assertEqual(len(C), 0)
        self.assertListEqual(list(C.columns.values),
                             ['_id', 'l_id', 'r_id'])


# test OverlapFilter.filter_candset method
class FilterCandsetTestCases(unittest.TestCase):
    def setUp(self):
        self.tokenizer = create_delimiter_tokenizer(' ')
        self.overlap_filter = OverlapFilter(self.tokenizer,
                                            overlap_size=1)

    def test_valid_candset(self):
        A = pd.DataFrame([{'l_id': 1, 'l_attr':'ab cd ef aa bb'},
                          {'l_id': 2, 'l_attr':''},
                          {'l_id': 3, 'l_attr':'ab'},
                          {'l_id': 4, 'l_attr':'ll oo pp'},
                          {'l_id': 5, 'l_attr':'xy xx zz fg'}])
        B = pd.DataFrame([{'r_id': 1, 'r_attr':'mn'},
                          {'r_id': 2, 'r_attr':'he ll'},
                          {'r_id': 3, 'r_attr':'xy pl ou'},
                          {'r_id': 4, 'r_attr':'aa'},
                          {'r_id': 5, 'r_attr':'fg cd aa ef'}])

        # generate cartesian product A x B to be used as candset
        A['tmp_join_key'] = 1
        B['tmp_join_key'] = 1
        C = pd.merge(A[['l_id', 'tmp_join_key']],
                     B[['r_id', 'tmp_join_key']],
                     on='tmp_join_key').drop('tmp_join_key', 1)

        expected_one_overlap_pairs = set(['1,4', '1,5', '4,2', '5,3', '5,5'])
        D = self.overlap_filter.filter_candset(C,
                                               'l_id', 'r_id',
                                               A, B,
                                               'l_id', 'r_id',
                                               'l_attr', 'r_attr')
        self.assertEquals(len(D), len(expected_one_overlap_pairs))
        self.assertListEqual(list(D.columns.values),
                             ['l_id', 'r_id'])
        actual_one_overlap_pairs = set()
        for idx, row in D.iterrows():
            actual_one_overlap_pairs.add(','.join((str(row['l_id']),
                                                   str(row['r_id']))))

        self.assertEqual(len(expected_one_overlap_pairs),
                         len(actual_one_overlap_pairs))
        common_pairs = actual_one_overlap_pairs.intersection(
                           expected_one_overlap_pairs)
        self.assertEqual(len(common_pairs),
                         len(expected_one_overlap_pairs))

    def test_empty_candset(self):
        A = pd.DataFrame(columns=['l_id', 'l_attr'])
        B = pd.DataFrame(columns=['r_id', 'r_attr'])

        # generate cartesian product A x B to be used as candset
        A['tmp_join_key'] = 1
        B['tmp_join_key'] = 1
        C = pd.merge(A[['l_id', 'tmp_join_key']],
                     B[['r_id', 'tmp_join_key']],
                     on='tmp_join_key').drop('tmp_join_key', 1)

        D = self.overlap_filter.filter_candset(C,
                                               'l_id', 'r_id',
                                               A, B,
                                               'l_id', 'r_id',
                                               'l_attr', 'r_attr')
        self.assertEqual(len(D), 0)
        self.assertListEqual(list(D.columns.values),
                             ['l_id', 'r_id'])
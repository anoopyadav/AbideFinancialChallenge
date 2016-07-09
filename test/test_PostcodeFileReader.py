import unittest
from FileReader.PostcodeLookupReader import PostcodeLookupReader


class PostcodeListSizeTest(unittest.TestCase):
    def test(self):
        postcode_lookup = PostcodeLookupReader('samples/postcode_sample.csv', None)
        postcode_lookup.set_iteration_method('lazy_read')

        for row in postcode_lookup:
            postcode_lookup.process_file(row)

        self.assertEquals(postcode_lookup.get_total_postcodes(), 8)


class RegionFromPostcodePassTest(unittest.TestCase):
    def test(self):
        postcode_lookup = PostcodeLookupReader('samples/postcode_sample.csv', None)
        postcode_lookup.set_iteration_method('lazy_read')

        for row in postcode_lookup:
            postcode_lookup.process_file(row)

        self.assertEquals(postcode_lookup.get_region_from_postcode('BH21'), 'South West')
        self.assertEquals(postcode_lookup.get_region_from_postcode('WA3'), 'North West')


class RegionFromPostcodeFailTest(unittest.TestCase):
    def test(self):
        postcode_lookup = PostcodeLookupReader('samples/postcode_sample.csv', None)
        postcode_lookup.set_iteration_method('lazy_read')

        for row in postcode_lookup:
            postcode_lookup.process_file(row)

        self.assertRaises(KeyError, postcode_lookup.get_region_from_postcode, 'Junk')

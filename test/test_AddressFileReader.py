import unittest
from FileReader.AddressFileReader import AddressFileReader


class SearchLocationNotSetTest(unittest.TestCase):
    def test(self):
        header = ("Period", "practice_code", "practice_name", "practice_building",
                  "address", "locality", "town", "postcode")
        process_address_file = AddressFileReader('samples/address_sample.csv', header)
        process_address_file.set_iteration_method('chunky_lazy_read')

        for row in process_address_file:
            process_address_file.process_file(row)

        self.assertEquals(process_address_file.get_location_count(), 0)


class CountLocationsTest(unittest.TestCase):
    def test(self):
        header = ("Period", "practice_code", "practice_name", "practice_building",
                  "address", "locality", "town", "postcode")
        process_address_file = AddressFileReader('samples/address_sample.csv', header)
        process_address_file.set_iteration_method('chunky_lazy_read')
        process_address_file.set_location_to_search('LONDON')

        for row in process_address_file:
            process_address_file.process_file(row)

        self.assertEquals(process_address_file.get_location_count(), 2)


class PracticeCodeToPostcodeDictNotInitialisedTest(unittest.TestCase):
    def test(self):
        header = ("Period", "practice_code", "practice_name", "practice_building",
                  "address", "locality", "town", "postcode")
        process_address_file = AddressFileReader('samples/address_sample.csv', header)
        process_address_file.set_iteration_method('chunky_lazy_read')

        self.assertRaises(ValueError, process_address_file.get_postcode_for_practice, 'Practice_Code')


class PopulatePracticeCodeToPostcodeTest(unittest.TestCase):
    def test(self):
        header = ("Period", "practice_code", "practice_name", "practice_building",
                  "address", "locality", "town", "postcode")
        process_address_file = AddressFileReader('samples/address_sample.csv', header)
        process_address_file.set_iteration_method('chunky_lazy_read')

        for row in process_address_file:
            process_address_file.process_file(row)

        self.assertEquals(process_address_file.get_practice_code_to_postcode_count(), 12)


class PostcodeFromPracticeCodeTest(unittest.TestCase):
    def test(self):
        header = ("Period", "practice_code", "practice_name", "practice_building",
                  "address", "locality", "town", "postcode")
        process_address_file = AddressFileReader('samples/address_sample.csv', header)
        process_address_file.set_iteration_method('chunky_lazy_read')

        for row in process_address_file:
            process_address_file.process_file(row)

        self.assertEquals(process_address_file.get_postcode_for_practice('A81010'), 'TS24 9DN')


class PostcodeForNonexistantPracticeCodeTest(unittest.TestCase):
    def test(self):
        header = ("Period", "practice_code", "practice_name", "practice_building",
                  "address", "locality", "town", "postcode")
        process_address_file = AddressFileReader('samples/address_sample.csv', header)
        process_address_file.set_iteration_method('chunky_lazy_read')

        for row in process_address_file:
            process_address_file.process_file(row)

        self.assertEquals(process_address_file.get_postcode_for_practice('JUNK'), None)

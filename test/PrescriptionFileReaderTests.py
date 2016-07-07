import unittest
from unittest.mock import MagicMock
from FileReader.PrescriptionFileReader import PrescriptionFileReader


def dummy_postcode_lookup_method(practice_code):
    practice_code_to_postcode = {'A86001': 'XYZ1 ABC', 'A86003': 'XYZ2 ABC', 'A86004': 'XYZ3 ABC',
                                 'A86006': 'XYZ4 ABC', 'A86007': 'XYZ5 ABC', 'A86008': 'XYZ6 ABC', 'PRACTICE': None}
    return practice_code_to_postcode[practice_code]


def dummy_postcode_to_region_lookup(postcode):
    postcode_to_region = {'XYZ1 ABC': 'LONDON', 'XYZ2 ABC': 'LONDON', 'XYZ3 ABC': 'SOUTH EAST',
                          'XYZ4 ABC': 'SOUTH WEST', 'XYZ5 ABC': 'SOUTH WEST', 'XYZ6 ABC': 'NORTH WEST',
                          None: None}
    return postcode_to_region[postcode]


class AverageCostOfPrescriptionTest(unittest.TestCase):
    def test(self):
        process_prescription_file = PrescriptionFileReader('samples/prescription_sample.csv', None)
        process_prescription_file.set_iteration_method('lazy_sequential_read')
        process_prescription_file.set_postcode_to_region_lookup(MagicMock(return_value=None))
        process_prescription_file.set_practice_code_to_postcode_lookup(MagicMock(return_value=None))

        for row in process_prescription_file:
            process_prescription_file.process_file(row)

        self.assertEquals(process_prescription_file.get_average_cost_of_prescription(), 107.58)


class AverageCostInformationNotPopulatedTest(unittest.TestCase):
    def test(self):
        process_prescription_file = PrescriptionFileReader('samples/prescription_sample.csv', None)
        process_prescription_file.set_iteration_method('lazy_sequential_read')

        self.assertRaises(ValueError, process_prescription_file.get_average_cost_of_prescription)


class Top5SpendersTest(unittest.TestCase):
    def test(self):
        process_prescription_file = PrescriptionFileReader('samples/prescription_sample.csv', None)
        process_prescription_file.set_iteration_method('lazy_sequential_read')
        process_prescription_file.set_postcode_to_region_lookup(MagicMock(return_value=None))
        process_prescription_file.set_practice_code_to_postcode_lookup(dummy_postcode_lookup_method)

        for row in process_prescription_file:
            process_prescription_file.process_file(row)

        expected_list = [('XYZ2 ABC', 1181.79), ('XYZ3 ABC', 126.75), ('XYZ6 ABC', 97.11), ('XYZ5 ABC', 34.5),
                         ('XYZ4 ABC', 28.2)]
        self.assertCountEqual(process_prescription_file.get_top_5_spenders(), expected_list)


class AveragePriceByRegionTest(unittest.TestCase):
    def test(self):
        process_prescription_file = PrescriptionFileReader('samples/prescription_sample.csv', None)
        process_prescription_file.set_iteration_method('lazy_sequential_read')
        process_prescription_file.set_postcode_to_region_lookup(dummy_postcode_to_region_lookup)
        process_prescription_file.set_practice_code_to_postcode_lookup(dummy_postcode_lookup_method)
        process_prescription_file.setup_region_based_dictionaries(['LONDON', 'SOUTH EAST', 'SOUTH WEST', 'NORTH WEST'])

        for row in process_prescription_file:
            process_prescription_file.process_file(row)

        self.assertCountEqual(process_prescription_file.get_average_price_by_region(),
                              {'SOUTH EAST': 4.29, 'SOUTH WEST': 7.22, 'LONDON': 3.09, 'NORTH WEST': 4.49})

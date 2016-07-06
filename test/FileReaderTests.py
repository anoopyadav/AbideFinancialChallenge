import unittest
from FileReader.FileReader import FileReader


class DummyFileReader(FileReader):
    def __init__(self, filename, header):
        FileReader.__init__(self, filename, header)

    def write_output_to_file(self):
        pass

    def process_file(self, row):
        pass


class InvalidFileTest(unittest.TestCase):
    def test(self):
        self.assertRaises(FileNotFoundError, DummyFileReader, 'samples/junk.csv', None)


class ChunkyLazyReadLineWidthTest(unittest.TestCase):
    def test(self):
        dummy_file_reader = DummyFileReader('samples/sample.csv', None)
        dummy_file_reader.set_iteration_method('chunky_lazy_read')
        self.assertEqual(dummy_file_reader.get_line_width(), 168)


class LineCountTest(unittest.TestCase):
    def test(self):
        dummy_file_reader = DummyFileReader('samples/sample.csv', None)
        dummy_file_reader.set_iteration_method('lazy_sequential_read')

        for row in dummy_file_reader:
            pass

        self.assertEqual(dummy_file_reader.get_line_count(), 10)


class LineCountLazyReadTest(unittest.TestCase):
    def test(self):
        dummy_file_reader = DummyFileReader('samples/sample.csv', None)
        dummy_file_reader.set_iteration_method('lazy_read')

        for row in dummy_file_reader:
            pass

        self.assertEqual(dummy_file_reader.get_line_count(), 9)


class LazyReadHeaderTest(unittest.TestCase):
    def test(self):
        dummy_file_reader = DummyFileReader('samples/prescription_sample.csv', None)
        dummy_file_reader.set_iteration_method('lazy_read')

        self.assertCountEqual(list(dummy_file_reader.get_csv_header()),
                              ['SHA', 'PCT', 'PRACTICE', 'BNF CODE', 'BNF NAME', 'ITEMS', 'NIC', 'ACT COST', 'PERIOD'])


class CustomHeaderTest(unittest.TestCase):
    def test(self):
        dummy_file_reader = DummyFileReader('samples/sample.csv', [i for i in range(8)])
        dummy_file_reader.set_iteration_method('chunky_lazy_read')

        self.assertCountEqual(list(dummy_file_reader.get_csv_header()), [i for i in range(8)])


class GetColumnIndexTest(unittest.TestCase):
    def test(self):
        dummy_file_reader = DummyFileReader('samples/prescription_sample.csv', None)
        dummy_file_reader.set_iteration_method('chunky_lazy_read')

        self.assertTrue(0 <= dummy_file_reader.get_column_index('BNF NAME') <= 7)


class GetColumnIndexFailTest(unittest.TestCase):
    def test(self):
        dummy_file_reader = DummyFileReader('samples/prescription_sample.csv', None)
        dummy_file_reader.set_iteration_method('chunky_lazy_read')

        self.assertRaises(KeyError, dummy_file_reader.get_column_index, 'JUNK')


class CommaInFieldsTest(unittest.TestCase):
    def test(self):
        dummy_file_reader = DummyFileReader('samples/postcode_sample.csv', None)
        dummy_file_reader.set_iteration_method('chunky_lazy_read')

        with self.assertRaises(ValueError):
            for row in dummy_file_reader:
                pass

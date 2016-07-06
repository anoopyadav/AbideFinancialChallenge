from abc import ABCMeta, abstractmethod
import csv
import os.path

""" FileReader abstract class
    Contains various methods to read the contents of a file
    Implements the Iterator interface
    Attributes: filename - Fully qualified path to the source CSV file
                header   - The column names for the CSV
"""


class FileReader(metaclass=ABCMeta):
    def __init__(self, filename, header):
        if not os.path.isfile(filename):
            raise FileNotFoundError('The file ' + filename + ' does not exist.')

        self.__filename = filename
        self.__filter_expression = None
        self.__line_count = 0
        self.__iteration_methods = {'lazy_read': self.__lazy_read, 'chunky_lazy_read': self.__chunky_lazy_read,
                                    'lazy_sequential_read': self.__lazy_sequential_read}
        self.__iteration_method = None
        self.__header = header
        self.__column_to_index = None
        self.__line_width = 0
        self.__output_file = 'output.txt'

        self.populate_csv_header(header)

    """ Allows iteration over a FileReader object
    """
    def __iter__(self):
        return self.__iteration_method()

    def set_iteration_method(self, iteration_method):
        self.__iteration_method = self.get_iteration_methods()[iteration_method]

        if iteration_method is 'chunky_lazy_read':
            self.__set_line_width_for_chunks()

    def get_iteration_methods(self):
        return self.__iteration_methods

    def set_filter(self, filter_expression):
        self.__filter_expression = filter_expression

    def get_filter(self):
        return self.__filter_expression

    def get_line_count(self):
        return self.__line_count

    def get_line_width(self):
        return self.__line_width

    """ Reads the first line of the CSV assuming it contains the header fields
        Populates a dictionary with fields as keys and integer indices as values
    """
    def populate_csv_header(self, header):
        if header is None:
            with open(self.__filename, "rt") as f:
                column_list = [h.strip() for h in f.__next__().split(',')]
                self.__column_to_index = dict(zip(column_list, [x for x in range(len(column_list))]))
        else:
            self.__column_to_index = dict(zip(header, [x for x in range((len(header)))]))

    def get_column_index(self, column_name):
        if column_name not in self.__column_to_index.keys():
            raise KeyError(column_name + ' key not in column_to_index dict.')
        return self.__column_to_index[column_name]

    def get_csv_header(self):
        return self.__column_to_index.keys()

    """ Use this method with CSVs that have a well-defined header as the first line.
        Returns each row of the file as a dictionary indexed by the header.
    """
    def __lazy_read(self):
        with open(self.__filename, "rt") as f:
            reader = csv.DictReader(f, fieldnames=self.__header, delimiter=',')

            for row in reader:
                self.__line_count += 1
                yield row

    def __set_line_width_for_chunks(self):
        for line in open(self.__filename, 'rt'):
            self.__line_width = len(line)
            break

    """ Reads a CSV multiple lines at a time, then returns each row as a list of items.
    """

    def __chunky_lazy_read(self):
        with open(self.__filename, "rt") as f:
            while True:
                lines = f.read(self.__line_width * 15000)
                if lines:
                    lines_list = lines.split("\n")

                    for line in lines_list:
                        self.__line_count += 1
                        if self.__filter_expression:
                            if self.__filter_expression in line:
                                yield line.split(',')
                            else:
                                continue
                        else:
                            if len(line) > 1:
                                fields = line.split(',')
                                if len(fields) is len(self.get_csv_header()):
                                    yield fields
                                else:
                                    raise ValueError("The CSV contains ',' in one or more fields."
                                                     " Please use the lazy_read method to correctly process this CSV.")

                else:
                    break

    """ Reads a file one line at a time.
        Returns each row as a list of items.
    """
    def __lazy_sequential_read(self):
        for line in open(self.__filename):
            self.__line_count += 1
            yield line.split(',')

    """ Methods to be over-ridden by concrete classes
    """
    @abstractmethod
    def write_output_to_file(self):
        pass

    """ This is a launcher method that ideally will call private methods that perform the analysis
    """
    @abstractmethod
    def process_file(self, row):
        pass

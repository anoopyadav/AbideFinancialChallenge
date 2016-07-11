from FileReader import FileReader
import re


class AddressFileReader(FileReader):
    def __init__(self, filename, header):
        FileReader.__init__(self, filename, header)

        self.__location_to_search = None
        self.__location_count = 0
        self.__practice_code_to_postcode = {}

    def set_location_to_search(self, location_to_search):
        self.__location_to_search = location_to_search

    def process_file(self, row):
        if len(row) is not len(self.get_csv_header()):
            return
        else:
            self.__populate_practice_code_to_postcode(row)

        if self.__location_to_search is None:
            return
        else:
            self.__count_locations(row)

    """ Look for LONDON in the town field, then the locality field and finally in the address field.
        This is because certain entries have empty fields.
    """
    def __count_locations(self, row):
        location_regex = re.compile(r'^' + self.__location_to_search + '\s*$')

        if row[self.get_column_index('town')] and location_regex.search(row[self.get_column_index('town')]) is not None:
            self.__location_count += 1
        elif row[self.get_column_index('locality')] \
                and location_regex.search(row[self.get_column_index('locality')]) is not None:
            self.__location_count += 1
        elif row[self.get_column_index('address')] \
                and location_regex.search(row[self.get_column_index('address')]) is not None:
            self.__location_count += 1

    """ Populate a dictionary with practice_code as key and postcode as values.
        This will be useful for future lookup.
    """
    def __populate_practice_code_to_postcode(self, row):
        self.__practice_code_to_postcode[row[self.get_column_index('practice_code')]]\
            = row[self.get_column_index('postcode')]

    def get_postcode_for_practice(self, practice_code):
        if len(self.__practice_code_to_postcode) == 0:
            raise ValueError('practice_code_to_postcode dictionary is not initialised!')

        return self.__practice_code_to_postcode.get(practice_code, None)

    def get_location_count(self):
        return self.__location_count

    def get_practice_code_to_postcode_count(self):
        return len(self.__practice_code_to_postcode)

    def write_output_to_file(self):
        f = open(self.get_output_file(), 'w')
        f.write('Number of practices in London: ' + str(self.get_location_count()) + '\n\n')

from FileReader.FileReader import FileReader
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
        self.__populate_practice_code_to_postcode(row)

        if self.__location_to_search is None:
            return
        else:
            self.__count_locations(row)

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

    def __populate_practice_code_to_postcode(self, row):
        self.__practice_code_to_postcode[row[self.get_column_index('practice_code')]]\
            = row[self.get_column_index('postcode')]

    def get_postcode_for_practice(self, practice_code):
        if len(self.__practice_code_to_postcode) == 0:
            raise ValueError('practice_code_to_postcode dictionary is not initialised!')

        return self.__practice_code_to_postcode.get(practice_code, None)

    def get_location_count(self):
        return self.__location_count

    def write_output_to_file(self):
        pass

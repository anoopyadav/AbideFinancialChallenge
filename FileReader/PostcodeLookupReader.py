from FileReader.FileReader import FileReader


class PostcodeLookupReader(FileReader):
    def __init__(self, header, filename):
        FileReader.__init__(self, header, filename)
        self.__postcode_to_region_lookup = {}
        self.__regions = []

    def process_file(self, row):
        self.__populate_postcode_to_region_lookup(row)

    """ Populates a dictionary with the outer postcode as key and region as values
    """
    def __populate_postcode_to_region_lookup(self, row):
        outer_postcode = row['Postcode 3'].split(' ')[0]
        region = row['Region Name']

        if region and region is not '':
            self.__postcode_to_region_lookup[outer_postcode] = region
            if region not in self.__regions:
                self.__regions.append(region)

    def get_total_postcodes(self):
        return len(self.__postcode_to_region_lookup)

    """ Getter method to query region from postcode
    """
    def get_region_from_postcode(self, postcode):
        outer_postcode = postcode.split(' ')[0]
        if outer_postcode in self.__postcode_to_region_lookup.keys():
            return self.__postcode_to_region_lookup[outer_postcode]
        else:
            raise KeyError('The region for this postcode is not available.')

    def get_regions_list(self):
        return self.__regions

    def write_output_to_file(self):
        pass

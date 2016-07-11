from time import time
import sys
import getopt
from FileReader.PostcodeLookupReader import PostcodeLookupReader
from FileReader.PrescriptionFileReader import PrescriptionFileReader
from FileReader.AddressFileReader import AddressFileReader


def print_usage():
    print('Usage: python3 main.py -c <Postcode_File_Name> -a <Address_File_Name> -p <Prescription_file_name>')
    print('The file names should be fully qualified paths if not in current directory.')


def parse_args(args):
    postcode_file = ''
    address_file = ''
    prescription_file = ''

    try:
        opts, args = getopt.getopt(args, "hc:a:p:")
    except getopt.GetoptError:
        print_usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt is '-h':
            print_usage()
            sys.exit(1)
        elif opt in '-c':
            postcode_file = arg
        elif opt in '-p':
            prescription_file = arg
        elif opt in '-a':
            address_file = arg

    if postcode_file is '' or prescription_file is '' or address_file is '':
        print_usage()
        sys.exit(1)
    else:
        return [postcode_file, address_file, prescription_file]


def main():
    start_time = time()
    postcode_file, address_file, prescription_file = parse_args(sys.argv[1:])

    process_postcodes_file = PostcodeLookupReader(postcode_file, None)
    process_postcodes_file.populate_csv_header(None)
    process_postcodes_file.set_iteration_method('lazy_read')

    for row in process_postcodes_file:
        process_postcodes_file.process_file(row)

    header = ("Period", "practice_code", "practice_name", "practice_building",
              "address", "locality", "town", "postcode")

    process_address_file = AddressFileReader(address_file, header)
    process_address_file.set_iteration_method('chunky_lazy_read')

    process_address_file.set_location_to_search('LONDON')

    for row in process_address_file:
        process_address_file.process_file(row)

    process_address_file.write_output_to_file()

    process_prescription_file = PrescriptionFileReader(prescription_file, None)
    process_prescription_file.set_iteration_method('lazy_sequential_read')
    process_prescription_file.set_practice_code_to_postcode_lookup(process_address_file.get_postcode_for_practice)
    process_prescription_file.set_postcode_to_region_lookup(process_postcodes_file.get_region_from_postcode)
    process_prescription_file.setup_region_based_dictionaries(process_postcodes_file.get_regions_list())

    for row in process_prescription_file:
        process_prescription_file.process_file(row)

    end_time = time()

    print('Results written to ' + process_prescription_file.get_output_file())
    print('Execution time: ' + str(end_time - start_time))

    process_prescription_file.write_output_to_file()

if __name__ == "__main__":
    main()

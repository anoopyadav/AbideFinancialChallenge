from FileReader import FileReader
import re
import locale


class PrescriptionFileReader(FileReader):
    def __init__(self, filename, header):
        FileReader.__init__(self, filename, header)

        """ Keep track of number of locations and cost of prescriptions
        """
        self.__prescription_location_count = 0
        self.__prescription_total_cost = 0.0

        """ Plugin a method to lookup postcode from practice code
            Maintain a dictionary with outer postcodes as keys and actual spend as values
        """
        self.__postcode_lookup_method = None
        self.__post_codes_by_actual_spend = {}

        """ Plugin a method to lookup region from postcode
            Compile a regex to look for a particular prescription
            Track the cost and prescription count nationally
        """
        self.__region_lookup_method = None
        self.__average_price_per_region = {}
        self.__prescription_count_by_region = {}
        self.__prescription_regex = re.compile(r'^Flucloxacillin\s*\w*')
        self.__cost_per_prescription = 0
        self.__prescription_count = 0

        """ Keep track of various anti-depressant prescriptions
        """
        self.__antidepressant_prescriptions = 'Fluoxetine Hydrochloride Citalopram Hydrobromide Paroxetine' \
                                              ' Hydrochloride Sertraline Hydrochloride Duloxetine Hydrochloride' \
                                              ' Venlafaxine Mirtazapine'
        self.__antidepressant_prescription_count_by_region = {}

    def process_file(self, row):
        self.__calculate_average_cost(row)
        self.__update_actual_spend_by_post_code(row)
        self.__update_per_region_data(row)
        if len(self.__average_price_per_region) is not 0:
            self.__update_cost_per_prescription(row)
        if len(self.__antidepressant_prescription_count_by_region) is not 0:
            self.__update_antidepressant_count_by_region(row)

    """ Q2. Increment the location count and total cost of matching prescription
    """
    def __calculate_average_cost(self, row):
        if 'Peppermint Oil' in row[self.get_column_index('BNF NAME')]:
            self.__prescription_location_count += 1
            self.__prescription_total_cost += float(row[self.column_to_index['ACT COST']])

    def get_average_cost_of_prescription(self):
        if self.__prescription_location_count is 0 or self.__prescription_total_cost is 0.0:
            raise ValueError('Prescription information is not populated!')

        return round(self.__prescription_total_cost / self.__prescription_location_count, 2)

    """ Q3. Populate a dictionary with postcodes as keys and total actual spend as values
    """
    def __update_actual_spend_by_post_code(self, row):
        if self.__postcode_lookup_method is None:
            raise ValueError('postcode_lookup_method not set.')

        practice_postcode = self.__postcode_lookup_method(row[self.column_to_index['PRACTICE']])
        if practice_postcode is not None:
            self.__post_codes_by_actual_spend.setdefault(practice_postcode, 0.0)
            self.__post_codes_by_actual_spend[practice_postcode] += float(row[self.column_to_index['ACT COST']])

    def set_practice_code_to_postcode_lookup(self, lookup_method):
        self.__postcode_lookup_method = lookup_method

    def get_top_5_spenders(self):
        if len(self.__post_codes_by_actual_spend) is 0:
            return None

        top_spenders = []

        for i in range(5):
            index = max(self.__post_codes_by_actual_spend, key=self.__post_codes_by_actual_spend.get)
            top_spenders.append((index, round(self.__post_codes_by_actual_spend.pop(index), 2)))

        return top_spenders

    """ Q4. Populate a dictionary with region as key and average prescription price as value
            Populate a dictionary with region as key and total prescriptions as value
    """
    def __update_per_region_data(self, row):
        if self.__prescription_regex.search(row[self.column_to_index['BNF NAME']]) is None:
            return
        if self.__average_price_per_region is None:
            raise ValueError('average_price_per_region dict not set up.')

        postcode = self.__postcode_lookup_method(row[self.column_to_index['PRACTICE']])
        if postcode is not None:
            region = self.__region_lookup_method(postcode)

            self.__average_price_per_region[region] += \
                float(row[self.column_to_index['ACT COST']]) / float(row[self.column_to_index['ITEMS']])

            self.__prescription_count_by_region[region] += 1

    def set_postcode_to_region_lookup(self, lookup_method):
        self.__region_lookup_method = lookup_method

    def setup_region_based_dictionaries(self, regions):
        for region in regions:
            self.__average_price_per_region.setdefault(region, 0)
            self.__prescription_count_by_region.setdefault(region, 0)
            self.__antidepressant_prescription_count_by_region.setdefault(region, 0)

    def get_average_price_by_region(self):
        price_by_region_dict = {}

        for region in self.__average_price_per_region.keys():
            if region not in price_by_region_dict.keys():
                price_by_region_dict.setdefault(region, 0)

            try:
                price_by_region_dict[region] = \
                    round(self.__average_price_per_region[region] / self.__prescription_count_by_region[region], 2)
            except ZeroDivisionError:
                price_by_region_dict[region] = 0.0

        return price_by_region_dict

    """ Calculate the average value of a prescription across the nation
    """
    def __update_cost_per_prescription(self, row):
        if self.__prescription_regex.search(row[self.column_to_index['BNF NAME']]) is None:
            return

        if self.__is_number(row[self.column_to_index['ACT COST']]):
            if not self.__is_number(row[self.column_to_index['ITEMS']]):
                return
            self.__cost_per_prescription += \
                float(row[self.column_to_index['ACT COST']]) / float(row[self.column_to_index['ITEMS']])
            self.__prescription_count += 1

    def get_cost_per_prescription(self):
        if self.__prescription_count is 0:
            raise ValueError('cost_per_prescription information is not populated')
        return round(self.__cost_per_prescription / self.__prescription_count, 2)

    """ Q5. Populate a dictionary with region as key and total prescriptions as value
    """
    def __update_antidepressant_count_by_region(self, row):
        prescription_name = row[self.column_to_index['BNF NAME']].rstrip()
        if prescription_name not in self.__antidepressant_prescriptions:
            return

        postcode = self.__postcode_lookup_method(row[self.column_to_index['PRACTICE']])
        if postcode is not None:
            region = self.__region_lookup_method(postcode)

            self.__antidepressant_prescription_count_by_region[region] += int(row[self.column_to_index['ITEMS']])

    def get_antidepressant_count_by_region(self):
        return self.__antidepressant_prescription_count_by_region

    """ Utility Method to determine if the supplied string is a float value
    """
    @staticmethod
    def __is_number(string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    """ Utility method to format number as currency
    """
    @staticmethod
    def __format_as_currency(value):
        currency = "%.2f" % value
        return currency

    def write_output_to_file(self):
        locale.setlocale(locale.LC_ALL, '')
        f = open(self.get_output_file(), 'a')
        f.write('Average cost of Peppermint Oil: £' + str(
            self.__format_as_currency(round(self.get_average_cost_of_prescription(), 2))) + '\n')

        f.write('\nTop 5 postcodes by Actual Spend:\n')
        for row in self.get_top_5_spenders():
            f.write('Postcode ' + str(row[0]) + ' spent £' + str("{:,}".format(round(row[1], 2))) + '\n')

        f.write('\nSpending by region per prescription of Flucloxacillin:\n')
        national_mean = round(self.get_cost_per_prescription(), 2)
        for key, value in self.get_average_price_by_region().items():
            f.write('The average cost in the ' + str(key) + ' region was £')
            f.write(str(self.__format_as_currency(round(value, 2))) + '.')
            difference = round(national_mean - round(value, 2), 2)
            f.write(' This was £' + str(self.__format_as_currency(abs(difference))))
            if difference > 0:
                f.write(' less than ')
            else:
                f.write(' greater than ')
            f.write('the national mean.\n')

        f.write('\nNational Mean: £' + str(self.__format_as_currency(round(self.get_cost_per_prescription(), 2))) + '\n')

        f.write('\nAntidepressant prescriptions by region:\n')
        for key, value in self.get_antidepressant_count_by_region().items():
            f.write('The total number of anti-depressant prescriptions in the ' + str(key) + ' region were ')
            f.write(str("{:,}".format(value)) + '.\n')

        f.close()

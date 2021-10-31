import datetime
import utils
import math
import numpy as np

def process( startyear  = 2016,
             startmonth = 10,
             endyear    = 2016,
             endmonth   = 10):
    ''' Processes data from FOIL201*/trip_data_*.csv into compressed .npz files.

    Returns nothing. Processes month-by-month.

    # Arguments:
        startyear, startmonth, endyear, endmonth: Integers representing
            the files to start and end processing on.
        width, height: Integers representing the resolution of the grid
            that trips are mapped to.
        n: Integer, the number of time slots per hour.
        V: Boolean; if True, print extra information to console.
        restart: Boolean; if True, don't save the processed data for
            the first year, month.
    '''
    # List of year-month dates to iterate over.
    dates = utils.generate_dates(startyear, startmonth, endyear, endmonth)

    # Generate empty arrays for the 'next month' of data.

    total_count = 0
    delta_counts = [0] * 7
    invalid_count = 0    # Entries that are parsable, but are not a valid trip
    unparsable_count = 0 # Entries that raise an error on parsing
    valid_count = 0
    for (year, month) in dates:

        load_filename = "./data.nosync/yellow_tripdata_"+f"{year:04}"+"-"+f"{month:02}"+".csv"
        print(load_filename)
        # load_filename = "./demoData.text"

        with open(load_filename, "r", encoding='UTF-8') as read_f:
            read_f.readline() # Skip header
            lines = read_f.readlines()

            for line in lines:
                total_count += 1
                try:
                    entry = utils.process_entry(line=line)
                    if utils.check_valid(entry=entry, year=year, month=month):
                        valid_count += 1
                        if entry['deltat'] <= 0:
                            delta_counts[0] += 1
                        elif entry['deltat'] <= 3600:
                            delta_counts[math.ceil(entry['deltat'] / 600.0) - 1] += 1
                        else:
                            delta_counts[6] += 1
                    else:
                        invalid_count += 1
                except:
                    unparsable_count += 1
                    print("  ERROR - could not parse line")
        print("Finish ", load_filename)
        print("Total Count: ", total_count)
        print("Valid Count: ", valid_count)
        print("Invalid Count: ", invalid_count)
        print("Unparsable Count: ", unparsable_count)
        print("Distribute Map: ", delta_counts)

    print("$$$$$$$$$$$")
    print("Total Count: ", total_count)
    print("Valid Count: ", valid_count)
    print("Invalid Count: ", invalid_count)
    print("Unparsable Count: ", unparsable_count)
    print("Distribute Map: ", delta_counts)


if __name__ == '__main__':
    # Parse arguments
    process( startyear  = 2015,
             startmonth = 1,
             endyear    = 2015,
             endmonth   = 12)

import datetime
import utils
import numpy as np

EMPTY_ID = "EMPTY_ID"

def print_time():
    ''' Print the current time. '''
    print("  Timestamp:", datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"))

def process( startyear  = 2016,
             startmonth = 10,
             endyear    = 2016,
             endmonth   = 10,
             width      = 10,
             height     = 20,
             n          = 4,
             V          = False,
             restart    = False ):
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

    for (year, month) in dates:
        invalid_count = 0    # Entries that are parsable, but are not a valid trip
        unparsable_count = 0 # Entries that raise an error on parsing
        line_number = 0

        load_filename = "./data.nosync/yellow_tripdata_"+f"{year:04}"+"-"+f"{month:02}"+".csv"
        print(load_filename)
        # load_filename = "./demoData.text"

        vdata = utils.gen_empty_vdata(year=year, month =month, w=width, h=height, n=n)
        fdata = utils.gen_empty_fdata(year=year, month =month, w=width, h=height, n=n)

        if V:
            print("Starting on",year,month)
            print_time()

        with open(load_filename, "r", encoding='UTF-8') as read_f:
            read_f.readline() # Skip header
            lines = read_f.readlines()

            for line in lines:
                line_number += 1
                if V and ((line_number % 1000000) == 0):
                    print("    Line", line_number)
                # try:
                    # This is where the processing happens.
                entry = utils.process_entry(line=line, n=n)
                if utils.check_valid(entry=entry, year=year, month=month):
                    utils.update_data(entry=entry,
                                    vdata=vdata,
                                    fdata=fdata,
                                    w=width,
                                    h=height,
                                    n=n)
                else:
                    invalid_count += 1
                # except:
                    # unparsable_count += 1
                    # print("  ERROR - could not parse line", line_number)
                if line_number % 300000 == 0:
                    print(load_filename + ": ", line_number)

        print("Finish ", load_filename)

        save_filename_date = str(year)+"-"+str(month).zfill(2)+"-"+str(60/n)
        np.savez_compressed(save_filename_date + ".npz", vdata = vdata, fdata = fdata, errors = np.array([invalid_count, unparsable_count]))

    if V:
        print("All finished!")
        print_time()

if __name__ == '__main__':
    # Parse arguments
    process( startyear  = 2015,
             startmonth = 1,
             endyear    = 2015,
             endmonth   = 12,
             width      = 16,
             height     = 16,
             n          = 1,
             V          = False,
             restart    = False)
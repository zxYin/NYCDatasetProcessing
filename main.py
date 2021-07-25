import datetime
import argparse
import utils
import numpy as np

EMPTY_ID = "EMPTY_ID"

def print_time():
    ''' Print the current time. '''
    print("  Timestamp:", datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"))

def get_next(year, month):
    ''' Get the (year, month) combo following the provided (year, month)'''
    if month == 12:
        return (year + 1, 1)
    else:
        return (year, month + 1)

def process( startyear  = 2016,
             startmonth = 10,
             endyear    = 2016,
             endmonth   = 11,
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
    vdata_next_mo = utils.gen_empty_vdata(year=startyear, month=startmonth, w=width, h=height, n=n)
    fdata_next_mo = utils.gen_empty_fdata(year=startyear, month=startmonth, w=width, h=height, n=n)

    for (year, month) in dates:
        trips = np.zeros((2, 2)) # Statistical info about the trips this month. (See README)
        invalid_count = 0    # Entries that are parsable, but are not a valid trip
        unparsable_count = 0 # Entries that raise an error on parsing
        line_number = 0

        # Shift the vdata, fdata that are in-focus to this month
        vdata = vdata_next_mo
        fdata = fdata_next_mo

        # Generate new, empty 'next-month' arrays
        #   (For trips that cross the boundary, e.g. 2-28 at 11:59 to 3:01 at 0:02
        next_year, next_month = get_next(year=year, month=month)
        vdata_next_mo = utils.gen_empty_vdata(year=next_year, month=next_month, w=width, h=height, n=n)
        fdata_next_mo = utils.gen_empty_fdata(year=next_year, month=next_month, w=width, h=height, n=n)

        # load_filename = "../decompressed/FOIL"+str(year)+"/trip_data_"+str(month)+".csv"
        load_filename = "./demoData.text"

        if V:
            print("Starting on",year,month)
            print_time()

        with open(load_filename, "r", encoding='UTF-8') as read_f:
            read_f.readline() # Skip header
            lines = read_f.readlines()
            start_entry = {"id": EMPTY_ID}

            for line in lines:
                line_number += 1
                if V and ((line_number % 1000000) == 0):
                    print("    Line", line_number)
                try:
                    # This is where the processing happens.
                    (entry, is_next) = utils.process_entry(line=line, start_entry=start_entry, n=n, is_last=(line is lines[-1]))
                    if is_next:
                        if not start_entry["id"] == EMPTY_ID:
                            if utils.check_valid(entry=entry, start_entry=start_entry, year=year, month=month):
                                utils.update_data(entry=entry,
                                                start_entry=start_entry,
                                                vdata=vdata,
                                                fdata=fdata,
                                                vdata_next_mo=vdata_next_mo,
                                                fdata_next_mo=fdata_next_mo,
                                                trips=trips,
                                                w=width,
                                                h=height,
                                                n=n)
                            else:
                                invalid_count += 1

                        start_entry = entry
                except:
                    unparsable_count += 1
                    print("  ERROR - could not parse line", line_number)

        print("    Line", line_number)

        if restart and year == startyear and month == startmonth:
            if V:
                print("Not saving for", year, month, "due to restart flag.")
        else:
            # Save the file
            save_filename_date = str(year)+"-"+str(month).zfill(2)

            if V:
                print("Saving",save_filename_date)
                print_time()
            np.savez_compressed(save_filename_date + "-data.npz", vdata = vdata, fdata = fdata, trips = trips, errors = np.array([invalid_count, unparsable_count]))

    if V:
        print("All finished!")
        print_time()

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description="NYC Dataset processing")
    parser.add_argument("--startyear", "-sy",
                        help="Year to start processing from. Default 2010",
                        type=int, nargs=1)
    parser.add_argument("--startmonth", "-sm",
                        help="Month to start processing from. Default 1.",
                        type=int, nargs=1)
    parser.add_argument("--endyear", "-ey",
                        help="Year to finish processing (inclusive). Default 2013.",
                        type=int, nargs=1)
    parser.add_argument("--endmonth", "-em",
                        help="Month to finish processing (inclusive). Default 12.",
                        type=int, nargs=1)
    parser.add_argument("--width", "-x",
                        help="Width of grid (default 10)",
                        type=int, nargs=1)
    parser.add_argument("--height", "-y",
                        help="Width of grid (default 20)",
                        type=int, nargs=1)
    parser.add_argument("--nslotsperhour", "-n",
                        help="Discretize time into n slots per hour. Must be integer divisor of 60. (Default 4)",
                        type=int, nargs=1)
    parser.add_argument("--verbose", "-v",
                        help="",
                        action="store_true")
    parser.add_argument("--restart", "-r",
                        help="Does not save the first month of data. Used to restart code when it crashes. (E.g. 2010 08 can have trips starting in 2010 07 that end in 2010 08)",
                        action="store_true")

    args = parser.parse_args()

    # Defaults
    startyear   = 2016  if args.startyear   is None else args.startyear[0]
    startmonth  = 10     if args.startmonth  is None else args.startmonth[0]
    endyear     = 2016  if args.endyear     is None else args.endyear[0]
    endmonth    = 11    if args.endmonth    is None else args.endmonth[0]
    width       = 10    if args.width       is None else args.width[0]
    height      = 20    if args.height      is None else args.height[0]
    n           = 4     if args.nslotsperhour is None else args.nslotsperhour[0]
    V = args.verbose
    restart = args.restart

    print("NYCDataProcessing/main.py started.")

    if V:
        print_time()
        print("Running with arguments:")
        print("  Verbose")
        print("  ",startyear, ", ", startmonth, " to ", endyear, ", ", endmonth, ".",sep="")
        print("  With",n,"samples year hour.")
        print("  On a grid of size ",width,"x",height,".", sep="")

    # Begin processing data
    process( startyear  = startyear,
             startmonth = startmonth,
             endyear    = endyear,
             endmonth   = endmonth,
             width      = width,
             height     = height,
             n          = n,
             V          = V,
             restart    = restart)


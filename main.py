import datetime
import argparse
import utils
import numpy as np

def print_time():
    ''' Print the current time. '''
    print("  Timestamp:", datetime.datetime.now().strftime("%Y/%m/%d, %H:%M:%S"))

def get_next(year, month):
    ''' Get the (year, month) combo following the provided (year, month)'''
    if month == 12:
        return (year + 1, 1)
    else:
        return (year, month + 1)

def process( startyear  = 2010,
             startmonth = 1,
             endyear    = 2013,
             endmonth   = 12,
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
    flow_data_next_mo = utils.gen_empty_flow_data(year=startyear, month=startmonth, w=width, h=height, n=n)
    transition_data_next_mo = utils.gen_empty_transition_data(year=startyear, month=startmonth, w=width, h=height, n=n)
    od_data_next_mo = utils.gen_empty_od_data(year=startyear, month=startmonth, w=width, h=height, n=n)
    
    for (year, month) in dates:
        invalid_count = 0    # Entries that are parsable, but are not a valid trip
        unparsable_count = 0 # Entries that raise an error on parsing
        line_number = 0
        
        # Shift the flow_data, transition_data that are in-focus to this month
        flow_data = flow_data_next_mo
        transition_data = transition_data_next_mo
        od_data = od_data_next_mo
        
        # Generate new, empty 'next-month' arrays
        #   (For trips that cross the boundary, e.g. 2-28 at 11:59 to 3:01 at 0:02
        next_year, next_month = get_next(year=year, month=month)
        flow_data_next_mo = utils.gen_empty_flow_data(year=next_year, month=next_month, w=width, h=height, n=n)
        transition_data_next_mo = utils.gen_empty_transition_data(year=next_year, month=next_month, w=width, h=height, n=n)
        od_data_next_mo = utils.gen_empty_od_data(year=next_year, month=next_month, w=width, h=height, n=n)
        
        # load_filename = "../decompressed/FOIL"+str(year)+"/trip_data_"+str(month)+".csv"
        load_filename = "example.csv"
        
        if V:
            print("Starting on",year,month)
            print_time()
        
        with open(load_filename, "r") as read_f:
            read_f.readline() # Skip header
            for line in read_f:
                line_number += 1
                if V and ((line_number % 1000000) == 0):
                    print("    Line", line_number)
                try:
                    # This is where the processing happens.
                    entry = utils.process_entry(line=line, n=n)
                    if utils.check_valid(entry=entry, year=year, month=month):
                        utils.update_data(entry=entry,
                                            flow_data=flow_data,
                                            transition_data=transition_data,
                                            od_data=od_data,
                                            flow_data_next_mo=flow_data_next_mo,
                                            w=width,
                                            h=height,
                                            n=n)
                    else:
                        invalid_count += 1
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
            np.savez_compressed(save_filename_date + "-data.npz", flow_data = flow_data, transition_data = transition_data, od_data = od_data, errors = np.array([invalid_count, unparsable_count]))
        
    if V:
        print("All finished!")
        print_time()

if __name__ == '__main__':

  
    # Begin processing data
    process( startyear  = 2011,
             startmonth = 1,
             endyear    = 2014,
             endmonth   = 12,
             width      = 16,
             height     = 16,
             n          = 24,
             V          = False,
             restart    = False)
    

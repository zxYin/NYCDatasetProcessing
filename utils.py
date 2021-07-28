''' A number of functions used in main.py to process the data.'''

import regex as re
from datetime import datetime
from GPSUtils import pgps_to_xy, gps_distance
from math import floor
import numpy as np

def get_t(hour, minute, n=4):
    ''' Returns the sample numbr given the day, hour, and minute.
    Day is 1-indexed, hour and minute is 0 indexed.'''
    return floor( ((hour*60) + minute)/floor((60/n)) )

def process_entry(line, start_entry, n=4, is_last=False):
    ''' Given string line from the .csv,
        return a dict representing that entry. '''
    entry_strings = line.strip().replace("[", "").replace("]", "").replace("'", "").split(",")
    
    id = entry_strings[0].strip() + "_" + entry_strings[1].strip()

    if id == start_entry['id'] and not is_last:
        return ({}, False)

    # Parse the times using datetime
    timestamp = int(entry_strings[2].strip())
    time = datetime.fromtimestamp(timestamp)
    
    # Starting and ending GPS coordinates
    lon = float(entry_strings[3].strip())
    lat = float(entry_strings[4].strip())
    
    # Starting and ending grid coordinates and straight-line (l2) distance
    # Warning: Uses prebaked Manhattan values.
    x, y = pgps_to_xy(lon, lat)
    # Get the starting and ending times
    t = get_t( hour   = time.hour,
               minute = time.minute,
               n      = n)
    
    # Convention:
    # 's' stands for 'start', 'e' stands for 'end',
    # 'x' and 'y' stand for x/y coordinates respectively,
    # 't' stands for time slot or seconds.
    entry = {
        'id': id,
        'lon': lon,
        'lat': lat,
        'x' : x,
        'y' : y,
        't' : t,
        'timestamp': timestamp,
        'year'  : time.year,
        'month' : time.month,
        'day'   : time.day,
        'hour'  : time.hour,
        'min'   : time.minute,
        'sec'   : time.second,
    }
    
    return (entry, True)

def check_valid(entry, start_entry, year, month, day, min_time=59, max_speed=36, min_distance=100):
    ''' Ensure an entry meets these following rules:
    1. Starts during the same year/month as the provided parameters.
    2. l2 distance is at least min_distance  (100m)
    3. Trip lasts at least min_time (59s)
    4. Trip speed straight line distance doesn't exceed max speed (36m/s)
    
    Returns 'True' if valid, 'False' if not.
    '''
    if not start_entry['year']  == year:   return False
    if not start_entry['month'] == month:  return False
    if not start_entry['day'] == day:  return False

    l2distance = gps_distance((start_entry['lat'], start_entry['lon']), (entry['lat'], entry['lon']))
    if not l2distance >= min_distance: return False

    deltat = abs(entry['timestamp'] - start_entry['timestamp'])
    if not deltat >= min_time: return False

    if not (l2distance / deltat) <= max_speed: return False

    return True
    

def generate_dates(start_year = 2010, start_month = 1, start_day = 1, end_year = 2013, end_month = 12, end_day = 30):
    ''' Returns a list of (year, month) tuples from
        (start_year, start_month) to (end_year, end_month), inclusive.'''
    year = start_year
    month = start_month
    day = start_day
    dates = []
    while True:
        days = no_days_in_mo(year, month)
        while not (year, month, day) == (end_year, end_month, end_day):
            if day <= days:
                dates.append((year, month, day))
                day += 1
            else:
                day = 1
                break
        if (year, month, day) == (end_year, end_month, end_day):
            break

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    
    return dates

def no_days_in_mo(year, month):
    ''' Return int: the number of days in a given year-month combo.'''
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    elif month in (4, 6, 9, 11):
        return 30
    else: # month = 2 (February)
        if year % 4 != 0:
            return 28
        elif year % 100 != 0:
            return 29
        elif year % 400 != 0:
            return 28
        else:
            return 29

def gen_empty_vdata(w=10, h=20, n=4):
    ''' Return an all-zero 'vdata' numpy array.
    Used to store volume data, as per the STDN.'''
    return np.zeros((24 * n, w, h, 2), dtype=np.int16)

def gen_empty_fdata(w=10, h=20, n=4):
    ''' Return an all-zero 'fdata' numpy array.
    Used to store flow data, as per the STDN.'''
    return np.zeros((2, 24 * n, w, h, w, h), dtype=np.int16)

def update_data(entry, start_entry, vdata, fdata, vdata_next_mo, fdata_next_mo, trips, w=10, h=20, n=4):
    ''' Updates the given numpy arrays with data from the provided entry.
        Returns nothing.
    
    # Arguments:
        entry: Dictionary providing pertinent values for a given trip.
        vdata, fdata: Numpy arrays representing the volume and flow
            data for a given month.
        vdata_next_mo, fdata_next_mo: Numpy array representing the
            volume and flow data for the next month. (Useful for those
            trips that start in this month and end in the next.)
        trips: Numpy array that stores statistical information about
            the total number of trips and passengers in the month.
        w, h: Ints; width and height of the grud
        n: Number of timeslots per hour.
    '''
    # starts_inside, ends_inside: Booleans.
    # True if the trip starts within Manhattan, false otherwise
    start_inside = (0 <= start_entry['x'] <= 1) and (0 <= start_entry['y'] <= 1)
    end_inside = (0 <= entry['x'] <= 1) and (0 <= entry['y'] <= 1)
    
    starts_and_ends_in_same_day = (start_entry['day'] == entry['day'])

    # Variable names:
    #   s/e stands for start/end, g stands for grid, x/y are coordinates
    sgx = floor(start_entry['x']*w) #start-x, mapped to grid coordinates
    sgy = floor(start_entry['y']*h) #start-y, mapped to grid coordinates
    egx = floor(entry['x']*w) #end-x, mapped to grid coordinates
    egy = floor(entry['y']*h) #end-y, mapped to grid coordinates
    
    # Trips is a (2,2,2) array: [starts in/outside, ends in/side, passenger/trip count]
    trips[int(not start_inside), int(not end_inside)] += 1
    
    # Data-update rules below come from the definition of volume and flow, per the STDN paper.
    # Data shape is taken from the shape used in the original STDN code.
    #   Note: Here, Passenger count and trip count are recorded separately.
    if start_inside:
        # Update volume data for the start of the trip
        vdata[start_entry['t'], sgx, sgy, 0] += 1
        
        if end_inside:
            # Update volume data only if the trip starts and ends within Manhattan.
            if start_entry['t'] == entry['t']:
                # st == et, so we don't need to check if et is in the
                #    next month.
                fdata[0, entry['t'], sgx, sgy, egx, egy] += 1
            else:
                if starts_and_ends_in_same_month:
                    fdata[1, entry['t'], sgx, sgy, egx, egy] += 1
                else: # End time crosses over to the next month
                    fdata_next_mo[1, entry['t'], sgx, sgy, egx, egy] += 1

    if end_inside:
        # Update volume data for the end of the trip.
        if starts_and_ends_in_same_day:
            vdata[entry['t'], egx, egy, 1] += 1
        
        else: # Ends during the next month, so use the array representing the next month
            vdata_next_mo[entry['t'], egx, egy, 1] += 1
            
    # Returns nothing - numpy arrays are updated by reference.

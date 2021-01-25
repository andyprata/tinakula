import time
from datetime import datetime, timedelta
import numpy as np
import glob
import xarray as xr


start = time.process_time()

# --- TINAKULA 2017 --- #
vname = 'tinakula'
vlon, vlat = 165.804, -10.386
path_data = '/media/aprata/TOSHIBA EXT/satellite/tinakula/netcdf/'
start_time = datetime(2017, 10, 20, 19)
end_time = datetime(2017, 10, 21, 5)
time_interval_mins = 10
path_out = '/home/aprata/satellite/volcanoes/tinakula/himawari8/proc/'
# ------------------ #

# crop data based on +- 2.5 deg lat/lon centered on volcano
extent = [vlon-2.5, vlon+2.5, vlat-2.5, vlat+2.5]
# time step in minutes
dt = 10.
time_diff = end_time - start_time
time_minutes = time_diff.total_seconds()/60.
nt = int(time_minutes/dt) + 1
get_geoloc = True
print("PROCESSING " + str(nt) + " TIME STEPS...")
for nti in range(nt):
    print("--- READING IN SATELLITE DATA ---")
    current_time = start_time + timedelta(minutes=nti*dt)
    hour_minute = current_time.strftime("%H%M")
    current_time_str = current_time.strftime("%Y%m%d_%H%M")
    print("Processing: " + current_time_str)
    if hour_minute == '0240' or hour_minute == '1440':
        print("House keeping time! Skipping...")
    else:
        files = glob.glob(path_data + '*%s*.nc' % (current_time_str))
        if len(files) == 0:
            print("File(s) not found! Skipping...")
        else:
            with xr.open_dataset(files[0]) as ds:
                lons_fd = ds.longitude.values
                lats_fd = ds.latitude.values
                T_69_fd = ds.tbb_09.values
                T_73_fd = ds.tbb_10.values
                T_86_fd = ds.tbb_11.values
                T_10_fd = ds.tbb_13.values
                T_11_fd = ds.tbb_14.values
                T_12_fd = ds.tbb_15.values
                satzen_fd = ds.SAZ.values
            # subset data
            lon_inds = np.where((lons_fd > extent[0]) & (lons_fd < extent[1]))[0]
            lat_inds = np.where((lats_fd > extent[2]) & (lats_fd < extent[3]))[0]
            T69 = T_69_fd[np.ix_(lat_inds, lon_inds)]
            T73 = T_73_fd[np.ix_(lat_inds, lon_inds)]
            T86 = T_86_fd[np.ix_(lat_inds, lon_inds)]
            T10 = T_10_fd[np.ix_(lat_inds, lon_inds)]
            T11 = T_11_fd[np.ix_(lat_inds, lon_inds)]
            T12 = T_12_fd[np.ix_(lat_inds, lon_inds)]

            # Save to numpy compressed file
            print("--- WRITING TO COMPRESSED FILE ---")
            np.savez_compressed(path_out + current_time_str, T69=T69, T73=T73, T87=T86, T11=T11, T12=T12)
            print("--- DONE ---")

            # write geolocation data (only once)
            if get_geoloc:
                lons_1d = lons_fd[lon_inds]
                lats_1d = lats_fd[lat_inds]
                lons, lats = np.meshgrid(lons_1d, lats_1d)
                satzen = satzen_fd[np.ix_(lat_inds, lon_inds)]
                np.savez_compressed(path_out + 'geoloc', lons=lons, lats=lats, satzen=satzen)
                get_geoloc = False
print("--- DONE ---")

# Print runtime
end = time.process_time()
time_len = end - start
if time_len >= 60.0:
    print('--- RUNTIME = {} minutes ---'.format(time_len/60.))
else:
    print('--- RUNTIME = {} seconds ---'.format(time_len))

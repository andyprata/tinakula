# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import os
os.environ['PROJ_LIB'] = "/home/aprata/anaconda3/envs/satpy-env/share/proj"
import xarray as xr
import numpy as np
from datetime import datetime, timedelta
from matplotlib.path import Path
import geog
import shapely.geometry


def gen_polygon_circle(center_lon, center_lat, n_points, radius):
    # reference: https://gis.stackexchange.com/questions/268250/generating-polygon-representing-rough-100km-circle-around-latitude-longitude-poi
    import json
    p = shapely.geometry.Point([center_lon, center_lat])
    # n_points = 20
    angles = np.linspace(0, 360, n_points)
    polygon = geog.propagate(p, angles, radius)
    #print(json.dumps(shapely.geometry.mapping(shapely.geometry.Polygon(polygon))))
    return polygon


extent = [164, 167.5, -12, -9]

# single file
path_data = '/media/aprata/TOSHIBA EXT/satellite/tinakula/netcdf/'
start_time = datetime(2017, 10, 20, 19)
end_time = datetime(2017, 10, 21, 5)
time_interval_mins = 10

time_diff = end_time - start_time
time_minutes = time_diff.total_seconds()/60.
num = int(time_minutes/time_interval_mins) + 1

fn_out = 'tinakula_2017_minT_50km.txt'
datetime_list = []
mT_11_list = []
mlon_T_11_list = []
mlat_T_11_list = []


for i in range(num):
    current_time = start_time + timedelta(minutes=i*time_interval_mins)
    hour_minute = current_time.strftime("%H%M")
    current_time_str = current_time.strftime("%Y%m%d_%H%M")
    res = 'R21'
    fn_data = 'NC_H08_' + current_time_str + '_' + res + '_FLDK.06001_06001.nc'
    print(fn_data)

    try:
        ds = xr.open_dataset(path_data + fn_data)
    except:
        if hour_minute == '0240' and hour_minute == '1440':
            print("House keeping time! Skipping...")
        else:
            print("File not found! Skipping...")
    else:
        lons_arr = ds.longitude.values
        lats_arr = ds.latitude.values
        # band 11.20 microns
        T_112_arr = ds.tbb_14.values


        buffer = 0.1
        lon_inds = np.where((lons_arr > extent[0]-buffer) & (lons_arr < extent[1]+buffer))[0]
        lat_inds = np.where((lats_arr > extent[2]-buffer) & (lats_arr < extent[3]+buffer))[0]

        lons_subset = lons_arr[lon_inds]
        lats_subset = lats_arr[lat_inds]
        T_11_subset = T_112_arr[np.ix_(lat_inds, lon_inds)]

        # Tinakula location based on GVP
        vlon, vlat = 165.804, -10.386

        n_points = 100  # [number of points for circle]
        radius = 50. * 1000.  # [meters]
        polygon = gen_polygon_circle(vlon, vlat, n_points, radius)

        lons_subset, lats_subset = np.meshgrid(lons_subset, lats_subset)

        x, y = lons_subset.flatten(), lats_subset.flatten()
        points = np.vstack((x, y)).T
        p = Path(polygon)  # make a polygon
        grid = p.contains_points(points)
        mask = grid.reshape(lats_subset.shape)
        T_11_box = np.ma.array(T_11_subset, mask=mask == False)
        lons_box = np.ma.array(lons_subset, mask=mask == False)
        lats_box = np.ma.array(lats_subset, mask=mask == False)

        # get minimum brightness temperature within radius
        mlon, mlat = lons_box[T_11_box == T_11_box.min()][0], lats_box[T_11_box == T_11_box.min()][0]
        mT11 = T_11_box.min() - 273.15

        datetime_list.append(current_time_str)
        mT_11_list.append(mT11)
        mlon_T_11_list.append(mlon)
        mlat_T_11_list.append(mlat)
        ds.close()

# write data to file
path = '/home/aprata/satellite/tinakula/himawari8/data/timeseries/'
np.savetxt(path+fn_out, np.c_[datetime_list, mT_11_list, mlon_T_11_list, mlat_T_11_list], fmt="%s")

# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import os
os.environ['PROJ_LIB'] = "/home/aprata/anaconda3/envs/satpy-env/share/proj"
import xarray as xr
import numpy as np
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from matplotlib import rcParams
import matplotlib.font_manager as font_manager
from codecs import encode
from matplotlib.path import Path
import geog
import shapely.geometry


def mm2inch(mm):
    return mm*0.0393701


def act_to_list(act_file):
    # Read binary data
    with open(act_file, 'rb') as act:
        raw_data = act.read()

    # Convert it to hexadecimal values
    hex_data = encode(raw_data, 'hex')

    # Decode colors from hex to string and split it by 6 (because colors are #1c1c1c)
    colors = [hex_data[i:i+6].decode() for i in range(0, (len(hex_data)-8), 6)]

    # Add # to each item and filter empty items if there is a corrupted total_colors_count bit
    colors = ['#'+i for i in colors if len(i)]

    return colors


def gen_polygon_circle(center_lon, center_lat, n_points, radius):
    # reference: https://gis.stackexchange.com/questions/268250/generating-polygon-representing-rough-100km-circle-around-latitude-longitude-poi
    import json
    p = shapely.geometry.Point([center_lon, center_lat])
    # n_points = 20
    angles = np.linspace(0, 360, n_points)
    polygon = geog.propagate(p, angles, radius)
    #print(json.dumps(shapely.geometry.mapping(shapely.geometry.Polygon(polygon))))
    return polygon

# read in cloudsat lons/lats
# path_cldsat = '/home/aprata/satellite/krakatau/cloudsat/'
# fn_cldsat = "2018361055805_67456_CS_1B-CPR-FL_GRANULE_P_R04_E06.hdf"
# cldsat_lons, cldsat_lats = read_cldsat(path_cldsat, fn_cldsat)

# when font doesn't load try clearing cache: rm ~/.cache/matplotlib -rf
path = '/home/aprata/.fonts/HelveticaNeue.ttf'
prop = font_manager.FontProperties(fname=path)
rcParams['font.family'] = prop.get_name()
rcParams['font.weight'] = 'normal'
rcParams['font.size'] = 12
rcParams['mathtext.default'] = 'regular'

bg_col = 'white'
line_col = 'black'

plt.close('all')

axes = [0.08, 0.06, 0.81, 0.88]
axes_cb = [0.90, 0.06, 0.02, 0.88]

fig = plt.figure(figsize=(mm2inch(183.), mm2inch(247/2.)))


ax = fig.add_axes(axes)
ax_cb = fig.add_axes(axes_cb)

extent = [164, 167.5, -12, -9]

bm = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[2],
             urcrnrlon=extent[1], urcrnrlat=extent[3],
             epsg=3857, resolution='h', fix_aspect=False, ax=ax)

# single file
path_data = '/media/aprata/TOSHIBA EXT/satellite/tinakula/netcdf/'
start_time = datetime(2017, 10, 20, 19)
end_time = datetime(2017, 10, 21, 5)
time_interval_mins = 10

time_diff = end_time - start_time
time_minutes = time_diff.total_seconds()/60.
num = int(time_minutes/time_interval_mins) + 1

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
        # # band 6.95 microns
        # T_070_arr = ds.tbb_09.values
        # # band 7.35 microns
        # T_074_arr = ds.tbb_10.values
        # # band 8.60 microns
        # T_086_arr = ds.tbb_11.values
        # # band 10.45 microns
        # T_105_arr = ds.tbb_11.values
        # band 11.20 microns
        T_112_arr = ds.tbb_14.values
        # # band 12.35 microns
        # T_124_arr = ds.tbb_15.values

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

        # Plot data on the map
        print("Plotting data...")
        lon_step = 1
        lat_step = 1
        lw = 0.4
        vsize = 6
        bm.drawcoastlines(linewidth=lw, color=sns.xkcd_rgb[line_col])
        bm.drawcountries(linewidth=lw, color=sns.xkcd_rgb[line_col])
        bm.drawmeridians(np.arange(extent[0], extent[1] + lon_step, lon_step),
                         labels=[False, False, False, True], textcolor=line_col,
                         color='w', dashes=[1, 3], linewidth=0.1)
        bm.drawparallels(np.arange(extent[2], extent[3] + lat_step, lat_step),
                         labels=[True, False, False, False], textcolor=line_col,
                         color='w', dashes=[1, 3], linewidth=0.1)

        # Plot Tinakula based on GVP
        bm.plot(vlon, vlat, '^', color='r', ms=vsize, markeredgecolor='w', markeredgewidth=lw + 0.25, zorder=15,
                latlon=True)

        T_11_min = -90
        T_11_max = 30.

        cmaplist_hex = act_to_list("/home/aprata/Documents/colortables/NEO_modis_sst_45.act")
        cmaplist = [matplotlib.colors.hex2color(cmhex) for cmhex in cmaplist_hex]
        cmaplist.remove((0., 0., 0.))
        #cmaplist = cmaplist[::-1]
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list('cmap', cmaplist, len(cmaplist))
        cmap.set_over(color=bg_col, alpha=0)
        bt11_bw_pcm = bm.pcolormesh(lons_subset, lats_subset, T_11_subset - 273.15, vmin=T_11_min, vmax=T_11_max, cmap='Greys',
                                    latlon=True)
        bt11_pcm = bm.pcolormesh(lons_subset, lats_subset, T_11_box - 273.15, vmin=T_11_min, vmax=T_11_max, cmap=cmap,
                                 latlon=True)

        # add colorbar
        cb = plt.colorbar(bt11_pcm, cax=ax_cb, pad=0.02)
        cb.set_label(label="11 $\mu$m Brightness Temperature [°C]", size=10, rotation=270, labelpad=10, color=line_col)
        cb.ax.tick_params(labelsize=10, color=line_col, labelcolor=line_col)

        # # plot cold point over volcano
        # box_buffer = 0.25
        # extent_box = [vlon - box_buffer, vlon + box_buffer, vlat - box_buffer, vlat + box_buffer]
        # lon_inds_box = np.where((lons_arr > extent_box[0]) & (lons_arr < extent_box[1]))[0]
        # lat_inds_box = np.where((lats_arr > extent_box[2]) & (lats_arr < extent_box[3]))[0]
        # lons_arr_box = lons_arr[lon_inds_box]
        # lats_arr_box = lats_arr[lat_inds_box]
        # T_11_box = T_112_arr[np.ix_(lat_inds_box, lon_inds_box)]
        # lons_2d_box, lats_2d_box = np.meshgrid(lons_arr_box, lats_arr_box)
        # lons_box, lats_box = bm(lons_2d_box, lats_2d_box)

        # plot box boundaries
        box_col = line_col
        # ax.plot(lons_box[0, :], lats_box[0, :], color=box_col, lw=1)
        # ax.plot(lons_box[:, 0], lats_box[:, 0], color=box_col, lw=1)
        # ax.plot(lons_box[-1, :], lats_box[-1, :], color=box_col, lw=1)
        # ax.plot(lons_box[:, -1], lats_box[:, -1], color=box_col, lw=1)

        # plot cold point within box
        mlon, mlat = lons_box[T_11_box == T_11_box.min()][0], lats_box[T_11_box == T_11_box.min()][0]
        mT11 = T_11_box.min() - 273.15
        bm.plot(mlon, mlat, '+', color=box_col, ms=vsize, markeredgecolor='w', markeredgewidth=1, latlon=True,
                zorder=20)
        # ax.annotate(str(round(mT11, 2)), (mlon, mlat), color=line_col, zorder=20)
        ax.annotate("BT$_{min}$ = " + str(round(mT11, 2)) + " °C", (bm(extent[1] - 0.1, extent[2] + 0.1)), color='w',
                    horizontalalignment='right', zorder=20)
        ax.annotate(str(int(radius / 1000.)) + " km radius", (bm(extent[0] + 0.1, extent[2] + 0.1)), color='w',
                    horizontalalignment='left', zorder=20)

        ax.set_aspect('auto')
        title = "Himawari-8 | AHI | " + current_time.strftime("%Y-%m-%d %H:%M UTC") + \
                " | Processed by Andrew Prata (BSC) | Data courtesy JMA"
        ax.set_title(title, y=1, x=0.5, color=line_col, size=10)
        print("Saving to disk...")
        path_img = '/home/aprata/satellite/tinakula/himawari8/img/bt11/'
        fn_img = fn_data.replace('.nc', '_bt11')
        fig.savefig(path_img + '/' + fn_img + '.png', facecolor=bg_col, transparent=True, dpi=300)
        ds.close()
    ax.cla()
    ax_cb.cla()
plt.close('all')

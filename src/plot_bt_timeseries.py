# plot and check output
import pandas as pd
import matplotlib.pyplot as plt
import locale
import matplotlib.dates as mdates
from datetime import datetime


# read data
path_data = '/home/aprata/satellite/tinakula/himawari8/data/timeseries/'
fn_out = 'tinakula_2017_minT_50km.txt'
df = pd.read_csv(path_data + fn_out, delim_whitespace=True, header=None)
dt_list = [datetime.strptime(dt, '%Y%m%d_%H%M') for dt in df.values[:, 0]]
bt_arr = df.values[:, 1]

# setup figure
fig = plt.figure(figsize=(8, 4))
axes = [0.1, 0.12, 0.85, 0.81]
ax = fig.add_axes(axes)

# plot data
ax.plot(dt_list, bt_arr, 'o-')

# Format axes (see http://strftime.org for datetime formats)
locale.setlocale(locale.LC_ALL, 'en_GB.utf8')
days = mdates.DayLocator()  # every day
#hours = mdates.HourLocator(byhour=np.arange(4, 24+4, 4))  # every 4 hours
hours = mdates.HourLocator(interval=2)  # every 4 hours
#dayFmt = mdates.DateFormatter('%d %b %H:%M')
dayFmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
hourFmt = mdates.DateFormatter('%H:%M')
emptyDateFmt = mdates.DateFormatter('')
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(emptyDateFmt)
ax.xaxis.set_minor_locator(hours)
ax.xaxis.set_minor_formatter(hourFmt)
ax.set_xlim(datetime(2017, 10, 20, 19), datetime(2017, 10, 21, 5))
ax.set_xlabel("Time")
ax.set_ylabel("Cloud-top temperature (°C)")
ax.annotate("20 October 2017", xy=(datetime(2017, 10, 20, 19, 10), -25),
            size=12, ha='left')
ax.annotate("21 October 2017", xy=(datetime(2017, 10, 21, 0, 10), -25),
            size=12, ha='left')
ax.axvline(datetime(2017, 10, 21), lw=1, ls=':', color='k')
ax.set_title('Tinakula 2017 minimum BTs within 50 km radius')
path_png = '/home/aprata/satellite/tinakula/himawari8/img/timeseries/'
fn_png = fn_out.replace('.txt', '.png')
fig.savefig(path_png+fn_png, dpi=600)

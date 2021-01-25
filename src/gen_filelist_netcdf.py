# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

path_netcdf_stub = 'ftp://ftp.ptree.jaxa.jp/jma/netcdf/'


# Tinakula 2017 eruption
path = '/media/aprata/TOSHIBA EXT/satellite/tinakula/netcdf/'
start_time = datetime(2017, 10, 20, 19)
end_time = datetime(2017, 10, 21, 5)

time_diff = end_time - start_time
time_minutes = time_diff.total_seconds()/60.
num = int(time_minutes/10.) + 1
fn = 'wget.txt'

with open(path + fn, 'w') as f:
    for i in range(num):
        current_time = start_time + timedelta(minutes=i*10)
        year_month = current_time.strftime("%Y%m")
        day = current_time.strftime("%d")
        hour = current_time.strftime("%H")
        current_time_str = current_time.strftime("%Y%m%d_%H%M")

        path_netcdf = path_netcdf_stub + year_month + '/' + day + '/'
        res = 'R21'
        fn_netcdf = 'NC_H08_' + current_time_str + '_' + res + '_FLDK.06001_06001.nc'
        f.write(path_netcdf+fn_netcdf+'\n')

print("Number of files = "+str(num)+', predicted total download size: ' + str(num * 0.6) + ' GB')
print("To download the files:")
print("cd "+path)
print("wget --ftp-user=andyprata_gmail.com --ftp-password=SP+wari8 -nc -i "+fn)

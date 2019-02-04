#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tues Dec  4 10:41:31 2018

@author: Sébastien Gardoll
"""
from multiprocessing import Pool

import common

from predict_cyclone_utils import fetch_setting, open_cyclone_db, compute_recorded_cyclones
from predict_cyclone_utils import normalize_netcdf, compute_chunks, allocate_channel_array
from predict_cyclone_utils import prediction_analysis, save_results, extract_region
from predict_cyclone_utils import open_netcdf_files, display_intermediate_time

import time
start = time.time()

year, month, day, time_step, lat_min, lat_max, lon_min, lon_max,\
file_prefix, cyclone_lat_size, cyclone_lon_size, nb_proc, is_debug,\
has_save_results = fetch_setting()

cyclone_dataframe = open_cyclone_db()

chunk_list_df,index_list, id_counter = compute_chunks(lat_min, lat_max,
                                                      lon_min, lon_max)

netcdf_dict, shape = open_netcdf_files(year, month)

recorded_cyclones, nb_cyclones = compute_recorded_cyclones(cyclone_dataframe, year, month, day, time_step)

normalized_dataset = normalize_netcdf(file_prefix, netcdf_dict, shape, day, time_step)

channels_array = allocate_channel_array(id_counter)

def wapper_extract_region(img_spec):
  return extract_region(img_spec, normalized_dataset, channels_array)

print(f'> extracting the {id_counter} subregions (proc: {nb_proc})')
with Pool(processes = nb_proc) as pool:
  pool.map(wapper_extract_region, index_list)
display_intermediate_time()

cyclone_images_df = prediction_analysis(file_prefix, channels_array,
                                recorded_cyclones, chunk_list_df, cyclone_lat_size,
                                cyclone_lon_size, nb_cyclones)
if has_save_results:
  save_results(cyclone_images_df, file_prefix, year, month, day, time_step)

stop = time.time()
formatted_time =common.display_duration((stop-start))
print(f'> spend {formatted_time} processing')
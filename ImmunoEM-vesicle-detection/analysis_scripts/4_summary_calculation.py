from time import time
from functools import wraps
import timeit
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import skimage
from zipfile import ZipFile
from scipy.spatial import distance
from sklearn.metrics import pairwise_distances_argmin_min
import cv2
import matplotlib.pyplot as plt
from loguru import logger
import functools

logger.info('Import OK')

input_folder = f'ImmunoEM-vesicle-detection/python_results/ImmunoEM-vesicle-detection_Analyzed/feature_properties/'
output_folder = f'ImmunoEM-vesicle-detection/python_results/ImmunoEM-vesicle-detection_Analyzed/feature_summaries/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# ------------------Initialize dataframes------------------
feature_properties = pd.read_csv(f'{input_folder}feature_properties.csv')
min_distances = pd.read_csv(f'{input_folder}feature_coords_distances.csv')

# label cell line in feature properties
feature_properties['cell_line'] = feature_properties['roi_key'].str.split('-').str[1]

# ------------------find min distance between membrane x (cleft or RBC) and vesicle membrane------------------
# make unique key per otherRoi
min_distances['otherRoi'] = min_distances['otherRoi_key'].str.split('_').str[1]

# make 'image' column from the vesicle_key column
min_distances['image'] = min_distances['vesicle_key'].str.split('_').str[0]

# make 'cell_line' column from the image column
min_distances['cell_line'] = min_distances['image'].str.split('-').str[1]

# keep the min distance to cleft & membrane
min_distances = min_distances.iloc[min_distances.groupby(['vesicle_key', 'otherRoi'])[
    'measure_distance'].idxmin()]
min_distances = min_distances.reset_index(drop=True)


# ----------Grab major and minor_axis_length for vesicles & clefts----------
vesicle_minor_axis = feature_properties[feature_properties['feature'] == 'vesicle'].groupby(
    ['image_name']).mean()['minor_axis_length']
vesicle_major_axis = feature_properties[feature_properties['feature'] == 'vesicle'].groupby(
    ['image_name']).mean()['major_axis_length']

cleft_minor_axis = feature_properties[feature_properties['feature'] == 'cleft'].groupby(
    ['image_name']).mean()['minor_axis_length']
cleft_major_axis = feature_properties[feature_properties['feature'] == 'cleft'].groupby(
    ['image_name']).mean()['major_axis_length']

# ----------Calculate average size of vesicles & clefts per cell----------
ves_av_size = feature_properties[feature_properties['feature'] == 'vesicle'].groupby(
    ['image_name']).mean()['area'].reset_index()
cleft_av_size = feature_properties[feature_properties['feature'] == 'cleft'].groupby(
    ['image_name']).mean()['area'].reset_index()

# ------------------Summarise------------------
vesicle_summary = functools.reduce(lambda left, right: pd.merge(left, right, on=['image_name'], how='outer'), [
                           ves_av_size, vesicle_minor_axis, vesicle_major_axis])
vesicle_summary.columns = ['image_name', 'mean_area',
                           'mean_minor_axis', 'mean_major_axis']

# make 'cell_line' column
vesicle_summary['cell_line'] = vesicle_summary['image_name'].str.split(
    '-').str[1]

cleft_summary = functools.reduce(lambda left, right: pd.merge(left, right, on=['image_name'], how='outer'), [
                           cleft_av_size, cleft_minor_axis, cleft_major_axis])
cleft_summary.columns = ['image_name', 'mean_area',
                         'mean_minor_axis', 'mean_major_axis']

# make 'cell_line' column
cleft_summary['cell_line'] = cleft_summary['image_name'].str.split('-').str[1]

# ------------------Additional calculations------------------
# make a df for vesicle -> cleft distances only
clefts = min_distances.loc[(min_distances['otherRoi'] == 'cleft')]

# how many vesicles within x nm of clefts?
distance = 100
vesicles_to_clefts = clefts.loc[(clefts['measure_distance'] < distance)]
vesicles_to_clefts['cell_line'] = [row.split('-')[1]
                                   for row in vesicles_to_clefts['otherRoi_key']]
vesicles_to_clefts_count = vesicles_to_clefts.groupby(['otherRoi_key','cell_line']).count().reset_index()

# list and ratio of vesicles x distance from cleft
distance = 100
perc_CS2_vesicles = ((sum((clefts['cell_line'] == 'CS2') & (
    clefts['measure_distance'] <= distance)) / sum((clefts['cell_line'] == 'CS2')))*100)
perc_OC03_vesicles = ((sum((clefts['cell_line'] == 'OC03') & (
    clefts['measure_distance'] <= distance)) / sum((clefts['cell_line'] == 'OC03')))*100)
perc_OC60_vesicles = ((sum((clefts['cell_line'] == 'OC60') & (
    clefts['measure_distance'] <= distance)) / sum((clefts['cell_line'] == 'OC60')))*100)
perc_OC61_vesicles = ((sum((clefts['cell_line'] == 'OC61') & (
    clefts['measure_distance'] <= distance)) / sum((clefts['cell_line'] == 'OC61')))*100)
perc_OC62_vesicles = ((sum((clefts['cell_line'] == 'OC62') & (
    clefts['measure_distance'] <= distance)) / sum((clefts['cell_line'] == 'OC62')))*100)
perc_OC63_vesicles = ((sum((clefts['cell_line'] == 'OC63') & (
    clefts['measure_distance'] <= distance)) / sum((clefts['cell_line'] == 'OC63')))*100)

percent_vesicles = pd.DataFrame({'cell_line': ['CS2', 'OC03', 'OC60', 'OC61', 'OC62', 'OC63'], f'percent_vesicles_in_{distance}_nm': [
                                perc_CS2_vesicles, perc_OC03_vesicles, perc_OC60_vesicles, perc_OC61_vesicles,
                                perc_OC62_vesicles,
                                perc_OC63_vesicles]})

# ------------------save relevant info for plotting ------------------
min_distances.to_csv(f'{output_folder}min_distances.csv')
vesicles_to_clefts.to_csv(f'{output_folder}vesicles_to_clefts.csv')
percent_vesicles.to_csv(f'{output_folder}percent_vesicles.csv')
vesicles_to_clefts_count.to_csv(f'{output_folder}vesicles_to_clefts_count.csv')
vesicle_summary.to_csv(
    f'{output_folder}calculated_properties_vesicle_summary.csv')
cleft_summary.to_csv(
    f'{output_folder}calculated_properties_cleft_summary.csv')

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import skimage.io
import functools
from loguru import logger

logger.info('Import OK')

# input_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/feature_collection_1/'
# output_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/summary_calculations_1/'
# scale_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_scale_1/'
input_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/feature_collection/'
output_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/summary_calculations/'
scale_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_scale/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# --------------Initialise file lists--------------
# read in calculated pixel data
features = pd.read_csv(f'{input_folder}feature_summary.csv')
features.drop([col for col in features.columns.tolist() if 'Unnamed: ' in col], axis=1, inplace=True)

# do we need coords?
coords = pd.read_csv(f'{input_folder}feature_coords.csv')
coords.drop([col for col in coords.columns.tolist() if 'Unnamed: ' in col], axis=1, inplace=True)

image_scaled = pd.read_csv(f'{scale_folder}scale_assigned.csv')

# --------------Add pixes per µm factor--------------
# make pixel per µm dictionary
image_scaled_dict = dict(
    zip(image_scaled['image_name'], image_scaled['scaled_pixels_um']))

# map dictionary to features df
features['scaled_pixels_um'] = features['image_name'].map(image_scaled_dict)

features['pixels_nm'] = features['scaled_pixels_um']/1000

# scale: area and axes lengths
features['area_nm'] = (features['area'] / (features['pixels_nm']**2))
features['major_axis_length_nm'] = (
    features['major_axis_length'] / features['pixels_nm'])
features['minor_axis_length_nm'] = (
    features['minor_axis_length'] / features['pixels_nm'])

# --------------Grab major and minor_axis_length for knobs--------------
minor_axis = features[features['ROI_type'] == 'knob'].groupby(
    ['image_name', 'cell_number']).mean()['minor_axis_length_nm']
major_axis = features[features['ROI_type'] == 'knob'].groupby(
    ['image_name', 'cell_number']).mean()['major_axis_length_nm']

# --------------Calculate average size of knobs per cell--------------
av_size = features[features['ROI_type'] == 'knob'].groupby(
    ['image_name', 'cell_number']).mean()['area_nm'].reset_index()

# --------------Calculate proportion of area in knobs--------------
cell_size = features[features['ROI_type'] == 'cell'].set_index(
    ['image_name', 'cell_number'])['area_nm']
knob_area = features[features['ROI_type'] == 'knob'].groupby(
    ['image_name', 'cell_number']).sum()['area_nm']
knob_proportion = ((knob_area / cell_size) *
                   100).reset_index().rename(columns={'area_nm': 'proportion_knob_area'})

# --------------Calculate number of 'knobs' per cell--------------
# NOTE: due to focus issues, cell shape changes etc, this measure is likely not valid. Generating it just in case!
knob_count = features[features['ROI_type'] == 'knob'].groupby(
    ['image_name', 'cell_number']).count()['area_nm']
knobs_per_area = (knob_count / (cell_size/10000)
                  ).reset_index().rename(columns={'area_nm': 'knobs_per_100_nm2'})

# --------------Calculate knob density (count/area in µm) --------------
knob_density = (knob_count / (cell_size/1000000)
                ).reset_index().rename(columns={'area_nm': 'proportion_knob_area'})

# --------------Summarise, save to csv--------------
summary = functools.reduce(lambda left, right: pd.merge(left, right, on=['image_name', 'cell_number'], how='outer'), [av_size, cell_size.reset_index(
), knob_area.reset_index(), knob_proportion, knob_count.reset_index(), knobs_per_area, knob_density, minor_axis, major_axis])
summary.columns = ['image_name', 'cell_number', 'mean_knob_area', 'cell_size', 'total_knob_area',
                   'knob_area_proportion', 'knob_count', 'knobs_per_100_nm2', 'knob_density_um2', 'knob_mean_minor_axis', 'knob_mean_major_axis']

# make 'cell_line' column
summary['cell_line'] = summary['image_name'].str.split('-').str[1]

summary.to_csv(f'{output_folder}calculated_properties_summary.csv')

# --------------visualise calculated parameters--------------
palette_trunc = {
    'OC60': 'palevioletred',
    'OC61': 'crimson',
    'OC62': 'purple',
    'OC63': 'midnightblue',
}

palette_ko = {
    'CS2': 'palevioletred',
    'OC03': 'crimson',
}

for parameter in ['mean_knob_area', 'knob_area_proportion', 'knob_count', 'knobs_per_100_nm2', 'mean_minor_axis', 'mean_major_axis']:
    fig, ax = plt.subplots()
    sns.swarmplot(x='cell_line', y=parameter,
                  data=summary, palette=palette_trunc)
    plt.xlabel('cell_line')
    plt.ylabel(parameter)
    plt.show()

sns.histplot(x=summary['knob_area_proportion'],
             kde=True, hue=summary['cell_line'], palette=palette_trunc)
plt.show()


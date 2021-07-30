import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import skimage.io
import functools
from scipy import stats
# from GEN_Utils import FileHandling
from loguru import logger

logger.info('Import OK')

input_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/pixel_collection/'
output_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/summary_calculations/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# --------------Initialise file lists--------------
# read in calculated pixel data
features = pd.read_csv(f'{input_folder}feature_summary.csv')
features.drop([col for col in features.columns.tolist()
              if 'Unnamed: ' in col], axis=1, inplace=True)

um_px_scale = 65.33/512
nm_px_scale = um_px_scale*1000

# scale: area and axes lengths
features['area_nm'] = [row*(nm_px_scale**2) for row in features['area']]
features['minor_axis_length_nm'] = [
    row*(nm_px_scale) for row in features['minor_axis_length']]
features['major_axis_length_nm'] = [
    row*(nm_px_scale) for row in features['major_axis_length']]

# ----------Grab major and minor_axis_length for nuclei----------
nuc_minor_axis = features[features['ROI_type'] == 'nucleus'].groupby(
    ['image_name', 'cell_number']).mean()['minor_axis_length_nm']
nuc_major_axis = features[features['ROI_type'] == 'nucleus'].groupby(
    ['image_name', 'cell_number']).mean()['major_axis_length_nm']

# ----------Grab major and minor_axis_length for puncta----------
minor_axis = features[features['ROI_type'] == 'puncta'].groupby(
    ['image_name', 'cell_number']).mean()['minor_axis_length_nm']
major_axis = features[features['ROI_type'] == 'puncta'].groupby(
    ['image_name', 'cell_number']).mean()['major_axis_length_nm']

# ----------Calculate average size of puncta per cell----------
av_size = features[features['ROI_type'] == 'puncta'].groupby(
    ['image_name', 'cell_number']).mean()['area_nm'].reset_index()

# -----------Calculate nucleus area-----------
nuc_size = features[features['ROI_type'] == 'nucleus'].groupby(
    ['image_name', 'cell_number']).mean()['area_nm']

# -----------Calculate proportion of puncta/cytoplasm area-----------
cytoplasm_area = features[features['ROI_type'] == 'cytoplasm'].groupby(
    ['image_name', 'cell_number']).mean()['area_nm']
puncta_area = features[features['ROI_type'] == 'puncta'].groupby(
    ['image_name', 'cell_number']).sum()['area_nm']
puncta_cyto_proportion = ((puncta_area / cytoplasm_area) *
                          100).reset_index()

# -----------Calculate 'puncta' area per cell-----------
puncta_area_mean = features[features['ROI_type'] == 'puncta'].groupby(
    ['image_name', 'cell_number']).mean()['area_nm']
puncta_area_mean_norm = ((puncta_area/nuc_size)).reset_index()

# -----------Calculate number of 'puncta' per cell-----------
puncta_count = features[features['ROI_type'] == 'puncta'].groupby(
    ['image_name', 'cell_number']).count()['ROI_type']

puncta_count_norm = ((puncta_count/nuc_major_axis)*100).reset_index()

# -----------Calculate number of 'puncta' per cell-----------
puncta_euler_number = features[features['ROI_type'] == 'puncta'].groupby(
    ['image_name', 'cell_number']).mean()['euler_number']

puncta_solidity = features[features['ROI_type'] == 'puncta'].groupby(
    ['image_name', 'cell_number']).mean()['solidity']

# ------------------Summarise, save to csv------------------
summary = functools.reduce(lambda left, right: pd.merge(left, right, on=['image_name', 'cell_number'], how='outer'), [
                           av_size, nuc_size.reset_index(), cytoplasm_area.reset_index(), puncta_area.reset_index(), puncta_cyto_proportion,  puncta_count.reset_index(), nuc_minor_axis, nuc_major_axis, minor_axis, major_axis, puncta_euler_number, puncta_solidity, puncta_area_mean, puncta_area_mean_norm, puncta_count_norm])
summary.columns = ['image_name', 'cell_number', 'mean_puncta_area', 'mean_nucleus_area', 'cell_size', 'total_puncta_area',
                   'puncta_cyto_proportion', 'puncta_count', 'nuc_minor_axis_length', 'nuc_major_axis_length', 'mean_minor_axis', 'mean_major_axis', 'puncta_euler_number', 'puncta_solidity', 'puncta_area_mean', 'puncta_area_mean_norm', 'puncta_count_norm']

# make 'cell_line' column
summary['cell_line'] = summary['image_name'].str.split('_').str[1]

# remove rows with values <1
summary = summary[(summary[['mean_puncta_area', 'mean_nucleus_area', 'cell_size', 'total_puncta_area',
                                'puncta_cyto_proportion', 'puncta_count', 'nuc_minor_axis_length', 'nuc_major_axis_length', 'mean_minor_axis', 'mean_major_axis']] > 1).all(axis=1)]

summary.to_csv(f'{output_folder}calculated_properties_summary.csv')

# -------------------visualise calculated parameters & stats-------------------
for parameter in ['mean_puncta_area', 'cell_size', 'total_puncta_area',
                  'puncta_cyto_proportion', 'puncta_count', 'mean_minor_axis', 'mean_major_axis', 'puncta_euler_number', 'puncta_solidity', 'nuc_major_axis_length', 'puncta_area_mean_norm', 'puncta_count_norm']:
    fig, ax = plt.subplots()
    sns.swarmplot(x='cell_line', y=parameter,
                  data=summary)
    plt.xlabel('cell_line')
    plt.ylabel(parameter)
    plt.show()

sns.histplot(x=summary['puncta_cyto_proportion'],
             kde=True, hue=summary['cell_line'])
plt.show()

sns.boxplot(x=summary['puncta_area_mean'], y=summary['cell_line'])
plt.show()

for cell_line, cell_line_df in summary.groupby(['cell_line']):
    fig, ax = plt.subplots()
    plt.title(cell_line)
    sns.regplot(x=cell_line_df['nuc_major_axis_length'],
                y=cell_line_df['puncta_count'])
    corr, p_value = stats.pearsonr(
        cell_line_df['nuc_major_axis_length'], cell_line_df['puncta_cyto_proportion'])
    
    print(f'{cell_line}: Pearsons corr= {corr}, p_value {p_value}, n = {len(cell_line_df)}')

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns
import skimage.io
from skimage import measure
import functools
from loguru import logger

logger.info('Import OK')

# image_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/initial_cleanup/'
# mask_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_masking/'
# output_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/feature_collection/'
image_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/initial_cleanup_1/'
mask_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_masking_1/'
output_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/feature_collection_1/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)


def feature_extractor(mask, properties=False):

    if not properties:
        properties = ['area', 'coords', 'centroid', 'convex_area', 'eccentricity', 'euler_number', 'label', 'local_centroid', 'major_axis_length', 'minor_axis_length', 'orientation', 'perimeter', 'solidity']

    return pd.DataFrame(skimage.measure.regionprops_table(mask, properties=properties))


# --------------Initialise file lists--------------
# read in masks
images = [f'{image.strip("_mask.npy")}' for image in os.listdir(mask_folder) if '.npy' in image]
masks = {}
for image_name in images:
    logger.info(f'Processing {image_name}')
    masks[f'{image_name}'] = {cell.replace('.npy', ''): np.load(f'{mask_folder}{image_name}/{cell}') for cell in os.listdir(f'{mask_folder}{image_name}/')}
    logger.info(f'Masks loaded for {len(masks[f"{image_name}"].keys())} cells')

# ----------------collect feature information----------------
feature_information = []
for image_name, mask_dict in masks.items():
    logger.info(f'Processing {image_name}')
    for cell, mask_stack in mask_dict.items():
        cell_properties = feature_extractor(mask_stack[0, :, :])
        cell_properties['ROI_type'] = 'cell'
        feature_properties = feature_extractor(mask_stack[1, :, :])
        feature_properties['ROI_type'] = 'knob'
        properties = pd.concat([cell_properties, feature_properties])
        properties['image_name'] = image_name
        properties['cell_number'] = cell
        feature_information.append(properties)
feature_information = pd.concat(feature_information)
logger.info('Completed feature collection')

# Extract pixel coords info to separate df
coords = feature_information[['image_name', 'cell_number', 'ROI_type', 'label', 'coords']].copy()
feature_information.drop('coords', axis=1, inplace=True)
coords = coords.explode('coords')

# ----------------Save to csv----------------
coords.to_csv(f'{output_folder}feature_coords.csv')
feature_information.to_csv(f'{output_folder}feature_summary.csv')

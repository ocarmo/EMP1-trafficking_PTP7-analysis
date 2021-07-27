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

image_folder = f'experimental_data/initial_cleanup_zoom/'
mask_folder = f'python_results/napari_masking/'
output_folder = f'python_results/feature_collection/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)


def feature_extractor(mask, properties=False):

    if not properties:
        properties = ['area', 'coords', 'centroid', 'convex_area', 'eccentricity', 'euler_number', 'label', 'local_centroid', 'major_axis_length', 'minor_axis_length', 'orientation', 'perimeter', 'solidity']

    return pd.DataFrame(skimage.measure.regionprops_table(mask, properties=properties))

# ----------------Initialise file lists----------------

# read in masks
filtered_masks = {masks.replace('_mask.npy', ''): np.load(
    f'{mask_folder}{masks}') for masks in os.listdir(f'{mask_folder}') if '.npy' in masks}

# ----------------collect feature information----------------
feature_information = []
for image_name, stack in filtered_masks.items():
    image_name
    logger.info(f'Processing {image_name}')
    mask = (stack[1, :, :]).astype(int)
    feature_properties = feature_extractor(mask)
    feature_properties['ROI_type'] = 'knob'
    # properties = pd.concat([feature_properties])
    feature_properties['image_name'] = image_name
    feature_information.append(feature_properties)
feature_information = pd.concat(feature_information)
logger.info('Completed feature collection')
feature_information.drop('coords', axis=1, inplace=True)

# ----------------save to csv----------------
feature_information.to_csv(f'{output_folder}feature_summary.csv')

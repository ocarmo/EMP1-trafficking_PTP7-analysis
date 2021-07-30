import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import skimage.io
import functools
import xlsxwriter
from skimage import measure
from loguru import logger

logger.info('Import OK')

# define location parameters
image_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/initial_cleanup/'
mask_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/napari_masking/'
output_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/pixel_collection/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)


def feature_extractor(mask, properties=False):

    if not properties:
        properties = ['area', 'centroid', 'convex_area', 'eccentricity', 'euler_number', 'label',
                      'local_centroid', 'major_axis_length', 'minor_axis_length', 'solidity', 'filled_area']

    return pd.DataFrame(skimage.measure.regionprops_table(mask, properties=properties))


# --------------Initialise file lists--------------
# read in images, including transpose to put in x, y, z format
file_list = [filename for filename in os.listdir(
    image_folder) if '.tif' in filename]
images = {filename.replace('.tif', ''): skimage.io.imread(
    f'{image_folder}{filename}') for filename in file_list}

# fails try/except if no masks found therefore skip that image
masks = {}
for image_name, img in images.items():
    # logger.info(f'Processing {image_name}')
    try:
       masks[image_name] = {cell_number.replace('.npy', ''): np.load(
           f'{mask_folder}{image_name}/{cell_number}') for cell_number in os.listdir(f'{mask_folder}{image_name}')}
    #    logger.info(f'Masks loaded for {len(masks[image_name].keys())} cells')
    except:
        logger.info(f'{image_name} not processed as no mask found')
logger.info('Completed mask dictionary writing')

# ---------------collect feature information---------------
feature_information = []
for image_name, mask_dict in masks.items():
    # logger.info(f'Processing {image_name}')
    for cell, mask_stack in mask_dict.items():
        if 1 in mask_stack[1, :, :]:
            if 1 in mask_stack[2, :, :]:
                image_name
                cytoplasm_properties = feature_extractor(mask_stack[0, :, :])
                cytoplasm_properties['ROI_type'] = 'cytoplasm'
                nuc_properties = feature_extractor(mask_stack[1, :, :])
                nuc_properties['ROI_type'] = 'nucleus'
                puncta_properties = feature_extractor(mask_stack[2, :, :])
                puncta_properties['ROI_type'] = 'puncta'
                # collect all properties
                properties = pd.concat(
                    [cytoplasm_properties, nuc_properties, puncta_properties])
                properties['image_name'] = image_name
                properties['cell_number'] = cell
                feature_information.append(properties)
feature_information = pd.concat(feature_information)
logger.info('Completed feature collection')

# ---------------save feature information---------------
feature_information.to_csv(f'{output_folder}feature_summary.csv')

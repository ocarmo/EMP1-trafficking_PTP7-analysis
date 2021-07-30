import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import skimage
from skimage import measure
import napari
import pytesseract
import skimage.io
import re
from loguru import logger

logger.info('Import OK')

image_folder = f'SEM-internal-cell-texture/python_results/SEM-internal-cell-texture_Analyzed/initial_cleanup_zoom/'
input_folder = f'SEM-internal-cell-texture/python_results/SEM-internal-cell-texture_Analyzed/napari_scale/'
output_folder = f'SEM-internal-cell-texture/python_results/SEM-internal-cell-texture_Analyzed/napari_scale/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# --------------Initialize file lists--------------
# reading in all images + masks
file_list = [filename for filename in os.listdir(
    image_folder) if '.tif' in filename]

# reading in all channels for each image, and transposing to correct dimension of array
imgs = [skimage.io.imread(f'{image_folder}{filename}')
        for filename in file_list]

# clean filenames
img_names = [filename.replace('.tif', '') for filename in file_list]

# import scales
found_hfw = pd.read_csv(f'{input_folder}find_hfw.csv')
hfw_df = pd.read_csv(f'{input_folder}hfw.csv')

# --------------Correct scaling--------------
# make found_hfw dictionary
found_hfw_dict = dict(zip(found_hfw['image_name'], found_hfw['substring']))

# replace hfw values and clean up dataframe
hfw_df['hfw'] = hfw_df['image_name'].map(found_hfw_dict)
hfw_df['hfw'] = hfw_df['hfw'].fillna(hfw_df['substring'])
hfw_df.drop(['image_string', 'substring', 'Unnamed: 0'], axis=1, inplace=True)

hfw_list = hfw_df['hfw'].tolist()

# grab the pixel width of each original image
pixel_width_list = [arr.shape[1] for arr in imgs]

# check that aspect ratio is consistent
pixel_height_list = [arr.shape[0] for arr in imgs]
shape_ratio = [width / height for width,
               height in zip(pixel_width_list, pixel_height_list)]

# zip together lists
image_width_df = pd.DataFrame(list(map(list, zip(
    img_names, pixel_width_list, hfw_list))), columns=['image_name', 'pixel_width', 'hfw'])

# image pixel width / hfw = pixels / um
image_width_df['pixels_um'] = (image_width_df['pixel_width'] /
    image_width_df['hfw'])

# add width of 'scaled' images (performed prior to segmentation/masking)
image_width_df['scaled_px_width'] = [
    768 for row in image_width_df['pixels_um']]

# calculate scaled ratio
image_width_df['scaled_ratio'] = (
    image_width_df['scaled_px_width'] / image_width_df['pixel_width'])

# correct pixels per um for scaling factor
image_width_df['scaled_pixels_um'] = (
    image_width_df['pixels_um'] * image_width_df['scaled_ratio'])

# --------------Export scaling--------------
image_width_df.to_csv(f'{output_folder}scale_assigned.csv')

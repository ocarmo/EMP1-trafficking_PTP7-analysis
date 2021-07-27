import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from aicsimageio.writers import OmeTiffWriter
from aicsimageio import AICSImage
from loguru import logger
import skimage.io
import numpy as np
import os
import re
from shutil import copyfile
import mrc

logger.info('Import ok')

# input_path = f'/Users/oliviacarmo/Desktop/2021.03.27-restacked/'
input_path = f'/Users/oliviacarmo/Desktop/2020.06.25-restacked/'
output_folder = f'python_results/initial_cleanup/'


def dv_projector(image_name, input_folder, output_folder, tiff=True, array=True):
    # Read in before and after images for each field of view and concatenate the two into single np array
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Read tif file
    img = skimage.io.imread(f'{input_folder}{image_name}.tif').transpose(1, 0, 2, 3,)
    
    # project dic z-stack
    dic_max_projection = np.max(img[0, :, :, :], axis=0)
    
    # project GFP z-stack
    gfp_max_projection = np.max(img[1, :, :, :], axis=0)

    # concatenate
    image = np.stack([dic_max_projection, gfp_max_projection])

    if tiff == True:
        # Save image to TIFF file with image number
        OmeTiffWriter.save(
            image, f'{output_folder}{image_name}.tif', dim_order='CYX')
        logger.info(
            f'{image_name} converted to tiff with {image.shape} dimensions.')

    if array == True:
        np.save(f'{output_folder}{image_name}.npy', image)
        logger.info(
            f'{image_name} converted to numpy array with {image.shape} dimensions.')


# ---------------Initalize file_list---------------
# read in all folders with image files
file_list_ext = [filename for filename in os.listdir(
    input_path) if '.log' not in filename]

# clean filenames
file_list = [filename.replace('.tif', '') for filename in os.listdir(
    input_path) if '.log' not in file_list_ext]

do_not_quantitate = ['oc55', 'oc56', 'oc48']

# ---------------Collect image names & convert---------------
image_names = []
for filename in file_list:
    if not any(word in filename for word in do_not_quantitate):
        filename = filename.split(' ')[0]
        image_names.append(filename)

# grab dic ref image and project GFP channel for ea. file
for name in image_names:
    dv_projector(name, input_folder=f'{input_path}',
                 output_folder=f'{output_folder}', tiff=True, array=True)

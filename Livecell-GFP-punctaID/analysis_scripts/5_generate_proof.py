import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import image
import napari
import skimage.io
from skimage import data
from PIL import Image
from matplotlib_scalebar.scalebar import ScaleBar

from loguru import logger
#from GEN_Utils import FileHandling

logger.info('Import OK')

input_path = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/summary_calculations/'
output_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/plot/'
image_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/initial_cleanup/'
feature_masks_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/napari_masking/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# --------------Initialise file lists--------------
# reading in raw images
image_list_tif = [filename for filename in os.listdir(
    image_folder) if '.tif' in filename]

raw_images = [skimage.io.imread(
    f'{image_folder}{filename}') for filename in image_list_tif]

# reading in feature arrays
image_list_npy = [filename.replace('.tif', '_mask.npy') for filename in image_list_tif]

valid_narrays = [np.load(f'{feature_masks_folder}{filename}') for filename in image_list_npy]

# generating hyperstack and labeling in dict
imgs_and_masks = np.column_stack([raw_images, valid_narrays])

image_list = [filename.replace('.tif', '')
              for filename in image_list_tif]

imgs_and_masks_dict = {}
imgs_and_masks_dict = dict(zip(image_list, imgs_and_masks))

# --------------Plotting--------------
# TODO: ONLY plot cells for which features were extracted.
for image_name, stack in imgs_and_masks_dict.items():
    image_name
    # unpack
    dic = stack[0, :, :]
    # plt.imshow(dic, cmap='gray')
    gfp = stack[1, :, :]
    # where = (condition, true, false) to make binary shapes
    cell = np.where(stack[2, :, :] != 0, 255, np.nan)
    nucleus = np.where(stack[3, :, :] != 0, 255, np.nan)
    puncta = np.where(stack[4, :, :] != 0, 255, np.nan)

    # fig, ax = plt.subplots(figsize = ())
    fig, ax = plt.subplots()
    plt.imshow(cell, cmap='magma', alpha=0.4, origin='lower')
    plt.imshow(stack[3, :, :], cmap='Greys_r', alpha=0.4, origin='lower')
    plt.imshow(stack[4, :, :], cmap='Greens', alpha=0.4, origin='lower')

    # Create scale bar
    scale = 65.33/dic.shape[0]
    scalebar = ScaleBar(scale, 'um', location='lower right',
                        pad=0.3, sep=2, box_alpha=0)
    ax.add_artist(scalebar)
    plt.show()
    
    fig.savefig(f'{output_folder}{image_name}.png')
    logger.info(f'Proof for {image_name} saved.')
    plt.clf()

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
import cv2
from matplotlib_scalebar.scalebar import SI_LENGTH

logger.info('Import OK')

input_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/feature_collection/'
scale_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_scale/'
output_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/plot/'
np_mask_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_masking/'
image_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/initial_cleanup/'
mask_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/cellpose_masking/'

# input_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/feature_collection_1/'
# scale_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_scale_1/'
# output_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/plot/'
# np_mask_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_masking_1/'
# image_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/initial_cleanup_1/'
# mask_folder = 'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/cellpose_masking_1/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# --------------Initialise file lists--------------
# read in calculated pixel data
features = pd.read_csv(f'{input_folder}feature_summary.csv')
features.drop([col for col in features.columns.tolist()
              if 'Unnamed: ' in col], axis=1, inplace=True)

# scale assigned
image_scaled = pd.read_csv(f'{scale_folder}scale_assigned.csv')

# file list from raw images (initial cleanup)
file_list = [filename for filename in os.listdir(
    image_folder) if '.tif' in filename]
file_list_masknpy = [filename.replace('.tif','_mask.npy') for filename in file_list]
image_stack = np.load(f'{mask_folder}scaled_images.npy')
down_sized_images = {filename.replace(
    '.tif', ''): image_stack[x, :, :] for x, filename in enumerate(file_list)}

# # To reload previous masks for per-cell extraction
filtered_masks = [np.load(
    f'{np_mask_folder}{masks}') for masks in file_list_masknpy]

knob_stacks = [array[1, :, :] for array in filtered_masks]

# interleave masks to create single stack per image
raw_masks = {
    image_name: np.stack((image_stack[x], knob_stacks[x]))
    for x, image_name in (enumerate(down_sized_images.keys()))
}

# --------------Add pixes per µm factor--------------
# make pixel per µm dictionary
image_scaled_dict = dict(
    zip(image_scaled['image_name'], image_scaled['scaled_pixels_um']))

# --------------Plotting--------------
#for image_name in image_narray_list:
for image_name, stack in raw_masks.items():
    # unpack
    image = stack[0, :, :]
    # where = (condition, true, false) to make binary shapes
    knobs = np.where(stack[1, :, :] != 0, 255, np.nan)
    knob_colors = stack[1, :, :]

    # figure
    fig, ax = plt.subplots()
    plt.imshow(image, cmap='Greys_r', origin='lower')
    plt.imshow(knob_colors, cmap='magma', alpha = 0.4, origin='lower')

    # Create scale bar
    scale = 1/image_scaled_dict[image_name]
    scalebar = ScaleBar(scale, 'um', location='lower right',
                        pad=0.3, sep=2, box_alpha=0.5)
    ax.add_artist(scalebar)
    plt.show()
    
    fig.savefig(f'{output_folder}{image_name}.png')
    logger.info(f'Proof for {image_name} saved.')
    plt.clf()

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
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.font_manager as fm

logger.info('Import OK')

input_folder = 'SEM-internal-cell-texture/python_results/SEM-internal-cell-texture_Analyzed/feature_collection/'
scale_folder = 'SEM-internal-cell-texture/python_results/SEM-internal-cell-texture_Analyzed/napari_scale/'
output_folder = 'SEM-internal-cell-texture/python_results/SEM-internal-cell-texture_Analyzed/plot/'
np_mask_folder = 'SEM-internal-cell-texture/python_results/SEM-internal-cell-texture_Analyzed/napari_masking/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# --------------Initialise file lists--------------
# read in calculated pixel data
features = pd.read_csv(f'{input_folder}feature_summary.csv')
features.drop([col for col in features.columns.tolist()
              if 'Unnamed: ' in col], axis=1, inplace=True)

# scale assigned
image_scaled = pd.read_csv(f'{scale_folder}scale_assigned.csv')

filtered_masks = {masks.replace('_mask.npy', ''): np.load(
    f'{np_mask_folder}{masks}') for masks in os.listdir(f'{np_mask_folder}') if '.npy' in masks}

# ----------Add pixes per µm factor----------
# make pixel per µm dictionary
image_scaled_dict = dict(
    zip(image_scaled['image_name'], image_scaled['scaled_pixels_um']))

# --------------Plotting--------------
for image_name, stack in filtered_masks.items():
    # unpack
    image = stack[0, :, :]
    # where = (condition, true, false) to make binary shapes
    knobs = np.where(stack[1, :, :] != 0, 255, np.nan)
    knob_colors = stack[1, :, :]

    fig, ax = plt.subplots()
    plt.imshow(image, cmap='Greys_r', origin='lower')
    plt.imshow(knob_colors, cmap='magma', alpha=0.4, origin='lower')

    # Create scale bar
    scale = 1/image_scaled_dict[image_name]
    scalebar = ScaleBar(scale, 'um', location='lower right',
                        pad=0.3, sep=2, box_alpha=0.5)
    ax.add_artist(scalebar)
    plt.show()

    fig.savefig(f'{output_folder}{image_name}.png')
    logger.info(f'Proof for {image_name} saved.')
    plt.clf()

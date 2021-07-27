import napari
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os, shutil
import collections
import skimage.io
from skimage import data
from skimage.transform import resize
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label
from skimage.morphology import closing, square, remove_small_objects
from loguru import logger

logger.info('Import ok')

# Remember to add napari.run() calls after each loop!
# from napari.utils.settings import SETTINGS
# SETTINGS.application.ipy_interactive = False

image_folder = f'python_results/initial_cleanup_zoom/'
mask_folder = f'python_results/cellpose_masking/'
output_folder = f'python_results/napari_masking/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)


def draw_masks(image_stack, image_name):

    feature_mask = np.zeros(image_stack.shape)

    with napari.gui_qt():
        # create the viewer and add the image
        viewer = napari.view_image(image_stack, name='image_stack')
        # add the labels
        viewer.add_labels(feature_mask, name='features')
        
        """
        - Select the cell layer and using the fill tool set to 0, remove all unwanted cells.
        - Repeat with the aggregates layer.
        - Finally, using the brush tool add or adjust any additional features (e.g. knobs) within the appropriate layer.
        """
        napari.run()
    feature_mask = label(feature_mask)

    np.save(f'{output_folder}{image_name}_mask.npy',
            np.stack([image_stack, feature_mask]))
    logger.info(f'Processed {image_name}. Mask saved to {output_folder}{image_name}')

    return np.stack([image_stack, feature_mask])

# ----------------Initialise file list----------------
# reading in all images

file_list = [filename for filename in os.listdir(image_folder) if '.tif' in filename]
images = {filename.replace('.tif', ''): skimage.io.imread(f'{image_folder}{filename}') for filename in file_list}

image_stack = np.load(f'{mask_folder}scaled_images_zoom.npy')
down_sized_images = {filename.replace('.tif', ''): image_stack[x, :, :] for x, filename in enumerate(file_list)}

# ----------------read in masks----------------
feature_masks = np.load(f'{mask_folder}cellpose_features.npy')

# interleave masks to create single stack per image
raw_masks = {
    image_name: feature_masks[x, :, :]
    for x, image_name in (enumerate(images.keys()))
}

# ----------------Manually filter masks----------------
# Run this chunk once to avoid over-writing masks
filtered_masks = {}
for image_name, image_stack in down_sized_images.items():
    filtered_masks[image_name] = draw_masks(
        image_stack, image_name)


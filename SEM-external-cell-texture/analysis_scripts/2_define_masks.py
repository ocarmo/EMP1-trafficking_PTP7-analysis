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

# Remember to add napari.run() calls after each loop!
# from napari.utils.settings import SETTINGS
# SETTINGS.application.ipy_interactive = False

# image_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/initial_cleanup/'
# mask_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/cellpose_masking/'
# output_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_masking/'
image_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/initial_cleanup_1/'
mask_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/cellpose_masking_1/'
output_folder = f'SEM-external-cell-texture/python_results/SEM-external-cell-texture_Analyzed/napari_masking_1/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)


def filter_masks(image_stack, image_name, mask_stack):

    cells = mask_stack[0, :, :].copy()
    feature_mask = mask_stack[1, :, :].copy()

    with napari.gui_qt():
        # create the viewer and add the image
        viewer = napari.view_image(image_stack, name='image_stack')
        # add the labels
        viewer.add_labels(cells, name='cells')
        viewer.add_labels(feature_mask, name='features')
        
        """
        - Select the cell layer and using the fill tool set to 0, remove all unwanted cells.
        - Repeat with the aggregates layer.
        - Finally, using the brush tool add or adjust any additional features (e.g. knobs) within the appropriate layer.
        """
        napari.run()
    # collect labelled shapes to individual structures
    cells = label(cells)
    feature_mask = label(feature_mask)

    np.save(f'{output_folder}{image_name}_mask.npy', np.stack([cells, feature_mask]))
    logger.info(f'Processed {image_name}. Mask saved to {output_folder}{image_name}')

    return np.stack([cells, feature_mask])


# ----------------Initialise file list----------------
# reading in all images, and transposing to correct dimension of array
file_list = [filename for filename in os.listdir(image_folder) if '.tif' in filename]
images = {filename.replace('.tif', ''): skimage.io.imread(f'{image_folder}{filename}') for filename in file_list}

image_stack = np.load(f'{mask_folder}scaled_images.npy')
down_sized_images = {filename.replace('.tif', ''): image_stack[x, :, :] for x, filename in enumerate(file_list)}

# ----------------read in masks and resize to match image shape----------------
cell_masks = np.load(f'{mask_folder}cellpose_cells_1.npy')
feature_masks = np.load(f'{mask_folder}cellpose_features_1.npy')

# interleave masks to create single stack per image
raw_masks = {
    image_name: np.stack([cell_masks[x, :, :], feature_masks[x, :, :]])
    for x, image_name in (enumerate(images.keys()))
}

# ----------------Manually filter masks----------------
# Run this chunk ONLY ONCE to avoid over-writing masks.
filtered_masks = {}
for image_name, image_stack in down_sized_images.items():
    mask_stack = raw_masks[image_name].copy()
    filtered_masks[image_name] = filter_masks(image_stack, image_name, mask_stack)

# to reprocess individual images:
# filtered_masks = {}
# images_to_process = ['10xPR_1']
# for image_name, image_stack in images.items():
#     if image_name in images_to_process:
#         mask_stack = raw_masks[image_name].copy()
#         # remove existing masks
#         if os.path.exists(f'{output_folder}{image_name}/'):
#             shutil.rmtree(f'{output_folder}{image_name}/') 
#         filtered_masks[image_name] = filter_masks(image_stack, image_name, mask_stack)

# ----------------Process filtered masks----------------
# To reload previous masks for per-cell extraction
filtered_masks = {masks.replace('_mask.npy', ''): np.load(f'{output_folder}{masks}') for masks in os.listdir(f'{output_folder}') if '.npy' in masks}

# For each set of masks, separate according to cell number
final_masks = {}
for image_name, image in images.items():
    image_name
    mask_stack = filtered_masks[image_name].copy()
    for cell_number in np.unique(mask_stack[0, :, :]):
        logger.info(cell_number)
        if cell_number > 0:
            cells = np.where(mask_stack[0, :, :] == cell_number, 1, 0)
            features = np.where(cells == 1, mask_stack[1, :, :], 0)
            features = label(features)

            final_masks[(image_name, cell_number)] = np.stack([cells, features])

# ----------------Save arrays----------------
for (image_name, cell_number), array_stack in final_masks.items():

    #create folder for each image output
    if not os.path.exists(f'{output_folder}{image_name}/'):
        os.makedirs(f'{output_folder}{image_name}/')

    # save associated cell mask arrays
    np.save(f'{output_folder}{image_name}/cell_{int(cell_number)}.npy', array_stack)

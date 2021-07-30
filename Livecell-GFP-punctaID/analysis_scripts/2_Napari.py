import napari
import numpy as np
import matplotlib.pyplot as plt
import os
import collections
import skimage.io
from loguru import logger
from skimage.measure import label
from skimage.segmentation import clear_border

# Remember to add napari.run() calls after each loop!
from napari.utils.settings import SETTINGS
SETTINGS.application.ipy_interactive = False

image_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/initial_cleanup/'
mask_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/cellpose_masking/'
output_folder = f'Livecell-GFP-punctaID/python_results/Livecell-GFP-punctaID_Analyzed/napari_masking/'


def filter_masks(image_stack, image_name, mask_stack):

    cells = mask_stack[0, :, :].copy()
    # remove cells touching the border
    cells = clear_border(cells)
    nuc_mask = mask_stack[1, :, :].copy()
    puncta_mask = np.where(mask_stack[0, :, :] != 0, mask_stack[2, :, :], 0).copy()

    # swap dic and gfp for ease of manual filtering
    dic = image_stack[0, :, :]
    gfp = image_stack[1, :, :]
    image_stack = np.stack([gfp,dic])

    with napari.gui_qt():
        # create the viewer and add the image
        viewer = napari.view_image(image_stack, name='image_stack')
        # add the labels
        viewer.add_labels(cells, name='cells', opacity = 0.02)
        viewer.add_labels(nuc_mask, name='nuclei', opacity=0.02)
        viewer.add_labels(puncta_mask, name='puncta', opacity=0.5)
        """
        - Select the cell layer and using the fill tool set to 0, remove all unwanted cells.
        - Repeat with the aggregates layer.
        - Finally, using the brush tool add or adjust any additional features (e.g. aggregates) within the appropriate layer.
        """
        napari.run()
        #viewer = napari.Viewer()
    
    # collect labelled shapes to individual structures
    cells = label(cells)
    nuc_mask = label(nuc_mask)
    puncta_mask = label(puncta_mask)

    np.save(f'{output_folder}{image_name}_mask.npy',
            np.stack([cells, nuc_mask, puncta_mask]))
    logger.info(
        f'Processed {image_name}. Mask saved to {output_folder}{image_name}')

    return np.stack([cells, nuc_mask, puncta_mask])


# ---------------Read in masks & initialise file list---------------
# read in numpy masks
cell_masks = np.load(f'{mask_folder}cellpose_cell_masks.npy')
nuc_masks = np.load(f'{mask_folder}cellpose_nuc_masks.npy')
puncta_masks = np.load(f'{mask_folder}cellpose_puncta_masks.npy')

file_list = [filename for filename in os.listdir(
    image_folder) if 'npy' in filename]
images = {filename.replace('.npy', ''): np.load(
    f'{image_folder}{filename}') for filename in file_list}

# interleave masks to create single stack per image
raw_masks = {
    image_name: np.stack([cell_masks[x, :, :], nuc_masks[x, :, :], puncta_masks[x, :, :]])
    for x, image_name in (enumerate(images.keys()))}

# ---------------Manually filter masks---------------
# ONLY RUN THIS CHUNK ONCE. Manually filter GFP-puncta and nuclei (if ≥2 nuclei per cell).
filtered_masks = {}
for image_name, image_stack in images.items():
    mask_stack = raw_masks[image_name].copy()
    filtered_masks[image_name] = filter_masks(
        image_stack, image_name, mask_stack)

# ---------------Process filtered masks---------------
# To reload previous masks for per-cell extraction
filtered_masks = {masks.replace('_mask.npy', ''): np.load(
    f'{output_folder}{masks}') for masks in os.listdir(f'{output_folder}') if '.npy' in masks}

# For each set of masks, separate according to cell number
final_masks = {}
for image_name, image in images.items():
    mask_stack = filtered_masks[image_name].copy()
    for cell_number in np.unique(mask_stack[0, :, :]):
        if cell_number > 0:
            whole_cell = np.where(mask_stack[0, :, :] == cell_number, 1, 0)
            nucleus = np.where(whole_cell == 1, mask_stack[1, :, :], 0)
            cytoplasm = np.where(nucleus == 0, whole_cell, 0)
            # remove nuclear GFP signal by using cytoplasm mask condition
            puncta = np.where(cytoplasm == 1, mask_stack[2, :, :], 0)
            for coord in nucleus:
                # filter for cells that contain a nucleus
                if coord.any() == 1:
                    nucleus = label(nucleus)
                    puncta = label(puncta)

                    final_masks[(image_name, cell_number)
                                ] = np.stack([cytoplasm, nucleus, puncta])

# ---------------save arrays---------------
for (image_name, cell_number), array_stack in final_masks.items():

    #create folder for each image output
    if not os.path.exists(f'{output_folder}{image_name}/'):
        os.makedirs(f'{output_folder}{image_name}/')

    # save associated cell mask arrays
    np.save(f'{output_folder}{image_name}/cell_{int(cell_number)}.npy', array_stack)
    logger.info(f'{image_name}-{cell_number} saved')

import os
import numpy as np
import matplotlib.pyplot as plt
import skimage.io
from cellpose import models
from cellpose import plot
import collections
from loguru import logger

import napari
# Remember to add napari.run() calls after each loop!
from napari.utils.settings import SETTINGS
SETTINGS.application.ipy_interactive = False

logger.info('Import ok')

input_folder = f'python_results/initial_cleanup/'
output_folder = f'python_results/cellpose_masking/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)


def apply_cellpose(images, image_type, channels=[0, 0], diameter=None, flow_threshold=0.4, cellprob_threshold=0.0):
    """Apply model to list of images. Returns masks, flows, styles, diams.
    - model type is 'cyto' or 'nuclei'
    - define CHANNELS to run segementation on (grayscale=0, R=1, G=2, B=3) where channels = [cytoplasm, nucleus]. If NUCLEUS channel does not exist, set the second channel to 0
    """
    model = models.Cellpose(model_type=image_type)
    masks, flows, styles, diams = model.eval(
        images, diameter=diameter, channels=channels, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold)
    return masks, flows, styles, diams


def visualise_cell_pose(images, masks, flows, channels=[0, 0]):
    """Display cellpose results for each image
    """
    for image_number, image in enumerate(images):
        maski = masks[image_number]
        flowi = flows[image_number][0]

        fig = plt.figure(figsize=(12, 5))
        plot.show_segmentation(fig, image, maski, flowi, channels=channels)
        plt.tight_layout()
        plt.show()


# ---------------Initialise file list---------------
npy_list = [filename for filename in os.listdir(
    input_folder) if 'npy' in filename]

np_imgs = [np.load(f'{input_folder}{filename}') for filename in npy_list]

# ---------------outline cell---------------
# collecting only channel 0 (BF) for cytoplasm
cyto_masks = [image[0, :, :] for image in np_imgs]

# Apply cellpose then visualise
cell_masks, flows, styles, diams = apply_cellpose(
    cyto_masks, image_type='cyto', diameter=60)
visualise_cell_pose(cyto_masks, cell_masks, flows, channels=[0, 0])

# ---------------outline nuclei---------------
# collecting only channel 0 (BF) for nuclei
nuclei_masks = [image[0, :, :] for image in np_imgs]

# Apply cellpose then visualise
nuc_masks, nuc_flows, nuc_styles, nuc_diams = apply_cellpose(
    nuclei_masks, image_type='nuclei', diameter=30)
visualise_cell_pose(nuclei_masks, nuc_masks, nuc_flows, channels=[0, 0])

# ---------------outline gfp puncta---------------
# collecting only channel 1 (FITC) for gfp puncta
gfp_puncta_mask = [image[1, :, :] for image in np_imgs]
# plt.imshow(gfp_puncta_mask[0])

puncta_masks, puncta_flows, puncta_styles, puncta_diams = apply_cellpose(
    gfp_puncta_mask, image_type='nuclei', diameter=6, cellprob_threshold=-10, flow_threshold=100)
visualise_cell_pose(gfp_puncta_mask, puncta_masks,
                    puncta_flows, channels=[0, 0])

# ---------------Save masks---------------
# save associated cell mask arrays
np.save(f'{output_folder}cellpose_cell_masks.npy', cell_masks)
np.save(f'{output_folder}cellpose_nuc_masks.npy', nuc_masks)
np.save(f'{output_folder}cellpose_puncta_masks.npy', puncta_masks)

from skimage.morphology import closing, square, remove_small_objects
from skimage.measure import label
from skimage.segmentation import clear_border
from skimage.filters import threshold_otsu
import os
import numpy as np
import matplotlib.pyplot as plt
import skimage.io
import skimage
from skimage.color import rgb2gray
from skimage import exposure
import pandas as pd
from cellpose import models
from cellpose import plot
import collections
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
import cv2
from skimage.feature import canny
from scipy import ndimage as ndi
from skimage import morphology
from skimage.filters import try_all_threshold
from loguru import logger

input_folder = f'python_results/initial_cleanup_zoom/'
output_folder = f'python_results/cellpose_masking/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)


def apply_cellpose(images, image_type='cyto', channels=[0,0], diameter=None, flow_threshold=0.4, cellprob_threshold=0.0):
    """Apply model to list of images. Returns masks, flows, styles, diams.
    - model type is 'cyto' or 'nuclei'
    - define CHANNELS to run segementation on (grayscale=0, R=1, G=2, B=3) where channels = [cytoplasm, nucleus]. If NUCLEUS channel does not exist, set the second channel to 0
    """
    model = models.Cellpose(model_type=image_type)
    masks, flows, styles, diams = model.eval(images, diameter=diameter, channels=channels, flow_threshold=flow_threshold, cellprob_threshold=cellprob_threshold)
    return masks, flows, styles, diams

def visualise_cell_pose(images, masks, flows, channels=[0,0]):
    """Display cellpose results for each image
    """
    for image_number, image in enumerate(images):
        maski = masks[image_number]
        flowi = flows[image_number][0]

        fig = plt.figure(figsize=(12,5))
        plot.show_segmentation(fig, image, maski, flowi, channels=channels)
        plt.tight_layout()
        plt.show()

# ----------------Initialise file list----------------
file_list = [filename for filename in os.listdir(input_folder) if '.tif' in filename]

# reading in all channels for each image, and transposing to correct dimension of array
imgs = [skimage.io.imread(f'{input_folder}{filename}') for filename in file_list]

# clean filenames
img_names = [filename.replace('.tif', '') for filename in file_list]

# ----------------Collect images, remove background----------------
# resize to more useable image dimensions
scaled_images = []
for x, (image_name, image) in enumerate(zip(img_names, imgs)):
    # make image sizes consistent
    resize = cv2.resize(image, dsize=(6144, 4376), interpolation=cv2.INTER_CUBIC)
    # trim label section
    new_image = resize[:4096, :].copy()
    new_image = skimage.transform.resize(
        new_image, (new_image.shape[0] / 8, new_image.shape[1] / 8), anti_aliasing=True, anti_aliasing_sigma=None) * 255
    scaled_images.append(new_image)

# ----------------outline aggregates----------------
feature_masks, feature_flows, feature_styles, feature_diams = apply_cellpose(scaled_images, image_type='nuclei', diameter=8, flow_threshold=10)
visualise_cell_pose(
    scaled_images, feature_masks, feature_flows, channels=[0, 0])

# ----------------save scaled images & masks----------------
# save scaled images - note these have the gamma and size adjusted so should NOT be used for intensity quantitation
np.save(f'{output_folder}scaled_images.npy', np.stack(scaled_images))
# save associated cell mask arrays
np.save(f'{output_folder}cellpose_features.npy', feature_masks)
np.save(f'{output_folder}scaled_images_zoom.npy', np.stack(scaled_images))

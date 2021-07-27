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

logger.info('Import ok')

# input_folder = f'experimental_data/initial_cleanup/'
# output_folder = f'python_results/cellpose_masking/'
input_folder = f'experimental_data/initial_cleanup_1/'
output_folder = f'python_results/cellpose_masking_1/'

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

# find pixel width of each image
pixel_width_list = []
pixel_width_list = [skimage.io.imread(
    f'{input_folder}{filename}') for filename in file_list]
pixel_width_list = [arr.shape[1] for arr in pixel_width_list]

# zip together filenames and image widths
image_width = pd.DataFrame(zip(img_names, pixel_width_list), columns = ['img_name','pixel_w'])

# make list of small images
small_images = []
small_images = image_width.loc[(image_width['pixel_w'] != 6144), [
    'img_name', 'pixel_w']]
small_images = small_images['img_name'].tolist()

# ----------------Collect images, remove background----------------
# resize to more useable image dimensions
scaled_images = []
for x, (image_name, image) in enumerate(zip(img_names, imgs)):
    if image_name in small_images:
        # inflate small images by factor of 2
        resize = cv2.resize(image, dsize=(6144, 4376), interpolation=cv2.INTER_CUBIC)
        # trim label section
        new_image = resize[:4096, :].copy()
        # new_image = gaussian_filter(new_image, sigma=200)
        new_image = exposure.adjust_gamma(new_image, 2)
        new_image = skimage.transform.resize(
            new_image, (new_image.shape[0] / 8, new_image.shape[1] / 8), anti_aliasing=True, anti_aliasing_sigma=None) * 255
        scaled_images.append(new_image)
    else:
        # trim label section
        new_image = image[:4096, :].copy()
        # new_image = gaussian_filter(new_image, sigma=200)
        new_image = exposure.adjust_gamma(new_image, 2)
        new_image = skimage.transform.resize(new_image, (new_image.shape[0] / 8, new_image.shape[1] / 8), anti_aliasing=True, anti_aliasing_sigma=None) * 255
        scaled_images.append(new_image)

for image in scaled_images:
    plt.imshow(image)
    plt.show()

# combine into single image, with padding between
combined_image = np.concatenate([np.vstack((np.full((100, image.shape[1]), np.mean(image.flatten())), image)) for image in scaled_images])
plt.imshow(combined_image)

# Apply cellpose then visualise
masks, flows, styles, diams = apply_cellpose([combined_image], image_type='nuclei', diameter=500, flow_threshold=0.8)
visualise_cell_pose([combined_image], masks, flows, channels=[0, 0])

# extract individual cell masks
mask = masks[0]
individual_cell_masks = [arr[100:, :] for arr in np.split(mask, len(scaled_images), axis=0)]

# ----------------outline aggregates----------------
feature_masks, feature_flows, feature_styles, feature_diams = apply_cellpose(scaled_images, image_type='nuclei', diameter=5, flow_threshold=10, cellprob_threshold=-6)
visualise_cell_pose(scaled_images, feature_masks, feature_flows, channels=[0, 0])

# ----------------save arrays----------------
np.save(f'{output_folder}cellpose_cells_1.npy', individual_cell_masks)
np.save(f'{output_folder}cellpose_features_1.npy', feature_masks)
# save scaled images - note these have the gamma and size adjusted so should NOT be used for intensity quantitation:
np.save(f'{output_folder}scaled_images_1.npy', np.stack(scaled_images))

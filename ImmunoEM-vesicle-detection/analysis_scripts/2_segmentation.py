import collections
import os

#import cv2
import higra as hg
import matplotlib.pyplot as plt
import napari
import numpy as np
import pandas as pd
import skimage.io
from loguru import logger

from scipy.ndimage import gaussian_filter
from skimage import (filters, img_as_float, io, measure, segmentation, viewer, morphology)
from skimage.filters import (gaussian, threshold_otsu)
from skimage.measure import label, regionprops
from skimage.morphology import (closing, label, reconstruction, remove_small_objects, square)

import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

from collections import defaultdict

input_folder = f'python_results/initial_cleanup/'
output_folder = f'python_results/segmentation/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def plot_reconstruction(image, dilated, image_name):
    fig, (ax0, ax1, ax2) = plt.subplots(nrows=1,
                                        ncols=3,
                                        figsize=(8, 2.5),
                                        sharex=True,
                                        sharey=True)

    ax0.imshow(image, cmap='gray')
    ax0.set_title('original image')
    ax0.axis('off')

    ax1.imshow(dilated, vmin=image.min(), vmax=image.max(), cmap='gray')
    ax1.set_title('dilated')
    ax1.axis('off')

    ax2.imshow(image - dilated, cmap='gray')
    ax2.set_title('image - dilated')
    ax2.axis('off')

    plt.suptitle(f"Image {image_name}")

    fig.tight_layout()
    plt.show()


def higra_watershed(img, area_thold=500):
    """Alternate to traditional watershedding taken from here: # https://stackoverflow.com/questions/62896061/merge-image-segments-depending-on-length-of-the-watershed-line-in-between-using

    Parameters
    ----------
    img : [np array]
        image to be watershedded (recommended to first binary mask and gaussian blur)
    area_thold : int, optional
        minimum size of generated regions, by default 500
    """    

    size = img.shape[:2]
    graph = hg.get_4_adjacency_graph(size)
    
    edge_weights = hg.weight_graph(graph, img, hg.WeightFunction.mean)
    tree, altitudes = hg.quasi_flat_zone_hierarchy(graph, edge_weights)

    attr = hg.attribute_volume(tree, altitudes)

    saliency = hg.saliency(tree, attr) 
    # Take a look at this :)
    # grid = hg.graph_4_adjacency_2_khalimsky(graph, saliency)
    # plt.imshow(grid)
    # plt.show()
    
    attr_thold = np.mean(saliency) / 4  # arbitrary

    segments = hg.labelisation_horizontal_cut_from_threshold(tree, attr, attr_thold)
    segments = measure.label(remove_small_objects(segments, area_thold))

    # with napari.gui_qt():
    #     viewer = napari.view_image(image)
    #     viewer.add_labels(segments, name='segmentation')
    
    return segments


def plot_interactive_properties(image, labels, properties_to_show=[]):

    if len(properties_to_show) < 1:

        properties_to_show = ['area',
        'centroid',
        'convex_area',
        'eccentricity',
        'euler_number',
        'local_centroid',
        'major_axis_length',
        'minor_axis_length',
        'orientation',
        'perimeter',
        'solidity']

    fig = px.imshow(image, binary_string=True)
    fig.update_traces(hoverinfo='skip') # hover is only for label info


    props = measure.regionprops(labels, image)

    # For each label, add a filled scatter trace for its contour,
    # and display the properties of the label in the hover of this trace.
    for index in range(len(np.unique(labels))-1):
        label = props[index].label
        contour = measure.find_contours(labels == label, 0.5)[0]
        y, x = contour.T
        hoverinfo = ''.join(
            f'<b>{prop_name}: {getattr(props[index], prop_name)}</b><br>'
            for prop_name in properties_to_show
        )

        fig.add_trace(go.Scatter(
            x=x, y=y, name=label,
            mode='lines', fill='toself', showlegend=False,
            hovertemplate=hoverinfo, hoveron='points+fills'))

    return fig


def prepare_for_labelling(image):
    # Initial inversion and blur
    inv_image = (255 - image)
    image = img_as_float(inv_image)
    image = gaussian_filter(image, 3)
    # Remove background using regional maximum
    seed = np.copy(image)
    seed[1:-1, 1:-1] = image.min()
    mask = image
    dilated = reconstruction(seed, mask, method='dilation')
    img = (image - dilated)
    plot_reconstruction(image, dilated, image_name)
    # threshold, fill holes, then blur result
    thresh = threshold_otsu((255-img))
    bw = closing( (255-img) < thresh, square(5))
    blur = filters.gaussian(bw, sigma=3)
    # perform inverse binary thresholding
    mask = blur < 0.1
    # final blur step
    blur_mask = filters.gaussian(mask, sigma=2)
    return blur_mask


# ----------------Initialise file list----------------
# read in pre-stacked arrays if 'tif' in filename (or more specific label)
file_list = [filename for filename in os.listdir(
    input_folder) if '2021062' in filename]

# reading in all images, and transposing to correct dimension of array
images = {filename.replace('.tif', ''): skimage.io.imread(f'{input_folder}{filename}') for filename in file_list}

# remove the scale bar at the bottom - assuming images are square, should be 4096x4096 (remove 128 pixels)
images = {key: image[:4096, :] for key, image in images.items()}

# ----------------to process a subset of images, add items to the list----------------
images_to_process = [filename.replace('.tif', '')
                     for filename in file_list]

if len(images_to_process) < 1:
    images_to_process = list(images.keys())
    logger.info('Processing all images')

# ----------------generate segmentation for each ROI----------------
segmentation = defaultdict(dict)

# Prepare initial images for segmentation
for image_name in images_to_process:
    image = images[image_name]

    # prepare image with background removal, sequential blur and masking
    clean_image = prepare_for_labelling(image) 
    segmentation[image_name]['clean_image'] = clean_image

# Perform higra watershed segmentation and labelling
possible_properties = ['area', 'centroid', 'convex_area', 'eccentricity', 'euler_number', 'label', 'local_centroid', 'major_axis_length', 'minor_axis_length', 'orientation', 'perimeter', 'solidity']
for image_name in images_to_process:
    clean_image = segmentation[image_name]['clean_image'].copy()
    labelled_image = higra_watershed(clean_image, area_thold=300)
    properties =  pd.DataFrame(measure.regionprops_table(labelled_image, properties=possible_properties))

    # filter only large objects
    properties = properties[properties['area'] > 3000]
    segmentation[image_name]['properties'] = properties

    # select only big objects in label mask
    big_labels = properties['label'].tolist()
    big_objects_mask = np.isin(labelled_image, big_labels)
    big_objects = np.where(big_objects_mask, labelled_image, 0)
    segmentation[image_name]['segmentation'] = big_objects

# optional: plot interactive version of labelled objects overlayed on original image
# for image_name in images_to_process:
#     big_objects = segmentation[image_name]['segmentation']
#     image = images[image_name]
#     fig = plot_interactive_properties(image, big_objects)
#     fig.show()

# Assign labelled features to new label based on convex_area vs eccentricity
for image_name in images_to_process:
    big_objects = segmentation[image_name]['segmentation']
    properties = segmentation[image_name]['properties']

    membranes_mask = np.isin(big_objects, properties[properties['eccentricity'] > 0.9]['label'].tolist())
    big_objects = np.where(membranes_mask, 1, big_objects)

    clefts_mask = np.isin(big_objects, properties[(properties['eccentricity'] < 0.9) & (properties['convex_area'] > 500000)]['label'].tolist())
    big_objects = np.where(clefts_mask, 2, big_objects)

    vesicles_mask = np.isin(big_objects, properties[(properties['eccentricity'] < 0.9) & (properties['convex_area'] < 500000)]['label'].tolist())
    big_objects = np.where(vesicles_mask, 3, big_objects)

    segmentation[image_name]['structural_features'] = big_objects

for image_name in images_to_process:
    image = images[image_name]
    features = segmentation[image_name]['structural_features']

    # to visualise an example image
    with napari.gui_qt():
       viewer = napari.view_image(image)
       viewer.add_labels(features, name='features')

# ----------------Save image, mask to np array----------------
for image_name in images_to_process:
    image = images[image_name]
    mask = segmentation[image_name]['structural_features']

    # save associated arrays
    np.save(f'{output_folder}{image_name}.npy', np.array([image, mask]))
    logger.info(f'Segmentation for {image_name} saved.')

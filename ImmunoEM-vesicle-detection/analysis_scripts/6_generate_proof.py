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

logger.info('Import OK')

input_path = 'ImmunoEM-vesicle-detection/python_results/ImmunoEM-vesicle-detection_Analyzed/feature_summaries/'
output_folder = 'ImmunoEM-vesicle-detection/python_results/ImmunoEM-vesicle-detection_Analyzed/plot/'
feature_masks_folder = 'ImmunoEM-vesicle-detection/python_results/ImmunoEM-vesicle-detection_Analyzed/feature_validation_combined/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# --------------Initialise file lists--------------
min_distances = pd.read_csv(f'{input_path}min_distances.csv')

# reading in feature arrays
image_narray_list = [
    filename for filename in os.listdir(feature_masks_folder)]
valid_narrays = {filename.replace('.npy', ''): np.load(
    f'{feature_masks_folder}{filename}') for filename in image_narray_list}

# --------------Dataframe work--------------
# using eval to replace coordinate strings with coordinate tuples
min_distances['vesicle_coord'] = [eval(row)
                                  for row in min_distances['vesicle_coord']]
min_distances['otherRoi_coord'] = [
    eval(row) for row in min_distances['otherRoi_coord']]

# keep the min distance to cleft & membrane
min_distances = min_distances.iloc[min_distances.groupby(['vesicle_key'])['measure_distance'].idxmin()]
min_distances = min_distances.reset_index(drop=True)

# --------------Plotting--------------
for image_name, stack in valid_narrays.items():
    image_name
    # unpack
    image = stack[0, :, :]
    # where = (condition, true, false) to make binary shapes
    membrane = np.where(stack[1, :, :] != 0, 255, np.nan)
    cleft = np.where(stack[2, :, :] != 0, 255, np.nan)
    vesicle = np.where(stack[3, :, :] != 0, 255, np.nan)

    coord_df = pd.DataFrame()
    coord_df['vesicle'] = min_distances.loc[min_distances['image']
                                            == image_name, 'vesicle_coord'].reset_index(drop=True)

    coord_df['other'] = min_distances.loc[min_distances['image']
                                          == image_name, 'otherRoi_coord'].reset_index(drop=True)

    coord_list = coord_df.values.tolist()

    fig, ax = plt.subplots()
    plt.imshow(image, cmap='Greys_r', origin='lower')
    plt.imshow(membrane, cmap='Purples_r', origin='lower')
    plt.imshow(cleft, cmap='Blues_r', alpha=0.6, origin='lower')
    plt.imshow(vesicle, cmap='Oranges_r', alpha=0.6, origin='lower')

    for coord in coord_list:
        y, x = zip(*coord)
        plt.plot(x, y, color="Magenta", linewidth=0.5)
        # add arrowprops
    plt.axis('off')

    # Create scale bar
    scalebar = ScaleBar(540, 'nm', location = 'lower right', pad = 0.3, sep = 2, box_alpha = 0)
    ax.add_artist(scalebar)
    plt.show()

    fig.savefig(f'{output_folder}{image_name}.png')
    logger.info(f'Proof for {image_name} saved.')
    plt.clf()

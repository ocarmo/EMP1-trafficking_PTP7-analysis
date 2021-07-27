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
from loguru import logger

logger.info('Import OK')

input_path = 'python_results/feature_summaries/'
output_folder = 'python_results/plot/'
image_folder = 'python_results/initial_cleanup/'
feature_masks_folder = 'python_results/feature_validation/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# --------------Initialise file lists--------------
feature_area = pd.read_csv(f'{input_path}feature_area.csv')
min_distances = pd.read_csv(f'{input_path}min_distances.csv')
vesicles_to_clefts = pd.read_csv(f'{input_path}vesicles_to_clefts.csv')
# ------------------Plot results------------------
feature_colors = {'vesicle': 'paleturquoise',
          'cleft': 'rebeccapurple', 'membrane': 'darkorange'}

cell_line_dict = {'CS2': 'CS2',
                  'OC03': 'CS2∆85c', 'OC55': '1-317', 'OC48': '∆265-317'}

cell_line_dict = {'CS2': 'paleturquoise',
                  'OC03': 'darkorange', 'OC60': 'rebeccapurple', 'OC61': 'darkred', 'OC62': 'green', 'OC63':'blue'}

display_name_colors = {'CS2': 'paleturquoise',
                       'CS2∆85c': 'darkorange', '1-317': 'rebeccapurple', '∆265-317': 'darkred'}

# plot the two datasets
for (roi_type), roi_type_df in min_distances.groupby(['otherRoi']):
    roi_type_df
    fig, ax = plt.subplots()
    plt.title(roi_type)
    sns.histplot(x=roi_type_df['measure_distance'], kde=True,
                 binwidth=50, hue=roi_type_df['cell_line'])
    # fig.savefig(f'{output_folder}{roi_type}_{group}.svg')
    # logger.info(f'Distance plot for {roi_type} saved.')
    # plt.show()



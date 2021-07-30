import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import skimage
from skimage import measure
import napari
import pytesseract
import skimage.io
import re
import cv2
from loguru import logger

logger.info('Import OK')

image_folder = f'SEM-internal-cell-texture/python_results/SEM-internal-cell-texture_Analyzed/initial_cleanup_zoom/'
output_folder = f'SEM-internal-cell-texture/python_results/SEM-internal-cell-texture_Analyzed/napari_scale/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# --------------Initialize file lists--------------
# reading in all images
file_list = [filename for filename in os.listdir(
    image_folder) if '.tif' in filename]

# reading in all channels for each image, and transposing to correct dimension of array
imgs = [skimage.io.imread(f'{image_folder}{filename}')
        for filename in file_list]

# clean filenames
img_names = [filename.replace('.tif', '') for filename in file_list]

# --------------Find scale bar HFW value--------------
label_panels = []
# perform scaling to enable easier CellPose
for x, (image_name, image) in enumerate(zip(img_names, imgs)):
    # make all images same dimensions
    resize = cv2.resize(image, dsize=(6144, 4376),
                        interpolation=cv2.INTER_CUBIC)
    # trim label section
    new_image = resize[4096:6144, :].copy()        
    image_string = pytesseract.image_to_string(new_image)
    # append to list
    label_panels.append(str(image_string))
    # to visualize
    # plt.imshow(new_image)
    
# remove new lines (number of new lines can vary per label)
scale_hfw_list = [row.replace('\n', '') for row in label_panels]

# make regular expression list for splitting labels
regular_exp = ['mag', 'mode', 'nm', 'mm', 'um', 'pm', 'Tt', ' ']
regex = r"\b(?:{})\b".format("|".join(regular_exp))

# zip together file_list and scalebar_text_list
image_string_df = pd.DataFrame(list(map(list, zip(file_list, scale_hfw_list))), columns = ['image_name', 'image_string'])

# select nth element corresponding to HFW (µm) measurement
image_string_df['substring'] = [(re.split(regex, row))
                      for row in image_string_df['image_string']]
image_string_df['substring'] = [row[-4]
                                for row in image_string_df['substring']]

# fill rows with '0' if incorrect length
image_string_df['substring'] = [row if len(row) == 4 else '0' for row in image_string_df['substring']]

# Make HFW (µm) measurement a float
image_string_df['substring'] = [float(row) for row in image_string_df['substring']]

# Isolate images with 0.00 values (where HFW must be manually entered)
find_hfw_df = image_string_df.loc[image_string_df['substring']==0]

# --------------Export extracted and 'to find' scale bars--------------
find_hfw_df.to_csv(f'{output_folder}find_hfw.csv')
image_string_df.to_csv(f'{output_folder}hfw.csv')

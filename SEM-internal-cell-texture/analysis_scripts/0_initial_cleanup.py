import os
import re
from shutil import copyfile
import numpy as np
import skimage.io
from loguru import logger

logger.info('Import ok')

input_path = f'/Users/oliviacarmo/Desktop/Microscopy/EM/SEM/20180716_AB35_Pf_CS2_OC-KOs'
output_path = f'python_results/initial_cleanup_zoom/'

if not os.path.exists(f'{output_path}'):
    os.makedirs(f'{output_path}')


def jarvis(input_path, output_path):
    file_list = [[f'{root}/{filename}' for filename in files if '.tif' in filename] for root, dirs, files in os.walk(f'{input_path}')]
    # flatten file_list
    file_list = [item for sublist in file_list for item in sublist]
    # List of key words to not quantitate (e.g. 3D7c background cell lines)
    do_not_quantitate = ['OC03b', 'Uninf']
    test_list = []

    for filename in file_list:
        # collect one 'zoom' image per cell (there is one _02 zoomed image per cell)
        if '_02' in filename:
            if not any(word in filename for word in do_not_quantitate):
                test_list.append(filename)
                acquisition_date = filename.split('/')[7].split('_')[0]
                cellline = filename.split('/')[-1].split('_')[1]
                image_number = re.split(
                        '_|\.|-', filename.split('Cell')[-1])[0].zfill(2)
                # below commented out for Adam's data set in favor of line above
                # image_number = re.split('_|\.|-', filename.split('/')[-1])[0].zfill(2)
                new_name = f'{acquisition_date}-{cellline.upper()}-{image_number}.tif'
                logger.info(f'{new_name}')
                copyfile(filename, output_path+new_name)


#----------------Run Jarvis :)----------------
jarvis(input_path, output_path)

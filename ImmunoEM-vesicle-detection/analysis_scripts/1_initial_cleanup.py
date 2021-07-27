import os
import re
from shutil import copyfile
import numpy as np
import skimage.io

from loguru import logger
logger.info('Import ok')

input_path = f'/Users/oliviacarmo/Desktop/Microscopy/EM/ImmunoEM/20210629_Olivia_ImmunoEM'
output_path = f'python_results/initial_cleanup/'


def jarvis(input_path, output_path):

    file_list = [[f'{root}/{filename}' for filename in files if '.tif' in filename] for root, dirs, files in os.walk(f'{input_path}')]
    # flatten file_list
    file_list = [item for sublist in file_list for item in sublist]
    # List of key words to not quantitate (e.g. negative control or poorly scaled datasets)
    do_not_quantitate = ['NONE', 'scale', 'dup', 'focus']
    for filename in file_list:
        nonestest_path = 10
        nested_path = 11
        # if len(filename.split('/')) == nonestest_path:
        #     acquisition_date = filename.split('/')[7].split('_')[0]
        #     experiment_date = acquisition_date
        # I only want the nested files (nested_path) for quantitation
        if len(filename.split('/')) == nonestest_path:
            if not any(word in filename for word in do_not_quantitate):
                filename
                acquisition_date = filename.split('/')[7].split('_')[0]
                #experiment_date = filename.split('/')[8]
                cellline, antisera = re.split(r' |_',filename.split('/')[-2])
                image_number = re.split('_|\.|-', filename.split('/')[-1])[0].zfill(2)
                #new_name = f'{acquisition_date}-{experiment_date}-{cellline.upper()}-{antisera.upper()}-{image_number}.tif'
                new_name = f'{acquisition_date}-{cellline.upper()}-{antisera.upper()}-{image_number}.tif'
                logger.info(f'{new_name}')
                copyfile(filename, output_path+new_name)

# --------------Run jarvis :)--------------
jarvis(input_path, output_path)

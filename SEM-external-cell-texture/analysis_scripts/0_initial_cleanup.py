import os
import re
from shutil import copyfile
from loguru import logger

logger.info('Import ok')

# input_path = f'/Users/oliviacarmo/Desktop/Microscopy/EM/SEM/20210412_Olivia_SEM'
# output_path = f'python_results/initial_cleanup/'
input_path = f'/Users/oliviacarmo/Desktop/Microscopy/EM/SEM/20180703_cs2_oc03_whole'
output_path = f'experimental_data/initial_cleanup_1/'

if not os.path.exists(f'{output_path}'):
    os.makedirs(f'{output_path}')
                

def jarvis(input_path, output_path):
    file_list = [[f'{root}/{filename}' for filename in files if '.tif' in filename] for root, dirs, files in os.walk(f'{input_path}')]
    # flatten file_list
    file_list = [item for sublist in file_list for item in sublist]
    do_not_quantitate = ['OC48', 'OC55']
    for filename in file_list:
        nested_path = 10
        if len(filename.split('/')) == nested_path:
            if not any(word in filename for word in do_not_quantitate):
                acquisition_date = filename.split('/')[7].split('_')[0]
                cellline = filename.split('/')[-2]
                image_number = re.split(
                    '_|\.|-', filename.split('Cell')[-1])[0].zfill(2)
                # # commented out line below for '20180703_cs2_oc03_whole' dataset in favor of line above
                # image_number = re.split('_|\.|-', filename.split('/')[-1])[0].zfill(2)
                new_name = f'{acquisition_date}-{cellline.upper()}-{image_number}.tif'
                logger.info(f'{new_name}')
                copyfile(filename, output_path+new_name)


# ---------------Run jarvis---------------
jarvis(input_path, output_path)

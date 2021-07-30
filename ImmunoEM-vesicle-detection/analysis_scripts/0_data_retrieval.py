# script adapted from https://github.com/dezeraecox-manuscripts/COX_Proteome-stability
import os
import re
import zipfile
import gzip
import shutil
from shutil import copyfile
from loguru import logger
from contextlib import closing
import urllib.request as request
import tarfile

logger.info('Import OK')


def download_resources(filename, url, resource_folder):
    """
    Worker function to download and save file from URL.
    
    inputs
    ======
    filename: (str) name of output file (including extension)
    url: (str) complete location of file to be downloaded
    output_path: (str) relative or complete path to directory where folder will be saved.
    returns:
    ======
    None
    """
    if not os.path.exists(resource_folder):
        os.makedirs(resource_folder)

    try:
        with closing(request.urlopen(url)) as r:
            with open(f'{resource_folder}{filename}', 'wb') as f:
                shutil.copyfileobj(r, f)
        logger.info(f'Downloaded {filename}')
    except:
        logger.info(f'Downloaded failed for {filename}.')


if __name__ == "__main__":

    url = 'https://zenodo.org/record/5146871/files/ImmunoEM-vesicle-detection_Analyzed.zip?download=1'
    file_name = 'ImmunoEM-vesicle-detection'
    output_folder = 'ImmunoEM-vesicle-detection/python_results'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Download file from repository
    download_resources(
        filename=f'{folder_name}.zip', url=url, resource_folder=output_folder)
    with zipfile.ZipFile(f'{output_folder}{folder_name}.zip', 'r') as zip_ref:
        zip_ref.extractall(f'{output_folder}')

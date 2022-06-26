import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import napari
from loguru import logger

logger.info('Import OK')

input_folder = 'raw_data/'
output_folder = 'python_results/summary_results/'
napari_output_folder = 'python_results/napari/'
images_folder = 'python_results/images/'

# initialize python_results folders
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
    
if not os.path.exists(images_folder):
    os.mkdir(images_folder)
    
if not os.path.exists(napari_output_folder):
    os.mkdir(napari_output_folder)

def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])


def filter_proofs(image, image_name):
    """If FIJI Macro segmentation was poor, use paint brush or fill tool to mark the image. Marked images (irregardless of color/label) will be filtered out as 'invalid'

    Args:
        image (ndarray): np array of proof image
        image_name (str): image name key

    Returns:
        image (nd_array): stacked np array of original [0] and labeled [1] image
    """
    
    proof = image[0, :, :].copy()
    mark_if_invalid = image[1, :, :].copy()

    # create the viewer and add the image
    viewer = napari.view_image(proof, name='proof')
    # add the labels
    viewer.add_labels(mark_if_invalid, name='mark_if_invalid')
    napari.run()

    np.save(f'{napari_output_folder}{image_name}_mask.npy',
            np.stack([proof, mark_if_invalid]))
    logger.info(
        f'Processed {image_name}. Mask saved to {napari_output_folder}{image_name}')

    return np.stack([proof, mark_if_invalid])


# ---------------- initialize file list ----------------
desktop_dir = '/Users/oliviacarmo/Desktop/PF3D7_0301700-tag_timecourses/'

# set up co-occur dataframe
data_list = [f'{input_folder}{filename}' for filename in os.listdir(
    input_folder) if 'csv' in filename]
cooccur_df = pd.concat(map(pd.read_csv, data_list)).reset_index(drop=True)

# read in filelist all proofs
file_list = [[f'{root}/{filename}' for filename in files if 'co-occ_proof.tif' in filename] for root, dirs, files in os.walk(f'{desktop_dir}')]

# flatten file_list
file_list = [item for sublist in file_list for item in sublist if '4PX' not in item]

# copy all images #! comment out when completed to avoid re-writing
for file_path in file_list:
    img = plt.imread(file_path)
    # convert to grayscale
    gray = rgb2gray(img).astype(int)
    # make name more human readable
    img_name = ''.join(file_path.split('/')[-1].split('.')[:-2])
    np.save(f'{images_folder}{img_name}.npy', gray)

# ---------------- quality control using proofs ----------------
# list of viable proofs, keep cells with 4<x<60 puncta total
cooccur_df = cooccur_df[(cooccur_df['C2_only'] >= 4) & (
    cooccur_df['C2_only'] < 60)]
cooccur_df = cooccur_df[(cooccur_df['C3_only'] >= 4) & (
    cooccur_df['C3_only'] < 60)]
cooccur_df['Imagename'] = [
    ''.join(row.split('.')[:-2]) for row in cooccur_df['Imagename']]

viable_img_names = cooccur_df['Imagename'].to_list()
# viable_img_names = [(item+'.dv_stack_co-occ_proof.tif')
#                     for item in viable_img_names]

viable_img_dict = {img_name.replace('.npy', ''): np.load(f'{images_folder}{img_name}') for img_name in os.listdir(
    f'{images_folder}') if img_name.replace('.npy', '') in viable_img_names}

blank_shape = (list(viable_img_dict.values())[0]).shape
blank_layer = np.zeros((blank_shape), dtype=int)

viable_img_layer_dict = {k:(np.stack((v, blank_layer))) for k, v in viable_img_dict.items()}

#! Manually validate FIJI Macro segmentation. Comment out code block when complete to avoid re-writing.
filtered_proofs = {}
for image_name, image_stack in viable_img_layer_dict.items():
    image_stack
    filtered_proofs[image_name] = filter_proofs(
        image_stack, image_name)
    
#! if had to abort validation, recall already validated images and remove from viable_img_layer_dict. Comment out code block when complete to avoid re-writing.
validated_proofs = {proofs.replace('_mask.npy', ''): np.load(
    f'{napari_output_folder}{proofs}') for proofs in os.listdir(f'{napari_output_folder}') if '.npy' in proofs}
validated_proofs_keys = list(validated_proofs.keys())
viable_img_layer_dict_update = {k:v for k, v in viable_img_layer_dict.items() if k not in validated_proofs_keys}
# launch napari again
filtered_proofs = {}
for image_name, image_stack in viable_img_layer_dict_update.items():
    image_stack
    filtered_proofs[image_name] = filter_proofs(
        image_stack, image_name)

# collect validated proofs
validated_proofs = {proofs.replace('_mask.npy', ''): np.load(
    f'{napari_output_folder}{proofs}') for proofs in os.listdir(f'{napari_output_folder}') if '.npy' in proofs}

invalid = [img_name for img_name,
           img in validated_proofs.items() if len(np.unique(img[1, :, :])) > 1]

cooccur_df = cooccur_df[~cooccur_df['Imagename'].isin(invalid)].copy()

# ---------------- data carpentry ----------------
# timepoint
hpi_list = ['16-18', '20-22', '24-26', '28-30']
cooccur_df['hpi'] = [row.split('hpi')[0].split('_')[-1] for row in cooccur_df['Imagename']]
# if timepoint not explicit, then it is the first timepoint (:eyeroll:)
cooccur_df['hpi'] = ['16-18' if row not in hpi_list else row for row in cooccur_df['hpi']]

# date & cell line
cooccur_df['date'] = [row.split('_')[0] for row in cooccur_df['Imagename']]
cooccur_df['cell_line'] = [row.split('_')[1] for row in cooccur_df['Imagename']]

# pull antibodies from Imagename column
antibodies = ['0801', 'PTP2', 'REX1', 'M1', 'MAHRP1', 'M2', 'MAHRP2', '3031']
cooccur_df_list = []
for serum in antibodies:
    serum
    cooccur_df_serum_slice = cooccur_df.loc[cooccur_df['Imagename'].str.contains(serum)].copy()
    cooccur_df_serum_slice['antibody'] = f'{serum}'
    cooccur_df_list.append(cooccur_df_serum_slice)
cooccur_df = pd.concat(cooccur_df_list).reset_index(drop=True)

# reduce antibody duplicates & relabel '3031'
cooccur_df['antibody'] = cooccur_df['antibody'].str.replace(
    'M2', 'MAHRP2')
cooccur_df['antibody'] = cooccur_df['antibody'].str.replace(
    'M1', 'MAHRP1')
cooccur_df['antibody'] = cooccur_df['antibody'].str.replace(
    '3031', 'EMP1')

# make dates more computer readable
cooccur_df['date_fill'] = [('2022'+row.split('-')[1]+row.split('-')[2])
                    if len(row.split('-')) > 1 else row for row in cooccur_df['date']]

# remove timepoints with ≤4 cells
cooccur_df_list = []
for (cellline_serum), cellline_serum_df in cooccur_df.groupby(['cell_line', 'antibody', 'date', 'hpi']):
    cellline_serum
    if len(cellline_serum_df) >= 4:
        cooccur_df_list.append(cellline_serum_df)
cooccur_df = pd.concat(cooccur_df_list).reset_index(drop=True)

# simple calculations
cooccur_df['perc_both'] = (cooccur_df['Both'] / cooccur_df['Total'])*100
cooccur_df['perc_gfp_both'] = (
    cooccur_df['Both'] / (cooccur_df['C3_only']+cooccur_df['Both']))*100
cooccur_df['perc_c2'] = (cooccur_df['C2_only'] / cooccur_df['Total'])*100
cooccur_df['perc_c3'] = (cooccur_df['C3_only'] / cooccur_df['Total'])*100

# ---------------- summarize ----------------
summary_df = cooccur_df.groupby(['cell_line', 'antibody', 'hpi','date_fill']).mean()

# find range of biological repeats
cooccur_df_biogroups = cooccur_df[[
    'cell_line', 'antibody', 'hpi', 'date_fill']].drop_duplicates()
biorpt_min = cooccur_df_biogroups.groupby(
    ['cell_line', 'antibody', 'hpi'])['hpi'].count().min()
biorpt_max = cooccur_df_biogroups.groupby(
    ['cell_line', 'antibody', 'hpi'])['hpi'].count().max()

#--------------save calculations------------------
cooccur_df.to_csv(f'{output_folder}cooccur_df.csv')
summary_df.to_csv(f'{output_folder}summary_results.csv')

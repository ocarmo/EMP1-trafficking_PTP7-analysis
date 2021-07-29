import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import skimage.io
import functools
from skimage import measure
from scipy.spatial import distance
from sklearn.metrics import pairwise_distances_argmin_min
from loguru import logger
import numpy as np
import matplotlib.pyplot as plt

logger.info('Import OK')

# define location parameters
input_folder = f'python_results/feature_validation/'
output_folder = f'python_results/feature_properties/'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)


def find_edge(feature_coords):
    edge = pd.DataFrame()
    # for (roi_type), roi_type_df in feature_coords.groupby(['roi_key']):
    for (roi), roi_type_df in feature_coords.groupby(['roi_key']):
        roi_type_df
        # explode df
        roi_type_df = roi_type_df.explode('coords')
        roi_type_df = roi_type_df.reset_index()
        # assign x and y
        roi_type_df['x'] = roi_type_df['coords'].str[0]
        roi_type_df['y'] = roi_type_df['coords'].str[1]
        scanX = roi_type_df.groupby(['roi_key', 'x']).agg(y_min=pd.NamedAgg(
            column='y', aggfunc='min'), y_max=pd.NamedAgg(column='y', aggfunc='max'))
        scanX = scanX.reset_index()
        #GET TO USE MELT :))))))
        scanX = pd.melt(scanX, id_vars=['roi_key', 'x'],
                        value_vars=['y_min', 'y_max'], value_name='y')
        scanX = scanX.drop(['variable'], axis=1)
        edge = edge.append(scanX)
    logger.info('Edges prepared')
    return edge


#stackoverflow: https://stackoverflow.com/questions/48887912/find-minimum-distance-between-points-of-two-lists-in-python/48888321
def get_closest_pair_of_points(point_list_1, point_list_2):
    """
    Determine the two points from two disjoint lists of points that are closest to 
    each other and the distance between them.

    Args:
        point_list_1: First list of points.
        point_list_2: Second list of points.

    Returns:
        Two points that make the closest distance and the distance between them.
    """
    indeces_of_closest_point_in_list_2, distances = pairwise_distances_argmin_min(
        point_list_1, point_list_2)

    # Get index of a point pair that makes the smallest distance.
    min_distance_pair_index = np.argmin(distances)

    # Get the two points that make this smallest distance.
    min_distance_pair_point_1 = point_list_1[min_distance_pair_index]
    min_distance_pair_point_2 = point_list_2[indeces_of_closest_point_in_list_2[min_distance_pair_index]]

    min_distance = distances[min_distance_pair_index]

    return min_distance_pair_point_1, min_distance_pair_point_2, min_distance


def measure_edge_dist(df_1, df_2):  # measuring euclid distance b/w coordinate pairs
    df_1coord = [(coord1, coord2)
                 for coord1, coord2 in df_1[['x', 'y']].values]
    df_2coord = [(coord1, coord2)
                 for coord1, coord2 in df_2[['x', 'y']].values]
    return get_closest_pair_of_points(df_1coord, df_2coord)


def compare_edges(scanX):  # start with roi_key, x, y of out lines
    # make dfs of each image
    # res = dict(tuple(scanX.groupby('roi_key')))
    scanX['image_name'] = scanX['roi_key'].str.split('_').str[0]
    edge_distances = []
    for image, image_df in scanX.groupby('image_name'):
        logger.info(f'processing {image}')
        image_df['roi_type'] = image_df['roi_key'].str.split('_').str[1]
        vesicles_only = image_df[image_df['roi_type'] == 'vesicle']
        clefts_only = image_df[image_df['roi_type'] == 'cleft']
        membranes_only = image_df[image_df['roi_type'] == 'membrane']
        for vesicle, vesicle_df in vesicles_only.groupby('roi_key'):
            #logger.info(f'processing {vesicle}')
            for cleft, cleft_df in clefts_only.groupby('roi_key'):
                measure_distance = measure_edge_dist(vesicle_df, cleft_df)
                #unpack the tuple
                edge_distances.append(
                    [vesicle, cleft, measure_distance[0], measure_distance[1], measure_distance[2]])
            #logger.info(f'measuring {vesicle} distance to next membrane')
            for membrane, membrane_df in membranes_only.groupby('roi_key'):
                measure_distance = measure_edge_dist(vesicle_df, membrane_df)
                edge_distances.append(
                    [vesicle, membrane, measure_distance[0], measure_distance[1], measure_distance[2]])
    # turn edge_distances into df
    edge_distances = pd.DataFrame(edge_distances, columns=[
                                  'vesicle_key', 'otherRoi_key', 'vesicle_coord', 'otherRoi_coord', 'measure_distance'])     # turn edge_distances into df
    return edge_distances


# --------------Scale variable--------------
# 540 pixes per 200 nm (measured in FIJI)
scale = 540/200

# --------------Initialise file lists--------------
image_list_ext = [folder for folder in os.listdir(input_folder)]

do_not_quantitate = []

image_list = [filename.replace('.npy', '') for filename in image_list_ext if not any(
    word in filename for word in do_not_quantitate)]

valid_narrays = {filename.replace('.npy', ''): np.load(f'{input_folder}{filename}.npy') for filename in image_list}

logger.info('valid numpy arrays loaded')

features = pd.DataFrame()
features_labeled = features.append(valid_narrays, ignore_index=True)

# --------------Collect feature properties--------------
possible_properties = ['area', 'centroid', 'convex_area', 'eccentricity', 'euler_number', 'label',
                       'local_centroid', 'major_axis_length', 'minor_axis_length', 'orientation', 'perimeter', 'solidity']

# define an empty list to collect dfs
dfs_to_concat = []
for image_name, array_stack in valid_narrays.items():
    image_name
    #layer order: image, membranes, clefts, vesicles
    vesicles_properties = measure.regionprops_table(
        array_stack[3, :, :], properties=possible_properties)
    clefts_properties = measure.regionprops_table(
        array_stack[2, :, :], properties=possible_properties)
    membranes_properties = measure.regionprops_table(
        array_stack[1, :, :], properties=possible_properties)

    vesicles_properties = pd.DataFrame.from_dict(
        vesicles_properties, orient='columns', dtype=None, columns=None)
    vesicles_properties['feature'] = 'vesicle'
    vesicles_properties['image_name'] = image_name

    clefts_properties = pd.DataFrame.from_dict(
        clefts_properties, orient='columns', dtype=None, columns=None)
    clefts_properties['feature'] = 'cleft'
    clefts_properties['image_name'] = image_name

    membranes_properties = pd.DataFrame.from_dict(
        membranes_properties, orient='columns', dtype=None, columns=None)
    membranes_properties['feature'] = 'membrane'
    membranes_properties['image_name'] = image_name

    dfs_to_concat.append([vesicles_properties, clefts_properties, membranes_properties])

#flatten the nested list, not necessary if use nested for loop
dfs_to_concat = [item for sublist in dfs_to_concat for item in sublist]

# concat all dataframes
feature_properties = pd.concat(dfs_to_concat)

#add new column label + feature
feature_properties['roi_key'] = feature_properties['image_name'].map(
    str) + '_' + feature_properties['feature'].map(
    str) + '_' + feature_properties[f'label'].map(str)

logger.info('Feature properties collected')

# correct for scale
feature_properties['area'] = feature_properties['area']/(scale**2)
feature_properties['major_axis_length'] = feature_properties['major_axis_length'] / scale
feature_properties['minor_axis_length'] = feature_properties['minor_axis_length'] / scale

# filter for objects larger than 30 nm wide
feature_properties = feature_properties[(
    feature_properties[['major_axis_length']] > 30).all(axis=1)]
logger.info('Feature properties trimmed')

# make list of filtered roi keys for coordinate extraction
valid_roi_keys = feature_properties['roi_key'].tolist()

# --------------Collect feature coordinates--------------
#repeat for loop, but collecting coordinates instead
possible_properties = ['coords', 'label']
# define an empty list to collect dfs
dfs_to_concat = []
for image_name, array_stack in valid_narrays.items():
    image_name
    #layer order: image, membranes, clefts, vesicles
    vesicles_properties = measure.regionprops_table(
        array_stack[3, :, :], properties=possible_properties)
    clefts_properties = measure.regionprops_table(
        array_stack[2, :, :], properties=possible_properties)
    membranes_properties = measure.regionprops_table(
        array_stack[1, :, :], properties=possible_properties)

    vesicles_properties = pd.DataFrame.from_dict(
        vesicles_properties, orient='columns', dtype=None, columns=None)
    vesicles_properties['feature'] = 'vesicle'
    vesicles_properties['image_name'] = image_name

    clefts_properties = pd.DataFrame.from_dict(
        clefts_properties, orient='columns', dtype=None, columns=None)
    clefts_properties['feature'] = 'cleft'
    clefts_properties['image_name'] = image_name

    membranes_properties = pd.DataFrame.from_dict(
        membranes_properties, orient='columns', dtype=None, columns=None)
    membranes_properties['feature'] = 'membrane'
    membranes_properties['image_name'] = image_name

    logger.info(f'{image_name} coords collected')

    dfs_to_concat.append([vesicles_properties, clefts_properties, membranes_properties])

#flatten the nested list, not necessary if use nested for loop
dfs_to_concat = [item for sublist in dfs_to_concat for item in sublist]

# concat all dataframes
feature_coords = pd.concat(dfs_to_concat)

logger.info(f'Coordinate dfs concatenated')

feature_coords['roi_key'] = feature_coords['image_name'].map(
    str) + '_' + feature_coords['feature'].map(
    str) + '_' + feature_coords[f'label'].map(str)

# trim coordinates from tiny features
feature_coords = feature_coords[feature_coords['roi_key'].isin(valid_roi_keys)]
logger.info('Feature coordinates trimmed')

# # --------------Save feature coordinates--------------
# # This will be a huge file (>10 GB). Save at your own risk
# feature_coords.to_csv(f'{output_folder}feature_coords.csv')
# logger.info('Feature coords saved')

# --------------Run distance measurements--------------
edges = find_edge(feature_coords)
min_distances = compare_edges(edges)

# correct for scale
min_distances['measure_distance'] = [row/scale for row in min_distances['measure_distance']]

# --------------Save distance measurements--------------
min_distances.to_csv(f'{output_folder}feature_coords_distances.csv')
feature_properties.to_csv(f'{output_folder}feature_properties.csv')

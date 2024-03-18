import numpy as np
import pandas as pd


def world2px(trans_mat, world_coords):
    """
    Convert SCiLS Lab world coordinates to pixel coordinates based on x-y raster points.

    :param trans_mat: 4x4 transformation matrix for a given region of interest.
    :type trans_mat: numpy.array
    :param world_coords: World coordinates for a given region of interest.
    :type world_coords: numpy.array
    :return: Tuple of x-y pixel coordinates.
    :rtype: tuple[int]
    """
    back_trans = np.linalg.inv(trans_mat)[0:2, 0:2]
    px_ind = back_trans @ world_coords
    px_ind_int = np.round(px_ind + (np.mean(np.round(px_ind) - px_ind, axis=1)[:, np.newaxis]))
    px_ind_int = px_ind_int - np.min(px_ind_int, axis=1)[:, np.newaxis] + 1
    x = px_ind_int[0, :]
    y = px_ind_int[1, :]
    return x.astype(int), y.astype(int)


def add_pixel_coords_to_region_spots(scils_dataset):
    """
    Add pixel coordinates to region_spots and convert into a pandas DataFrame.

    :param scils_dataset: SCiLS Lab dataset connection loaded in with the SCiLS Lab API.
    :type scils_dataset: scilslab.DatasetProxy
    :return: pandas DataFrame containing spot_id, world x-y-z coordinates, and pixel x-y coordinates.
    :rtype: pandas.DataFrame
    """
    region_spots = scils_dataset.get_region_spots('Regions')
    region_spots_df = pd.DataFrame(region_spots)
    index_images = scils_dataset.get_index_images('Regions')
    world_coords = np.array([region_spots['x'], region_spots['y']])
    region_spots_subset_dfs = []
    for img_obj in index_images:
        trans_mat = img_obj.transformation
        region_spots_df['x_pixel'], region_spots_df['y_pixel'] = world2px(trans_mat, world_coords)
        spots = pd.DataFrame({'spot_id': img_obj.values.flatten()})
        region_spots_subset_dfs.append(region_spots_df.merge(spots, on='spot_id'))
    region_spots_df = pd.concat(region_spots_subset_dfs, axis=0, ignore_index=True)
    region_spots_df.sort_values(by='spot_id')
    region_spots_df.reset_index(drop=True)
    return region_spots_df

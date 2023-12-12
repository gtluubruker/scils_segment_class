import argparse
import os
import numpy as np
import pandas as pd
import skimage.measure
from scilslab import LocalSession


def get_args():
    """
    Parse command line parameters.

    :return: Arguments with default or user specified values.
    :rtype: dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--scils',
                        help='Path to SCiLS .slx file.',
                        required=True,
                        type=str)
    parser.add_argument('--spot_list',
                        help='Path to flexImaging Spot List .txt file.',
                        required=True,
                        type=str)
    parser.add_argument('--roi',
                        help='Name of the region of interest from the SCiLS region tree.',
                        required=True,
                        type=str)
    parser.add_argument('--label',
                        help='Name of the new Label to be written to the SCiLS file.',
                        required=True,
                        type=str)
    arguments = parser.parse_args()
    return vars(arguments)


def args_check(args):
    """
    Check relevant arguments to ensure user input values are valid.

    :param args: Arguments obtained from get_args().
    type args: dict
    """
    if not os.path.exists(args['scils']):
        raise Exception('SCiLS file does not exist.')
    if not os.path.splitext(args['scils'][1]) != 'slx':
        raise Exception('SCiLS file is not a .slx file.')

    if not os.path.exists(args['spot_list']):
        raise Exception('flexImaging Spot List does not exist.')
    if not os.path.splitext(args['spot_list'][1]) != 'txt':
        raise Exception('flexImaging Spot List is not a .txt file.')


def parse_fleximaging_coord(coord):
    """
    Function to parse flexImaging Spot List spots to get region ID and x-y coordinates.

    :param coord: Coordinate information in format R--X---Y---.
    :type coord: str
    :return: Tuple containing region, x coord, and y coord.
    :rtype: tuple[int]
    """
    tmp_split = coord.split('X')
    region = int(tmp_split[0][1:])
    tmp_split = tmp_split[1].split('Y')
    x = int(tmp_split[0])
    y = int(tmp_split[1])
    return region, x, y


def main():
    args = get_args()
    args_check(args)

    # Start connection to SCiLS dataset.
    with LocalSession(filename=args['scils']) as session:
        # Import SCiLS dataset.
        dataset = session.dataset_proxy

        # Get region tree information.
        region_tree = dataset.get_region_tree()

        # Get pandas dataframe with coordinates, spot IDs, and raster IDs for each pixel in the dataset.
        # Users must ensure that the default master 'Regions' label (top of the region tree) has not been renamed.
        if region_tree.get_all_regions()[0].name == 'Regions':
            scils_spot_list_df = pd.DataFrame(region_tree.get_all_regions()[0].spots)

        # Import Spot List exported from flexImaging to get different formatted x-y coordinate system to be used for 2D
        # numpy arrays.
        fleximaging_spot_list_df = pd.read_table(args['spot_list'],
                                                 delimiter=' ',
                                                 skiprows=2,
                                                 names=['x-pos', 'y-pos', 'spot', 'region'])

        # Get flexImaging Spot List formatted x-y coordinates and region IDs.
        coords = [parse_fleximaging_coord(i) for i in fleximaging_spot_list_df['spot']]
        coords = [*zip(*coords)]
        fleximaging_spot_list_df['raster'] = coords[0]
        fleximaging_spot_list_df['x'] = coords[1]
        fleximaging_spot_list_df['y'] = coords[2]

        # Replace SCiLS format x-y coordinates with flexImaging Spot List formatted x-y coordinates
        scils_spot_list_df = scils_spot_list_df[['spot_id']]
        scils_spot_list_df['x'] = fleximaging_spot_list_df['x']
        scils_spot_list_df['y'] = fleximaging_spot_list_df['y']

        # Get dataframe containing spot IDs and raster IDs for the region named "single_cell_test" from the region tree.
        roi = [i for i in region_tree.get_all_regions() if i.name.endswith(args['roi'])]
        if len(roi) <= 1:
            roi = roi[0]
        else:
            raise Exception('More than one ROI in list.')
        roi_df = pd.DataFrame(roi.spots)
        roi_df = roi_df[['spot_id', 'raster']]

        # Merge the ROI dataframe to get x-y coordinates.
        roi_df = roi_df.merge(scils_spot_list_df, on='spot_id')
        roi_df['x'] = roi_df['x'] - min(roi_df['x'])  # subtraction to make min x coord 0
        roi_df['y'] = roi_df['y'] - min(roi_df['y'])  # subtraction to make min y coord 0
        # Create empty numpy array filled with zeros for each pixel in the ROI of interest ("single_cell_test")
        img_matrix = np.zeros((max(roi_df['y']) + 1, max(roi_df['x']) + 1))

        # Each "pixel" in the numpy array that is found in the ROI of interest is given a value of 1.
        for index, row in roi_df.iterrows():
            img_matrix[row['y'], row['x']] = 1

        """
        skimage.measure.label() uses connected component labeling algorithm to find neighboring pixels in the array 
        that are connected, working under the assumption that connected pixels are part of the same cell. This relies 
        on proper segmentation analysis prior to running the script. The following algorithms are used by 
        skimage.measure.label():

        [1] Christophe Fiorio and Jens Gustedt, “Two linear time Union-Find strategies for image processing”, 
            Theoretical Computer Science 154 (1996), pp. 165-181.
        [2] Kensheng Wu, Ekow Otoo and Arie Shoshani, “Optimizing connected component labeling algorithms”, Paper 
            LBNL-56864, 2005, Lawrence Berkeley National Laboratory (University of California), 
            http://repositories.cdlib.org/lbnl/LBNL-56864

        A connectivity value of 2 means the algorithm considers diagnonal pixels as connected pixels. Returns an 
        integer label.
        """
        connected_segments = skimage.measure.label(img_matrix, connectivity=2)
        # Put these labels in a new dataframe with their x-y coordinates.
        connected_segments_labels = pd.DataFrame({'x': np.nonzero(connected_segments)[1],
                                                  'y': np.nonzero(connected_segments)[0],
                                                  'label': connected_segments[np.where(connected_segments != 0)]})
        # Merge with ROI dataframe to get a dataframe that has both the spot IDs and the labels
        connected_segments_labels = roi_df.merge(connected_segments_labels, how='left', on=['x', 'y'])
        # Get dictionary in which the spot IDs are the key and the labels are the value.
        spot_labels = pd.Series(connected_segments_labels.label.values,
                                index=connected_segments_labels.spot_id).to_dict()
        # Write out this new label to the SCiLS dataset (will return the ID of the new label).
        dataset.write_label(name=args['label'], spot_label=spot_labels)


if __name__ == '__main__':
    main()

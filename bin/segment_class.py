import numpy as np
import pandas as pd
import skimage.measure
from scilslab import LocalSession
from bin.args import get_args, args_check
from bin.util import add_pixel_coords_to_region_spots


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
        scils_spot_list_df = add_pixel_coords_to_region_spots(dataset)

        # Get dataframe containing spot IDs and raster IDs for the region named "single_cell_test" from the region tree.
        roi = [i for i in region_tree.get_all_regions() if i.name.endswith(args['roi'])]
        if len(roi) == 1:
            roi = roi[0]
        else:
            raise Exception('More than one ROI in list.')
        roi_df = pd.DataFrame(roi.spots)
        roi_df = roi_df[['spot_id', 'raster']]

        # Merge the ROI dataframe to get x-y coordinates.
        roi_df = roi_df.merge(scils_spot_list_df, on='spot_id')
        roi_df['x_pixel'] = roi_df['x_pixel'] - min(roi_df['x_pixel'])  # subtraction to make min x coord 0
        roi_df['y_pixel'] = roi_df['y_pixel'] - min(roi_df['y_pixel'])  # subtraction to make min y coord 0
        # Create empty numpy array filled with zeros for each pixel in the ROI of interest ("single_cell_test")
        img_matrix = np.zeros((max(roi_df['y_pixel']) + 1, max(roi_df['x_pixel']) + 1))

        # Each "pixel" in the numpy array that is found in the ROI of interest is given a value of 1.
        for index, row in roi_df.iterrows():
            img_matrix[int(row['y_pixel']), int(row['x_pixel'])] = 1

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
        connected_segments_labels = pd.DataFrame({'x_pixel': np.nonzero(connected_segments)[1],
                                                  'y_pixel': np.nonzero(connected_segments)[0],
                                                  'label': connected_segments[np.where(connected_segments != 0)]})
        # Merge with ROI dataframe to get a dataframe that has both the spot IDs and the labels
        connected_segments_labels = roi_df.merge(connected_segments_labels, how='left', on=['x_pixel', 'y_pixel'])
        # Get dictionary in which the spot IDs are the key and the labels are the value.
        spot_labels = pd.Series(connected_segments_labels.label.values,
                                index=connected_segments_labels.spot_id).to_dict()
        # Write out this new label to the SCiLS dataset (will return the ID of the new label).
        dataset.write_label(name=args['label'], spot_label=spot_labels)


if __name__ == '__main__':
    main()

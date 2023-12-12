# SCiLS Lab Segment Class

## About

This workflow was built with single cell mass spectrometry imaging in mind with the goal of labeling individual cells whose pixels are grouped together into a SCiLS class during segmentation. This is done using the SCiLS Lab Python API to access SCiLS datasets to avoid manual ROI definiton for each cell. Here, a cell is defined as a group of pixels from the same ROI that are connected; pixel connection is determined using a [connected component labeling](https://en.wikipedia.org/wiki/Connected-component_labeling) algorithm implemented in `skimage.measure.label()`. See the `scikit-image` documentation for more details.


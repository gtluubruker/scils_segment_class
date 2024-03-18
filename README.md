# SCiLS Lab Segment Class

## About

This workflow was built with single cell mass spectrometry imaging in mind with the goal of labeling individual cells 
whose pixels are grouped together into a SCiLS class during segmentation. This is done using the SCiLS Lab Python API 
to access SCiLS datasets to avoid manual ROI definiton for each cell. Here, a cell is defined as a group of pixels from 
the same ROI that are connected; pixel connection is determined using a 
[connected component labeling](https://en.wikipedia.org/wiki/Connected-component_labeling) algorithm implemented in 
`skimage.measure.label()`. See the `scikit-image` documentation for more details.

## Installation

As SCiLS Lab is only available on Windows, this workflow is also exclusive to Windows and only tested in that 
environment.

1. If not installed, install 
[Anaconda for Windows](https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Windows-x86_64.exe).
2. Open `Anaconda Prompt`
3. Create a new `conda venv` and activate it.
```
conda create -n scils_segment_class python=3.11
conda activate scils_segment_class
```
4. Install this workflow.
```
pip install [/path/to/]scils_segment_class
```
5. Install the SCiLS Lab Python API using the instructions in the API documentation.

## Usage

#### Parameters

- `scils`: Path to the SCiLS .slx file containing region, spectral, and processing data/metadata.
- `roi`: Name of the region of interest from the SCiLS region tree to be segmented based on connectivity.
- `label`: Name of the new label to be written to the SCiLS file.

#### Running the Workflow

This workflow can be run using the following command:
```
segment_class --scils dataset.slx --roi single_cell_region_name --label label_name
```

To check the list of available ROI names, use the following command:
```
list_regions --scils dataset.slx
```

# GFP puncta identification

**Purpose**: Identify GFP-puncta in P. falciparum infected red blood cells. Livecell images acquired at 100x on a widefield microscopy and Huygens deconvolved[1].

**Data produced**: From Huygens deconvolved TIFF stacks, cells and nuclei were outlined using a maximum projection of the bright field channel and GFP-puncta outlined using a maximum projection of the FITC (GFP) channel. The mask arrays were export as a pandas dataframe/csv for further processing.

**Figures in manuscript**: Used to generate data depicted in S10.

**Analysis software**: [CellPose](https://www.cellpose.org/) package, python; [napari](https://napari.org/) package, python.

**References/Resources**: Stringer C, Wang T, Michaelos M, Pachitariu M. Cellpose: a generalist algorithm for cellular segmentation. bioRxiv; 2020. DOI: 10.1101/2020.02.02.931238 ; napari contributors (2019). napari: a multi-dimensional image viewer for python. doi:10.5281/zenodo.3555620. 
[1] Images were deconvolved with Huygens Professional version 19.04 (Scientific Volume Imaging, The Netherlands, http://svi.nl), using the CMLE algorithm with 50 iterations.
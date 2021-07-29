# GFP puncta identification

**Purpose**: 
Implement general-purpose scripts to integrate CellPose cell quantification into a range of workflows.

**Cell Types tested**: 
- Neuro-2a 
- HEK293T
- *P. falciparum* infected RBCs

**Instrument/techniques**:
- Confocal microscopy datasets at 100X or 63X zoom
- Widefield microscopy datasets at 100X

**Data produced:** 
- From Huygens deconvolved TIFF stacks, outline cells and nuclei using the bright field image and GFP-puncta using the FITC image.
- Export this is pandas dataframe/csv for further processing

**Analysis:** 
- Live cell microscopy: Extract features of GFP-labeled puncta in *P. falciparum* infected RBCs for comparisons between different cell lines.

**Getting started:**
- All dependancies can be found in the ```environment.yml``` file. To install these automatically into a new conda environment:
```conda env create -f environment.yml```
- After installation, don't forget to activate your new environment (```conda activate droplet_analysis```)

**References/Resources:** 
- CellPose [homepage](http://www.cellpose.org/), [documentation](https://cellpose.readthedocs.io/en/latest/) and [repository](https://github.com/MouseLand/cellpose)
- Napari [repository](https://github.com/napari/napari), [documentation](https://napari.org/docs/) and [tutorials](https://napari.org/tutorials/)


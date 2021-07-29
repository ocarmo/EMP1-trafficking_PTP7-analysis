# Immuno-electron microscropy: vesicle detection

**Purpose**: Identify the red blood cell membrane, Maurer's clefts, and vesicles of *Plasmodium falciparum* infected red blood cells in immuno electron micrographs. Cells were Equinatoxin II permeabilized to clear intracellular hemoglobin, then probed with the antibody indicated before 1-2% OSO4 staining, embedding, and sectioning for TEM.

**Data produced**: Segmented image masks, vesicle to other ROI distances, and object properties.

**Analysis software**: [CellPose](https://www.cellpose.org/) package, python; [Napari](https://napari.org/) package, python.

**References/Resources**: Stringer C, Wang T, Michaelos M, Pachitariu M. Cellpose: a generalist algorithm for cellular segmentation. bioRxiv; 2020. DOI: 10.1101/2020.02.02.931238 ; napari contributors (2019). napari: a multi-dimensional image viewer for python. doi:10.5281/zenodo.3555620.
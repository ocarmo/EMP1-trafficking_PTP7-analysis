# Immuno-electron microscropy: vesicle detection

**Purpose**: Identify the red blood cell membrane, Maurer's clefts, and vesicles of *Plasmodium falciparum* infected red blood cells in immuno-electron micrographs. Cells were Equinatoxin II permeabilized to clear intracellular hemoglobin, then probed with the antibody indicated before 1-2% OSO4 staining, embedding, and sectioning for TEM. Gold secondary antibodies confirm the efficacy of immunolabeling (no-primary antibody negative controls run in parallel). Gold particles are not relevant to this quantitation, so no-primary antibody controls were included in this analysis.

**Data produced**: Segmented image masks, distances between vesicles and other objects of interest (ROIs), and object properties such as area and diameter. Due to size constraints, results from the ```1_segmentation.py``` script are not provided in the data repository, however they can be reproduced on your machine by following the 'Reproducing workflow' instructions on the main README. However, validated segmented masks are available in the 'feature_validation' folder after retrieving the data (run ```0_data_retrieval.py```).

**Figures in manuscript**: Used to generate data depicted in Fig 4 and Fig 6.

**Analysis software**: [CellPose](https://www.cellpose.org/) package, python; [Napari](https://napari.org/) package, python.

**References/Resources**: Stringer C, Wang T, Michaelos M, Pachitariu M. Cellpose: a generalist algorithm for cellular segmentation. bioRxiv; 2020. DOI: 10.1101/2020.02.02.931238 ; napari contributors (2019). napari: a multi-dimensional image viewer for python. doi:10.5281/zenodo.3555620.
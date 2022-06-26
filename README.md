[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5146871.svg)](https://zenodo.org/record/5146871) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6747921.svg)](https://zenodo.org/record/6747921)
# EMP1 trafficking 
This repository contains the analysis scripts associated with the manuscript titled *Deletion of the* Plasmodium falciparum *exported protein PTP7 leads to Maurer’s clefts vesiculation, host cell remodeling defects, and loss of surface presentation of EMP1* (PLOS Pathogens doi pending). The project was led by Olivia Carmo and analysis scripts were written with Dr. Dezerae Cox<sup id="a1">[1](#f1)</sup>.

## Biology background
*Plasmodium falciparum* causes more than 200 million malaria infections every year, killing more than 400,000 people<sup id="a2">[2](#f2)</sup>. After invading the red blood cells, *P. falciparum* must traffic a virulence factor, *P. falciparum* erythrocyte membrane protein 1 (EMP1) to the red blood cell surface to evade the host immune response. An important question is: how is EMP1 – an integral membrane protein – trafficked to its correct destination given that the red blood cell is a terminally differentiated cell that has lost most of its protein trafficking machinery? 
Without host cell trafficking machinery to co-opt, the parasite exports ~500 unique proteins beyond its boundary into the host red blood cell, including EMP1<sup id="a3">[3](#f3),</sup><sup id="a4">[4](#f4)</sup>. Previous work suggests that EMP1 is trafficked as a chaperoned complex to membranous structures in the red blood cell cytoplasm, called Maurer’s clefts, where it is inserted into the cleft membrane. EMP1 has also been reported to be associated with vesicles; however, given that trafficking is GTP-independent and that the canonical machinery is absent from the host cell and exported *P. falciparum* proteins, it remains unclear how EMP1 is trafficked from the Maurer’s clefts to the red blood cell membrane. 
In our submitted study, we describe a protein, PF3D7_0301700 (PTP7), that functions at the nexus between the Maurer’s cleft and the red blood cell surface. Genetic disruption of PTP7 leads to accumulation of vesicles at the Maurer’s clefts, grossly aberrant knob morphology, and failure to deliver EMP1 to the red blood cell surface.  We show that an expanded low complexity sequence in the C-terminal region of PTP7, found only in the Laverania clade of Plasmodium, is critical for efficient virulence protein trafficking.

## Data management
Functional characterization of PTP7 relied on quantitative and qualitative analysis of light and electron microscopy images. Representative raw images of each dataset were provided in the submitted manuscript (PLOS Pathogens doi pending). Additional raw images are available in zipped folders with the relevant title and the suffix '-raw-images' from the open-access [Zenodo dataset](https://zenodo.org/record/5146871). For quantitation, objects (*e.g.* vesicles, knobs, gfp-puncta) were masked so that the coordinates and/or features (*e.g.* area, diameter) could be measured. For each analysis set, folders of mask images are available in addition to *proofs* which overlay the masked features and the raw image. Please see [analyses](#f20) for analysis details of each dataset, and [reproducing workflow](#f21) for advice if you would like to reproduce the analysis pipeline on your machine.

## Analyses <b id="f20"></b>
### Fluorescence image analysis 
**Live cell image quantification** was performed using custom Python scripts, leveraging the Cellpose<sup id="a5">[5](#f5)</sup> and napari<sup id="a6">[6](#f6)</sup> packages. Briefly, the logic was as follows: widefield images brightfield and GFP image acquisitions were Huygens deconvolved<sup id="a7">[7](#f7)</sup>, maximum projected, and segmented with Cellpose to identify GFP-positive puncta and the red blood cells and parasite cell boundaries. Segmentation was then manually inspected using napari to ensure the accuracy of GFP puncta assignment and remove multiply infected red blood cells. Any parasite-GFP signal was excluded, and features of the cell, parasite, and cytoplasmic GFP-puncta were extracted using sci-kit image<sup id="a8">[8](#f8)</sup>. This analysis was used to generate data in Fig S10.

**Indirect immunofluorescence quantification** was performed using FIJI software<sup id="a9">[9](#f9)</sup>. The FIJI Macro scripts ```CytoCleft_rMFI.ijm``` and ```Co_occurrence_EMP1vREX1.ijm``` was used as described previously<sup id="a10">[10](#f10)</sup>, to analyze the mean fluorescence intensity, count Maurer’s cleft, and determine particle co-occurrence exhibited (Fig 3, S8). In ```Co_occurrence_C2-C3.ijm```, minor thresholding alterations were added for agnostic quantitation of different immunolabels (Fig 1, S2).

### Scanning electron micrograph analysis. 
Scanning electron microscope images of the external and internal surface of the infected red blood cell membrane were quantified for knob coverage and knob diameter using Cellpose<sup id="a5">[5](#f5)</sup> and napari<sup id="a6">[6](#f6)</sup>. Images were segmented using Cellpose to identify the cell boundary and knob structures. These boundaries and structures were manually verified using napari, then features of the infected red blood cells were extracted using sci-kit image<sup id="a8">[8](#f8)</sup> (Fig 2, 5, S5).

### Immunoelectron micrograph image analysis. 
Immunoelectron micrographs were higra watershed segmented and large objects were classified as red blood cells membranes, clefts, or vesicles based on their eccentricity and convex area. Object masks were manually validated using napari prior to extraction of objects’ feature properties and coordinates using sci-kit image<sup id="a8">[8](#f8)</sup>. The distance between each vesicle and the nearest non-vesicle object was calculated as the minimum Euclidean distance between boundary pixels of each vesicle/non-vesicle object pair (Fig 4, 5).

### Statistical analysis.
Analysis generated by these scripts were visualized and statistically tested using [GraphPad Prism 9.2.0](https://www.graphpad.com/scientific-software/prism/) Macintosh Version by Software MacKiev © 1994-2021.

## Reproducing workflow <b id="f21"></b>
### Prerequisites
FIJI Macro scripts were written and executed through FIJI software<sup id="a9">[9](#f9)</sup>. Packages required for Python scripts can be accessed in the ```environment.yml``` file available in each analysis folder. To create a new conda environment containing all packages, run ```conda create -f environment.yml```. 

### Workflow
To view analysis results, including masks and validated object classification, all processing steps available as an open-access [Zenodo dataset](https://zenodo.org/record/5146871). To reproduce analysis presented in the manuscript run the ```0_data_retrieval.py``` script for the analysis workflow of interest. The data retrieval script downloads and unzips the original images along with their masks and summary tables. Analysis for the paper was conducted by running the scripts in the enumerated order. To regenerate these results yourself, run the code in the order indicated by the script number for each folder.

## References

<b id="f1">1.</b> This repository format adapted from https://github.com/dezeraecox-manuscripts/COX_Proteome-stability [↩](#a1)

<b id="f2">2.</b> World Health Organization. [World malaria report 2020](https://www.who.int/data/gho/publications/world-health-statistics) [↩](#a2)

<b id="f3">3.</b> Sargeant T, Marti M, Caler E, Carlton J, Simpson K, Speed T, et al. Lineage-specific expansion of proteins exported to erythrocytes in malaria parasites. Genome Biol. 2006;7: R12. doi:10.1186/gb-2006-7-2-r12. [↩](#a3)

<b id="f4">4.</b> Heiber A, Kruse F, Pick C, Grüring C, Flemming S, Oberli A, et al. Identification of New PNEPs Indicates a Substantial Non-PEXEL Exportome and Underpins Common Features in Plasmodium falciparum Protein Export. Przyborski JM, editor. PLoS Pathog. 2013;9: e1003546. doi:10.1371/journal.ppat.1003546. [↩](#a4)

<b id="f5">5.</b> Stringer C, Wang T, Michaelos M, Pachitariu M. Cellpose: a generalist algorithm for cellular segmentation. Nat Methods. 2021;18: 100–106. doi:10.1038/s41592-020-01018-x. [↩](#a5)

<b id="f6">6.</b> Sofroniew N, Lambert T, Evans K, Nunez-Iglesias J, Winston P, Bokota G, et al. napari/napari: 0.4.9rc2. Zenodo; 2021. doi:10.5281/zenodo.4915656. [↩](#a6)
updates: napari contributors (2019). napari: a multi-dimensional image viewer for python. doi:10.5281/zenodo.3555620 [↩](#a6)

<b id="f7">7.</b> Images were deconvolved with Huygens Professional version 19.04 (Scientific Volume Imaging, The Netherlands, http://svi.nl), using the CMLE algorithm with 50 iterations. [↩](#a7)

<b id="f8">8.</b> Walt S van der, Schönberger JL, Nunez-Iglesias J, Boulogne F, Warner JD, Yager N, et al. scikit-image: image processing in Python. PeerJ. 2014;2: e453. doi:10.7717/peerj.453. [↩](#a8)

<b id="f9">9.</b> Schindelin J, Arganda-Carreras I, Frise E, Kaynig V, Longair M, Pietzsch T, et al. Fiji: an open-source platform for biological-image analysis. Nat Methods. 2012;9: 676–682. doi:10.1038/nmeth.2019. [↩](#a9)

<b id="f10">10.</b> McHugh E, Carmo OMS, Blanch A, Looker O, Liu B, Tiash S, et al. Role of Plasmodium falciparum Protein GEXP07 in Maurer’s Cleft Morphology, Knob Architecture, and P. falciparum EMP1 Trafficking. mBio. 2020;11. doi:10.1128/mBio.03320-19. [↩](#a10)

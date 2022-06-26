# Analysis: FIJI Macro scripts

**Purpose**: Quantitation of deconvolved<sup id="a1">[1](#f1)</sup> immunofluorescence micrographs using FIJI software<sup id="a2">[2](#f2)</sup>. The FIJI Macro scripts ```CytoCleft_rMFI.ijm``` and ```Co_occurrence_EMP1vREX1.ijm``` were used as described previously<sup id="a3">[3](#f3)</sup> to fractionate the cytoplasm and cleft fluorescence, analyze the mean fluorescence intensity, count Maurer’s cleft, and determine particle co-occurrence exhibited (Fig 3, S8). In ```Co_occurrence_C2-C3.ijm```, minor thresholding alterations were added for agnostic quantitation of different immunolabels (Fig 1, S2). The co_occurrence scripts determine particle co-occurrence using Huygens deconvolved<sup id="a1">[1](#f1)</sup> widefield images. 
All FIJI Macro scripts generate 'proof' montage images, displaying the merged fluorescent channels beside the merged labeled objects. Proof images were manually validated to remove cells were segmentation failed. For ```Co_occurrence_C2-C3.ijm``` scripts were written to expedite manual validation by opening each proof, marking cells where segmentation failed (using napari<sup id="a4">[4](#f4)</sup>), and programmatically removing those cells from the dataframes (.csv files) saved after ```Co_occurrence_C2-C3.ijm``` analysis (```1_analysis.py``` in Co_occurrence_C2-C3 folder). 
All immunofluorescence images were acquired on the DeltaVision Elite (GE) widefield microscope. The ```Channel_put-together-er_fromHD.ijm``` file was used to re-stack channels after deconvolution and prior to segmentation.

**Data produced**: Mean fluorescence intensity of anti-EMP1 in the cytoplasm and/or cleft, Maurer’s cleft counts (determined by anti-REX1), and particle co-occurrence. Data, produced as a table from FIJI, was copied to Excel (Microsoft Corporation) for storage before visualization and statistical testing with [GraphPad Prism 9.2.0](https://www.graphpad.com/scientific-software/prism/) Macintosh Version by Software MacKiev © 1994-2021. 
For ```Co_occurrence_C2-C3.ijm``` validated output, data was plotted using seaborn<sup id="a5">[5](#f5)</sup> as implemented in ```2_plotting.py``` in Co_occurrence_C2-C3 folder.

**Figures in manuscript**: Used to generate data depicted in Fig 1, 3, S2, and S8.

**Analysis software**: FIJI 2.1.0<sup id="a2">[2](#f2)</sup>

**References**
<b id="f1">1.</b> Images were deconvolved with Huygens Professional version 19.04 (Scientific Volume Imaging, The Netherlands, http://svi.nl), using the CMLE algorithm with 50 iterations. [↩](#a1)

<b id="f2">2.</b> Schindelin J, Arganda-Carreras I, Frise E, Kaynig V, Longair M, Pietzsch T, et al. Fiji: an open-source platform for biological-image analysis. Nat Methods. 2012;9: 676–682. doi:10.1038/nmeth.2019. [↩](#2)

<b id="f3">3.</b> McHugh E, Carmo OMS, Blanch A, Looker O, Liu B, Tiash S, et al. Role of *Plasmodium falciparum* Protein GEXP07 in Maurer’s Cleft Morphology, Knob Architecture, and *P. falciparum* EMP1 Trafficking. mBio. 2020;11. doi:10.1128/mBio.03320-19. [↩](#a3)

<b id="f4">4.</b> Sofroniew N, Lambert T, Evans K, Nunez-Iglesias J, Winston P, Bokota G, et al. napari/napari: 0.4.9rc2. Zenodo; 2021. doi:10.5281/zenodo.4915656. [↩](#a4)
updates: napari contributors (2019). napari: a multi-dimensional image viewer for python. doi:10.5281/zenodo.3555620 [↩](#a4)

<b id="f5">5.</b> Waskom, M. L., (2021). seaborn: statistical data visualization. Journal of Open Source Software, 6(60), 3021, https://doi.org/10.21105/joss.03021 [↩](#a5)

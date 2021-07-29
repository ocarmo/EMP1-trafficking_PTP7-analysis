/* CytoCleft_rMFI.ijm
 * last updated 2020.04.16
 * 
 * This macro takes hyperstacks of IFAs probed for ATS (EMP1 marker) and REX1 (cleft marker) 
 * and staining DNA with DAPI.
 * 
 * REX1, EMP1, and DAPI maximum intensity projections (MIP) are merged and converted to create a 'cellmask'.
 * 
 * REX1 is used to create a cleft 'REX1_mask' and generate the cytoplasm sans clefts
 * mean gray value measurements of each mask are redirected to the EMP1_MIP
 * 
 * added stop-gap to exclude stacks that have >= 2 'cytoplasm's
 * 
 * Adapted from Ellie Cho's Co-occurrence macro from the 2019 BOMP FIJI Macro workshop.
 */
	
	//get input and output directories	
	indir = getDirectory("select a source folder");
	outdir = getDirectory("select a destination folder");
	
	//get the image list
 	list = getFileList(indir);

 	//Batch?
	setBatchMode(true);

	//start batch loop
	for(i=0; i<list.length; i++){
		
		run("Close All");
		
		//open image, grab the file name
 		open(indir + list[i]);
		nameonly = File.nameWithoutExtension;

		//split channels and rename each channels with static name
		run("Split Channels");
		image = "C1-"+ list[i]; 	
		selectWindow(image);
		run("Z Project...", "projection=[Max Intensity]");
		rename("DAPI_MIP");
		
		image = "C2-"+ list[i]; 	
		selectWindow(image);
		run("Z Project...", "projection=[Max Intensity]");
		rename("EMP1_MIP");
		
		image = "C3-"+ list[i]; 
		selectWindow(image);
		run("Z Project...", "projection=[Max Intensity]");
		rename("REX1_MIP");

		image = "C4-"+ list[i]; 
		selectWindow(image);
		rename("DIC");

		//Setting up DAPI-DIC merge for proof
		//grab center DIC slice
		selectWindow("DIC");
		n = nSlices;
		o = round(n/2);
		setSlice(o);
		run("Duplicate...", " ");
		rename("DIC_slice");
		//c1-7: 1-red, 2-green, 3-blue, 4-gray, 5-cyan, 6-magenta, and 7-yellow
		run("Merge Channels...", "c3=DAPI_MIP c4=DIC_slice create keep");
		run("Stack to RGB");
		rename("DAPI_DIC_merge_");

		//create masks

		//make single cell mask w/ gaussian blur
		imageCalculator("Add create","EMP1_MIP","REX1_MIP");
		run("Gaussian Blur...", "sigma=2");
		setOption("ScaleConversions", true);
		run("8-bit");
		run("Auto Threshold", "method=Huang white");
		run("Set Measurements...", "  redirect=None decimal=3");
		run("Watershed Irregular Features", "erosion=1 convexity_threshold=0.98 separator_size=0-Infinity exclude");
		run("Morphological Filters", "operation=Opening element=Disk radius=8");
		run("Convert to Mask");
		rename("cellmask");

		
		//check number of cells
		selectWindow("cellmask");
		roiManager("reset");
		run("Set Measurements...", "  redirect=None decimal=3");
		run("Analyze Particles...", "add");
		count = roiManager("count");
	
		if (count <= 2){
		
			/*
			//make cell mask w/ CONVEXHULL
			imageCalculator("Add create","EMP1_MIP","REX1_MIP");
			rename("EMP1_REX1_MIP");
			run("Duplicate...", " ");
			run("Gaussian Blur...", "sigma=2");
			setOption("ScaleConversions", true);
			run("8-bit");
			run("Auto Threshold", "method=Moments white");
			//run("Auto Threshold", "method=Intermodes white");
			//run("Auto Threshold", "method=MaxEntropy white");
			//run("Auto Threshold", "method=Shanbhag white");
			//run("Auto Threshold", "method=Isodata white");
			run("Set Measurements...", "area redirect=None decimal=3");
			run("Analyze Particles...", "size=3-Infinity pixel circularity=0.25-1.00 exclude clear add");
			count = getValue("results.count");
			
			if (count >= 2){
				roiManager("Select", Array.getSequence(roiManager("count")));
				roiManager("combine");
				run("Convex Hull");
			}else{
			roiManager("Select", Array.getSequence(roiManager("count")));
			run("Convex Hull");
			}
			
			run("Fill");
			run("Convert to Mask");
			run("Gaussian Blur...", "sigma=2");
			run("Auto Threshold", "method=Default white");
			run("Morphological Filters", "operation=Dilation element=Disk radius=2");
			run("Fill Holes");
			run("Morphological Filters", "operation=Opening element=Disk radius=10");
			rename("cellmask");
			*/
			
			//make nucleus mask via DAPI
			selectWindow("DAPI_MIP");
			run("Duplicate...", " ");
			run("Median...", "sigma=15");
			setAutoThreshold("Default dark");
			run("Convert to Mask");
			rename("DAPI_mask");

			//Select EMP1 largest particle			
			selectWindow("EMP1_MIP");
			run("Duplicate...", " ");
			setOption("ScaleConversions", true);
			run("8-bit");
			run("Auto Local Threshold", "method=Niblack radius=30 parameter_1=0 parameter_2=0 white");
			run("Keep Largest Region");
			run("Gaussian Blur...", "sigma=2");
			setAutoThreshold("Default dark");
			run("Convert to Mask");
			run("Morphological Filters", "operation=Opening element=Disk radius=5");
			rename("EMP1_MIP-1-largest");

			//Make paramask - stopgap to catch events where largest EMP1 particle not at the parasite periphery
			imageCalculator("Add create", "EMP1_MIP-1-largest", "DAPI_mask");
			run("Watershed");
			rename("prelim_paramask");
			roiManager("reset");
			run("Set Measurements...", "  redirect=None decimal=3");
			run("Analyze Particles...", "add");
			count = roiManager("count");

			if (count == 1){
				selectWindow("prelim_paramask");
			}else{
				selectWindow("DAPI_mask");
			}
			
			run("Morphological Filters", "operation=Opening element=Disk radius=5");
			rename("paramask");

			//check number of parasites - stopgap for greater than 2 parasites per image
			selectWindow("paramask");
			roiManager("reset");
			run("Set Measurements...", "  redirect=None decimal=3");
			run("Analyze Particles...", "add");
			count = roiManager("count");

			if (count <= 2){

				//make cytoplasm
				imageCalculator("Subtract create", "cellmask", "paramask");
				rename("cytoplasm");

				//REX1 clefts mask (local threshold)
				selectWindow("REX1_MIP");
				run("Duplicate...", " ");
				setOption("ScaleConversions", true);
				run("8-bit");
				run("Auto Local Threshold", "method=Bernsen radius=5 parameter_1=0 parameter_2=0 white");
				rename("REX1mask_clefts");
				imageCalculator("AND create", "REX1mask_clefts","cytoplasm");
				run("Watershed");
				run("Set Measurements...", "  redirect=None decimal=3");
				run("Analyze Particles...", "size=3-Infinity pixel circularity=0.2-1.00 show=Masks");
				run("Invert LUT");
				rename("REX1mask");

				//check number of clefts
				selectWindow("REX1mask");
				roiManager("reset");
				run("Set Measurements...", "  redirect=None decimal=3");
				run("Analyze Particles...", "add");
				count = roiManager("count");

				if (count <= 40){
				
					//cytoplasm sans clefts - erode cytoplasm ("cytoplasm_small") to minimize cell boundary inflation from earlier guassian blur
					selectWindow("cellmask");
					run("Duplicate...", " ");
					run("Morphological Filters", "operation=Erosion element=Disk radius=5");
					rename("cellmask_small");
					imageCalculator("Subtract create", "cellmask_small","paramask");
					rename("cytoplasm_small");
					imageCalculator("Subtract create", "cytoplasm_small","REX1mask");
					rename("cytoplasm-clefts");

			
				//measuring MFI and StDev of EMP1 signal
			
				//measure REX1mask
				selectWindow("REX1mask");
				rename(nameonly+"_clefts");
				run("Set Measurements...", "area mean redirect=EMP1_MIP decimal=3");
				run("Analyze Particles...", "size=0-Infinity pixel show=Nothing summarize");
				rename("clefts_merge_");

				//measure cytoplasm
				selectWindow("cytoplasm-clefts");
				rename(nameonly+"_cytoplasm");
				run("Set Measurements...", "area mean redirect=EMP1_MIP decimal=3");
				run("Analyze Particles...", "show=[Masks] summarize");
				run("Invert LUT");
				run("Convert to Mask");
				rename("EMP1_cyto");

				//measure invert_cellmask (background)
				selectWindow("EMP1_MIP");
				run("Duplicate...", " ");
				run("Gaussian Blur...", "sigma=2");
				setOption("ScaleConversions", true);
				run("8-bit");
				run("Auto Threshold", "method=Huang white");
				run("Morphological Filters", "operation=Dialation element=Disk radius=3");
				run("Invert");
				setAutoThreshold("Shanbhag dark");
				run("Convert to Mask");
				rename(nameonly+"-bkgrd");
				run("Analyze Particles...", "show=[Masks] summarize");
				run("Invert LUT");
				rename("InvOutline");
				imageCalculator("Add create", "EMP1_cyto","InvOutline");
				rename("inv_merge_");

	
			//make 'rMFI' proof
			//c1-7: 1-red, 2-green, 3-blue, 4-gray, 5-cyan, 6-magenta, and 7-yellow
			run("Merge Channels...", "c6=REX1_MIP c2=EMP1_MIP c3=DAPI_MIP create keep");
			run("Stack to RGB");
			rename("Merge_merge_");
			run("Images to Stack", "name=[] title=_merge_ use");
			run("Make Montage...", "columns=4 rows=1 scale=1 border=1");
			run("Scale Bar...", "width=2 height=1 font=6 color=Gray background=None location=[Lower Right] hide overlay");
			//run("Flatten");
			saveAs("tif", outdir+nameonly+"_rMFI_proof");
		
			//clear up workspace, memory
			run("Close All");
			run("Collect Garbage");

				}else{
				//clear up workspace, memory
				run("Close All");
				run("Collect Garbage");
				}
	
			}else{
			//clear up workspace, memory
			run("Close All");
			run("Collect Garbage");
			}
	
	}else{
		//clear up workspace, memory
		run("Close All");
		run("Collect Garbage");
	}
	}
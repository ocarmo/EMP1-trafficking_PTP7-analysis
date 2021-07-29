/* Co-occurence_EMP1vREX1_count.ijm
 * last updated 2020.04.16
 * 
 * This macro takes hyperstacks of IFAs probed for ATS (EMP1 marker) and REX1 (cleft marker)
 * to generate representative puncta masks and then identify co-occuring particles.
 * 
 * Adapted from Ellie Cho's Co-occurrence macro from the 2019 BOMP FIJI Macro workshop.
 */
 
	//get input and output directories	
	indir = getDirectory("select a source folder");
	outdir = getDirectory("select a destination folder");
	
	//get the image list
 	list = getFileList(indir);

	//make result table
	title1 = "Puncta_counting";
	title2 = "["+title1+"]";
	if (isOpen(title1)) {
		selectWindow(title1);
		run("Close"); 
	} 
	run("Table...", "name="+title2+" width=600 height=300"); 
	print(title2, "\\Headings:Imagename \t Total \t EMP1 only \t REX1 only \t Both");

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
		// ATS = acidic terminal segment of PfEMP1. EMP1 and ATS are used interchangeably in this script.
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
		rename("DAPI_DIC_stack_");

		//create masks

		//make single cell mask w/ gaussian blur
		imageCalculator("Add create","EMP1_MIP","REX1_MIP");
		run("Gaussian Blur...", "sigma=4");
		setOption("ScaleConversions", true);
		run("8-bit");
		run("Auto Threshold", "method=Huang white");
		run("Morphological Filters", "operation=Opening element=Disk radius=8");
		run("Convert to Mask");
		rename("cellmask");
		
		//check number of cells
		selectWindow("cellmask");
		roiManager("reset");
		run("Set Measurements...", "  redirect=None decimal=3");
		run("Analyze Particles...", "add");
		count = roiManager("count");
	
		if (count <= 3){
		
			/*
			//make cell mask w/ convexhull
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
			//run("Auto Local Threshold", "method=Phansalkar radius=15 parameter_1=0 parameter_2=0 white");
			//run("Auto Local Threshold", "method=Phansalkar radius=5 parameter_1=0 parameter_2=0 white");
			//run("Auto Local Threshold", "method=Contrast radius=4 parameter_1=0 parameter_2=0 white");
			run("Keep Largest Region");
			run("Gaussian Blur...", "sigma=2");
			setAutoThreshold("Default dark");
			run("Convert to Mask");
			run("Morphological Filters", "operation=Opening element=Disk radius=5");
			rename("EMP1_MIP-1-largest");

			//Make paramask
			imageCalculator("Add create", "EMP1_MIP-1-largest", "DAPI_mask");
			run("Watershed");
			rename("prelim_paramask");
			roiManager("reset");
			run("Set Measurements...", "  redirect=None decimal=3");
			run("Analyze Particles...", "add");
			count = roiManager("count");

			if (count == 1){
				selectWindow("prelim_paramask");
				rename("paramask");
			}else{
				selectWindow("DAPI_mask");
				rename("paramask");	
			}
			
			run("Morphological Filters", "operation=Opening element=Disk radius=5");
			rename("paramask");

			//check number of parasites
			selectWindow("paramask");
			roiManager("reset");
			run("Set Measurements...", "  redirect=None decimal=3");
			run("Analyze Particles...", "add");
			count = roiManager("count");

			if (count <= 2){

				//make cytoplasm (=cellmask - DAPI_mask)
				imageCalculator("Subtract create", "cellmask", "paramask");
				rename("cytoplasm");

				//REX1 clefts mask (local threshold)
				selectWindow("REX1_MIP");
				run("Duplicate...", " ");
				setOption("ScaleConversions", true);
				run("8-bit");
				run("Auto Local Threshold", "method=Bernsen radius=2 parameter_1=0 parameter_2=0 white");
				rename("REX1mask_clefts");
				selectWindow("cellmask");
				imageCalculator("AND create", "cellmask","REX1mask_clefts");
				imageCalculator("AND create", "REX1mask_clefts","cytoplasm");
				run("Watershed");
				run("Set Measurements...", "  redirect=None decimal=3");
				run("Analyze Particles...", "size=2-Infinity pixel circularity=0.2-1.00 show=Masks");
				run("Invert LUT");
				rename("REX1mask");

				//EMP1 antigen mask (local threshold)
				selectWindow("EMP1_MIP");
				run("Duplicate...", " ");
				setOption("ScaleConversions", true);
				run("8-bit");
				run("Auto Local Threshold", "method=Bernsen radius=2 parameter_1=0 parameter_2=0 white");
				rename("EMP1mask_puncta");
				run("Watershed");
				selectWindow("cellmask");
				imageCalculator("AND create", "cellmask","EMP1mask_puncta");
				rename("EMP1_binary2");
				imageCalculator("AND create", "EMP1_binary2","cytoplasm");
				run("Watershed");
				run("Set Measurements...", "  redirect=None decimal=3");
				run("Analyze Particles...", "size=2-Infinity pixel circularity=0.2-1.00 show=Masks");
				run("Invert LUT");
				rename("EMP1mask");

				//check number of clefts
				selectWindow("REX1mask");
				roiManager("reset");
				run("Set Measurements...", "  redirect=None decimal=3");
				run("Analyze Particles...", "add");
				count = roiManager("count");

				if (count <= 40){
			
					//create 'both' mask
					imageCalculator("Add create", "EMP1mask","REX1mask");
					rename("Bothmask");

		//run analyse particle and add to ROI manager
		roiManager("reset"); 
		run("Analyze Particles...", "show=Nothing include add");

		//create 3 new black images - Redonly, Greenonly, Both
		imageCalculator("Subtract create", "Bothmask","Bothmask");
		rename("REX1only");
		run("Duplicate...", "title=EMP1only");
		run("Duplicate...", "title=Both");

		//make a counter
		all=roiManager("count");
		EMP1only=0;
		REX1only=0;
		both=0;
		
		//set drawing color to white
		setForegroundColor(255, 255, 255);

		//run FOR loop for all ROIs
		for(a=0;a<all;a++){
			
			//for each ROI, check if it is positive to green or red mask
			selectWindow("REX1mask");
			roiManager("Select", a);
			List.setMeasurements; 
			REX1den = List.getValue("RawIntDen"); 
			
			selectWindow("EMP1mask");
			roiManager("Select", a); 
			List.setMeasurements; 
			EMP1den = List.getValue("RawIntDen"); 

			//sort ROI and draw on each image
			if(REX1den>0 && EMP1den>0){
				selectWindow("Both");
				roiManager("Select", a); 
				run("Fill", "slice");
				both++;
			}else if(REX1den>0 && EMP1den==0){
				selectWindow("REX1only");
				roiManager("Select", a); 
				run("Fill", "slice");
				REX1only++;
			}else if(REX1den==0 && EMP1den>0){
				selectWindow("EMP1only");
				roiManager("Select", a); 
				run("Fill", "slice");
				EMP1only++;
			}
		}
		
		//log counting to table
		print(title2, list[i] + "\t" + all + "\t" + EMP1only + "\t" + REX1only + "\t" + both);

		//make raw MIP proof (including DAPI)
		//c1-7: 1-red, 2-green, 3-blue, 4-gray, 5-cyan, 6-magenta, and 7-yellow
		run("Merge Channels...", "c6=REX1_MIP c2=EMP1_MIP c3=DAPI_MIP create keep");
		run("Stack to RGB");
		rename("rawimage");
		run("Select All");
		setForegroundColor(255, 255, 255);
		run("Draw", "slice");

		//make counting proof
		//c1-7: 1-red, 2-green, 3-blue, 4-gray, 5-cyan, 6-magenta, and 7-yellow
		run("Merge Channels...", "c6=REX1only c2=EMP1only c4=Both create keep");
		run("Stack to RGB");
		rename("counted_masks");
		run("Select All");
		setForegroundColor(255, 255, 255);
		run("Draw", "slice");
		run("Combine...", "stack1=rawimage stack2=counted_masks");
		
		//Draw static scale bar and labels
		run("Scale Bar...", "width=2 height=1 font=6 color=Gray background=None location=[Lower Right] hide overlay");	
		//run("Flatten");
		
		saveAs("tif", outdir+nameonly+"_co-occ_proof");
		close();

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
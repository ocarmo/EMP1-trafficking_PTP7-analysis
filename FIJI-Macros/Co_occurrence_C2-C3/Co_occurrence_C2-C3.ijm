/* Co-occurence_C2vC3_count.ijm
 * 2022-05-10 added 'invert LUT' to fix weird bugs re: masking (lines 195, 212, 232, 240)
 *     and changed pixel size threshold from 4 to 3 pixels.
 * 2022-01-18 added 'invert LUT' to fix weird bugs re: masking (lines 195, 212, 232, 240)
 *     and changed pixel size threshold from 4 to 3 pixels.
 * 2021-03-03 This macro takes hyperstacks of IFAs with distinct antibodies in channels 2 and 3 to generate representative puncta masks and then identify co-occuring particles.
 * 
 * Adapted from Ellie Cho's Co-occurrence macro from the 2019 BOMP FIJI Macro workshop.
 */

	//Batch?
	setBatchMode(true);
 	
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
	print(title2, "\\Headings:Imagename \t Total \t C2 only \t C3 only \t Both");

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
		rename("C2_MIP");
		
		image = "C3-"+ list[i]; 
		selectWindow(image);
		run("Z Project...", "projection=[Max Intensity]");
		rename("C3_MIP");

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
		imageCalculator("Add create","C2_MIP","C3_MIP");
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
			
			//make nucleus mask via DAPI
			selectWindow("DAPI_MIP");
			run("Duplicate...", " ");
			run("Gaussian Blur...", "sigma=3"); //changed from median sigma 15
			setAutoThreshold("Default dark");
			run("Convert to Mask");
			rename("DAPI_mask");

			//Select EMP1 largest particle			
			selectWindow("C2_MIP");
			run("Duplicate...", " ");
			setOption("ScaleConversions", true);
			run("8-bit");
			run("Auto Local Threshold", "method=Niblack radius=30 parameter_1=0 parameter_2=0 white");
			run("Keep Largest Region");
			run("Gaussian Blur...", "sigma=2");
			setAutoThreshold("Default dark");
			run("Convert to Mask");
			//run("Morphological Filters", "operation=Opening element=Disk radius=5");
			rename("C2_MIP-1-largest");

			//Make paramask
			imageCalculator("Add create", "C2_MIP-1-largest", "DAPI_mask");
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
			
			run("Morphological Filters", "operation=Opening element=Disk radius=3");
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

				//C3 mask (local threshold)
				selectWindow("C3_MIP");
				run("Duplicate...", " ");
				setOption("ScaleConversions", true);
				run("8-bit");
				run("Auto Local Threshold", "method=Bernsen radius=2 parameter_1=0 parameter_2=0 white");
				rename("C3mask_clefts");
				selectWindow("cellmask");
				imageCalculator("AND create", "cellmask","C3mask_clefts");
				imageCalculator("AND create", "C3mask_clefts","cytoplasm");
				run("Invert LUT");
				run("Watershed");
				run("Set Measurements...", "  redirect=None decimal=3");
				run("Analyze Particles...", "size=1-Infinity pixel circularity=0.01-1.00 show=Masks");
				run("Invert LUT");
				rename("C3mask");

				//C2 clefts mask (local threshold)
				selectWindow("C2_MIP");
				run("Duplicate...", " ");
				setOption("ScaleConversions", true);
				run("8-bit");
				run("Auto Local Threshold", "method=Bernsen radius=2 parameter_1=0 parameter_2=0 white");
				rename("C2mask_clefts");
				selectWindow("cellmask");
				imageCalculator("AND create", "cellmask","C2mask_clefts");
				imageCalculator("AND create", "C2mask_clefts","cytoplasm");
				run("Invert LUT");
				run("Watershed");
				run("Set Measurements...", "  redirect=None decimal=3");
				run("Analyze Particles...", "size=1-Infinity pixel circularity=0.01-1.00 show=Masks");
				run("Invert LUT");
				rename("C2mask");

				//check number of clefts
				selectWindow("C2mask");
				roiManager("reset");
				run("Set Measurements...", "  redirect=None decimal=3");
				run("Analyze Particles...", "add");
				count = roiManager("count");

				if (count <= 100){
			
					//create 'both' mask
					imageCalculator("Add create", "C2mask","C3mask");
					rename("Bothmask");
					run("Invert LUT");

		//run analyse particle and add to ROI manager
		roiManager("reset"); 
		run("Analyze Particles...", "show=Nothing include add");

		//create 3 new black images - Redonly, Greenonly, Both
		imageCalculator("Subtract create", "Bothmask","Bothmask");
		run("Invert LUT");
		rename("C2only");
		run("Duplicate...", "title=C3only");
		run("Duplicate...", "title=Both");

		//make a counter
		all=roiManager("count");
		C2only=0;
		C3only=0;
		both=0;
		
		//set drawing color to white
		setForegroundColor(255, 255, 255);

		//run FOR loop for all ROIs
		for(a=0;a<all;a++){
			
			//for each ROI, check if it is positive to green or red mask
			selectWindow("C3mask");
			roiManager("Select", a);
			List.setMeasurements; 
			C3den = List.getValue("RawIntDen"); 
			
			selectWindow("C2mask");
			roiManager("Select", a); 
			List.setMeasurements; 
			C2den = List.getValue("RawIntDen"); 

			//sort ROI and draw on each image
			if(C2den>0 && C3den>0){
				selectWindow("Both");
				roiManager("Select", a); 
				run("Fill", "slice");
				both++;
			}else if(C2den>0 && C3den==0){
				selectWindow("C2only");
				roiManager("Select", a); 
				run("Fill", "slice");
				C2only++;
			}else if(C2den==0 && C3den>0){
				selectWindow("C3only");
				roiManager("Select", a); 
				run("Fill", "slice");
				C3only++;
			}
		}
		
		//log counting to table
		print(title2, list[i] + "\t" + all + "\t" + C2only + "\t" + C3only + "\t" + both);

		//make raw MIP proof (including DAPI)
		//c1-7: 1-red, 2-green, 3-blue, 4-gray, 5-cyan, 6-magenta, and 7-yellow
		run("Merge Channels...", "c2=C2_MIP c6=C3_MIP c3=DAPI_MIP create keep");
		run("Stack to RGB");
		rename("rawimage");
		run("Select All");
		setForegroundColor(255, 255, 255);
		run("Draw", "slice");

		//make counting proof
		//c1-7: 1-red, 2-green, 3-blue, 4-gray, 5-cyan, 6-magenta, and 7-yellow
		run("Merge Channels...", "c2=C2only c6=C3only c4=Both create keep");
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
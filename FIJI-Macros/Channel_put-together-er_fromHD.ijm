/* Channel_put-together-er_fromHD.ijm
 * adapted from 'Channel_put-together-er', now designed for whole field-of-view deconvolved images.
 * 
 * merging channels into hyperstacks post Huygens Deconvolution
 */

indir=getDirectory("Choose a Directory");
outdir=getDirectory("Choose a Directory");

//Batch?
setBatchMode(true);

list = getFileList(indir);

C1=Array.copy(list);
C2=Array.copy(list);
C3=Array.copy(list);
C4=Array.copy(list);

a=0;b=0;c=0;d=0;

for (i = 0; i < list.length; i++) {
	if(endsWith(list[i], "_ch00.tif")){  
		C1[a]=list[i];a++;
	}else if(endsWith(list[i], "_ch01.tif")){  
		C2[b]=list[i];b++;
	}else if(endsWith(list[i], "_ch02.tif")){  
		C3[c]=list[i];c++;
	}else if(endsWith(list[i], "_ch03.tif")){  
		C4[d]=list[i];d++;
	}
	}
C1=Array.trim(C1,a);		
C2=Array.trim(C2,b);
C3=Array.trim(C3,c);
C4=Array.trim(C4,d);

for (i = 0; i < C1.length; i++) {
	run("Close All");
 	
 	open(indir+C1[i]); rename("C1");
 	open(indir+C2[i]); rename("C2");
 	open(indir+C3[i]); rename("C3");
 	open(indir+C4[i]); rename("C4");
	
	run("Merge Channels...", "c1=C1 c2=C2 c3=C3 c4=C4 create keep");
	Stack.setDisplayMode("grayscale");

	filename = substring(C4[i], 3, lengthOf(C4[i]));
	saveAs("tif", outdir+filename);

	run("Close All");
	run("Collect Garbage");

}
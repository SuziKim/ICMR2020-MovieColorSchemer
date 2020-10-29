#############################
Imagelab Shot Detector (Ilsd)
#############################


### Compiling ###
In order to compile the Ilsd code, you need to have the OpenCV library installed (tested with OpenCV 3.0)
Ilsd comes with pre-compiled Windows binaries for x64 architectures.


### Usage ###
Sintax is:
ilsd.exe <video_name>.<video_ext> <W>
where <W> is the maximum window size (see reference paper [1]).

Example:
.\x64\Release\ilsd.exe video_rai\25008.mp4 3

Ilsd will analyze the input video and produce the following output files:
* <video_name>_shots.txt
  This is the actual output file, that contains the detected shots, one per row, using the format "<starting_frame>\t<ending_frame>\n"
* <video_name>_diffs.txt
  This file contains the computed M^n_w values. First column contains the n value each row refers to, while the following columns report M^n_w for each w, from 0.5 up to <W>.
* <video_name>_trans.txt
  This file contains the detected transitions at each window step.

# Additional features
* RAI dataset included
  The RAI shot and scene detection dataset, used to evaluate Ilsd in [1], is included in the video_rai directory.
  
* Performance evaluation
  Ilsd can evaluate itself using precision, recall and F1 measures.
  Just place a <video_name>_gt.txt file in the same directory of the video, with the ground-truth shots and using the same format of <video_name>_shots.txt.
  The Rai dataset comes with a ground-truth file for each video.

* Comparison with other algorithms
  Ilsd can also compare its performance against a second algorithm.
  To use this feature, place a <video_name>_comparison.txt file in the same directory of the video, with the shots detected by the second algorithm in the same format of <video_name>_shots.txt.
  In the Rai dataset, each video has a comparison.txt file, that lets you compare Ilsd results with those of [2].

* Caching of M^n_w values
  Ilsd caches the computed M^n_w values in <video_name>_diffs.txt. If this file is found along with <video_name>.<video_ext>, Ilsd will use the pre-computed values, regardless of specified window size <W>.
  This also means that if you need to test our algorithm with different <W> values you always have to delete <video_name>_diffs.txt before changing <W>.
  
  
### History ###

* March 2015: first Ilsd version is released.

### Bugs and contacts ###

If you find any bug please let us know. Also if you need clarifications on the code, feel free to drop us a line. You can find our contacts on our webpage:

http://imagelab.ing.unimore.it

### LICENSE CONDITIONS ###

Copyright (C) 2015 Imagelab

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

### References ####
[1] Baraldi, L., Grana, C., Cucchiara, R.: Shot and scene detection via hierarchical clustering for re-using broadcast video. Submitted to CAIP 2015
[2] Apostolidis, E., Mezaris, V.: Fast Shot Segmentation Combining Global and Local Visual Descriptors. In: IEEE Int. Conf. Acoustics, Speech and Signal Process. pp. 6583{6587 (2014)
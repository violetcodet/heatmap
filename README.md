heatmap.py
==========

Python module to create heatmaps.   See http://jjguy.com/heatmap/ for details.

And, you need to generate key points by yourself
A representation of the points (x,y values) to process.Can be a flattened array/tuple or any combination of 2 dimensional array or tuple iterables i.e. [x1,y1,x2,y2], [(x1,y1),(x2,y2)], etc.
If weights are being used there are expected to be 3 'columns' in the 2 dimensionable iterable or a multiple of 3 points in the flat array/tuple i.e. (x1,y1,z1,x2,y2,z2), ([x1,y1,z1],[x2,y2,z2]) etc. The third (weight) value can be anything but it is best to have a normalised weight between 0 and 1. For best performance, if convenient use a flattened array as this is what is used internally and requires no conversion.

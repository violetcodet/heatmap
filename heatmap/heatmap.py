import os
import sys
import ctypes
import platform
import math
from . import colorschemes
from PIL import Image
import glob

use_pyproj = False
try:
  import pyproj
  use_pyproj = True
except:
  pass

class Heatmap:
    """
    Create heatmaps from a list of 2D coordinates with optional weighting per coordinate pair.

    Heatmap requires the Python Imaging Library and Python 2.6+ for Python3 backports.

    Coordinates autoscale to fit within the image dimensions, so if there are
    anomalies or outliers in your dataset, results won't be what you expect. You
    can override the autoscaling by using the area parameter to specify the data bounds.

    The output is a PNG with transparent background, suitable alone or to overlay another
    image or such.  You can also save a KML file to use in Google Maps if x/y coordinates
    are lat/long coordinates. Make your own wardriving maps or visualize the footprint of
    your wireless network.

    For accurate geospatial results it is advised to use the optional [proj] install.
    This also allows for output in other coordinate systems such as Mercator.

    Most of the magic starts in heatmap(), see below for description of that function.
    """

    KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Folder>
    <GroundOverlay>
      <Icon>
        <href>%s</href>
      </Icon>
      <LatLonBox>
        <north>%2.16f</north>
        <south>%2.16f</south>
        <east>%2.16f</east>
        <west>%2.16f</west>
        <rotation>0</rotation>
      </LatLonBox>
    </GroundOverlay>
  </Folder>
</kml>"""

    def __init__(self, libpath=None):
        self.img = None
        # if you're reading this, it's probably because this
        # hacktastic garbage failed.  sorry.  I deserve a jab or two via @jjguy.

        if libpath:
            self._heatmap = ctypes.cdll.LoadLibrary(libpath)

        else:
            # establish the right library name, based on platform and arch.  Windows
            # are pre-compiled binaries; linux machines are compiled during setup.
            self._heatmap = None
            libname = "cHeatmap"
            if "cygwin" in platform.system().lower():
                libname = "cHeatmap.dll"
            if "windows" in platform.system().lower():
                libname = "cHeatmap-x86.dll"
                if "64" in platform.architecture()[0]:
                    libname = "cHeatmap-x64.dll"
            # now rip through everything in sys.path to find 'em.  Should be in site-packages
            # or local dir
            for d in sys.path:
                #if os.path.isfile(os.path.join(d, libname+'.so')):
                if os.path.isfile(os.path.join(d, libname)):
                    self._heatmap = ctypes.cdll.LoadLibrary(
                        #os.path.join(d, libname+'.so'))
                      os.path.join(d, libname))
            # check for cpython-*.so prefix for object files which seems to be the ones
            # copied on install in the travis python3 environment (even with the same version of setuptools)
            # may investigate further and do the test based on execution environment
            if not self._heatmap:
              for d in sys.path:
                file = glob.glob(os.path.join(d,libname+'.cpython-*.so'))
                if file:
                    self._heatmap = ctypes.cdll.LoadLibrary(file[0])

        if not self._heatmap:
            raise Exception("Heatmap shared library not found in PYTHONPATH.")

    def heatmap(self, points, dotsize=150, opacity=128, size=(1024, 1024), scheme="classic", area=None, 
                weighted=0, srcepsg=None, dstepsg='EPSG:3857'):
        """
        points   -> A representation of the points (x,y values) to process.
                    Can be a flattened array/tuple or any combination of 2 dimensional 
                    array or tuple iterables i.e. [x1,y1,x2,y2], [(x1,y1),(x2,y2)], etc.
                    If weights are being used there are expected to be 3 'columns'
                    in the 2 dimensionable iterable or a multiple of 3 points in the 
                    flat array/tuple i.e. (x1,y1,z1,x2,y2,z2), ([x1,y1,z1],[x2,y2,z2]) etc.
                    The third (weight) value can be anything but it is
                    best to have a normalised weight between 0 and 1.
                    For best performance, if convenient use a flattened array 
                    as this is what is used internally and requires no conversion.
        dotsize  -> the size of a single coordinate in the output image in
                    pixels, default is 150px.  Tweak this parameter to adjust
                    the resulting heatmap.
        opacity  -> the strength of a single coordiniate in the output image.
                    Tweak this parameter to adjust the resulting heatmap.
        size     -> tuple with the width, height in pixels of the output PNG
        scheme   -> Name of color scheme to use to color the output image.
                    Use schemes() to get list.  (images are in source distro)
        area     -> Specify bounding coordinates of the output image. Tuple of
                    tuples: ((minX, minY), (maxX, maxY)).  If None or unspecified,
                    these values are calculated based on the input data.
        weighted -> Is the data weighted (0 or 1)
        srcepsg  -> epsg code of the source, set to None to ignore.
                    If using KML output make sure this is set otherwise either the image
                    or the overlay coordinates will be out.
        dstepsg  -> epsg code of the destination, ignored if srcepsg is not set.
                    Defaults to EPSG:3857 (Cylindrical Mercator). 
                    Due to linear interpolation in heatmap.c it only makes sense to use linear 
                    output projections. If outputting to KML for google earth client overlay use 
                    EPSG:4087 (World Equidistant Cylindrical).
        """
        self.dotsize = dotsize
        self.opacity = opacity
        self.size = size
        self.points = points
        self.weighted = weighted
        self.srcepsg = srcepsg
        self.dstepsg = dstepsg

        if self.srcepsg and not use_pyproj:
          raise Exception('srcepsg entered but pyproj is not available')

        if area is not None:
            self.area = area
            self.override = 1
        else:
            self.area = ((0, 0), (0, 0))
            self.override = 0

        #convert area for heatmap.c if required
        ((east, south), (west, north)) = self.area
        if use_pyproj and self.srcepsg is not None and self.srcepsg != self.dstepsg:
          source = pyproj.Proj(init=self.srcepsg)
          dest = pyproj.Proj(init=self.dstepsg)
          (east,south) = pyproj.transform(source,dest,east,south)
          (west,north) = pyproj.transform(source,dest,west,north)

        if scheme not in self.schemes():
            tmp = "Unknown color scheme: %s.  Available schemes: %s" % (
                scheme, self.schemes())
            raise Exception(tmp)

        arrPoints = self._convertPoints()
        arrScheme = self._convertScheme(scheme)
        arrFinalImage = self._allocOutputBuffer()

        ret = self._heatmap.tx(
            arrPoints, len(arrPoints), size[0], size[1], dotsize,
            arrScheme, arrFinalImage, opacity, self.override,
            ctypes.c_float(east), ctypes.c_float(south),
            ctypes.c_float(west), ctypes.c_float(north), weighted)

        if not ret:
            raise Exception("Unexpected error during processing.")

        self.img = Image.frombuffer('RGBA', (self.size[0], self.size[1]), 
                                    arrFinalImage, 'raw', 'RGBA', 0, 1)
        return self.img

    def _allocOutputBuffer(self):
        return (ctypes.c_ubyte * (self.size[0] * self.size[1] * 4))()

    def _convertPoints(self):
        """ flatten the list of tuples, convert into ctypes array """

        if isinstance(self.points,tuple):
          self.points = list(self.points)
        if isinstance(self.points[0],tuple):
          self.points = list(sum(self.points,()))
        elif isinstance(self.points[0],list):
          self.points = sum(self.points,[])

        #convert if required, need to copy as may use points later for _range.
        if use_pyproj and self.srcepsg is not None and self.srcepsg != self.dstepsg:
          converted =list(self.points)
          source = pyproj.Proj(init=self.srcepsg)
          dest = pyproj.Proj(init=self.dstepsg) 
          #nicer way? map/lambda will retun 2/3 tuple so need to flatten again
          inc = 3 if self.weighted else 2
          for i in range(0, len(self.points), inc):
            (x,y) = pyproj.transform(source,dest,self.points[i],self.points[i+1])
            converted[i] = x
            converted[i+1] = y
          arr_pts = (ctypes.c_float * (len(converted))) (*converted)
        else:
          arr_pts = (ctypes.c_float * (len(self.points))) (*self.points)
        return arr_pts

    def _convertScheme(self, scheme):
        """ flatten the list of RGB tuples, convert into ctypes array """

        flat = list(sum(colorschemes.schemes[scheme],()))
        arr_cs = (ctypes.c_int * (len(flat)))(*flat)
        return arr_cs

    def _ranges(self):
        """ walks the list of points and finds the
        max/min x & y values in the set """
        minX = self.points[0]
        minY = self.points[1]
        maxX = minX
        maxY = minY
        inc = 3 if self.weighted else 2
        for i in range(0,len(self.points),inc):
            minX = min(self.points[i], minX)
            minY = min(self.points[i+1], minY)
            maxX = max(self.points[i], maxX)
            maxY = max(self.points[i+1], maxY)

        return ((minX, minY), (maxX, maxY))

    def saveKML(self, kmlFile):
        """
        Saves a KML template to use with google earth.  Assumes x/y coordinates
        are lat/long, and creates an overlay to display the heatmap within Google
        Earth.

        kmlFile ->  output filename for the KML.
        """
        if self.img is None:
            raise Exception("Must first run heatmap() to generate image file.")

        tilePath = os.path.splitext(kmlFile)[0] + ".png"
        self.img.save(tilePath)

        if self.override:
            ((west, south), (east, north)) = self.area
        else:
            ((west, south), (east, north)) = self._ranges()

        #convert overlay BBOX if required
        if use_pyproj and self.srcepsg is not None and self.srcepsg != 'EPSG:4326':
          source = pyproj.Proj(init=self.srcepsg)
          dest = pyproj.Proj(init='EPSG:4326')
          (east,south) = pyproj.transform(source,dest,east,south)
          (west,north) = pyproj.transform(source,dest,west,north)

        bytes = self.KML % (tilePath, north, south, east, west)
        fh = open(kmlFile, "w")
        fh.write(bytes)
        fh.close()

    def schemes(self):
        """
        Return a list of available color scheme names.
        """
        return colorschemes.valid_schemes()

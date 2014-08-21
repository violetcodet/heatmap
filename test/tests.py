import random

from PIL import Image

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import heatmap
from heatmap import colorschemes


class TestHeatmap(unittest.TestCase):
    """unittests for TestHeatmap"""

    def heatmapImage(self,name,pts,kwargs={},saveKML=False):
        img = self.heatmap.heatmap(pts, **kwargs)
        self.assertTrue(isinstance(img, Image.Image))
        if (saveKML):
          self.heatmap.saveKML(name+".kml")
        else:
          img.save(name+".png")
        return img
    
    def setUp(self):
        self.heatmap = heatmap.Heatmap()
    
    def test_heatmap_random_defaults(self):
        pts = [(random.random(), random.random()) for x in range(400)]
        self.heatmapImage("01-400-random", pts)
    
    def test_heatmap_vert_line(self):
        pts = [(50, x) for x in range(100)]
        self.heatmapImage("02-vert-line", pts, kwargs={"area" : ((0, 0), (200, 200))})

    def test_heatmap_horz_line(self):
        pts = [(x, 300) for x in range(600, 700)]
        self.heatmapImage("03-horz-line", pts, kwargs={ "size" : (800,400), "area" : ((0, 0), (800, 400))})

    def test_heatmap_random(self):
        # this should also generate a warning on stderr of overly dense
        pts = [(random.random(), random.random()) for x in range(40000)]
        self.heatmapImage("04-40k-random", pts , kwargs={ "dotsize" : 25, "opacity" : 128})

    def test_heatmap_square(self):
        pts = [(x*100, 50) for x in range(2, 50)]
        pts.extend([(4850, x*100) for x in range(2, 50)])
        pts.extend([(x*100, 4850) for x in range(2, 50)])
        pts.extend([(50, x*100) for x in range(2, 50)])
        self.heatmapImage("05-square", pts , kwargs={ "dotsize" : 100, "area" : ((0,0), (5000, 5000)) })

    def test_heatmap_single_point(self):
        pts = [(random.uniform(-77.012, -77.050), 
                random.uniform(38.888, 38.910)) for x in range(100)]
        self.heatmapImage("06-wash-dc", pts)

    def test_heatmap_weighted(self):
        #normal should be the same as 100%, 75% should have same pattern but smaller
        pts = [(random.uniform(30,40), random.uniform(-30,-40)) for x in range(400)]
        norm = self.heatmapImage("07-400-normal", pts, saveKML=True)
        weight = self.heatmapImage("07-400-100percent", list(map( lambda x_y : (x_y[0],x_y[1],1), pts)), kwargs={ "weighted" : 1 }, saveKML=True)
        self.assertEqual(norm,weight)
        weight2 = self.heatmapImage("07-400-75percent", list(map( lambda x_y : (x_y[0],x_y[1],.75), pts)), kwargs={ "weighted" : 1 }, saveKML=True)
        self.assertNotEqual(norm,weight2)

    def test_heatmap_random_datatypes(self):
        #all of the below should turn out to be the same, if not there are issues
        pts = tuple((random.random(),random.random(),1) for x in range(400))
        tt = self.heatmapImage("08-400-tupleoftuples", tuple(map(lambda x_y_z : (x_y_z[0],x_y_z[1]), pts)), saveKML=True)
        ttw = self.heatmapImage("08-400-tupleoftuplesweighted", pts , kwargs = { "weighted" : True }, saveKML=True)
        at = self.heatmapImage("08-400-arrayoftuples", list(map(lambda x_y_z : (x_y_z[0],x_y_z[1]), pts)), saveKML=True)
        atw = self.heatmapImage("08-400-arrayoftuplesweighted", list(pts), kwargs = { "weighted" : True }, saveKML=True)
        ta = self.heatmapImage("08-400-tupleofarrays", tuple(map(lambda x_y_z : [x_y_z[0],x_y_z[1]], pts)), saveKML=True)
        taw = self.heatmapImage("08-400-tupleofarraysweighted", tuple(map(lambda x_y_z : [x_y_z[0],x_y_z[1],x_y_z[2]], pts)), kwargs = { "weighted" : True }, saveKML=True)
        aa = self.heatmapImage("08-400-arrayofarrays", list(map(lambda x_y_z : [x_y_z[0],x_y_z[1]], pts)), saveKML=True)
        aaw = self.heatmapImage("08-400-arrayofarraysweighted", list(map(lambda x_y_z : [x_y_z[0],x_y_z[1],x_y_z[2]], pts)), kwargs = { "weighted" : True }, saveKML=True)
        f = self.heatmapImage("08-400-flat", sum(map(lambda x_y_z : [x_y_z[0],x_y_z[1]], pts),[]), saveKML=True)
        fw = self.heatmapImage("08-400-flatweighted", sum(map(lambda x_y_z : [x_y_z[0],x_y_z[1],x_y_z[2]], pts),[]), kwargs = { "weighted" : True }, saveKML=True)
        self.assertEqual(tt,ttw)
        self.assertEqual(tt,ttw)
        self.assertEqual(tt,at)
        self.assertEqual(tt,atw)
        self.assertEqual(tt,ta)
        self.assertEqual(tt,taw)
        self.assertEqual(tt,aa)
        self.assertEqual(tt,aaw)
        self.assertEqual(tt,f)
        self.assertEqual(tt,fw)

    def test_heatmap_area(self):
      MAX_SIZE=8192
      PPD=100
      dotsize=100
      pts = [[x*2,x, 1 if x==0 else 0.75] for x in range(-45,46)]
      pts = sum(pts,[])
      west = pts[0]
      south = pts[1]
      east = west
      north = south
      for i in range(0,len(pts),3):
          west = min(pts[i], west)
          south = min(pts[i+1], south)
          east = max(pts[i], east)
          north = max(pts[i+1], north)
      width = int((east - west)*PPD + dotsize/2)
      height = int((north - south)*PPD + dotsize/2)
      largestVal = max(width,height)
      if largestVal > MAX_SIZE:
         scale = float(MAX_SIZE)/largestVal
         height = int(height*scale)
         width = int(width*scale)
         PPD = float((width-dotsize/2))/(east-west)
      dotDegrees = dotsize/2/PPD
      bounds = ((west-dotDegrees, south-dotDegrees),(east+dotDegrees,north+dotDegrees))
      #these should be the same except less cutin off from manual area
      self.heatmapImage("11-400-areaTest", pts, { "size" : (width, height), "dotsize" : dotsize, "area" : bounds, "weighted" : 1}, saveKML = True)
      self.heatmapImage("11-400-areaTestNormal", pts , kwargs = { "size" : (width, height), "dotsize" : dotsize, "weighted" : 1}, saveKML = True)

    def test_heatmap_random_proj(self):
        pts = [(random.uniform(-180,180),random.uniform(-90,90)) for x in range(400)]
        norm = self.heatmapImage("09-400-normal", pts, saveKML = True)
        #4087 should be the same as 'normal' as no conversion required, kml boundary should be different (not tested) though as not converted to 4326
        epsg4087 = self.heatmapImage("90-400-EPSG4087", pts, kwargs = { "srcepsg" : "EPSG:4087", "dstepsg" : "EPSG:4087"}, saveKML = True)
        self.assertEqual(norm,epsg4087)
        #4326 should be roughly the same as 'normal' but not the same as WGS84 != 4087
        epsg4326 = self.heatmapImage("09-400-EPSG4326", pts, kwargs = { "srcepsg" : "EPSG:4326", "dstepsg" : "EPSG:4087" }, saveKML = True)
        self.assertNotEqual(norm,epsg4326)
        #3857DST should be well different
        epsg3857DST = self.heatmapImage("09-400-EPSG3857DST", pts, kwargs = { "srcepsg" : "EPSG:4326"}, saveKML = True)
        self.assertNotEqual(norm,epsg3857DST)
        #testing conversion of src epsg, image is possibly similar do to linearity at the equator but KML boundary should be very different (not tested)
        epsg3857 = self.heatmapImage("09-400-EPSG3857", pts, kwargs = { "srcepsg" : "EPSG:3857", "dstepsg" : "EPSG:4087" }, saveKML = True)

    def test_heatmap_weighted_proj(self):
        pts = [(x*2,x, 1 if x==0 else 0.75) for x in range(-89,90)]
        norm = self.heatmapImage("10-400-normal", pts, kwargs = { "size" : (2048, 1024), "dotsize" : 50, "weighted" : 1}, saveKML = True)
        #4087 should be the same as 'normal' as no conversion required, kml boundary should be different (not tested) though as not converted to 4326
        epsg4087 = self.heatmapImage("10-400-EPSG4087", pts, kwargs = { "srcepsg" : "EPSG:4087", "dstepsg" : "EPSG:4087", "size" : (2048, 1024), "dotsize" : 50, "weighted" : 1}, saveKML = True)
        self.assertEqual(norm,epsg4087)
        #4326 should be roughly the same as 'normal' but not the same as WGS84 != 4087
        norm = self.heatmapImage("10-400-normal", pts, kwargs = { "size" : (2048, 1024), "dotsize" : 50, "weighted" : 1}, saveKML = True)
        epsg4326 = self.heatmapImage("10-400-EPSG4326SRC", pts, kwargs = { "srcepsg" : "EPSG:4326", "dstepsg" : "EPSG:4087", "size" : (2048, 1024), "dotsize" : 50, "weighted" : 1}, saveKML = True)
        self.assertNotEqual(norm,epsg4326)
        #3857DST and 4087 should roughly meet at 0,0 as symetrical around the equator
        epsg3857DST = self.heatmapImage("10-400-EPSG3857DST", pts, kwargs = { "srcepsg" : "EPSG:4326", "size" : (2048, 1024), "dotsize" : 50, "weighted" : 1}, saveKML = True)
        self.assertNotEqual(norm,epsg3857DST)
        #testing conversion of src epsg, image is possibly similar do to linearity at the equator but KML boundary should be very different (not tested)
        epsg3857 = self.heatmapImage("10-400-EPSG3857", pts, kwargs = { "srcepsg" : "EPSG:3857", "dstepsg" : "EPSG:4087",  "size" : (2048, 1024), "dotsize" : 50, "weighted" : 1 }, saveKML = True)
    
    def test_heatmap_exceptions(self):
 
      #test invalid (empty) heatmap, should print error to stdout
      emptyHeatmapArgs = [Exception, 'Unexpected error', self.heatmap.heatmap, ([],)]
      emptyHeatmapKwargs = {}
      #test invalid scheme
      invalidColorSchemeArgs = [Exception, 'Unknown color scheme', self.heatmap.heatmap, ([],)]
      invalidColourSchemeKwargs = {'scheme' : 'invalid'}
      #test saveKML before create heatmap
      saveKMLArgs = [Exception, 'Must first run heatmap', self.heatmap.saveKML,"test.kml"]
      saveKMLKwargs = {}

      #better way? no __verison__ in unittest
      try:
        function = self.assertRaisesRegex
      except:
        try: 
          function = self.assertRaisesRegexp
        except:
          function = self.assertRaises
          emptyHeatmapArgs.pop(1)
          invalidColorSchemeArgs.pop(1)
          saveKMLArgs.pop(1)
      
      function(*emptyHeatmapArgs, **emptyHeatmapKwargs)
      function(*invalidColorSchemeArgs, **invalidColourSchemeKwargs)
      function(*saveKMLArgs, **saveKMLKwargs)

class TestColorScheme(unittest.TestCase):
    def test_schemes(self):
        keys = colorschemes.valid_schemes()
        self.assertEqual(sorted(list(keys)), sorted(['fire', 'pgaitch', 'pbj', 'omg', 'classic']))

    def test_values(self):
        for key, values in colorschemes.schemes.items():
            self.assertTrue(isinstance(values, list))
            self.assertEqual(len(values), 256)
            for value in values:
                self.assertTrue(isinstance(value, tuple))
                self.assertEqual(len(value), 3)
                
                r, g, b = value
                
                self.assertTrue(isinstance(r, int))
                self.assertTrue(isinstance(g, int))
                self.assertTrue(isinstance(b, int))

if __name__ == "__main__":
    unittest.main()

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
    
    def setUp(self):
        self.heatmap = heatmap.Heatmap()
    
    def test_heatmap_random_defaults(self):
        pts = [(random.random(), random.random()) for x in range(400)]
        img = self.heatmap.heatmap(pts)
        img.save("01-400-random.png")
        self.assertTrue(isinstance(img, Image.Image))
    
    def test_heatmap_vert_line(self):
        pts = [(50, x) for x in range(100)]
        img = self.heatmap.heatmap(pts, area=((0, 0), (200, 200)))
        img.save("02-vert-line.png")
        self.assertTrue(isinstance(img, Image.Image))

    def test_heatmap_horz_line(self):
        pts = [(x, 300) for x in range(600, 700)]
        img = self.heatmap.heatmap(pts, size=(800,400), area=((0, 0), (800, 400)))
        img.save("03-horz-line.png")
        self.assertTrue(isinstance(img, Image.Image))

    def test_heatmap_random(self):
        pts = [(random.random(), random.random()) for x in range(40000)]
        # this should also generate a warning on stderr of overly dense
        img = self.heatmap.heatmap(pts, dotsize=25, opacity=128)
        img.save("04-40k-random.png")
        self.assertTrue(isinstance(img, Image.Image))

    def test_heatmap_square(self):
        pts = [(x*100, 50) for x in range(2, 50)]
        pts.extend([(4850, x*100) for x in range(2, 50)])
        pts.extend([(x*100, 4850) for x in range(2, 50)])
        pts.extend([(50, x*100) for x in range(2, 50)])
        img = self.heatmap.heatmap(pts, dotsize=100, area=((0,0), (5000, 5000)))
        img.save("05-square.png")
        self.assertTrue(isinstance(img, Image.Image))

    def test_heatmap_single_point(self):
        pts = [(random.uniform(-77.012, -77.050), 
                random.uniform(38.888, 38.910)) for x in range(100)]
        img = self.heatmap.heatmap(pts)
        self.heatmap.saveKML("06-wash-dc.kml")
        self.assertTrue(isinstance(img, Image.Image))

    def test_heatmap_weighted(self):
        #normal should be the same as 100%, 75% should have same pattern but smaller
        pts = [(random.uniform(30,40), random.uniform(-30,-40)) for x in range(400)]
        # this should also generate a warning on stderr of overly dense
        img = self.heatmap.heatmap(pts)
        img.save("07-400-normal.png")
        self.heatmap.saveKML("07-400-normal.kml")
        self.assertTrue(isinstance(img, Image.Image))
        img = self.heatmap.heatmap(list(map( lambda x_y : (x_y[0],x_y[1],1), pts)), weighted=1)
        img.save("07-400-100percent.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("07-400-100percent.kml")
        img = self.heatmap.heatmap(list(map( lambda x_y : (x_y[0],x_y[1],.75), pts)), weighted=1)
        img.save("07-400-75percent.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("07-400-75percent.kml")

    def test_heatmap_random_datatypes(self):
        #all of the below should turn out to be the same, if not there are issues
        pts = tuple((random.random(),random.random(),1) for x in range(400))
        img = self.heatmap.heatmap(tuple(map(lambda x_y_z : (x_y_z[0],x_y_z[1]), pts)))
        img.save("08-400-tupleoftuples.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-tupleoftuples.kml")
        img = self.heatmap.heatmap(pts, weighted=1)
        img.save("08-400-tupleoftuplesweighted.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-tupleoftuplesweighted.kml")
        img = self.heatmap.heatmap(list(map(lambda x_y_z : (x_y_z[0],x_y_z[1]), pts)))
        img.save("08-400-arrayoftuples.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-arrayoftuples.kml")
        img = self.heatmap.heatmap(list(pts), weighted=1)
        img.save("08-400-arrayoftuplesweighted.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-arrayoftuplesweighted.kml")
        img = self.heatmap.heatmap(tuple(map(lambda x_y_z : [x_y_z[0],x_y_z[1]], pts)))
        img.save("08-400-tupleofarrays.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-tupleofarrays.kml")
        img = self.heatmap.heatmap(tuple(map(lambda x_y_z : [x_y_z[0],x_y_z[1],x_y_z[2]], pts)), weighted=1)
        img.save("08-400-tupleofarraysweighted.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-tupleofarrayweighted.kml")
        img = self.heatmap.heatmap(list(map(lambda x_y_z : [x_y_z[0],x_y_z[1]], pts)))
        img.save("08-400-arrayofarrays.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-arrayofarrays.kml")
        img = self.heatmap.heatmap(list(map(lambda x_y_z : [x_y_z[0],x_y_z[1],x_y_z[2]], pts)), weighted=1)
        img.save("08-400-arrayofarraysweighted.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-arrayofarraysweighted.kml")
        img = self.heatmap.heatmap(sum(map(lambda x_y_z : [x_y_z[0],x_y_z[1]], pts),[]))
        img.save("08-400-flat.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-flat.kml")
        img = self.heatmap.heatmap(sum(map(lambda x_y_z : [x_y_z[0],x_y_z[1],x_y_z[2]], pts),[]), weighted=1)
        img.save("08-400-flatweighted.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-flatweighted.kml")

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
      img = self.heatmap.heatmap(pts, size = (width, height), dotsize = dotsize, area=bounds, weighted = 1)
      img.save("11-400-areaTest.png")
      self.assertTrue(isinstance(img, Image.Image))
      self.heatmap.saveKML("11-400-areaTest.kml")
      img = self.heatmap.heatmap(pts, size = (width, height), dotsize = dotsize, weighted = 1)
      img.save("11-400-areaTestNormal.png")
      self.assertTrue(isinstance(img, Image.Image))
      self.heatmap.saveKML("11-400-areaTestNormal.kml")

    def test_heatmap_random_proj(self):
        #4087 should be the same as 'normal'
        pts = [(random.uniform(-180,180),random.uniform(-90,90)) for x in range(400)]
        img = self.heatmap.heatmap(pts)
        img.save("09-400-normal.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("09-400-normal.kml")
        img = self.heatmap.heatmap(pts,srcepsg='EPSG:4326')
        img.save("09-400-EPSG3857.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("09-400-EPSG3857.kml")
        img = self.heatmap.heatmap(pts, srcepsg='EPSG:4326',dstepsg='EPSG:4087')
        img.save("09-400-EPSG4087.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("09-400-EPSG4087.kml")
        img = self.heatmap.heatmap(pts, srcepsg='EPSG:3857',dstepsg='EPSG:4087')
        img.save("09-400-EPSG4087.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("09-400-EPSG4087.kml")

    def test_heatmap_weighted_proj(self):
        #normal should be the same as 4087
        #3857 and 4087 should roughly meet at 0,0 as symetrical around the equator
        pts = [(x*2,x, 1 if x==0 else 0.75) for x in range(-89,90)]
        img = self.heatmap.heatmap(pts, size = (2048, 1024), dotsize = 50, weighted = 1)
        img.save("10-400-normal.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("10-400-normal.kml")
        img = self.heatmap.heatmap(pts,srcepsg='EPSG:4326', size = (2048, 1024), dotsize = 50, weighted = 1)
        img.save("10-400-EPSG3857.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("10-400-EPSG3857.kml")
        img = self.heatmap.heatmap(pts, srcepsg='EPSG:4326',dstepsg='EPSG:4087', size = (2048, 1024), dotsize = 50, weighted = 1)
        img.save("10-400-EPSG4087.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("10-400-EPSG4087.kml")

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

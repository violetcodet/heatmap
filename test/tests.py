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

    def test_invalid_heatmap(self):
        self.assertRaises(Exception, self.heatmap.heatmap, ([],))

    def test_heatmap_weighted(self):
        pts = [(random.random(), random.random()) for x in range(400)]
        # this should also generate a warning on stderr of overly dense
        img = self.heatmap.heatmap(pts)
        img.save("07-400-normal.png")
        self.heatmap.saveKML("07-400-normal.kml")
        self.assertTrue(isinstance(img, Image.Image))
        img = self.heatmap.heatmap(map( lambda (x,y) : (x,y,1), pts), weighted=1)
        img.save("07-400-100percent.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("07-400-100percent.kml")
        img = self.heatmap.heatmap(map( lambda (x,y) : (x,y,.75), pts), weighted=1)
        img.save("07-400-75percent.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("07-400-75percent.kml")

    def test_heatmap_random_datatypes(self):
        pts = [[random.random(),random.random()] for x in range(400)]
        img = self.heatmap.heatmap(sum(pts,[]))
        img.save("08-400-array.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-array.kml")
        img = self.heatmap.heatmap(map(lambda (x,y) : (x,y), pts))
        img.save("08-400-arrayoftuples.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-arrayoftuples.kml")
        img = self.heatmap.heatmap(pts)
        img.save("08-400-arrayofarrays.png")
        self.assertTrue(isinstance(img, Image.Image))
        self.heatmap.saveKML("08-400-arrayofarrays.kml")

class TestColorScheme(unittest.TestCase):
    def test_schemes(self):
        keys = colorschemes.valid_schemes()
        self.assertEqual(keys, ['fire', 'pgaitch', 'pbj', 'omg', 'classic'])

    def test_values(self):
        for key, values in colorschemes.schemes.iteritems():
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

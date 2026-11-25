import unittest
from graphics.growth import hitung_kondisi, trapesium, FASE
from graphics.lsystem import string_tembakau

class GrowthTest(unittest.TestCase):
    def test_boundaries(self):
        for x, expected in [(0,0),(30,.5),(60,1),(180,1),(450,0),(1200,0)]:
            self.assertAlmostEqual(trapesium(x,0,60,180,450),expected)
    def test_stress(self):
        for i in range(len(FASE)):
            dry, wet, good = [hitung_kondisi(i,x) for x in (0,500,100)]
            self.assertGreater(dry['stres_kering'],0)
            self.assertEqual(dry['stres_basah'],0)
            self.assertGreater(wet['stres_basah'],0)
            self.assertEqual(good['indeks_kondisi'],100)
            self.assertEqual(good['jumlah_daun'],string_tembakau(FASE[i]['iter'],False).count('L'))

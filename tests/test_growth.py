import unittest
from graphics.growth import hitung_kondisi, trapesium, FASE
from graphics.lsystem import string_tembakau

class GrowthTest(unittest.TestCase):
    def test_boundaries(self):
        for x, expected in [(0,0),(30,.5),(60,1),(180,1),(450,0),(1200,0)]:
            self.assertAlmostEqual(trapesium(x,0,60,180,450),expected)
    def test_stress(self):
        for i in range(len(FASE)):
            dry, wet, good = [hitung_kondisi(i,x) for x in (0,500,150)]
            self.assertGreater(dry['stres_kering'],0)
            self.assertEqual(dry['stres_basah'],0)
            self.assertGreater(wet['stres_basah'],0)
            self.assertEqual(good['indeks_kondisi'],100)
            self.assertEqual(good['jumlah_daun'],string_tembakau(FASE[i]['iter'],False).count('L'))

    def test_fao_kc_scenario(self):
        for i, kc in enumerate((0.35, 0.35, 0.75, 1.10, 0.90)):
            demand = kc * 120
            half = hitung_kondisi(i, demand / 2)
            self.assertAlmostEqual(half["etc_skenario_mm"], demand)
            self.assertEqual(half["stres_kering"], 0.5)
            self.assertEqual(half["stres_basah"], 0.0)
            self.assertEqual(hitung_kondisi(i, demand)["indeks_kondisi"], 100)
            self.assertEqual(hitung_kondisi(i, 315)["stres_basah"], 0.5)
            self.assertEqual(hitung_kondisi(i, 450)["stres_basah"], 1.0)

import unittest
from app import app

class ApiTest(unittest.TestCase):
    def setUp(self): self.client = app.test_client()
    def test_info(self):
        for query in ('fase=99&hujan=NaN','fase=2&hujan=1200','fase=0&hujan=100'):
            r=self.client.get('/api/info?'+query)
            self.assertEqual(r.status_code,200)
            self.assertIn('kategori_simulasi',r.json['kondisi'])
    def test_png(self):
        r=self.client.get('/render.png?fase=4&hujan=100')
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.data.startswith(b'\x89PNG\r\n\x1a\n'))
    def test_data(self):
        r=self.client.get('/api/data')
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.json)

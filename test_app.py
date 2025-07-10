import unittest
from app import app, allowed_file  

class WhiteboxTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # --- UNIT TESTING ---
    def test_allowed_file_valid_extensions(self):
        self.assertTrue(allowed_file("video.mp4"))
        self.assertTrue(allowed_file("video.avi"))
        self.assertTrue(allowed_file("video.webm"))

    def test_allowed_file_invalid_extensions(self):
        self.assertFalse(allowed_file("video.txt"))
        self.assertFalse(allowed_file("video.jpeg"))
        self.assertFalse(allowed_file(""))

    # --- ROUTE TESTING ---
    def test_index_page_loads(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html', response.data)

    def test_login_page_loads(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username', response.data)

    def test_register_page_loads(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username', response.data)

    def test_dashboard_redirects_when_not_logged_in(self):
        response = self.app.get('/dashboard', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username', response.data)

if __name__ == '__main__':
    unittest.main()

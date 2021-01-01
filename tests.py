#!flask/bin/python
import os
import unittest
import logging
from eye_for_eye import app, db

class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_main_page(self):
        response = self.app.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        print('Main page tested')


if __name__ == '__main__':
    unittest.main()
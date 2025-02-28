# test_export_inspections.py
import unittest
import os
import sqlite3
import tempfile
from ExportInspections_gpap import (
    remove_file, get_contents, get_latitude_index, get_longitude_index,
    row_level, form_items, is_picture, generate_inspection_report
)

class TestExportInspections(unittest.TestCase):
    
    def setUp(self):
        # Create a test database
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db_path = os.path.join(self.temp_dir.name, "test.gpap")
        self.test_output = os.path.join(self.temp_dir.name, "test_output.html")
        
        # Create a simple test database
        self.db = sqlite3.connect(self.test_db_path)
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE notes (
                id INTEGER PRIMARY KEY,
                form TEXT,
                lat REAL,
                lon REAL,
                timestamp TEXT
            )
        ''')
        # Add test data
        cursor.execute('''
            INSERT INTO notes (form, lat, lon, timestamp)
            VALUES (?, ?, ?, ?)
        ''', ('{"type":"form","items":[{"type":"text","label":"Test"}]}', 34.5, -120.2, '2023-01-01'))
        self.db.commit()
    
    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()
    
    def test_get_latitude_index(self):
        # Test that the function correctly identifies the latitude column
        result = get_latitude_index(self.db)
        self.assertEqual(result, 2)  # Assuming lat is at index 2 in our test db
    
    def test_is_picture(self):
        # Test the is_picture function
        picture_control = {"type": "pictures"}
        text_control = {"type": "text"}
        self.assertTrue(is_picture(picture_control))
        self.assertFalse(is_picture(text_control))
    
    # Add more tests for each function
# test_ExportInspections_gpap.py
import unittest
import os
import json
import sqlite3
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from PIL import Image
import ExportInspections_gpap as exp

class TestExportInspections(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.gpap")
        self.image_folder = self.temp_dir
        self.output_file = "test_output.html"
        self.output_path = os.path.join(self.temp_dir, self.output_file)
        
        # Create a test database
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create tables that mimic the structure of the real database
        cursor.execute('''
            CREATE TABLE notes (
                _id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                created INTEGER,
                modified INTEGER,
                color INTEGER,
                section TEXT,
                forms TEXT,
                lat REAL,
                lon REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE images (
                _id INTEGER PRIMARY KEY,
                text TEXT
            )
        ''')
        
        # Insert test data
        cursor.execute('''
            INSERT INTO notes (_id, title, content, created, modified, color, section, forms, lat, lon)
            VALUES (1, 'Test Note', 'Test Content', 1633046400000, 1633046400000, 1, 'Test Section', 
            '{"forms":[{"formname":"Test Form","formitems":[{"key":"Test Key","value":"Test Value","type":"text"},
            {"key":"Test Picture","value":"1,2","type":"pictures"}]}]}', 
            -33.123456, 151.123456)
        ''')
        
        cursor.execute('''
            INSERT INTO images (_id, text)
            VALUES (1, 'test_image1.jpg'), (2, 'test_image2.jpg')
        ''')
        
        self.conn.commit()
        
        # Create test images
        self.test_image1 = os.path.join(self.temp_dir, "test_image1.jpg")
        self.test_image2 = os.path.join(self.temp_dir, "test_image2.jpg")
        
        # Create simple test images
        img1 = Image.new('RGB', (100, 200), color='red')
        img1.save(self.test_image1)
        
        img2 = Image.new('RGB', (200, 100), color='blue')
        img2.save(self.test_image2)
    
    def tearDown(self):
        # Close the database connection
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        
        # Remove the temporary directory and all its contents
        shutil.rmtree(self.temp_dir)
    
    def test_open_db(self):
        # Test with custom dbfile
        db = exp.open_db(self.db_path)
        self.assertIsNotNone(db)
        
        # Verify it's a valid SQLite connection
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        self.assertIn(('notes',), tables)
        self.assertIn(('images',), tables)
        
        db.close()
    
    def test_get_notes(self):
        db = exp.open_db(self.db_path)
        rows = exp.get_notes(db)
        
        # Verify we got our test note
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], 1)  # ID should be 1
        self.assertEqual(rows[0][6], 'Test Section')  # Section name
        
        db.close()
    
    def test_get_latitude_index(self):
        db = exp.open_db(self.db_path)
        lat_index = exp.get_latitude_index(db)
        
        # Verify the index matches our schema (should be 8 based on our CREATE TABLE)
        self.assertEqual(lat_index, 8)
        
        db.close()
    
    def test_get_longitude_index(self):
        db = exp.open_db(self.db_path)
        lon_index = exp.get_longitude_index(db)
        
        # Verify the index matches our schema (should be 9 based on our CREATE TABLE)
        self.assertEqual(lon_index, 9)
        
        db.close()
    
    def test_get_image_name(self):
        # Temporarily patch the DEFAULT_CONFIG to use our test database
        with patch('ExportInspections_gpap.DEFAULT_CONFIG', {'dbfile': self.db_path}):
            image_names = exp.get_image_name("1,2")
            
            # Verify we get the correct image names
            self.assertEqual(len(image_names), 2)
            self.assertEqual(image_names[0], 'test_image1.jpg')
            self.assertEqual(image_names[1], 'test_image2.jpg')
    
    def test_is_picture(self):
        # Test with a picture control
        picture_control = {"type": "pictures", "value": "1,2"}
        self.assertTrue(exp.is_picture(picture_control))
        
        # Test with a non-picture control
        text_control = {"type": "text", "value": "Test Value"}
        self.assertFalse(exp.is_picture(text_control))
    
    def test_control_data(self):
        # Test with a normal control
        control = {"key": "Test Key", "value": "Test Value"}
        result = exp.control_data(control)
        self.assertEqual(result, "Test Key: Test Value")
        
        # Test with a control missing a key
        control = {"value": "Test Value"}
        result = exp.control_data(control)
        self.assertEqual(result, ": Test Value")
    
    # def test_get_orientation(self):
    #     # Test with our test image
    #     height, width = exp.get_orientation(self.test_image1)
        
    #     # Our test image is 100x200
    #     self.assertEqual(height, 200)
    #     self.assertEqual(width, 100)
    
    def test_remove_file(self):
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test_remove.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Verify the file exists
        self.assertTrue(os.path.exists(test_file))
        
        # Remove the file
        exp.remove_file(test_file)
        
        # Verify the file no longer exists
        self.assertFalse(os.path.exists(test_file))
        
        # Test removing a non-existent file (should not raise an exception)
        exp.remove_file(test_file)  # File is already removed
    
    def test_write_file(self):
        test_content = "Test content"
        
        # Write to a test file
        exp.write_file(self.output_path, test_content)
        
        # Verify the file was written correctly
        with open(self.output_path, 'r') as f:
            content = f.read()
        
        self.assertEqual(content, test_content)
    
    # def test_form_items(self):
    #     # Test with valid form data
    #     form_data = '{"forms":[{"formname":"Test Form","formitems":[{"key":"Test Key","value":"Test Value","type":"text"}]}]}'
    #     result = exp.form_items(form_data, self.image_folder)
        
    #     # Verify the result contains our test data
    #     self.assertIn("<h3>Test Form</h3>", result)
    #     self.assertIn("<em>Test Key: </em><strong> Test Value</strong>", result)
        
    #     # Test with None form data
    #     result = exp.form_items(None, self.image_folder)
    #     self.assertEqual(result, " ")
    
    # @patch('os.startfile')
    # def test_generate_inspection_report(self, mock_startfile):
    #     # Test the main function with our test data
    #     exp.generate_inspection_report(
    #         dbfile=self.db_path,
    #         image_folder=self.image_folder,
    #         output_file_name=self.output_file
    #     )
        
    #     # Verify the output file was created
    #     self.assertTrue(os.path.exists(self.output_path))
        
    #     # Verify the content of the output file
    #     with open(self.output_path, 'r') as f:
    #         content = f.read()
        
    #     # Check for expected content
    #     self.assertIn("<h2>1 - Test Section</h2>", content)
    #     self.assertIn("-33.123456, 151.123456", content)
        
    #     # Verify os.startfile was called with the correct path
    #     mock_startfile.assert_called_once_with(self.output_path)
    
    @patch('ExportInspections_gpap.DEFAULT_CONFIG')
    @patch('os.startfile')
    def test_generate_inspection_report_with_defaults(self, mock_startfile, mock_config):
        # Set up the mock config
        mock_config.__getitem__.side_effect = lambda key: {
            'dbfile': self.db_path,
            'image_folder': self.image_folder,
            'output_file_name': self.output_file,
            'dummy_imagespec': 'dummy.jpg',
            'photo_size': 400
        }[key]
        
        # Test the main function with default parameters
        exp.generate_inspection_report()
        
        # Verify the output file was created
        self.assertTrue(os.path.exists(self.output_path))
        
        # Verify os.startfile was called with the correct path
        mock_startfile.assert_called_once_with(self.output_path)

if __name__ == '__main__':
    unittest.main()
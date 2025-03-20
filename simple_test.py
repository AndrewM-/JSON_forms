# simple_test.py
import unittest
import os
import ExportInspections_gpap as exp

class SimpleTestExportInspections(unittest.TestCase):
    def test_remove_file(self):
        # Create a test file
        test_file = "test_remove.txt"
        with open(test_file, 'w') as f:
            f.write("Test content")
        
        # Verify the file exists
        self.assertTrue(os.path.exists(test_file))
        
        # Remove the file
        exp.remove_file(test_file)
        
        # Verify the file no longer exists
        self.assertFalse(os.path.exists(test_file))

    def test_is_picture(self):
        # Test with a picture control
        picture_control = {"type": "pictures", "value": "1,2"}
        self.assertTrue(exp.is_picture(picture_control))
        
        # Test with a non-picture control
        text_control = {"type": "text", "value": "Test Value"}
        self.assertFalse(exp.is_picture(text_control))

if __name__ == '__main__':
    unittest.main()
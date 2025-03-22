# test_ExportInspections_gpap.py
import os
import json
import sqlite3
import tempfile
import shutil
import pytest
import sys
from unittest.mock import patch, MagicMock, mock_open
from PIL import Image

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import ExportInspections_gpap as exp


@pytest.fixture
def test_setup():
    # Create a temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.gpap")
    image_folder = temp_dir
    output_file = "test_output.html"
    output_path = os.path.join(temp_dir, output_file)
    
    # Create a test database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
    
    conn.commit()
    
    # Create test images
    test_image1 = os.path.join(temp_dir, "test_image1.jpg")
    test_image2 = os.path.join(temp_dir, "test_image2.jpg")
    
    # Create simple test images
    img1 = Image.new('RGB', (100, 200), color='red')
    img1.save(test_image1)
    
    img2 = Image.new('RGB', (200, 100), color='blue')
    img2.save(test_image2)
    
    # Return a dictionary with all the test data
    test_data = {
        'temp_dir': temp_dir,
        'db_path': db_path,
        'image_folder': image_folder,
        'output_file': output_file,
        'output_path': output_path,
        'conn': conn,
        'test_image1': test_image1,
        'test_image2': test_image2
    }
    
    yield test_data
    
    # Teardown - close the database connection
    if conn:
        conn.close()
    
    # Force garbage collection to release file handles
    import gc
    gc.collect()
    
    # Add a small delay to ensure file handles are released
    import time
    time.sleep(0.1)
    
    # Remove the temporary directory and all its contents
    try:
        shutil.rmtree(temp_dir)
    except PermissionError:
        print(f"Warning: Could not delete temporary directory {temp_dir}. It may be in use.")


def test_open_db(test_setup):
    # Test with custom dbfile
    db = exp.open_db(test_setup['db_path'])
    assert db is not None
    
    # Verify it's a valid SQLite connection
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    assert ('notes',) in tables
    assert ('images',) in tables
    
    db.close()


def test_get_notes(test_setup):
    db = exp.open_db(test_setup['db_path'])
    rows = exp.get_notes(db)
    
    # Verify we got our test note
    assert len(rows) == 1
    assert rows[0][0] == 1  # ID should be 1
    assert rows[0][6] == 'Test Section'  # Section name
    
    db.close()


def test_get_latitude_index(test_setup):
    db = exp.open_db(test_setup['db_path'])
    lat_index = exp.get_latitude_index(db)
    
    # Verify the index matches our schema (should be 8 based on our CREATE TABLE)
    assert lat_index == 8
    
    db.close()


def test_get_longitude_index(test_setup):
    db = exp.open_db(test_setup['db_path'])
    lon_index = exp.get_longitude_index(db)
    
    # Verify the index matches our schema (should be 9 based on our CREATE TABLE)
    assert lon_index == 9
    
    db.close()


def test_get_image_name(test_setup):
    # Temporarily patch the DEFAULT_CONFIG to use our test database
    with patch('ExportInspections_gpap.DEFAULT_CONFIG', {'dbfile': test_setup['db_path']}):
        image_names = exp.get_image_name("1,2")
        
        # Verify we get the correct image names
        assert len(image_names) == 2
        assert image_names[0] == 'test_image1.jpg'
        assert image_names[1] == 'test_image2.jpg'


def test_is_picture():
    # Test with a picture control
    picture_control = {"type": "pictures", "value": "1,2"}
    assert exp.is_picture(picture_control) is True
    
    # Test with a non-picture control
    text_control = {"type": "text", "value": "Test Value"}
    assert exp.is_picture(text_control) is False


def test_control_data():
    # Test with a normal control
    control = {"key": "Test Key", "value": "Test Value"}
    result = exp.control_data(control)
    assert result == "Test Key: Test Value"
    
    # Test with a control missing a key
    control = {"value": "Test Value"}
    result = exp.control_data(control)
    assert result == ": Test Value"


def test_get_orientation(test_setup):
    # Test with our test image
    height, width = exp.get_orientation(test_setup['test_image1'])
    
    # Our test image is 100x200
    assert height == 200
    assert width == 100


def test_remove_file(test_setup):
    # Create a test file
    test_file = os.path.join(test_setup['temp_dir'], "test_remove.txt")
    with open(test_file, 'w') as f:
        f.write("Test content")
    
    # Verify the file exists
    assert os.path.exists(test_file)
    
    # Remove the file
    exp.remove_file(test_file)
    
    # Verify the file no longer exists
    assert not os.path.exists(test_file)
    
    # Test removing a non-existent file (should not raise an exception)
    exp.remove_file(test_file)  # File is already removed


def test_write_file(test_setup):
    test_content = "Test content"
    
    # Write to a test file
    exp.write_file(test_setup['output_path'], test_content)
    
    # Verify the file was written correctly
    with open(test_setup['output_path'], 'r') as f:
        content = f.read()
    
    assert content == test_content


def test_form_items(test_setup):
    # Test with valid form data
    form_data = '{"forms":[{"formname":"Test Form","formitems":[{"key":"Test Key","value":"Test Value","type":"text"}]}]}'
    result = exp.form_items(form_data, test_setup['image_folder'])
    
    # Verify the result contains our test data
    assert "<h3>Test Form</h3>" in result
    assert "<em>Test Key: </em><strong> Test Value</strong>" in result
    
    # Test with None form data
    result = exp.form_items(None, test_setup['image_folder'])
    assert result == " "


@patch('os.startfile')
def test_generate_inspection_report(mock_startfile, test_setup):
    # Test the main function with our test data
    exp.generate_inspection_report(
        dbfile=test_setup['db_path'],
        image_folder=test_setup['image_folder'],
        output_file_name=test_setup['output_file']
    )
    
    # Verify the output file was created
    assert os.path.exists(test_setup['output_path'])
    
    # Verify the content of the output file
    with open(test_setup['output_path'], 'r') as f:
        content = f.read()
    
    # Check for expected content
    assert "<h2>1 - Test Section</h2>" in content
    # Use a more flexible check for the coordinates
    assert "-33.12" in content and "151.12" in content, "Coordinates not found in expected format"
    
    # Verify os.startfile was called with the correct path
    mock_startfile.assert_called_once_with(test_setup['output_path'])


@patch('ExportInspections_gpap.DEFAULT_CONFIG')
@patch('os.startfile')
def test_generate_inspection_report_with_defaults(mock_startfile, mock_config, test_setup):
    # Set up the mock config
    mock_config.__getitem__.side_effect = lambda key: {
        'dbfile': test_setup['db_path'],
        'image_folder': test_setup['image_folder'],
        'output_file_name': test_setup['output_file'],
        'dummy_imagespec': 'dummy.jpg',
        'photo_size': 400
    }[key]
    
    # Test the main function with default parameters
    exp.generate_inspection_report()
    
    # Verify the output file was created
    assert os.path.exists(test_setup['output_path'])
    
    # Verify os.startfile was called with the correct path
    mock_startfile.assert_called_once_with(test_setup['output_path'])
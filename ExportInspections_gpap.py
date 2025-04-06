# ACM
"""
ExportInspections_gpap.py
========================

This script exports inspection reports from a GPAP/SQLite database to a HTML file.
GPAP files are the native database files for the Smash digital mapper software.
"""
import os
import json
import sqlite3
import datetime
from typing import List, Dict, Any, Tuple, Optional, Union
from PIL import Image, ExifTags
from config import DEFAULT_CONFIG

# Use the config
def generate_inspection_report(dbfile: Optional[str] = None, 
                              image_folder: Optional[str] = None, 
                              output_file_name: Optional[str] = None, 
                              dummy_imagespec: str = "dummy.jpg", 
                              photo_size: int = 400,
                              auto_open: bool = True) -> None:
    # If parameters are not provided, use the config
    if dbfile is None or image_folder is None or output_file_name is None:
        config = DEFAULT_CONFIG
        dbfile = config["dbfile"]
        image_folder = config["image_folder"]
        output_file_name = config["output_file_name"]
        dummy_imagespec = config["dummy_imagespec"]
        photo_size = config["photo_size"]
    
    db = open_db(dbfile)
    all_rows = get_notes(db)
    output_filespec = os.path.join(image_folder, output_file_name)
    remove_file(output_filespec)
    web_text = get_contents(all_rows, db, image_folder, photo_size)
    write_file(output_filespec=output_filespec, t=web_text)
    db.close()
    print("done")
    if auto_open:
        try: # should work on Windows
            os.startfile(output_filespec)
        except OSError:
            print('Could not open URL')

def remove_file(f: str) -> None:
    try:
        os.remove(f)
    except:
        pass 
        
def get_contents(rows: List[Tuple], db: sqlite3.Connection, 
                image_folder: Optional[str] = None, 
                photo_size: Optional[int] = None) -> str:
    if image_folder is None:
        image_folder = DEFAULT_CONFIG["image_folder"]
    if photo_size is None:
        photo_size = DEFAULT_CONFIG["photo_size"]
        
    s = " "
    longitude_index = get_longitude_index(db)
    latitude_index = get_latitude_index(db)
    for row in rows:
         s += row_level(row, longitude_index, latitude_index, image_folder, photo_size, custom_db=db)

    return s

def get_latitude_index(db: sqlite3.Connection) -> Optional[int]:
    cursor = db.cursor()
    data = cursor.execute("SELECT * FROM notes")
    i = -1
    for columns in data.description:
        i += 1
        if columns[0].upper() == "LAT":
            return i
    return None

def get_longitude_index(db: sqlite3.Connection) -> Optional[int]:
    cursor = db.cursor()
    data = cursor.execute("SELECT * FROM notes")
    i = -1
    for columns in data.description:
        i += 1
        if columns[0].upper() == "LON":
            return i
    return None

def row_level(row_data: Tuple, 
             longitude_index: Optional[int], 
             latitude_index: Optional[int], 
             image_folder: str, 
             photo_size: int,
             custom_db: Optional[sqlite3.Connection] = None) -> str:
    try:
        row_level_text = "<!DOCTYPE html>\n"
        
        # Extract data safely with error handling
        try:
            id = str(row_data[0])
        except (IndexError, TypeError):
            id = "Unknown"
            
        try:
            forms = row_data[7]
        except (IndexError, TypeError):
            forms = None
            
        try:
            section_name = str(row_data[6]) if row_data[6] is not None else "Unknown"
        except (IndexError, TypeError):
            section_name = "Unknown"
            
        # Handle timestamp safely
        try:
            timestamp = row_data[4]
            date = datetime.datetime.fromtimestamp(timestamp / 1e3)
            timestamp_string = str(date.strftime('%Y-%m-%d %H:%M:%S'))
        except (IndexError, TypeError, ValueError, OverflowError):
            timestamp_string = "Unknown Date"

        # Handle coordinates safely
        longitude = "Unknown"
        latitude = "Unknown"
        
        if longitude_index is not None:
            try:
                longitude = str(round(row_data[longitude_index], 6))
            except (IndexError, TypeError, ValueError):
                pass

        if latitude_index is not None:
            try:
                latitude = str(round(row_data[latitude_index], 6))
            except (IndexError, TypeError, ValueError):
                pass

        # Build HTML output
        row_level_text += f"<h2>{id} - {section_name}</h2>\n"  
        row_level_text += f"<p>{timestamp_string} &nbsp({longitude}, {latitude})</p>\n"
        
        # Process form items with error handling
        try:
            row_level_text += form_items(forms, image_folder, photo_size, custom_db=custom_db)
        except Exception as e:
            print(f"Error processing form items: {str(e)}")
            row_level_text += "<p>Error processing form data</p>\n"
            
        return row_level_text
        
    except Exception as e:
        print(f"Error in row_level: {str(e)}")
        return f"<h2>Error processing row data</h2>\n<p>{str(e)}</p>\n"  

def form_items(form_data: Optional[str], 
              image_folder: Optional[str] = None, 
              photo_size: Optional[int] = None,
              custom_db: Optional[sqlite3.Connection] = None) -> str:
    if image_folder is None:
        image_folder = DEFAULT_CONFIG["image_folder"]
    if photo_size is None:
        photo_size = DEFAULT_CONFIG["photo_size"]
        
    form_name_level = ""
    if form_data is None:
        form_name_level = " "
    else:
        form_json = json.loads(form_data)
        form_name_level = top_dictionary(form_json, image_folder, photo_size, custom_db=custom_db)

    return form_name_level

def top_dictionary(dict_items: Dict[str, Any], 
                  image_folder: Optional[str] = None, 
                  photo_size: Optional[int] = None,
                  custom_db: Optional[sqlite3.Connection] = None) -> str:
    if image_folder is None:
        image_folder = DEFAULT_CONFIG["image_folder"]
    if photo_size is None:
        photo_size = DEFAULT_CONFIG["photo_size"]
        
    form_name_level = ""
    page_name = " "
    page_text = " "
    json_items = dict_items["forms"]
    for item in json_items:
        page_text += lower_dict(item, image_folder, photo_size, custom_db=custom_db)
    
    form_name_level = page_text + "</ul>\n"
    return form_name_level

def lower_dict(form_dict: Dict[str, Any], 
              image_folder: Optional[str] = None, 
              photo_size: Optional[int] = None,
              custom_db: Optional[sqlite3.Connection] = None) -> str:
    if image_folder is None:
        image_folder = DEFAULT_CONFIG["image_folder"]
    if photo_size is None:
        photo_size = DEFAULT_CONFIG["photo_size"]
        
    start_list = ""
    lower_dict_text = ""
    form_values = " "
    form_stuff = []
    form_name = form_dict["formname"]
    form_stuff = form_dict["formitems"]
    form_values = control_list(form_name, form_stuff, image_folder, photo_size, custom_db=custom_db).lstrip()
    if not form_values is None:
        lower_dict_text = form_values
    
    return lower_dict_text 
    
def control_list(form_name: str, 
                form_items: List[Dict[str, Any]], 
                image_folder: Optional[str] = None, 
                photo_size: Optional[int] = None,
                custom_db: Optional[sqlite3.Connection] = None) -> str:
    if image_folder is None:
        image_folder = DEFAULT_CONFIG["image_folder"]
    if photo_size is None:
        photo_size = DEFAULT_CONFIG["photo_size"]
        
    # Always include the form name in an h3 header
    control_top = "<h3>" + form_name + "</h3>\n"
    control_text = ""
    control_info = " "
    control: Dict[str, Any] = {}
    for control in form_items:
        if is_picture(control):
            try:
                photospec = get_image_name(control["value"], custom_db=custom_db)
                control_text = ""
                for images in photospec: 
                    image_spec = os.path.join(image_folder, images)
                    try:
                        height, width = get_orientation(image_spec)
                        scaled_height: int = 0
                        scaled_width: int = 0
                        if height > width:
                            scale_factor = height / photo_size
                            scaled_height = str(int(height / scale_factor))
                            scaled_width = str(int(width / scale_factor))
                        else:
                            scale_factor = width / photo_size
                            scaled_height = str(int(height / scale_factor))
                            scaled_width = str(int(width / scale_factor))

                        control_text += "<p><a href=\"" + "file:///" + image_spec + "\"><img width=\"" + scaled_width + "\" height=\"" + scaled_height + "\" src=\"" + "file:///" + image_spec + "\"/></a></p>\n"
                    except Exception as e:
                        # If there's an error processing the image, just add a text link instead
                        control_text += "<p><a href=\"" + "file:///" + image_spec + "\">" + images + "</a></p>\n"
            except Exception as e:
                # If there's an error getting the image name, just continue
                control_text += "<p>Error processing image: " + str(control["value"]) + "</p>\n"
        else:
            try:
                control_info = str(control_data(control).strip())
                if control_info[:1] == ":": 
                    control_info = ""
                else:
                    if control_info[-1] == ":" or control_info[-1] == "-":
                        pass
                    else:
                        # Check if there's a colon in the string before trying to find its index
                        if ":" in control_info:
                            split_position = control_info.index(":")
                            control_value = "\t<li><em>" + control_info[:split_position + 2] + "</em><strong> " + control_info[split_position + 2:] + "</strong></li>\n"
                            control_text += control_value
                        else:
                            # Handle case where there's no colon
                            control_value = "\t<li><em>" + control_info + "</em></li>\n"
                            control_text += control_value
            except Exception as e:
                # Log the exception for debugging
                print(f"Error processing control data: {str(e)}")
                pass
    
    return control_top + "<ul>\n" + control_text + "</ul>\n"

def is_picture(control: Dict[str, Any]) -> bool:
    if control["type"] == "pictures":
        return True
    else:
        return False

def maKe_picture_frames() -> None:
    pass

def control_data(control: Dict[str, Any]) -> str:
    try:
        control_name = control["key"]
    except:
        control_name = ""

    control_value = control["value"]
    return control_name + ": " + str(control_value)

def write_file(output_filespec: str, t: str) -> None:
    f = open(output_filespec, "w")
    f.write(t)
    f.close()

def open_db(custom_dbfile: Optional[str] = None) -> sqlite3.Connection:
    if custom_dbfile is None:
        # Use the default config if none is provided
        custom_dbfile = DEFAULT_CONFIG["dbfile"]
    
    db = sqlite3.connect(custom_dbfile) 
    return db

def get_notes(db: sqlite3.Connection) -> List[Tuple]:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notes")
    rows = cursor.fetchall()
    cursor.close()
    return rows

def get_image_name(image_ids: str, custom_db: Optional[sqlite3.Connection] = None) -> List[str]:
    try:
        # Handle empty or None input
        if not image_ids:
            return []
            
        image_ids = image_ids.replace(";", ",")
        
        # Use the provided database connection or create a new one
        close_db = False
        if custom_db is None:
            db = sqlite3.connect(DEFAULT_CONFIG["dbfile"])
            close_db = True
        else:
            db = custom_db
        
        # Validate image_ids format to prevent SQL injection
        id_list = []
        for id_str in image_ids.split(','):
            try:
                id_int = int(id_str.strip())
                id_list.append(str(id_int))
            except ValueError:
                continue
                
        if not id_list:
            return [DEFAULT_CONFIG["dummy_imagespec"]]
            
        # Use parameterized query for safety
        cursor = db.cursor()
        placeholders = ','.join(['?'] * len(id_list))
        sql = f"SELECT _id, text FROM images WHERE _id IN({placeholders})"
        cursor.execute(sql, id_list)
        rows = cursor.fetchall()
        cursor.close()
        
        # Only close the connection if we created it
        if close_db:
            db.close()
        
        image_names: List[str] = []
        for row in rows:
            image_names.append(row[1])
        
        return image_names
    except Exception as e:
        # If there's an error with the database connection or query,
        # return a list with a default image
        print(f"Error in get_image_name: {str(e)}")
        return [DEFAULT_CONFIG["dummy_imagespec"]]

def rotate_image(image_name: str) -> None:
    pass

def get_orientation(image_spec: str) -> Tuple[int, int]:
    try:
        # Check if file exists before attempting to open it
        if not os.path.exists(image_spec):
            print(f"Image file not found: {image_spec}")
            return 200, 100  # Default height, width
            
        # Use a context manager to ensure the image is properly closed
        with Image.open(image_spec) as image:
            width, height = image.size
            return height, width
    except Exception as e:
        print(f"Error getting image orientation: {str(e)}")
        # Return default values if there's an error
        return 200, 100  # Default height, width

if __name__ == '__main__':
     generate_inspection_report(auto_open=True)

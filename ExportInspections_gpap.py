import os
import json
import sqlite3
import datetime
from PIL import Image, ExifTags

# external variables
dbfile = "E:\\Wedgetail\\Eugowra\Photos\\2024-10-03\\Eugowra-plots.gpap"
image_folder = "E:/Wedgetail/Eugowra/Photos/2024-10-03"
output_file_name = "Eugowra_Plots.html"
dummy_imagespec = "dummy.jpg"
photo_size = 400

def remove_file(f):
    try:
        os.remove(f)
    except:
        pass 
        
def get_contents(rows):
    s = " "
    longitude_index = get_longitude_index(db)
    latitude_index = get_latitude_index(db)
    for row in rows:
         s += row_level(row, longitude_index, latitude_index)

    return s

def get_latitude_index(db):
    cursor = db.cursor()
    data = cursor.execute("SELECT * FROM notes")
    i = -1
    for columns in data.description:
        i += 1
        if columns[0].upper() == "LAT":
            return i

def get_longitude_index(db):
    cursor = db.cursor()
    data = cursor.execute("SELECT * FROM notes")
    i = -1
    for columns in data.description:
        i += 1
        if columns[0].upper() == "LON":
            return i

def row_level(row_data, longitude_index, latitude_index):
    row_level_text = "<!DOCTYPE html>\n"
    forms = {}
    id = " "
    section_name = " "
    section_description = " " 
    timestamp_string = " "   
    geom = " "  
    longitude = " "
    latitude = " "
    id = str(row_data[0])    
    forms = row_data[7]
    section_name = row_data[6]
    section_description = " "
    timestamp = 1
    timestamp = row_data[4]
    date = datetime.datetime.fromtimestamp(timestamp / 1e3)
    timestamp_string = str(date.strftime('%Y-%m-%d %H:%M:%S'))

    if longitude_index is not None:
        longitude = str(round(row_data[longitude_index],6))

    if latitude_index is not None:
        latitude = str(round(row_data[latitude_index],6))

    row_level_text += "<h2>" + id + " - " + section_name + "</h2>\n"  
    row_level_text += "<p>" + timestamp_string + " &nbsp(" + longitude + ", " + latitude + ")</p>\n"
    row_level_text += form_items(forms)  
    return row_level_text  

def form_items(form_data):
    form_name_level = ""
    if form_data is None:
        form_name_level = " "
    else:
        form_json = json.loads(form_data)
        form_name_level = top_dictionary(form_json)

    return form_name_level

def top_dictionary(dict_items):
    form_name_level = ""
    page_name = " "
    page_text = " "
    json_items = dict_items["forms"]
    for item in json_items:
        page_text += lower_dict(item)
    
    form_name_level = page_text + "</ul>\n"
    return form_name_level

def lower_dict(form_dict):
    start_list = ""
    lower_dict_text = ""
    form_values = " "
    form_stuff = []
    form_name = form_dict["formname"]
    form_stuff = form_dict["formitems"]
    form_values = control_list(form_name, form_stuff).lstrip()
    if not form_values is None:
        lower_dict_text = form_values
    
    return lower_dict_text 
    
def control_list(form_name, form_items):
    control_top = " "
    control_text = ""
    control_info = " "
    control = {}
    for control in form_items:
        if is_picture(control):
            photospec = get_image_name(control["value"])
            control_info = ""
            for images in photospec: 
                image_spec = image_folder + "/" + images
                height, width = get_orientation(image_spec)
                scaled_height = 0
                scaled_width = 0
                if height > width:
                    scale_factor = height / photo_size
                    scaled_height = str(int(height / scale_factor))
                    scaled_width = str(int(width / scale_factor))
                else:
                    scale_factor = width / photo_size
                    scaled_height = str(int(height / scale_factor))
                    scaled_width = str(int(width / scale_factor))

                control_info += "<p><img width=\"" + scaled_width + "\" height=\"" + scaled_height + "\" src=\"" + "file:///" + image_spec + "\"/></p>\n"
        else:
            control_info = str(control_data(control).strip())
            if control_info[:1] == ":": 
                control_top = "<h3>" + form_name + control_info + "</h3>\n"
                control_info = ""
            else:
                if control_info[-1] == ":" or control_info[-1] == "-":
                    control_info = "\t<li style=\"color:lightgray\">" + control_info + "</li>\n"
                else:
                    control_info = "\t<li>" + control_info[-1] + "</li>\n"
        
        control_text += control_info
    
    return control_top + "<ul>\n" + control_text + "</ul>\n"

def is_picture(control):
    if control["type"] == "pictures":
        return True
    else:
        return False

def maKe_picture_frames():
    pass

def control_data(control):
    try:
        control_name = control["key"]
    except:
        control_name = ""

    control_value = control["value"]
    return control_name + ": " + str(control_value)

def write_file(output_filespec, t):
    f = open(output_filespec, "w")
    f.write(t)
    f.close()

def open_db():
    db = sqlite3.connect(dbfile) 
    return db

def get_notes(db):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notes")
    rows = cursor.fetchall()
    cursor.close()
    return rows

def get_image_name(image_ids):
    image_ids = image_ids.replace(";", ",")
    db = sqlite3.connect(dbfile) 
    cursor = db.cursor()
    sql = "SELECT _id, text FROM images WHERE _id IN(" + str(image_ids) + ")"
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    file_names = []
    for row in rows:
        file_names.append(row[1])
    
    return file_names

def rotate_image(image_name):
    pass

def get_orientation(image_spec):
    try:
        image=Image.open(image_spec)
        height, width = image.size

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        
        exif = image._getexif()
        if exif == None:
            return height, width

        if exif[orientation] == 3:
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image=image.rotate(90, expand=True)

        image.save(image_spec)
        height, width = image.size
        image.close()
    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

    return height, width

if __name__ == '__main__':
    db = open_db()
    all_rows = get_notes(db)
    output_filespec = image_folder + "\\" +output_file_name
    remove_file(output_filespec)
    web_text = get_contents(all_rows)
    write_file(output_filespec=output_filespec, t=web_text)
    print("done")
    try: # should work on Windows
        os.startfile(output_filespec)
    except OSError:
        print('Could not open URL')

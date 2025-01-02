# ACM
import os
import json
import sqlite3
import struct

# from vegetation_clearing import a
# from qgis.utils import iface

dbfile = "E:/Wedgetail/Eugowra/FieldObs/Plots_week1/smash_export_20241007_212444.gpkg"
output_filespec = "C:/Temp/demofile6.html"

def remove_file(f):
    try:
        os.remove(f)
    except:
        pass 
        
def get_contents(rows):
    s = " "
    for row in rows:
         s += row_level(row)

    return s

def row_level(row_data):
    row_level_text = "<!DOCTYPE html>\n"
    forms = {}
    id = " "
    section_name = " "
    section_description = " "    
    timestamp = " " 
    geom = " "  
    longitude = " "
    latitude = " "
    id = str(row_data[0])    
    forms = row_data[5]
    section_name = row_data[4]
    section_description = row_data[1]
    timestamp = row_data[2]
    # longitude = str(round(row_data[17],6))
    # latitude = str(round(row_data[18],6))
    geom = row_data[-1]  # Assuming geometry is the last column
    # Basic parsing for Point geometry
    if geom[1:5] == b'\x00\x02\x00\x00\x00':  # Point geometry type
        # Extract x,y coordinates (assuming big endian)
        longitude, latitude = struct.unpack('>dd', geom[5:21])
        print(f"Longitude: {longitude}, Latitude: {latitude}")
    row_level_text += "<h2>" + id + " - " + section_name + "</h2>\n"  
    row_level_text += "<p>" + timestamp + " &nbsp(" + longitude + ", " + latitude + ")</p>\n"
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
        control_info = str(control_data(control).strip())
        if control_info[:1] == ":": 
            control_top = "<h3>" + form_name + control_info + "</h3>\n"
        else:
            if control_info[-1] == ":" or control_info[-1] == "-":
                control_info = "\t<span style=\"color:lightgray\"><li>" + control_info + "</li></span>\n"
            else:
                control_info = "\t<li>" + control_info + "</li>\n"
            control_text += control_info
    
    return control_top + "<ul>\n" + control_text + "</ul>\n"

def control_data(control):
    try:
        control_name = control["key"]
    except:
        control_name = ""

    control_value = control["value"]
    return control_name + ": " + control_value

def write_file(t):
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

db = open_db()
all_rows = get_notes(db)
remove_file(output_filespec)
web_text = get_contents(all_rows)
write_file(web_text)
print("done")

import sqlite3
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_CONFIG

def save_imageblobs(dbfile):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM imagedata")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    
    for row in rows:
        image_id = row[0]
        image_blob = row[1]
        image_name = row[2]

        output_file_path = DEFAULT_CONFIG["image_folder"] + "\\" + str(image_id) + ".jpg"

        if not os.path.exists(output_file_path):
            with open(output_file_path, "wb") as f:
                f.write(image_blob)
                print(f"Saved {output_file_path}")
        else:
            print(f"{output_file_path} already exists")   

if __name__ == "__main__":
    save_imageblobs(DEFAULT_CONFIG["dbfile"])           
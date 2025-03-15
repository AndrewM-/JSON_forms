import sqlite3
import os
import sys


# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DEFAULT_CONFIG

def get_image_ids(dbfile):
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
    cursor.execute("SELECT _id, text, imagedata_id FROM images")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows

def save_specific_images(dbfile, image_ids):
    """
    Save specific images by their IDs without loading all images.
    
    Args:
        dbfile: Path to the database file
        image_ids: List of image IDs to save
    """
    if not image_ids:
        print("No image IDs provided")
        return
        
    db = sqlite3.connect(dbfile)
    cursor = db.cursor()
                    
    image_folder = DEFAULT_CONFIG["image_folder"].replace('\\', '/').replace('//', '/')
    
    try:
        # Process each image ID individually to minimize memory usage
        for img_record in image_ids:
            # Each img_record is a tuple with (_id, text, imagedata_id)
            img_name = img_record[1]
            imagedata_id = img_record[2]
            
            # Query just one image at a time
            cursor.execute("SELECT _id, data FROM imagedata WHERE _id = ?", (imagedata_id,))
            row = cursor.fetchone()
            
            if row:
                # Create a filename using the image name from the images table
                output_file_path = os.path.join(image_folder, f"{img_name}")
                
                if not os.path.exists(output_file_path):
                    with open(output_file_path, "wb") as f:
                        f.write(row[1])  # row[1] contains the image blob data
                    print(f"Saved {output_file_path}")# Normalize path separators in config paths
                else:
                    print(f"{output_file_path} already exists")
            else:
                print(f"Image data for {img_name} (ID: {imagedata_id}) not found")

    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    image_ids = get_image_ids(DEFAULT_CONFIG["dbfile"])
    save_specific_images(DEFAULT_CONFIG["dbfile"], image_ids)         
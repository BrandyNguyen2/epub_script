import zipfile
import os
from bs4 import BeautifulSoup
from PIL import Image

# Paths
uploaded_file_path = 'PragmaticProgrammer.epub'
extracted_path = 'PragmaticProgrammer_extracted' 
fixed_epub_path = 'PragmaticProgrammer_fixed.epub' # returning new file

# Step 1: Extract the EPUB contents
def extract_epub(epub_path, output_path):
    with zipfile.ZipFile(epub_path, 'r') as epub_zip: # read epub file
        epub_zip.extractall(output_path)

# Step 2: Fix text rendering in HTML files
def fix_html_text_rendering(html_path):
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Remove <br> tags and merge paragraph lines
    for br in soup.find_all("br"):
        br.unwrap()
    # Removing unnecessary text
    for p in soup.find_all("p"):
        p.string = " ".join(p.stripped_strings)
    
    # Remove unwanted navigation elements
    for unwanted in soup.find_all(['a', 'img'], {'class': ['next', 'prev']}):
        unwanted.decompose()
    
    with open(html_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

# Step 3: Correct image orientation
def fix_image_orientation(image_path):
    try:
        with Image.open(image_path) as img:
            # Correct orientation based on EXIF data
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif = img._getexif()
                orientation_key = 274  # EXIF orientation tag
                if exif and orientation_key in exif:
                    orientation = exif[orientation_key]
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
            img.save(image_path)
    except Exception as e:
        print(f"Error fixing image {image_path}: {e}")

# Step 4: Repackage the EPUB
def repackage_epub(input_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as epub_zip:
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_full_path = os.path.join(root, file)
                arcname = os.path.relpath(file_full_path, input_path)
                epub_zip.write(file_full_path, arcname)

# Execute steps
extract_epub(uploaded_file_path, extracted_path)

# Fix each file
for root, dirs, files in os.walk(extracted_path):
    for file in files:
        file_path = os.path.join(root, file)
        if file.endswith('.html'):
            fix_html_text_rendering(file_path)
        elif file.endswith(('.jpg', '.jpeg', '.png')):
            fix_image_orientation(file_path)

# Repackage fixed EPUB
repackage_epub(extracted_path, fixed_epub_path)

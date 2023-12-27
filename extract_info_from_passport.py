import os
import string as st
from dateutil import parser
import matplotlib.image as mpimg
import cv2
from passporteye import read_mrz
import json
import easyocr
import sys
import base64
from PIL import Image
from io import BytesIO
import tempfile
#uvicorn main:app --reload
#windows:.\venv\Scripts\Activate
#Linux: source venv/bin/activate

from apiResponse import APIResponse
# lOAD OCR ENGINE (easyOCR)
reader=easyocr.Reader(lang_list=['en'], gpu=True)  # Enable gpu if available

# Will be used to convert country code to country name
with open('country_codes.json') as f:
    country_codes = json.load(f)

def parse_date(string, iob=True):
    date = parser.parse(string, yearfirst=True).date() 
    return date.strftime('%d/%m/%Y')

def clean(string):
    return ''.join(i for i in string if i.isalnum()).upper()

def get_country_name(country_code):
    country_name = ''
    for country in country_codes:
        if country['alpha-3'] == country_code:
            country_name = country['name']
            return country_name.upper()
    return country_code

def get_sex(code):
    if code in ['M', 'm', 'F', 'f']:
        sex = code.upper() 
    elif code == '0':
        sex = 'M'
    else:
        sex = 'F'
    return sex

def print_data(data):
    for key in data.keys():
        info = key.replace('_', ' ').capitalize()
        print(f'{info}\t:\t{data[key]}')
    return
  
def get_data(base64_string):
    try:
        user_info = {}    
        new_im_path = 'tmp.png'
        # Add padding if needed
        padding_needed = len(base64_string) % 4
        if padding_needed:
            base64_string += "=" * (4 - padding_needed)
        # Decode the base64 string
        image_data = base64.b64decode(base64_string)
        # Create a BytesIO object and read the image data
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)

        # Save the PIL.Image object to a temporary file
        temp_fd, temp_filename = tempfile.mkstemp(suffix=".png")
        os.close(temp_fd)
        image.save(temp_filename)
        # Create a BytesIO object and read the image data
        image_bytes = BytesIO(image_data)
        image = Image.open(image_bytes)
        # Crop image to Machine Readable Zone(MRZ)
        mrz = read_mrz(temp_filename, save_roi=True)

        if mrz:
            mpimg.imsave(new_im_path, mrz.aux['roi'], cmap='gray')
        
            img = cv2.imread(new_im_path)
            img = cv2.resize(img, (1110, 140))
            
            allowlist = st.ascii_letters+st.digits+'< '
            code = reader.readtext(img, paragraph=False, detail=0, allowlist=allowlist)
            a, b = code[0].upper(), code[1].upper()
            
            if len(a) < 44:
                a = a + '<'*(44 - len(a))
            if len(b) < 44:
                    b = b + '<'*(44 - len(b))
                    
            surname_names = a[5:44].split('<<', 1)
            if len(surname_names) < 2:
                surname_names += ['']
            surname, names = surname_names
            
            user_info['name'] = names.replace('<', ' ').strip().upper()
            user_info['surname'] = surname.replace('<', ' ').strip().upper()
            user_info['sex'] = get_sex(clean(b[20]))
            user_info['dateOfBirth'] = parse_date(b[13:19])
            user_info['nationality'] = get_country_name(clean(b[10:13]))
            user_info['passportType'] = clean(a[0:2])
            user_info['passportNumber']  = clean(b[0:9])
            user_info['issuingCountry'] = get_country_name(clean(a[2:5]))
            user_info['expirationDate'] = parse_date(b[21:27])
            user_info['personalNumber'] = clean(b[28:42])
            os.remove(new_im_path)
            apiResponse = APIResponse(code=200,message="Success", object=user_info)
            return apiResponse
        else:
            apiResponse = APIResponse(code=400,message="Failed to read passport,please take a clear picture!",object=None)
            return apiResponse
    except  ValueError as e:
            apiResponse = APIResponse(code=304,message=f"{e}",object=None)


    
    

import pytesseract
from PIL import Image
import io

def solvecaptcha(imagebytes):
    try:
        img = Image.open(io.BytesIO(imagebytes))
        img = img.convert('L')
        text = pytesseract.image_to_string(img, config='--psm 8')
        return text.strip()
    except:
        return None

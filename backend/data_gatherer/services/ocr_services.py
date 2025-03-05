import datetime
import re
import time
from PIL import Image, ImageEnhance, ImageFilter
from pytesseract import pytesseract
import numpy as np
import cv2

def read_text_from_img(img_path, top_percent, left_percent, width_percent, height_percent):
    path_to_tesseract = "tesseract"
    image_path = img_path

    img = Image.open(image_path)

    left = left_percent * 0.01 * img.width
    top = top_percent * 0.01 * img.height
    right = (width_percent * 0.01 * img.width) + left
    bottom = (height_percent * 0.01 * img.height) + top

    crop_img = img.crop((left, top, right, bottom))
    #crop_img.save("sus_imgage %s.png" % (str(datetime.datetime.now())))

    pytesseract.tesseract_cmd = path_to_tesseract

    crop_img = crop_img.convert('L')
    text = pytesseract.image_to_string(crop_img)

    if text == "":
        return "N.A."

    return text[:-1]





def special_username_text_from_img(img_path, top_percent, left_percent, width_percent, height_percent):
    path_to_tesseract = "tesseract"
    pytesseract.tesseract_cmd = path_to_tesseract

    image_path = img_path
    img = Image.open(image_path)

    left = left_percent * 0.01 * img.width
    top = top_percent * 0.01 * img.height
    right = (width_percent * 0.01 * img.width) + left
    bottom = (height_percent * 0.01 * img.height) + top

    # Crop the image
    image = img.crop((left, top, right, bottom))
    #image.save("image.png")

    # Open image
    img = image
    
    # Convert to RGB
    image_rgb = np.array(img.convert("RGB"))

    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2HSV)

    # Define blue range for Instagram's "Follow" button
    lower_blue = np.array([85, 40, 40])  
    upper_blue = np.array([135, 255, 255])

    # Create mask for blue text
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    # Invert mask to keep only non-blue areas
    mask_non_blue = cv2.bitwise_not(mask_blue)

    # Apply mask to remove blue text
    image_no_blue = cv2.bitwise_and(image_rgb, image_rgb, mask=mask_non_blue)

    # Convert back to PIL for further processing
    image_no_blue = Image.fromarray(image_no_blue)

    # Convert to grayscale
    gray = image_no_blue.convert("L")

    # Increase contrast
    enhancer = ImageEnhance.Contrast(gray)
    enhanced_image = enhancer.enhance(1)

    # Convert to OpenCV format
    cv_image = np.array(enhanced_image)

    # Adaptive thresholding to filter out faded text
    thresh = cv2.adaptiveThreshold(cv_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)

    # Further remove weak elements (like faded "Follow")
    #_, strong_text = cv2.threshold(cv_image, 180, 255, cv2.THRESH_BINARY)

    # Apply final mask
    #ocr_ready = cv2.bitwise_and(cv_image, cv_image)
    ocr_ready = cv_image

    # Convert back to PIL for OCR
    ocr_ready_pil = Image.fromarray(ocr_ready)
    #ocr_ready_pil.save("ocr_ready.png")  # Save for debugging

    # Perform OCR
    text = pytesseract.image_to_string(ocr_ready_pil).strip()

    # Extract only valid username characters (first valid word)
    match = re.search(r"^[a-zA-Z0-9_.]+", text)
    username = match.group(0) if match else text

    username = username.split("\n")[0].replace("Follow", "")

    print("Extracted Username:", username)
    return username 
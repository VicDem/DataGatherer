import cv2
import numpy as np
import os
from PIL import Image, ImageEnhance
from collections import Counter

def auto_crop_white_box(image_path):
    """ Automatically crops the largest white box in an image """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)  # Detect white areas

    # Find contours of the white box
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Crop and return
        return img[y:y+h, x:x+w]
    
    return None  # No white box found

def enhance_and_compress(image, output_path, quality=60):
    """ Enhances contrast for text readability and compresses the image """
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(pil_img)
    enhanced_img = enhancer.enhance(2)  # Adjust contrast factor if needed

    # Save with compression
    enhanced_img.save(output_path, "JPEG", quality=quality, optimize=True)

def find_most_common_width(cropped_images):
    """ Finds the most common width of the cropped images """
    widths = [img.shape[1] for img in cropped_images]
    if widths:
        # Find the most common width
        most_common_width, _ = Counter(widths).most_common(1)[0]
        return most_common_width
    return None

def process_images_in_folder(input_folder):
    """ Processes all images in the folder and saves results in <input_folder>_worked """
    output_folder = f"{input_folder}_worked"
    os.makedirs(output_folder, exist_ok=True)

    tot = len(os.listdir(input_folder))
    count = 0

    # Step 1: Crop white boxes and collect cropped images
    cropped_images = []
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):  # Process only images
            image_path = os.path.join(input_folder, filename)

            print(f"{count}/{tot} Processing {filename}...")

            # Crop the white box
            cropped_image = auto_crop_white_box(image_path)

            if cropped_image is not None:
                cropped_images.append(cropped_image)
            else:
                print(f"Skipping {filename} (no white box found)")

            count += 1

    # Step 2: Find the most common width among cropped images
    common_width = find_most_common_width(cropped_images)
    if common_width is None:
        print("No valid cropped images found.")
        return

    print(f"Most common width after cropping: {common_width}")

    # Step 3: Second crop to the most common width
    count = 0
    for filename, cropped_image in zip(os.listdir(input_folder), cropped_images):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):  # Process only images
            output_path = os.path.join(output_folder, filename)

            # Resize to the most common width, keeping the right part
            height, width = cropped_image.shape[:2]
            if width > common_width:
                cropped_image = cropped_image[:, width-common_width:]  # Keep the right part

            # Enhance and compress the image
            enhance_and_compress(cropped_image, output_path)

            count += 1

    print(f"All images processed. Results saved in: {output_folder}")

# Example usage
while True:
    input_folder = input("input: ")
    process_images_in_folder(input_folder)

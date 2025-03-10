import shutil
import cv2
import numpy as np
import os
from PIL import Image, ImageEnhance
from collections import Counter
from skimage.metrics import structural_similarity as ssim
import os
from tqdm import tqdm

import cv2
import os
from tqdm import tqdm  # Import tqdm for progress bar

def extract_frames(video_path, output_folder, frame_skip=3, diff_threshold=30):
    """
    Extracts distinct frames from a video while keeping timestamps.
    
    - `frame_skip`: Number of frames to skip for efficiency.
    - `diff_threshold`: Sensitivity for detecting changes.
    """
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total number of frames in the video
    prev_frame = None
    count = 0
    frame_number = 0

    # Use tqdm to show a progress bar based on total frames
    with tqdm(total=total_frames, desc="Extracting frames", unit="frame") as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Calculate timestamp of the frame
            timestamp = frame_number / fps  # Time in seconds

            if frame_number % frame_skip == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, gray)
                    if np.mean(diff) < diff_threshold:
                        frame_number += 1
                        continue  # Skip similar frames

                prev_frame = gray  # Update previous frame

                # Save frame with timestamp in filename
                frame_path = os.path.join(output_folder, f"frame_{count:05d}_{timestamp:.2f}s.jpg")
                cv2.imwrite(frame_path, frame)
                count += 1

            frame_number += 1
            pbar.update(1)  # Update progress bar

    cap.release()
    print(f"Extracted {count} distinct frames from {video_path} into {output_folder}")


def auto_crop_white_box(image_path):
    """ Automatically crops the largest white box in an image """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)  # Detect white areas

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return img[y:y+h, x:x+w]
    
    return None  # No white box found

def enhance_and_compress(image, output_path, quality=60):
    """ Enhances contrast for text readability and compresses the image """
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    enhancer = ImageEnhance.Contrast(pil_img)
    enhanced_img = enhancer.enhance(2)  # Adjust contrast factor if needed
    enhanced_img.save(output_path, "JPEG", quality=quality, optimize=True)

def find_most_common_width(cropped_images):
    """ Finds the most common width of the cropped images """
    widths = [img.shape[1] for img in cropped_images]
    return Counter(widths).most_common(1)[0][0] if widths else None

def process_images_in_folder(input_folder):
    """ Processes all images in the folder and saves results in the same folder """
    cropped_images = []
    filenames = []
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(input_folder, filename)
            cropped_image = auto_crop_white_box(image_path)

            if cropped_image is not None:
                cropped_images.append(cropped_image)
                filenames.append(filename)

    common_width = find_most_common_width(cropped_images)
    if common_width is None:
        print("No valid cropped images found.")
        return

    print(f"Most common width after cropping: {common_width}")

    # Step 1: Crop and enhance images, save them in the same folder
    for filename, cropped_image in zip(filenames, cropped_images):
        output_path = os.path.join(input_folder, filename)
        height, width = cropped_image.shape[:2]
        if width > common_width:
            cropped_image = cropped_image[:, width-common_width:]  # Keep right part

        enhance_and_compress(cropped_image, output_path)

    print(f"All images processed and saved in: {input_folder}")
    
    # Step 2: SSIM comparison and removal of duplicates
    move_duplicates(input_folder)

import os
from tqdm import tqdm
import cv2
from skimage.metrics import structural_similarity as ssim

def remove_duplicates(input_folder, similarity_threshold=0.95):
    """ Removes images that are similar to the previous 4 images in lexicographical order """
    images = {}
    
    # Load all processed images
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(input_folder, filename)
            img = cv2.imread(image_path)
            images[filename] = img

    # Sort filenames lexicographically (aaa to zzz)
    sorted_filenames = sorted(images.keys())

    to_remove = set()

    # Use tqdm for progress bar while comparing images
    with tqdm(total=len(sorted_filenames), desc="Comparing images", unit="image") as pbar:
        for i in range(1, len(sorted_filenames)):
            current_filename = sorted_filenames[i]
            current_img = images[current_filename]

            # Compare the current image to the previous 4 images
            for j in range(max(0, i - 4), i):
                previous_filename = sorted_filenames[j]
                previous_img = images[previous_filename]

                # Get the dimensions of both images
                height1, width1 = current_img.shape[:2]
                height2, width2 = previous_img.shape[:2]
                
                # Calculate the cropping region (smallest width and height)
                new_width = min(width1, width2)
                new_height = min(height1, height2)
                
                # Crop both images to the new dimensions
                current_img_cropped = current_img[:new_height, :new_width]
                previous_img_cropped = previous_img[:new_height, :new_width]
                
                # Compute SSIM similarity on the cropped images
                gray1 = cv2.cvtColor(current_img_cropped, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(previous_img_cropped, cv2.COLOR_BGR2GRAY)
                similarity = ssim(gray1, gray2)
                
                if similarity > similarity_threshold:
                    #print(f"Duplicate detected: {current_filename} and {previous_filename} with SSIM: {similarity:.2f}")
                    to_remove.add(current_filename)  # Mark current image for removal
                    break  # No need to compare with further previous images if a match is found

            pbar.update(1)  # Update progress bar

    # Remove duplicates
    for filename in to_remove:
        image_path = os.path.join(input_folder, filename)
        os.remove(image_path)
        print(f"Removed duplicate image: {filename}")

# Removed the print statements for future reference

def move_duplicates(input_folder, similarity_threshold=0.95):
    """ Moves images that are similar to the previous 4 images into a 'duplicates' folder """
    images = {}
    
    # Load all processed images
    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(input_folder, filename)
            img = cv2.imread(image_path)
            images[filename] = img

    # Sort filenames lexicographically (aaa to zzz)
    sorted_filenames = sorted(images.keys())

    # Create a 'duplicates' folder if it doesn't exist
    duplicates_folder = os.path.join(input_folder, "duplicates")
    os.makedirs(duplicates_folder, exist_ok=True)

    to_move = set()

    # Use tqdm for progress bar while comparing images
    with tqdm(total=len(sorted_filenames), desc="Comparing images", unit="image") as pbar:
        for i in range(1, len(sorted_filenames)):
            current_filename = sorted_filenames[i]
            current_img = images[current_filename]

            # Compare the current image to the previous 4 images
            for j in range(max(0, i - 4), i):
                previous_filename = sorted_filenames[j]
                previous_img = images[previous_filename]

                # Get the dimensions of both images
                height1, width1 = current_img.shape[:2]
                height2, width2 = previous_img.shape[:2]
                
                # Calculate the cropping region (smallest width and height)
                new_width = min(width1, width2)
                new_height = min(height1, height2)
                
                # Crop both images to the new dimensions
                current_img_cropped = current_img[:new_height, :new_width]
                previous_img_cropped = previous_img[:new_height, :new_width]
                
                # Compute SSIM similarity on the cropped images
                gray1 = cv2.cvtColor(current_img_cropped, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(previous_img_cropped, cv2.COLOR_BGR2GRAY)
                similarity = ssim(gray1, gray2)
                
                if similarity > similarity_threshold:
                    to_move.add(current_filename)  # Mark current image for moving
                    break  # No need to compare with further previous images if a match is found

            pbar.update(1)  # Update progress bar

    # Move duplicates to the 'duplicates' folder
    for filename in to_move:
        original_path = os.path.join(input_folder, filename)
        new_path = os.path.join(duplicates_folder, filename)
        shutil.move(original_path, new_path)  # Move the file to the duplicates folder







while True:
    # Example usage
    video_path = input("Enter video path: ")
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_dir = os.path.dirname(video_path)  # Get video directory
    frames_folder = os.path.join(video_dir, f"{video_name}_worked")  # Save in same folder

    extract_frames(video_path, frames_folder)
    process_images_in_folder(frames_folder)

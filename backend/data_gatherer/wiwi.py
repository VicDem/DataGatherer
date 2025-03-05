import cv2
import numpy as np

# Load the image
image = cv2.imread("/Users/vi.dematteis/Desktop/work/sceenshot hashtags/34_arte_worked/Screenshot 2025-03-04 alle 13.50.14.png")

# Convert the image to HSV color space
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the color range for yellow and pink (Instagram colors)
# Yellow range (can be adjusted)
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([40, 255, 255])

# Pink range (can be adjusted)
lower_pink = np.array([150, 100, 100])
upper_pink = np.array([170, 255, 255])

# Create masks for yellow and pink
mask_yellow = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
mask_pink = cv2.inRange(hsv_image, lower_pink, upper_pink)

# Combine both masks
combined_mask = cv2.bitwise_or(mask_yellow, mask_pink)

# Find contours in the combined mask
contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# If contours are found
if contours:
    # Find the largest contour (most likely the circle)
    largest_contour = max(contours, key=cv2.contourArea)

    # Get the bounding circle for the largest contour
    (x, y), radius = cv2.minEnclosingCircle(largest_contour)

    # Draw the circle and center on the original image (for visualization)
    output_image = image.copy()
    cv2.circle(output_image, (int(x), int(y)), int(radius), (0, 255, 0), 4)

    # Crop the image to the right of the circle
    cropped_image = image[:, int(x + radius):]

    # Show the original image with the detected circle and the cropped result
    cv2.imshow("Image with Detected Circle", output_image)
    cv2.imshow("Cropped Image", cropped_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No circle detected!")

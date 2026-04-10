import cv2
import numpy as np
from PIL import Image
import os

img_path = '/home/mdelop/.gemini/antigravity/brain/317178a9-89c8-4349-acdc-ea57c41679ac/uploaded_media_1775848237653.jpg'
out_path = '/home/mdelop/Escritorio/Antigravity/data-science-portfolio/web/profile.jpg'

img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Load face cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
faces = face_cascade.detectMultiScale(gray, 1.3, 5)

if len(faces) > 0:
    # Get the largest face
    faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
    x, y, w, h = faces[0]
    
    # Calculate a square crop around the face, including shoulders
    center_x = x + w//2
    center_y = y + h//2
    
    size = int(max(w, h) * 2.5) # generous crop around face
    size = min(size, img.shape[0]) # limit to image height
    
    x1 = max(0, center_x - size//2)
    y1 = max(0, center_y - int(size * 0.4)) # shift crop slightly up
    x2 = min(img.shape[1], x1 + size)
    y2 = min(img.shape[0], y1 + size)
    
    # Adjust to make it perfectly square if we hit edges
    actual_w = x2 - x1
    actual_h = y2 - y1
    min_dim = min(actual_w, actual_h)
    
    crop = img[y1:y1+min_dim, x1:x1+min_dim]
else:
    # Fallback to manual crop for lower left (approx user position)
    crop = img[200:700, 100:600]

# Resize to standard size
crop = cv2.resize(crop, (400, 400))

# Apply the "make me thinner" effect (scale X slightly and pad, or just resize aspect ratio)
# Let's compress width by 5% and keep height the same
thins_width = int(400 * 0.94)
thin_crop = cv2.resize(crop, (thins_width, 400))
# Now resize back to 400x400 (this stretches the pixels vertically, appearing thinner)
final_crop = cv2.resize(thin_crop, (400, 400))

cv2.imwrite(out_path, final_crop)
print(f"Profile saved to {out_path}")

import cv2
import pytesseract
from PIL import Image
import numpy as np

# Load screenshot
img = cv2.imread('debug_screenshots/tgobox_jkt_1747_gmail_com_1781536703_before_submit.png')
# The KTP is in the center. Let's crop it roughly.
# Wait, I don't know the exact coordinates. Let's just run OCR on the whole image and see what text it finds.
# Or better, convert to grayscale and threshold.
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
text = pytesseract.image_to_string(gray, lang='eng')
print(text)

# /// script
# dependencies = [
#   "pytesseract",
#   "numpy",
#   "pandas",
#   "matplotlib",
#   "pdf2image",
#   "opencv-python",
# ]
# ///
import cv2
import numpy as np
import pytesseract
import pandas as pd
import matplotlib.pyplot as plt
from pdf2image import convert_from_path

def extract_table_from_pdf(pdf_path, output_csv):
    # Convert PDF to image
    pages = convert_from_path(pdf_path, dpi=300)
    img = np.array(pages[0])  # assuming table is on the first page
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Thresholding (Otsu)
    _, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    img_bin = 255 - img_bin

    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, img.shape[1] // 100))
    vertical_lines = cv2.erode(img_bin, vertical_kernel, iterations=3)
    vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=3)

    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (img.shape[1] // 100, 1))
    horizontal_lines = cv2.erode(img_bin, horizontal_kernel, iterations=3)
    horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=3)

    # Combine horizontal and vertical lines
    combined_lines = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)

    # Find contours to detect table cells
    contours, hierarchy = cv2.findContours(combined_lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours (top to bottom)
    boundingBoxes = [cv2.boundingRect(c) for c in contours]
    (contours, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes), key=lambda b: b[1][1]))

    # Group contours into rows
    rows = []
    current_row = []
    mean_height = np.mean([b[3] for b in boundingBoxes])

    for box in boundingBoxes:
        if not current_row or abs(current_row[-1][1] - box[1]) < mean_height / 2:
            current_row.append(box)
        else:
            rows.append(sorted(current_row, key=lambda b: b[0]))
            current_row = [box]
    rows.append(sorted(current_row, key=lambda b: b[0]))

    # OCR and extraction
    final_data = []
    for row in rows:
        row_data = []
        for box in row:
            x, y, w, h = box
            cell_img = img[y:y+h, x:x+w]
            border = cv2.copyMakeBorder(cell_img, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=[255,255])
            resized = cv2.resize(border, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            text = pytesseract.image_to_string(resized, config='--psm 6').strip()
            row_data.append(text)
        final_data.append(row_data)

    # Convert to DataFrame
    df = pd.DataFrame(final_data)

    # Export to CSV
    df.to_csv(output_csv, index=False)

    # Optional: visualize
    plt.imshow(combined_lines, cmap='gray')
    plt.title('Extracted Table Structure')
    plt.show()

if __name__ == '__main__':
    pdf_path = 'resources/g500_f10_wet_cwai-off_pa0000.pdf'
    output_csv = 'output.csv'
    extract_table_from_pdf(pdf_path, output_csv)

import os
import argparse
import logging
import fitz
import shutil
from PIL import Image
from datetime import datetime
from pathlib import Path


def tiff2pdf(folder_path):
    timestamp = datetime.now().strftime("%d%m%Y-%H%M")
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    day = datetime.now().strftime("%d")

    output_folder = folder_path
    original_folder = os.path.join(folder_path, 'original tiff')
    working_folder = os.path.join(folder_path, 'workingconversion')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(original_folder):
        os.makedirs(original_folder)
    if not os.path.exists(working_folder):
        os.makedirs(working_folder)


    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.tiff') or file_name.lower().endswith('.tif'):
            try:
                tiff_image = Image.open(file_name)
                pdf_doc = fitz.open()

                for page_num in range(tiff_image.n_frames):
                    tiff_image.seek(page_num)
                    rgb_image = tiff_image.convert('RGB')
                    temp_file_path = os.path.join(working_folder, f"temp_page_{page_num}.png")
                    rgb_image.save(temp_file_path)
                    img_pdf = fitz.open(temp_file_path)

                    rect = fitz.Rect(0, 0, rgb_image.width, rgb_image.height)
                    pdf_page = pdf_doc.new_page(width=rgb_image.width, height=rgb_image.height)
                    pdf_page.insert_image(rect, filename=temp_file_path)


                save_name = Path(file_name).stem
                pdf_doc.save(os.path.join(output_folder, f"{save_name}.pdf"), deflate=True)
                pdf_doc.close()
                tiff_image.close()
                os.makedirs(os.path.join(original_folder, year, month, day), exist_ok=True)
                Path(file_name).rename(os.path.join(original_folder, year, month, day, f"{timestamp}-{file_name}"))
            except Exception as e:
                logging.error(f"error converting {file_name}: {e}", exc_info=True)
    shutil.rmtree(working_folder, ignore_errors=True)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='convert tiff to pdf')
    parser.add_argument('--folder-path', required=True, help='path to folder with tiff files')
    args = parser.parse_args()

    tiff2pdf(args.folder_path)

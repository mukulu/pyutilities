#!/usr/bin/env python
#  Copyright 2024 John Francis Mukulu <john.f.mukulu@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import os
import pytesseract
from PIL import Image
import subprocess
import tarfile

def rename_pdfs(pdf_directory):
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    for pdf_file in pdf_files:
        new_name = pdf_file.replace(" ", "_")
        if new_name != pdf_file:
            os.rename(os.path.join(pdf_directory, pdf_file), os.path.join(pdf_directory, new_name))
            print(f"Renamed '{pdf_file}' to '{new_name}'")

def convert_pdfs_to_images(pdf_directory, image_directory):
    os.makedirs(image_directory, exist_ok=True)
    
    command = f'for name in $(ls {pdf_directory}/*.pdf); do pdftoppm "$name" "{image_directory}/${{name##*/}}_image" -jpeg; done'
    subprocess.run(command, shell=True, check=True)

def image_to_text(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        return str(e)

def convert_images_to_texts(image_directory, text_directory):
    os.makedirs(text_directory, exist_ok=True)

    for filename in os.listdir(image_directory):
        if filename.lower().endswith('.jpg'):
            image_path = os.path.join(image_directory, filename)
            extracted_text = image_to_text(image_path)

            txt_filename = f"{os.path.splitext(filename)[0]}.txt"
            txt_path = os.path.join(text_directory, txt_filename)

            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(extracted_text)

            print(f"Converted {filename} to {txt_filename}")

def combine_texts_for_pdfs(pdf_directory, text_directory, combined_directory):
    os.makedirs(combined_directory, exist_ok=True)
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]

    for pdf_file in pdf_files:
        base_name = os.path.splitext(pdf_file)[0]
        combined_content = []

        for filename in os.listdir(text_directory):
            if filename.startswith(base_name) and filename.endswith('.txt'):
                file_path = os.path.join(text_directory, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    combined_content.append(file.read())

        combined_file_path = os.path.join(combined_directory, f"{base_name}_combined.txt")
        with open(combined_file_path, 'w', encoding='utf-8') as combined_file:
            combined_file.write('\n\n'.join(combined_content))

        print(f"Combined texts for {pdf_file} into {combined_file_path}")

def create_tarball(combined_directory, tarball_path):
    with tarfile.open(tarball_path, "w:gz") as tar:
        for filename in os.listdir(combined_directory):
            tar.add(os.path.join(combined_directory, filename), arcname=filename)
    print(f"Created tarball at {tarball_path}")

def combine_all_texts(combined_directory, final_text_path):
    combined_contents = []
    for filename in os.listdir(combined_directory):
        if filename.endswith('_combined.txt'):
            with open(os.path.join(combined_directory, filename), 'r', encoding='utf-8') as file:
                combined_contents.append(file.read())

    with open(final_text_path, 'w', encoding='utf-8') as final_file:
        final_file.write('\n\n'.join(combined_contents))
    print(f"Combined all texts into {final_text_path}")

if __name__ == "__main__":
    pdf_directory = 'pdfs'
    processing_directory = 'processing'
    image_directory = os.path.join(processing_directory, 'images')
    text_directory = os.path.join(processing_directory, 'texts')
    combined_directory = 'combinedtexts'
    tarball_path = os.path.join(combined_directory, 'combined_texts.tar.gz')
    final_text_path = os.path.join(combined_directory, 'final_combined_text.txt')

    os.makedirs(combined_directory, exist_ok=True)

    # Check if the pdfs directory exists and contains PDF files
    if not os.path.exists(pdf_directory) or not any(f.lower().endswith('.pdf') for f in os.listdir(pdf_directory)):
        print("No PDF files found in the 'pdfs' folder. Exiting the script.")
    else:
        # Rename PDF files by replacing spaces with underscores
        rename_pdfs(pdf_directory)

        convert_pdfs_to_images(pdf_directory, image_directory)
        convert_images_to_texts(image_directory, text_directory)
        combine_texts_for_pdfs(pdf_directory, text_directory, combined_directory)

        create_tarball(combined_directory, tarball_path)

        combine_all_texts(combined_directory, final_text_path)
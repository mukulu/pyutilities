#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path

def find_and_concatenate_txt_files():
    # Get the directory where the script is located
    script_dir = Path(__file__).parent
    
    # Initialize the content list
    all_content = []
    
    # Define the order of folders to process
    folders = ['Tech_Eng_2e_WB3_0intro']
    folders.extend([f'Unit_{i}' for i in range(1, 13)])  # Unit_1 to Unit_12
    
    for folder in folders:
        folder_path = script_dir / folder
        
        # Skip if folder doesn't exist
        if not folder_path.exists():
            print(f"Warning: Folder '{folder}' not found. Skipping...")
            continue
        
        # Collect all .txt files in the current folder (recursively)
        txt_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('.txt'):
                    txt_files.append(Path(root) / file)
        
        # Sort the files alphabetically by their full path
        txt_files.sort()
        
        # Read and append the content of each file
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    all_content.append(f.read())
            except Exception as e:
                print(f"Error reading file {txt_file}: {e}")
    
    # Write all content to the output file
    output_file = script_dir / 'all_concatenated_transcripts.txt'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_content))
        print(f"Successfully concatenated all files to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == '__main__':
    find_and_concatenate_txt_files()
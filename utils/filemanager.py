import os
import sys
import pandas as pd
from glob import glob
from .logger import logger
import re

def extract_parameter(text):
    '''
    Extract the parameter number from the text.

    Args:
        text ('str'): Text to search for the parameter number.

    Returns:
        parameter_number ('str'): Parameter number.
    '''
    match = re.search(r'Par(\w+)', text)
    if match:
        return 'Par' + match.group(1)
    else:
        return None



def get_points_paths(base_path, suffix, num_occurrences = 2):
    '''
    Get the paths of the transformed points.

    Args:
        args ('argparse.Namespace'): Command line arguments.
        suffix ('str'): Suffix of the file name.
        num_occurrences ('int'): Number of occurrences of the suffix in the path.

    Returns:
        paths ('list'): List of paths.
    '''
    paths = [path.replace('\\', '/') for path in sorted(glob(os.path.join(base_path, *["***"] * num_occurrences , f"*{suffix}.txt"), recursive=True))]
    return paths

def get_paths(args, suffix):
    '''
    Get the paths of the volumes and segmentations.

    Args:
        args ('argparse.Namespace'): Command line arguments.
        suffix ('str'): Suffix of the file name.

    Returns:
        paths ('list'): List of paths.
    '''
    paths = [path.replace('\\', '/') for path in sorted(glob(os.path.join(args.dataset_path, "***" , f"*{suffix}.nii.gz"), recursive=True))]
    return paths

def check_paths(args, paths, message):
    '''
    Check if the paths exist.

    Args:
        args ('argparse.Namespace'): Command line arguments.
        paths ('list'): List of paths.
        message ('str'): Message to display in the logger.

    Returns:
        None
    '''
    if len(paths) == 0:
        logger.error(f"No {message} found in {args.dataset_path} directory.")
        sys.exit(1)


def create_directory_if_not_exists(path):
    '''
    Create a directory if it does not exist.

    Args:
        path ('str'): Directory path.
    '''
    if not os.path.exists(path):
        os.makedirs(path)

def replace_text_in_file(file_path, search_text, replacement_text):
        '''
        Replace text in a text file.

        Args:
            file_path ('str'): Path to the text file.
            search_text ('str'): Text to search for in the file.
            replacement_text ('str'): Text to replace the searched text with.
        '''
        try:
            # Read the file
            with open(file_path, 'r') as file:
                content = file.read()

            # Replace the search_text with replacement_text
            modified_content = content.replace(search_text, replacement_text)

            # Write the modified content back to the file
            with open(file_path, 'w') as file:
                file.write(modified_content)

            # print(f"Text replaced in {file_path} and saved.")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        # except Exception as e:
        #     print(f"An error occurred: {e}")

def add_and_delete_rows(file_path, row1, row2):
    # Add two rows at the beginning of the file
    with open(file_path, 'r+') as file:
        content = file.read()
        file.seek(0, 0)
        file.write(row1 + '\n' + row2 + '\n' + content)

def delete_added_rows(file_path):
    # Delete the first two rows from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Handle different newline characters when writing back to the file
    with open(file_path, 'w', newline=os.linesep) as file:
        file.writelines(lines[2:])



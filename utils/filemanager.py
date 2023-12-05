import os
import pandas as pd

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



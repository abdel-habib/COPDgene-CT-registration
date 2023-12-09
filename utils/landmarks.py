import pandas as pd

def prepare_landmarks_for_transform(landmarks_list, landmarks_file_path, output_file_path):
    # to add the first two rows in the moving landmark file for elastix...

    pass

def write_landmarks_to_list(landmarks, file_path):
    '''
    Write the landmarks to a text file.

    Args:
        landmarks ('list'): List of landmarks.
        file_path ('str'): Path to the text file. It includes the file name and extension.

    Returns:
        None
    '''
    # Write the landmarks to a text file
    with open(file_path, 'w') as file:
        for row in landmarks:
            file.write('\t'.join(map(str, row)) + '\n')


def get_landmarks_from_txt(transformed_file_path, search_key='OutputIndexFixed'):
    '''
    Get the transformed landmarks from the text file using a given search_key column index.
    The searcu_key column index is the column name in the text file, where the landmarks (input or transformed)
    are stored. The default value is 'OutputIndexFixed', which is the transformed landmarks. Only two values are
    possible: 'OutputIndexFixed' or 'InputIndex'.

    Args:
        transformed_file_path ('str'): Path to the transformed text file.
        search_key ('str'): Column name in the text file where the landmarks are stored.

    Returns:
        landmarks_list ('list'): List of transformed landmarks.
    '''
    # validate the search key
    assert search_key in ['OutputIndexFixed', 'InputIndex'], "The search_key must be either 'OutputIndexFixed' or 'InputIndex'."

    # Define the column names based on the data in the text file
    columns = [
        'Point', 'InputIndex', 'InputPoint',
        'OutputIndexFixed', 'OutputPoint', 'Deformation'
    ]

    # Read the text file into a pandas DataFrame
    df = pd.read_csv(transformed_file_path, sep='\t;', comment=';', header=None, names=columns, engine='python')

    # select the required column
    df_col = df[search_key]
    
    # convert the column values to a list of lists
    landmarks_list = [list(map(int, df_col[idx].split(' ')[-4:-1])) for idx in range(len(df_col))]

    return landmarks_list

def visualize_landmarks():
    '''
    Visualize the landmarks on the reference image.
    '''
    pass
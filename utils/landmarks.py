import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib

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

def visualize_landmarks(landmarks_path=None, reference_image_path=None, slice_index=70, voxel_dim=(1, 1, 1)):
    '''
    Visualize the landmarks on the reference image or a mask.
    '''

    # Load the reference image
    nii_image = nib.load(reference_image_path)
    reference_image = nii_image.get_fdata()

    # transpose the axis to rotate for visualization
    reference_image = reference_image.transpose(2, 1, 0)

    # Load 3D landmarks from the file
    landmarks_data = np.loadtxt(landmarks_path)

    # Extract x, y, z coordinates
    x_coords = landmarks_data[:, 0].astype(int)
    y_coords = landmarks_data[:, 1].astype(int)
    z_coords = landmarks_data[:, 2].astype(int)

    # reshsaped_landmarks = np.array([z_coords, y_coords, x_coords]).T
    # voxel_dim = (voxel_dim[2], voxel_dim[1], voxel_dim[0])
    # reshsaped_landmarks = reshsaped_landmarks * voxel_dim

    # -1 to match the MATLAB visualizer indexing result
    slice_index = slice_index - 1
    
    # Visualize a specific slice
    plt.figure(figsize=(8, 8))
    plt.imshow(reference_image[slice_index, :, :], cmap='gray')
    plt.title(f"Slice {slice_index}")

    # Plot landmarks on the current slice
    plt.scatter(x_coords, y_coords, c='r', marker='+', label='Landmarks')
    plt.title('Landmarks on Volume Slice')
    plt.legend()
    plt.axis('off')
    plt.show()

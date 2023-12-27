import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib
import os
from matplotlib.colors import LinearSegmentedColormap

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

def visualize_landmarks(slice_index=70, subject='copd1'):
    '''
    Visualize the landmarks on the reference image or a mask.
    '''
    # Define the paths
    landmarks_path = os.path.join(os.getcwd(),f'../dataset/train/{subject}/{subject}_300_iBH_xyz_r1.txt')
    reference_image_path = os.path.join(os.getcwd(),f'../dataset/train/{subject}/{subject}_iBHCT.nii.gz') # _lung
    reference_mask_path = os.path.join(os.getcwd(),f'../dataset/train/{subject}/{subject}_iBHCT_lung.nii.gz') # _lung

    # -1 to match the MATLAB visualizer indexing result
    slice_index = slice_index - 1

    # Load the reference image
    nii_image = nib.load(reference_image_path)
    reference_image = nii_image.get_fdata()

    # Load the reference mask
    nii_mask = nib.load(reference_mask_path)
    reference_mask = nii_mask.get_fdata()

    # transpose the axis to rotate for visualization
    reference_image = reference_image.transpose(2, 1, 0)
    reference_mask = reference_mask.transpose(2, 1, 0)
    
    # Load 3D landmarks from the file
    landmarks_data = np.loadtxt(landmarks_path, skiprows=2)
    slice_landmarsk = np.array([inner_list for inner_list in landmarks_data if inner_list[2] == slice_index+1])
    
    # Create a red-green colormap with opacity
    cmap = LinearSegmentedColormap.from_list('red_green', ['red', 'green'], N=256)
    
    # Visualize a specific slice
    plt.figure(figsize=(8, 8))
    plt.imshow(reference_image[slice_index, :, :], cmap='gray')

    # Overlay the mask with color on the landmarks
    mask_overlay = np.ma.masked_where(reference_mask[slice_index, :, :] == 0, reference_mask[slice_index, :, :])
    plt.imshow(mask_overlay, cmap=cmap, alpha=0.5)

    if len(slice_landmarsk) > 0:
            
        # Extract x, y, z coordinates
        x_coords = slice_landmarsk[:, 0].astype(int)
        y_coords = slice_landmarsk[:, 1].astype(int)
        z_coords = slice_landmarsk[:, 2].astype(int)

        # Plot landmarks on the current slice
        plt.scatter(x_coords, y_coords, c='b', marker='+', label=f'{landmarks_path.split("/")[-1].split(".txt")[0]} landmarks')

    plt.legend()
    plt.axis('off')
    plt.title(f"Slice {slice_index+1}")
    plt.show()


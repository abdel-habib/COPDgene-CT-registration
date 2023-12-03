import numpy as np

def compute_TRE(fixed_points_file, moving_points_file, voxel_size):
    """
    Computes the Target Registration Error (TRE) to quantify the accuracy of the registration process. The TRE is calculated using 3D Euclidean 
    distance between the coordinates in the reference image (File 1) and the transformed coordinates in the registered image (File 2).

    Args:
        fixed_points_file (str): path to the file containing the coordinates of the fixed points
        moving_points_file (str): path to the file containing the coordinates of the moving points
        voxel_size (float): voxel size in mm

    Returns:
        mean_TRE (float): mean TRE in mm
        std_TRE (float): standard deviation of the TRE in mm
    """
    # load the files if paths are provided
    fixed_points = np.loadtxt(fixed_points_file)
    moving_points = np.loadtxt(moving_points_file)

    # Check if the number of points in both files is the same
    if len(fixed_points) != len(moving_points):
        raise ValueError("The number of points in the fixed and moving files must be the same.")

    # Compute the TRE
    TRE = np.linalg.norm((fixed_points - moving_points) * voxel_size, axis=1)

    return np.mean(TRE), np.std(TRE)
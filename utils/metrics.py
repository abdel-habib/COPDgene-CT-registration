import numpy as np

def compute_TRE(pts_exhale_file, pts_inhale_file, voxel_size):
    """
    Computes the Target Registration Error (TRE) to quantify the accuracy of the registration process. The TRE is calculated using 3D Euclidean 
    distance between the keypoints in the reference image (File 1) and the transformed keypoints in the registered image (File 2).

    Args:
        pts_exhale_file (str): path to the file containing the coordinates of the moving points
        pts_inhale_file (str): path to the file containing the coordinates of the fixed points
        voxel_size (tuple): voxel size in mm

    Returns:
        mean_TRE (float): mean TRE in mm
        std_TRE (float): standard deviation of the TRE in mm
    """
    # load the files if paths are provided
    pts_inhale = np.loadtxt(pts_inhale_file)
    pts_exhale = np.loadtxt(pts_exhale_file)

    # Check if the number of points in both files is the same
    if len(pts_inhale) != len(pts_exhale):
        raise ValueError("The number of points in the fixed and moving files must be the same.")

    # Compute the TRE - square root of the sum of the squared elements
    TRE = np.linalg.norm((pts_inhale - pts_exhale) * voxel_size, axis=1)

    return np.round(np.mean(TRE),2), np.round(np.std(TRE),2)
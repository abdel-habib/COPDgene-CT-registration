import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob

def plot_boxplot(experiment_name, output_dir, exclude=[], title="Boxplot"):
    '''
    Plot boxplot for the given data.

    Args:
        experiment_name (str): Name of the experiment.
        output_dir (str): Path to the output directory.
        exclude (list): List of columns to exclude from the boxplot.
        title (str): Title of the plot.

    Note:
        The dataframe holds the data in columns. Each column represents an experiment (single box plot) that we want to plot.
        We add the data to specific column of the experiment in the datafraame.

        Each row in the dataframe represents the result obtained from each subject in the experiment.

        >> df.head()
        >>          Par0003.affine  Par0003.bs-R1-fg  Par0003.bs-R6-ug  experiment_name
        >> copd1    10.62             26.25              1.34            ..
        >> copd2    10.07             21.45              2.68            ..
        >> copd3    03.57             12.04              1.27            ..
        >> copd4    07.48             29.45              1.53            ..

        If we describe the dataframe, we get the following:

        >> stats = df.describe()
        >> stats
        >>       Par0003.affine  Par0003.bs-R1-fg  Par0003.bs-R6-ug
        >> count  4.000000        4.000000          4.000000
        >> mean   7.935000        22.795000         1.705000
        >> std    3.417692        7.221071          0.700713
        >> min    3.570000        12.040000         1.270000
        >> 25%    6.345000        19.522500         1.330000
        >> 50%    8.775000        23.850000         1.435000
        >> 75%    10.365000       27.122500         2.060000
        >> max    10.620000       29.450000         2.680000

    Returns:
        None. The function generates and displays the box plot.
    '''

    # Get the data
    columns = os.listdir(f'../output/{experiment_name}/')
    TRE_sample_results = [path.replace('\\', '/') for path in sorted(glob(os.path.join(output_dir, experiment_name, "***", "points", "TRE_sample_results.csv"), recursive=True))]

    # Remove the excluded columns
    for column in exclude:
        if column in columns:
            columns.remove(column)

        TRE_sample_results = [item for item in TRE_sample_results if column not in item]

    # debugging
    # columns = columns[:5]
    # TRE_sample_results = TRE_sample_results[:5]
    # print(columns)
    # print(TRE_sample_results)

    # assert len(columns) == len(TRE_sample_results)
    assert  len(columns) == len(TRE_sample_results), f"Number of columns ({len(columns)}) does not match number of results ({len(TRE_sample_results)})"

    # Create a dataframe
    df = pd.DataFrame(columns=columns)

    for i, path in enumerate(TRE_sample_results):
        # Read the csv file
        data = pd.read_csv(path, index_col=0)

        # Add the data to the dataframe
        columns[i] = columns[i] + f" ({data['TRE_mean'].mean():.3f})"
        df[columns[i]] = data['TRE_mean']
        
    # Plot the boxplot
    boxplot = df.boxplot(column=columns, rot=90)

    # Get the lowest values for each column
    lowest_values = df.mean()

    # Get the column with the overall lowest minimum value
    lowest_column = lowest_values.idxmin()

    # Highlight the entire boxplot for the column with the lowest minimum value in red
    position = columns.index(lowest_column) + 1

    # 7 is the number of data that represents a single boxplot (divide len(boxplot.get_lines())//len(columns) to get the number of data per boxplot)
    boxplot.get_lines()[position * 7 - 7].set(color='red', linewidth=3) 

    # Set plot title
    plt.title(title)

    # Show the plot
    plt.show()

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
import sys
import argparse
import os

from utils.logger import logger
from utils.filemanager import create_directory_if_not_exists, get_paths, check_paths, extract_parameter

if __name__ == "__main__":
    # optional arguments from the command line 
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset_path', type=str, default='dataset/train', help='root dir for nifti data')
    parser.add_argument('--experiment_name', type=str, default='elastix_01', help='experiment name')
    parser.add_argument('--parameters_path', type=str, default='elastix-parameters/Par0003', help='root dir for elastix parameters. The script will use all the parameters in this directory. A single .txt file can also be used.')
    parser.add_argument('--output_path', type=str, default='output', help='root dir for output scripts')
    parser.add_argument("--use_masks", action='store_true', help='if True, segmentation masks will be used during the registration.')

    # parse the arguments
    args = parser.parse_args()

    # check if parameters_path is .txt file
    if os.path.isfile(args.parameters_path):
        parameters      = args.parameters_path

        # cteate params key folder name
        reg_params      = '-p "{}"'.format(parameters).replace('\\', '/')
        reg_params_key  = parameters.split('/')[-1].replace('.txt', '')
        transform_idx   = 0

    elif os.path.isdir(args.parameters_path):
        # get the parameters from the parameters_path
        parameters = os.listdir(args.parameters_path)

        if len(parameters) == 0:
            logger.error(f"No parameters found in {args.parameters_path} directory.")
            sys.exit(1)
    
        # cteate params key folder name
        reg_params      = ' '.join(['-p "{}"'.format(os.path.join(args.parameters_path, param)) for param in parameters]).replace('\\', '/')    
        reg_params_key  = '+'.join(['{}'.format(param.replace('.txt', '')) for param in parameters])
        transform_idx   = len(parameters) - 1

    # get the name of the parameters folder
    params_folder_name = extract_parameter(args.parameters_path) # Par0003, Par0004, ...

    # create experiment output
    # args.experiment_name is useful to distinguish between different experiments (e.g. with or without preprocessing, etc.)
    # reg_params_key is useful to distinguish between different registration parameters (e.g. Par0003, Par0004, etc.)
    args.exp_output = os.path.join(args.output_path, args.experiment_name, reg_params_key)
    create_directory_if_not_exists(args.exp_output)

    # get the exhale and inhale volumes and segmentations
    exhale_volumes = get_paths(args, "eBHCT")
    inhale_volumes = get_paths(args, "iBHCT")

    check_paths(args, exhale_volumes, "exhale volumes")
    check_paths(args, inhale_volumes, "inhale volumes")

    # get the exhale and inhale segmentations if args.use_masks is True
    exhale_seg = get_paths(args, "eBHCT_lung") if args.use_masks else [0 for _ in range(len(exhale_volumes))] # the list has to have values for the zip(*) to return the values inside
    inhale_seg = get_paths(args, "iBHCT_lung") if args.use_masks else [0 for _ in range(len(inhale_volumes))]

    if args.use_masks:
        check_paths(args, exhale_seg, "exhale segmentations")
        check_paths(args, inhale_seg, "inhale segmentations")

    logger.info(f"Creating .bat file in {args.exp_output} output directory for {args.experiment_name} experiment.")
    logger.info(f"Experimenting using {reg_params} params command...")
    logger.info(f"Key for the experiment: {reg_params_key}...")

    # creating the .bat file
    with open(os.path.join(args.exp_output, 'elastix_transformix.bat'), 'w') as file:
        file.write("@echo on\n")
        file.write(f"echo To execute this file, use: call {os.path.join(args.exp_output, 'elastix_transformix.bat')} \n")

        for e_path, i_path, e_seg_path, i_seg_path in zip(exhale_volumes, inhale_volumes, exhale_seg, inhale_seg):
            # Append commands to the .bat file
            file.write(f"\nREM Processing {e_path} and {i_path}\n")

            # defining the sample name and the file names
            sample_name = i_path.split('/')[-1].split('_')[0] #copd1, copd2, ...
            e_filename_full = e_path.split('/')[-1].split('.')[0] #copd1_eBHCT, ..
            i_filename_full = i_path.split('/')[-1].split('.')[0] #copd1_iBHCT, ..

            # defining fixed and moving paths
            fixed_path = i_path
            fMask = i_seg_path

            moving_path = e_path
            mMask = e_seg_path

            # defining the control point to be transformed abd transform file paths
            input_points = os.path.join(args.dataset_path ,f'{sample_name}/{sample_name}_300_iBH_xyz_r1.txt') # i_cntl_pt
            transform_path = f'{args.exp_output}/images/output_{i_filename_full}/{e_filename_full}/TransformParameters.{transform_idx}.txt'

            # Get the names of the fixed and moving images for the output directory, names without the file extensions
            reg_fixed_name  = fixed_path.replace("\\", "/").split("/")[-1].split(".")[0]
            reg_moving_name = moving_path.replace("\\", "/").split("/")[-1].split(".")[0]

            elastix_output_dir = f'{args.exp_output}/images/output_{reg_fixed_name}/{reg_moving_name}'
            transformix_output_dir = f'{args.exp_output}/points/output_{reg_fixed_name}/{reg_moving_name}'

            create_directory_if_not_exists(elastix_output_dir)
            create_directory_if_not_exists(transformix_output_dir)

            if params_folder_name == 'Par0003':
                # elastix version: 3.9 -- fails to allocate memory to register; also can't -def point transformation
                # elastix_v_path      = '.\\elastix-versions\\elastix_windows32_v3.9\\elastix'
                # transformix_v_path  = '.\\elastix-versions\\elastix_windows32_v3.9\\transformix'
                
                # using default is 4.7
                elastix_v_path      = '.\\elastix-versions\\elastix_windows64_v4.7\\elastix'
                transformix_v_path  = '.\\elastix-versions\\elastix_windows64_v4.7\\transformix'
            
            elif params_folder_name == 'Par0007':
                # elastix version: 4.0 -- fails to allocate memory to register; also can't -def point transformation
                # elastix_v_path      = '.\\elastix-versions\\elastix_windows32_v4.0\\elastix'
                # transformix_v_path  = '.\\elastix-versions\\elastix_windows32_v4.0\\transformix'

                # using default is 4.7
                elastix_v_path      = '.\\elastix-versions\\elastix_windows64_v4.7\\elastix'
                transformix_v_path  = '.\\elastix-versions\\elastix_windows64_v4.7\\transformix'

            elif params_folder_name == 'Par0011':
                # elastix version: 4.301
                elastix_v_path      = '.\\elastix-versions\\elastix_windows64_v4.3\\elastix'
                transformix_v_path  = '.\\elastix-versions\\elastix_windows64_v4.3\\transformix'
            else:
                # default is 4.7
                elastix_v_path      = '.\\elastix-versions\\elastix_windows64_v4.7\\elastix'
                transformix_v_path  = '.\\elastix-versions\\elastix_windows64_v4.7\\transformix'


            # create elastix command line
            if args.use_masks:
                elastix_command_line = f'{elastix_v_path} -f "{fixed_path}" -m "{moving_path}" -fMask "{fMask}" -mMask "{mMask}" {reg_params} -out "{elastix_output_dir}"'
            else:
                elastix_command_line = f'{elastix_v_path} -f "{fixed_path}" -m "{moving_path}" {reg_params} -out "{elastix_output_dir}"'

            # create transformix command line
            trasformix_command_line = f'{transformix_v_path} -def "{input_points}" -tp "{transform_path}"  -out "{transformix_output_dir}"'

            file.write(f"{elastix_command_line}\n")
            file.write(f"{trasformix_command_line}\n")
            
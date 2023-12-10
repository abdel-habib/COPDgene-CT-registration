import sys
import argparse
import os
from glob import glob

# importing utils and 
from utils.logger import logger, pprint

if __name__ == "__main__":
    # optional arguments from the command line 
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset_path', type=str, default='dataset/train', help='root dir for raw training data')
    parser.add_argument('--keypoint_type', type=str, default='inhale', help='type of keypoint to be prepared for transformix')

    # parse the arguments
    args = parser.parse_args()

    # check if the dataset_path exists
    if not os.path.exists(args.dataset_path):
        logger.error(f"Path {args.dataset_path} does not exist")
        sys.exit(1)

    # check if the keypoint_type is valid
    if args.keypoint_type not in ['inhale', 'exhale']:
        logger.error(f"Keypoint type {args.keypoint_type} is not valid")
        sys.exit(1)

    # get the list of exhale and inhale files from the dataset_path
    logger.info(f"Reading keypoint data from '{args.dataset_path}'")
    if args.keypoint_type == 'inhale':
        keypoint_files = [path.replace('\\', '/') for path in sorted(glob(os.path.join(args.dataset_path, "***" , "*300_iBH_xyz_r1.txt"), recursive=True))]
    else:
        keypoint_files = [path.replace('\\', '/') for path in sorted(glob(os.path.join(args.dataset_path, "***" , "*300_eBH_xyz_r1.txt"), recursive=True))]
    
    logger.info(f"Found {len(keypoint_files)} keypoint files for subjects ({[subject.split('/')[-2] for subject in keypoint_files]})")
    pprint(keypoint_files)

    print('''
          Prepare the points file to match transformix description in the manual:
          <index, point>
          <number of points>
          point1 x point1 y [point1 z]
          ...
          The first line indicates whether the points are given as “indices” (of the
          fixed image), or as “points” (in physical coordinates). The second line stores
          the number of points that will be specified. After that, the point data is given.\n''')

    for kp_file in keypoint_files:
        print(f"Processing {kp_file}")

        # read and update the keypoint file
        with open(kp_file, 'r+') as file:
            content = file.read()
            file.seek(0, 0)
            file.write('index' + '\n' + '300' + '\n' + content)

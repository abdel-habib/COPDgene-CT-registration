import sys
import argparse
import os
from glob import glob
import json
import SimpleITK as sitk

# importing utils and 
from utils.logger import logger
from utils.dataset import read_raw
from enums.dtype import DataTypes


if __name__ == "__main__":
    # optional arguments from the command line 
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset_path', type=str, default='dataset/train', help='root dir for raw training data')

    # parse the arguments
    args = parser.parse_args()

    # check if the dataset_path exists
    if not os.path.exists(args.dataset_path):
        logger.error(f"Path {args.dataset_path} does not exist")
        sys.exit(1)

    # get the list of exhale and inhale files from the dataset_path
    logger.info(f"Reading raw data from '{args.dataset_path}'")
    exhale_volumes = [path.replace('\\', '/') for path in sorted(glob(os.path.join(args.dataset_path, "***" , "*eBHCT.img"), recursive=True))]
    inhale_volumes = [path.replace('\\', '/') for path in sorted(glob(os.path.join(args.dataset_path, "***" , "*iBHCT.img"), recursive=True))]

    # log the number of exhale and inhale files
    logger.info(f"Found {len(exhale_volumes)} exhale volumes: ({[subject.split('/')[-2] for subject in exhale_volumes]})")
    logger.info(f"Found {len(inhale_volumes)} inhale volumes: ({[subject.split('/')[-2] for subject in inhale_volumes]})\n")

    # read the data dictionary
    with open(os.path.join(args.dataset_path.replace("train", "", 1), 'description.json'), 'r') as json_file:
        dictionary = json.loads(json_file.read())

    # iterate over all of the raw inhale and exhale volumes and export them as nifti files
    for exhale_volume, inhale_volume in zip(exhale_volumes, inhale_volumes):
        # get the subject name and information
        subject_name = exhale_volume.split('/')[-2]
        subject_information = dictionary['train'][subject_name]

        # Access the sitkPixelType value for RAW_DATA
        sitk_pixel_type = DataTypes.RAW_DATA.value

        # parse the data
        print(f"Parsing exhale and inhale volume of subject: {subject_name}, dtype: {sitk_pixel_type}")
        exhale_raw = read_raw(
            binary_file_name = exhale_volume, 
            image_size = subject_information['image_dim'], 
            sitk_pixel_type = sitk_pixel_type,
            image_spacing = subject_information['voxel_dim'],
            image_origin = subject_information['origin'],
            big_endian=False
            )
        inhale_raw = read_raw(
            binary_file_name = inhale_volume, 
            image_size = subject_information['image_dim'], 
            sitk_pixel_type = sitk_pixel_type,
            image_spacing = subject_information['voxel_dim'],
            image_origin = subject_information['origin'],
            big_endian=False
            )
        
        # log the image sizes
        assert exhale_raw.GetSize() == inhale_raw.GetSize(), "Exhale and inhale image sizes do not match"
        assert exhale_raw.GetSize() == tuple(subject_information['image_dim']), "Image size does not match the size in the data dictionary"
        
        logger.info(f"Exhale image size: {exhale_raw.GetSize()}")
        logger.info(f"Inhale image size: {inhale_raw.GetSize()}")
        
        # saving the nifti files
        logger.info(f"Saving the nifti files for subject {subject_name}. \n")
        sitk.WriteImage(exhale_raw, exhale_volume.replace('.img', '.nii.gz'))
        sitk.WriteImage(inhale_raw, inhale_volume.replace('.img', '.nii.gz'))

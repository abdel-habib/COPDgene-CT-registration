import sys
import argparse
import os
from glob import glob
import json
import SimpleITK as sitk

# importing utils and 
from utils.logger import logger, pprint
from utils.dataset import segment_lungs_and_remove_trachea
from enums.dtype import DataTypes


if __name__ == "__main__":
    # optional arguments from the command line 
    parser = argparse.ArgumentParser()

    parser.add_argument('--train_path', type=str, default='dataset/train', help='root dir for raw training data')

    # parse the arguments
    args = parser.parse_args()

    # check if the train_path exists
    if not os.path.exists(args.train_path):
        logger.error(f"Path {args.train_path} does not exist")
        sys.exit(1)

    # get the list of exhale and inhale files from the train_path
    logger.info(f"Reading nifti data from '{args.train_path}'")
    exhale_volumes = [path.replace('\\', '/') for path in sorted(glob(os.path.join(args.train_path, "***" , "*eBHCT.nii.gz"), recursive=True))]
    inhale_volumes = [path.replace('\\', '/') for path in sorted(glob(os.path.join(args.train_path, "***" , "*iBHCT.nii.gz"), recursive=True))]

    # log the number of exhale and inhale files
    logger.info(f"Found {len(exhale_volumes)} exhale volumes: ({[subject.split('/')[-2] for subject in exhale_volumes]})")
    logger.info(f"Found {len(inhale_volumes)} inhale volumes: ({[subject.split('/')[-2] for subject in inhale_volumes]})\n")
    pprint(exhale_volumes, inhale_volumes)
    print('\n')

    # read the data dictionary
    with open(os.path.join(args.train_path.replace("train", "", 1), 'description.json'), 'r') as json_file:
        dictionary = json.loads(json_file.read())

    # iterate over all of the nifti inhale and exhale volumes and segment the lungs
    for volume in exhale_volumes + inhale_volumes:
        # get the subject name and information
        subject_name = volume.split('/')[-2]
        subject_information = dictionary['train'][subject_name]

        logger.info(f"Segmenting {volume}")
        sitk_image = sitk.ReadImage(volume)
        np_image = sitk.GetArrayFromImage(sitk_image)

        # logs
        print(subject_information)
        print("sitk:\t\t", sitk_image.GetSize(), sitk_image.GetPixelIDTypeAsString(), sitk_image.GetOrigin(), sitk_image.GetSpacing())
        print("np:\t\t", np_image.shape, np_image.dtype)

        # segment the lungs
        if subject_name == 'copd2':
            # set a specific threshold to copd2
            threshold = 400
        else:
            threshold = 700 
        print("thresh:\t\t", threshold)

        _, _, _, lung_segmentation = \
            segment_lungs_and_remove_trachea(np_image, 
                                            threshold=threshold)
        
        lung_segmentation_sitk = sitk.GetImageFromArray(lung_segmentation)
        lung_segmentation_sitk.CopyInformation(sitk_image)

        # logs
        print("lung:\t\t", lung_segmentation.shape, lung_segmentation.dtype)
        print("lung_sitk:\t", lung_segmentation_sitk.GetSize(), lung_segmentation_sitk.GetPixelIDTypeAsString(), lung_segmentation_sitk.GetOrigin(), lung_segmentation_sitk.GetSpacing(), "\n")

        # save the lung segmentation
        sitk.WriteImage(lung_segmentation_sitk, volume.replace(".nii.gz", "_lung.nii.gz"))

    print("Segmentation complete!")



import argparse
import os
import numpy as np
import SimpleITK as sitk

from utils.logger import logger
from utils.filemanager import create_directory_if_not_exists, get_paths, check_paths
from utils.preprocess import bilateral_filter_3d, clahe_3d
from utils.dataset import segment_body, min_max_normalization

def export(args, sample_name, filename_full, final_processed_sitk):  
    '''
    Export the final processed image to the output folder.

    Args:
        args (argparse): arguments from the command line
        sample_name (str): sample name (e.g. copd1, copd2, ...)
        filename_full (str): filename full (e.g. copd1_eBHCT, copd1_iBHCT, ...)
        final_processed_sitk_int16 (sitk.Image): final processed image

    Returns:
        None
    '''  
    # cast the final processed image to sitk.int16
    final_processed_sitk_int16 = sitk.Cast(final_processed_sitk, sitk.sitkInt16)

    # save the final processed image
    logger.info(">> Saving the final processed image...")
    sample_output_path = os.path.join(args.exp_output, sample_name)
    create_directory_if_not_exists(sample_output_path)
    sitk.WriteImage(final_processed_sitk_int16, os.path.join(sample_output_path, f"{filename_full}.nii.gz"))

if __name__ == "__main__":
    # optional arguments from the command line 
    parser = argparse.ArgumentParser()

    parser.add_argument('--dataset_path', type=str, default='dataset/train', help='root dir for nifti data')
    parser.add_argument('--experiment_name', type=str, default='preprocessing1', help='experiment name')
    parser.add_argument('--output_path', type=str, default='dataset_processed', help='root dir for output scripts')

    # parse the arguments
    args = parser.parse_args()

    # get the split name from the dataset_path
    split_name = args.dataset_path.replace('\\', '/').split('/')[-1]

    # create experiment output
    args.exp_output = os.path.join(args.output_path, args.experiment_name, split_name)
    create_directory_if_not_exists(args.exp_output)

    # get the exhale and inhale volumes and segmentations
    exhale_volumes = get_paths(args, "eBHCT")
    inhale_volumes = get_paths(args, "iBHCT")

    check_paths(args, exhale_volumes, "exhale volumes")
    check_paths(args, inhale_volumes, "inhale volumes")

    # logs
    logger.warning("This script doesn't copy the landmarks, the lung masks (segmentation), or the dataset json to the output folder. Please copy them manually.")
    logger.info(f"Experiment name: {args.experiment_name}")
    logger.info(f"Split name: {split_name}")
    logger.info(f"Output path: {args.exp_output}")

    for sample_path in exhale_volumes + inhale_volumes:
        # defining the sample name and the file names
        sample_name = sample_path.split('/')[-1].split('_')[0] #copd1, copd2, ...
        filename_full = sample_path.split('/')[-1].split('.')[0] #copd1_eBHCT, copd1_iBHCT, ..

        logger.info(f"\nProcessing {sample_name} - {filename_full}")

        # read the sample
        sample_sitk     = sitk.ReadImage(sample_path)
        sample_image    = sitk.GetArrayFromImage(sample_sitk)

        # Get the minimum and maximum intensity values of the input image
        min_max_filter = sitk.MinimumMaximumImageFilter()
        min_max_filter.Execute(sample_sitk)

        original_min = min_max_filter.GetMinimum()
        original_max = min_max_filter.GetMaximum()

        # set a specific threshold to copd2
        if sample_name == 'copd2':
            threshold = 430
        else:
            threshold = 700

        print("thresh: ", threshold)

        # note that the gantry and black background are still present and we need to remove them.
        # segmenting the body and removing the gantry
        mask, labeled_mask, largest_masks, body_segmented = \
            segment_body(sample_image, threshold=threshold)
        
        # inverging the largest masks to focus on the body for being used as a mask
        largest_masks_sitk = sitk.GetImageFromArray(largest_masks)
        largest_masks_sitk.CopyInformation(sample_sitk)

        largest_masks_inverted_sitk = sitk.Not(largest_masks_sitk)
        largest_masks_inverted_image = sitk.GetArrayFromImage(largest_masks_inverted_sitk)

        # normalize the image using min-max normalization, excluding the gantry and black background using the largest mask that represents anything except the body
        logger.info(">> Normalizing using min-max...")
        normalized_image = min_max_normalization(sample_image, largest_masks_inverted_image).astype(np.int16) # 

        normalized_image_sitk = sitk.GetImageFromArray(normalized_image)
        normalized_image_sitk.CopyInformation(sample_sitk)

        # denoising the image using bilateral filter
        logger.info(">> Denoising using bilateral filter...")
        domain_sigma = 2.0
        range_sigma = 50.0 

        filtered_sitk = bilateral_filter_3d(normalized_image_sitk, domain_sigma, range_sigma)
        filtered_image = sitk.GetArrayFromImage(filtered_sitk)

        # contrast enhancment using adaptive histogram equalization
        logger.info(">> Contrast enhancement using CLAHE...")
        final_processed_sitk = clahe_3d(filtered_sitk, clip_limit=0.01)

        # export the final processed image to the output folder
        export(args, sample_name, filename_full, final_processed_sitk)









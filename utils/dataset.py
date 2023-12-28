import SimpleITK as sitk
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import binary_closing
from skimage import measure

def read_raw(
    binary_file_name,
    image_size,
    sitk_pixel_type,
    image_spacing=None,
    image_origin=None,
    big_endian=False,
):
    """
    Read a raw binary scalar image.

    Source: https://simpleitk.readthedocs.io/en/master/link_RawImageReading_docs.html

    Parameters
    ----------
    binary_file_name (str): Raw, binary image file content.
    image_size (tuple like): Size of image (e.g. [2048,2048])
    sitk_pixel_type (SimpleITK pixel type: Pixel type of data (e.g.
        sitk.sitkUInt16).
    image_spacing (tuple like): Optional image spacing, if none given assumed
        to be [1]*dim.
    image_origin (tuple like): Optional image origin, if none given assumed to
        be [0]*dim.
    big_endian (bool): Optional byte order indicator, if True big endian, else
        little endian.

    Returns
    -------
    SimpleITK image or None if fails.
    """

    pixel_dict = {
        sitk.sitkUInt8: "MET_UCHAR",
        sitk.sitkInt8: "MET_CHAR",
        sitk.sitkUInt16: "MET_USHORT",
        sitk.sitkInt16: "MET_SHORT",
        sitk.sitkUInt32: "MET_UINT",
        sitk.sitkInt32: "MET_INT",
        sitk.sitkUInt64: "MET_ULONG_LONG",
        sitk.sitkInt64: "MET_LONG_LONG",
        sitk.sitkFloat32: "MET_FLOAT",
        sitk.sitkFloat64: "MET_DOUBLE",
    }
    direction_cosine = [
        "1 0 0 1",
        "1 0 0 0 1 0 0 0 1",
        "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
    ]
    dim = len(image_size)
    header = [
        "ObjectType = Image\n".encode(),
        (f"NDims = {dim}\n").encode(),
        (
            "DimSize = " + " ".join([str(v) for v in image_size]) + "\n"
        ).encode(),
        (
            "ElementSpacing = "
            + (
                " ".join([str(v) for v in image_spacing])
                if image_spacing
                else " ".join(["1"] * dim)
            )
            + "\n"
        ).encode(),
        (
            "Offset = "
            + (
                " ".join([str(v) for v in image_origin])
                if image_origin
                else " ".join(["0"] * dim) + "\n"
            )
        ).encode(),
        ("TransformMatrix = " + direction_cosine[dim - 2] + "\n").encode(),
        ("ElementType = " + pixel_dict[sitk_pixel_type] + "\n").encode(),
        "BinaryData = True\n".encode(),
        ("BinaryDataByteOrderMSB = " + str(big_endian) + "\n").encode(),
        # ElementDataFile must be the last entry in the header
        (
            "ElementDataFile = " + os.path.abspath(binary_file_name) + "\n"
        ).encode(),
    ]
    fp = tempfile.NamedTemporaryFile(suffix=".mhd", delete=False)

    # print(header)

    # Not using the tempfile with a context manager and auto-delete
    # because on windows we can't open the file a second time for ReadImage.
    fp.writelines(header)
    fp.close()
    img = sitk.ReadImage(fp.name)
    os.remove(fp.name)
    return img

def convert_raw_to_nifti(
        dataset_dir: list, 
        output_dir: str,
        metadata: dict):
    '''
    Convert the dataset images from raw (.raw) to nifti (nii.gz) format and export it to a 
    given output directory. 

    Args:
        dataset_dir (list): list of paths to the dataset directories
        output_dir (str): path to the output directory
        metadata (dict): dictionary containing the metadata of the dataset

    Returns:
        None
    '''

    pass

def create_mask(volume, threshold = 700):
    '''
    Create a mask from a given volume using a given threshold.

    Args:
        volume (numpy array): volume to be masked
        threshold (int): threshold to be used for the masking

    Returns:
        numpy array: masked volume
    '''
    return np.where(volume <= threshold, 1, 0)

def label_regions(mask):
    '''
    Label connected components in a binary mask.

    Args:
        mask (numpy array): Binary mask.

    Returns:
        tuple: A tuple containing labeled mask and the number of labels.
    '''
    labeled_mask, num_labels = measure.label(mask, connectivity=2, return_num=True, background=0)
    return labeled_mask, num_labels

def get_largest_regions(labeled_mask, num_regions=2):
    '''
    Get the largest connected regions in a labeled mask.

    Args:
        labeled_mask (numpy array): Labeled mask.
        num_regions (int): Number of largest regions to retrieve.

    Returns:
        list: List of region properties for the largest regions.
    '''
    regions = measure.regionprops(labeled_mask)
    regions.sort(key=lambda x: x.area, reverse=True)
    regions = regions[:min(num_regions, len(regions))]
    # print([regions[i].axis_major_length for i in range(len(regions))])
    # print([regions[i].axis_minor_length for i in range(len(regions))])
    return regions

def create_masks(labeled_mask, regions):
    '''
    Create masks for specific regions in a labeled mask.

    Args:
        labeled_mask (numpy array): Labeled mask.
        regions (list): List of region properties for which masks need to be created.

    Returns:
        list: List of masks corresponding to the specified regions.
    '''
    masks = [labeled_mask == region.label for region in regions]
    return masks

def fill_holes_and_erode(mask, structure=(7, 7, 5)):
    '''
    Fill holes in a binary mask and perform erosion.

    Args:
        mask (numpy array): Binary mask.
        dilation_structure (tuple): Dilation structure for binary dilation.
        erosion_structure (tuple): Erosion structure for binary erosion.

    Returns:
        numpy array: Processed mask after filling holes and erosion.
    '''
    processed_mask = binary_closing(mask, structure=np.ones(structure))

    return processed_mask

def remove_trachea(largest_masks, get_largest_regions, create_masks):
    '''
    Remove the trachea from a set of largest masks with a shape (Slice, H, W).

    Args:
        largest_masks (numpy array): 3D array of largest masks.
        get_largest_regions (function): Function to get largest regions.
        create_masks (function): Function to create masks.

    Returns:
        numpy array: 3D array of masks with trachea removed.
    '''
    # Find bounding boxes for each region in the 3D mask
    labeled_mask_slices = np.array([label_regions(largest_masks[idx, :, :])[0] for idx in range(largest_masks.shape[0])])
    # labeled_mask_slices = np.transpose(labeled_mask_slices, (1, 2, 0))

    largest_regions_slices = [
        get_largest_regions(labeled_mask_slices[idx, :, :], num_regions=3)
        for idx in range(labeled_mask_slices.shape[0])
    ]

    largest_regions_masks = [
        # we filter the trachea by checking the difference between the major and minor axis length when there is only 1 region
        create_masks(labeled_mask_slices[idx, :, :], region)[0] if (len(region) == 1 and (abs(region[0].axis_major_length - region[0].axis_minor_length) > 30))

        # this handles the very first few slices with trachea that has a very small difference between the major and minor axis length
        else np.zeros_like(labeled_mask_slices[idx, :, :]) if (len(region) == 1 and (abs(region[0].axis_major_length - region[0].axis_minor_length) < 30)) 
        
        # remove the trachea if there are 3 regions, it will be the 3rd region as we sort by area (highest to lowest)
        else create_masks(labeled_mask_slices[idx, :, :], region)[0] + create_masks(labeled_mask_slices[idx, :, :], region)[1] if len(region) == 3 

        # when there are only 2 regions, we check the difference in the area (area of the first region has to be atleast 50 more than the second region) to indicate that it is a lung not a trachea
        # also check if the minor axis of the second region (trachea) is less than 100
        # this condition happens when both lungs are touching each other as a region, and trachea as another region
        else create_masks(labeled_mask_slices[idx, :, :], region)[0] if len(region) == 2 and (getattr(region[0], 'area') - getattr(region[1], 'area') > 50) and (region[1].axis_minor_length < 100) 

        # when there are only 2 regions, we combine them. This is after the previous condition is met (when only 2 lungs are detected)
        else create_masks(labeled_mask_slices[idx, :, :], region)[0] + create_masks(labeled_mask_slices[idx, :, :], region)[1] if len(region) == 2 

        else np.zeros_like(labeled_mask_slices[idx, :, :])
        for idx, region in enumerate(largest_regions_slices)
    ]
    # largest_regions_masks = np.transpose(largest_regions_masks, (1, 2, 0))

    return largest_regions_masks

def segment_lungs_and_remove_trachea(volume, threshold=700, structure=(7, 7, 5), fill_holes_before_trachea_removal=False):
    '''
    Segment lungs and remove trachea from a given 3D volume with shape (Slice, H, W). Note that this shape is a must for 
    the internal functions to compute as expected.

    Args:
        volume (numpy array): 3D volume shape (slice, H, W).
        threshold (int): Threshold for creating the initial mask.
        dilation_structure (tuple): Dilation structure for binary dilation.
        erosion_structure (tuple): Erosion structure for binary erosion.

    Returns:
        initial_mask (numpy array): Initial mask created from the volume.
        labeled_mask (numpy array): Labeled mask.
        largest_masks (numpy array): 3D array of largest masks.
        processed_mask_without_trachea (numpy array): 3D binary array of masks with trachea removed.
    '''
    # create a mask
    initial_mask = create_mask(volume, threshold=threshold)

    # Label connected components
    labeled_mask, _ = label_regions(initial_mask)

    # Get the largest three regions (two lungs and trachea)
    largest_regions = get_largest_regions(labeled_mask, num_regions=3)

    # Create masks for the largest three regions
    largest_masks = create_masks(labeled_mask, largest_regions)[1]

    # fill holes of the largest mask
    if fill_holes_before_trachea_removal:
        largest_masks = fill_holes_and_erode(largest_masks, structure=tuple([2*x for x in structure]))

    # remove the trachea
    largest_masks_without_trachea = remove_trachea(largest_masks, get_largest_regions, create_masks)

    # Exclude the trachea by subtracting it from the processed mask
    processed_mask_without_trachea = fill_holes_and_erode(largest_masks_without_trachea, structure=structure)

    return initial_mask, labeled_mask, largest_masks, processed_mask_without_trachea.astype(np.uint8)

def segment_body(image, threshold=700):
    '''
    Segment the body from a given 3D volume with shape (Slice, H, W). Note that this shape is a must for
    the internal functions to compute as expected.

    Args:
        image (numpy array): 3D volume shape (slice, H, W).
        threshold (int): Threshold for creating the initial mask.

    Returns:
        mask (numpy array): Initial mask created from the volume.
        labeled_mask (numpy array): Labeled mask.
        largest_masks (numpy array): 3D array of largest masks.
        body_segmented (numpy array): 3D binary array of masks with body segmented.

    '''
    mask = create_mask(image, threshold=threshold)
    labeled_mask, _ = label_regions(mask)
    largest_regions = get_largest_regions(labeled_mask, num_regions=3)
    largest_masks = create_masks(labeled_mask, largest_regions)[0]

    # to have zeros and ones instead of binary false and true
    largest_masks = largest_masks.astype(np.int8)

    body_segmented = np.zeros_like(image)
    body_segmented[largest_masks == 0] = image[largest_masks == 0]

    return mask, labeled_mask, largest_masks, body_segmented


def display_two_volumes(volume1, volume2, title1, title2, slice=70):
    '''
    Display two volumes side by side.

    Args:
        volume1 (numpy array): first volume to be displayed
        volume2 (numpy array): second volume to be displayed
        title1 (str): title of the first volume
        title2 (str): title of the second volume
        slice (int): slice to be displayed

    Returns:
        None
    '''
    plt.figure(figsize=(9, 6))

    plt.subplot(1, 2, 1)
    plt.imshow(volume1[slice, :, :], cmap='gray') 
    plt.title(title1)
    plt.axis('off')


    plt.subplot(1, 2, 2)
    plt.imshow(volume2[slice, :, :], cmap='gray') 
    plt.title(title2)
    plt.axis('off')

    plt.show()

def display_volumes(*volumes, **titles_and_slices):
    '''
    Display multiple volumes side by side.

    Args:
        volumes (tuple of numpy arrays): volumes to be displayed
        titles_and_slices (dict): titles and slices for each volume
        
    Returns:
        None
    '''
    num_volumes = len(volumes)
    
    plt.figure(figsize=(6 * num_volumes, 6))

    for i, volume in enumerate(volumes, start=1):
        title = titles_and_slices.get(f'title{i}', f'Title {i}')
        slice_val = titles_and_slices.get(f'slice{i}', 70)

        plt.subplot(1, num_volumes, i)
        plt.imshow(volume[slice_val, :, :], cmap='gray') #gray
        plt.title(title)
        plt.axis('off')

    plt.show()


def min_max_normalization(image, mask = None, max_value=None):
    '''
    Perform min-max normalization on a given image.

    Args:
        image ('np.array'): Input image to normalize.
        mask ('np.array'): Mask to be applied to the image.
        max_value ('float'): Maximum value for normalization.

    Returns:
        normalized_image ('np.array'): Min-max normalized image.
    '''

    if max_value is None:
        max_value = np.iinfo(image.dtype).max
        print(f"The maximum value for this volume {image.dtype} is: {max_value}")
    
    print("Using mask for normalization" if mask is not None else "Not using mask for normalization")

    # Ensure the image is a NumPy array for efficient calculations
    image = np.array(image)

    # Calculate the minimum and maximum pixel values
    min_value = np.min(image[mask == 1]) if mask is not None else np.min(image)
    max_actual = np.max(image[mask == 1]) if mask is not None else np.max(image)
    
    # Perform min-max normalization
    normalized_image = (image - min_value) / (max_actual - min_value) * max_value
    normalized_image = np.clip(normalized_image, 0, max_value)
    
    return normalized_image.astype(image.dtype)

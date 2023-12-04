import SimpleITK as sitk
import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt

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
    return np.where(volume > threshold, 1, 0)


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
    plt.imshow(volume1[:, :, slice], cmap='gray') 
    plt.title(title1)
    plt.axis('off')


    plt.subplot(1, 2, 2)
    plt.imshow(volume2[:, :, slice], cmap='gray') 
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
        plt.imshow(volume[:, :, slice_val], cmap='gray')
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

    # Ensure the image is a NumPy array for efficient calculations
    image = np.array(image)

    # Calculate the minimum and maximum pixel values
    min_value = np.min(image[mask == 1]) if mask is not None else np.min(image)
    max_actual = np.max(image[mask == 1]) if mask is not None else np.max(image)
    
    # Perform min-max normalization
    normalized_image = (image - min_value) / (max_actual - min_value) * max_value
    
    return normalized_image

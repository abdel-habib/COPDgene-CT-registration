import os
import SimpleITK as sitk
import numpy as np
from skimage import exposure

def anisotropic_diffusion_denoise_3d(input_volume, conductance_parameter, time_step, number_of_iterations):
    '''
    Denoise the input volume using anisotropic diffusion.

    Args:
        input_volume ('SimpleITK Image'): Input volume.
        conductance_parameter ('float'): Conductance parameter.
        time_step ('float'): Time step.
        number_of_iterations ('int'): Number of iterations.

    Returns:
        output_volume ('SimpleITK Image'): Denoised volume.

    '''
    # Convert the input volume to float
    input_volume_float = sitk.Cast(input_volume, sitk.sitkFloat32)

    anisotropic_diffusion = sitk.GradientAnisotropicDiffusionImageFilter()
    anisotropic_diffusion.SetConductanceParameter(conductance_parameter)
    anisotropic_diffusion.SetTimeStep(time_step)
    anisotropic_diffusion.SetNumberOfIterations(number_of_iterations)

    output_volume_float = anisotropic_diffusion.Execute(input_volume_float)
    output_volume = sitk.Cast(output_volume_float, sitk.sitkInt16)

    return output_volume

def bilateral_filter_3d(input_volume, domain_sigma, range_sigma):
    '''
    Apply bilateral filter to the input volume.

    Args:
        input_volume ('SimpleITK Image'): Input volume.
        domain_sigma ('float'): Domain sigma.
        range_sigma ('float'): Range sigma.

    Returns:
        output_volume ('SimpleITK Image'): Filtered volume.
    '''
    filtered_slices = []

    for z in range(input_volume.GetDepth()):
        # Get 2D slice
        input_slice = sitk.Extract(input_volume, (input_volume.GetWidth(), input_volume.GetHeight(), 1), (0, 0, z))

        # Apply bilateral filter to the 2D slice
        bilateral_filter = sitk.BilateralImageFilter()
        bilateral_filter.SetDomainSigma(domain_sigma)
        bilateral_filter.SetRangeSigma(range_sigma)
        output_slice = bilateral_filter.Execute(input_slice)

        # Append the filtered slice to the list
        filtered_slices.append(sitk.GetArrayFromImage(output_slice)[0]) # [0] to get the slice from the 3D volume

    # Convert the list of slices to a NumPy array
    filtered_slices_array = np.array(filtered_slices)
    output_volume = sitk.GetImageFromArray(filtered_slices_array)

    # Copy the information from the input volume to the output volume
    output_volume.CopyInformation(input_volume)

    return output_volume


def clahe_3d(input_volume, clip_limit=0.1):
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to a 3D image.
    
    Args:
        input_volume (SimpleITK Image): The input image.

    Returns:
        SimpleITK Image: The output image after applying CLAHE.
    """
    # Get the minimum and maximum intensity values of the input image
    min_max_filter = sitk.MinimumMaximumImageFilter()
    min_max_filter.Execute(input_volume)

    original_min = min_max_filter.GetMinimum()
    original_max = min_max_filter.GetMaximum()

    # Get the dimensions of the 3D volume
    size_x, size_y, size_z = input_volume.GetSize()

    # Determine kernel sizes in each dim relative to image shape
    kernel_size = (size_x // 5, size_y // 5, size_z // 2)

    # get the image from the input volume
    input_volume_image = sitk.GetArrayFromImage(input_volume)

    # Normalize intensity values to the range [0, 1]
    # input_volume_normalized = sitk.RescaleIntensity(input_volume_image, outputMinimum=0, outputMaximum=1)
    input_volume_normalized = exposure.rescale_intensity(input_volume_image, in_range='image', out_range=(0, 1))

    # Apply CLAHE to the normalized image
    input_volume_enhanced = exposure.equalize_adapthist(input_volume_normalized, kernel_size=kernel_size, clip_limit=clip_limit)

    # Rescale intensity values to the original range
    input_volume_rescaled = exposure.rescale_intensity(input_volume_enhanced, in_range='image', out_range=(original_min, original_max))

    # Convert the NumPy array to a SimpleITK image
    output_result = sitk.GetImageFromArray(input_volume_rescaled)
    output_result.CopyInformation(input_volume)

    return output_result
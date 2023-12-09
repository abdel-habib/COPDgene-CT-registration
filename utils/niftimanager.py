
import nibabel as nib
import matplotlib.pyplot as plt

def load_nifti(file_path):
        '''
        Load the NIfTI image and access the image data as a Numpy array.

        Args:
            file_path ('str'): Path to the NIfTI file.

        Returns:
            data_array ('np.array'): Numpy array representing the image data.
            nii_image: Loaded NIfTI image object.
        '''
        nii_image = nib.load(file_path)
        data_array = nii_image.get_fdata()

        return data_array, nii_image

def show_nifti(file_data, title, slice=25):
    '''
    Display a single slice from the NIfTI volume.

    Args:
        file_data ('np.array'): Numpy array representing the image data.
        title ('str'): Title for the plot.
        slice ('int'): Slice index to display.
    '''        
    plt.imshow(file_data[slice, :, :], cmap='gray')
    plt.title(title)
    # plt.colorbar()
    plt.axis('off')
    plt.show()
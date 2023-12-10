import numpy as np
import SimpleITK as sitk
from enum import Enum

class DataTypes(Enum):
    LANDMARK = np.int16
    RAW_DATA = sitk.sitkInt16
    MASK = np.uint8
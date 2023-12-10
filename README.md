###### Prepare the inhale keypoint file to match transformix requirements
`python prepare_keypoints_transformix.py --dataset_path "dataset/train" --keypoint_type "inhale"`

###### Parse raw files to nifti format
`python parse_raw.py --dataset_path "dataset/train"`

###### Segment the lung mask
`python segment.py --dataset_path "dataset/train"`
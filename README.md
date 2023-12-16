###### Prepare the inhale keypoint file to match transformix requirements
`python prepare_keypoints_transformix.py --dataset_path "dataset/train" --keypoint_type "inhale"`

###### Parse raw files to nifti format
`python parse_raw.py --dataset_path "dataset/train"`

###### Segment the lung mask
`python segment.py --dataset_path "dataset/train"`

###### Create elastix and transformix .bat file
`python .\create_script.py --experiment_name "elastix_None" --parameters_path "elastix-parameters/ParOurs" --use_masks`
or
`python .\create_script.py --experiment_name "elastix_None" --parameters_path "elastix-parameters/ParOurs/Parameter.affine.txt" --use_masks`

Inside the output folder of the experiment, you will find the command to call the created bat file.

###### To evaluate and create transformation points submission file
Use `--generate_report` when gt (exhale) points exist. This will create the transformation points file and log the results
`python evaluate_transformation.py --experiment_name "elastix_None" --reg_params_key "Parameter.affine+Parameter.bsplines" --generate_report --dataset_path "dataset\train"`

If the gt (exhale) points are not given, use the same command without `--generate_report` 
`python evaluate_transformation.py --experiment_name "elastix_None" --reg_params_key "Parameter.affine+Parameter.bsplines" --dataset_path "dataset\train"`

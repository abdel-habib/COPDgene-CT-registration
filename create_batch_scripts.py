from utils.elastix import excute_cmd
from utils.logger import logger

if __name__ == '__main__':
    # list down the parameters files to create a batch script for each
    parameters_base_path = 'elastix-parameters'

    single_parameters_to_script = [
        # Par0003
        f'{parameters_base_path}/Par0003/Par0003.affine.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R1-fg.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R1-ug.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R2-fg.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R2-ug.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R3-fg.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R3-ug.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R4-fg.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R4-ug.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R5-fg.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R6-ug.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R7-fg.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R7-ug.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R8-fg.txt',
        f'{parameters_base_path}/Par0003/Par0003.bs-R8-ug.txt',
        
        # Par0007
        f'{parameters_base_path}/Par0007/Parameters.MI.Coarse.Bspline_tuned.txt',
        f'{parameters_base_path}/Par0007/Parameters.MI.Fine.Bspline_tuned.txt',
        f'{parameters_base_path}/Par0007/Parameters.MI.RP.Bspline_tuned.txt',

        # Par0011
        f'{parameters_base_path}/Par0011/Parameters.Par0011.affine.txt',
        f'{parameters_base_path}/Par0011/Parameters.Par0011.bspline1_s.txt',
        f'{parameters_base_path}/Par0011/Parameters.Par0011.bspline2_s.txt',

        # Par0049
        f'{parameters_base_path}/Par0049/Par0049_stdT-advanced.txt',
        f'{parameters_base_path}/Par0049/Par0049_stdT2000itr.txt',
        f'{parameters_base_path}/Par0049/Par0049_stdTL-advanced.txt',
        f'{parameters_base_path}/Par0049/Par0049_stdTL.txt'
    ]

    # create a batch script for each parameters file
    for idx, param_path in enumerate(single_parameters_to_script):
        logger.info(f"[{idx+1}/{len(single_parameters_to_script)}] Creating batch script for {param_path}.")

        command = f'python create_script.py \
            --dataset_path "dataset_processed/Normalization+Bilateral+CLAHE/train" \
            --experiment_name "Normalization+Bilateral+CLAHE+UseMasks+SingleParamFile" \
            --parameters_path "{param_path}" \
            --use_masks'
        
        excute_cmd(command)
        

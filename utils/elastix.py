import subprocess
import os


def excute_cmd(command):
    '''
    Execute a command and check for success.

    Args:
        command ('str'): Command to execute.
    
    Returns:
        result ('str'): Output of the command if successful.
    '''
    # excute the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

    # Check the return code to see if the command was successful
    if result.returncode == 0:
        # print("Command executed successfully.")
        # print("Output:")
        return result.stdout
    else:
        print(f"Command failed with an error: {command}")
        print(result.stderr)
        return result.stderr

# Perform registration and label propagation
def register_elastix(fixed_path, 
                    moving_path, 
                    reg_params, 
                    create_dir_callback, 
                    excute_cmd_callback,
                    fMask = None):
    '''
    Perform image registration using elastix.

    Args:
        fixed_path ('str'): Path to the fixed image.
        moving_path ('str'): Path to the moving image.
        reg_params ('str'): Registration parameters for elastix.
        create_dir_callback ('function'): Callback function to create directories.
        excute_cmd_callback ('function'): Callback function to execute commands.
        fMask ('str'): Optional path to a mask file.

    Returns:
        None
    '''
    # Get the names of the fixed and moving images for the output directory, names without the file extensions
    reg_fixed_name  = fixed_path.replace("\\", "/").split("/")[-1].split(".")[0] # \\
    reg_moving_name = moving_path.replace("\\", "/").split("/")[-1].split(".")[0]

    # create output dir
    output_dir = f'output/images/output_{reg_fixed_name}/{reg_moving_name}'
    create_dir_callback(output_dir)

    # create elastix command line
    command_line = f'elastix -f "{fixed_path}" -m "{moving_path}" {reg_params} -out "{output_dir}"' if not fMask else \
                    f'elastix -f "{fixed_path}" -m "{moving_path}" -fMask {fMask} {reg_params} -out "{output_dir}"'

    # call elastix command
    excute_cmd_callback(command_line)

def label_propagation_transformix(
    fixed_path, 
    moving_path, 
    input_label, 
    transform_path, 
    replace_text_in_file_callback, 
    create_dir_callback, 
    excute_cmd_callback):
    '''
    Apply label propagation using transformix.

    Args:
        fixed_path ('str'): Path to the fixed image.
        moving_path ('str'): Path to the moving image.
        input_label ('str'): Path to the input label image.
        transform_path ('str'): Path to the transformation parameters.
        replace_text_in_file_callback ('function'): Callback function to replace text in a file.
        create_dir_callback ('function'): Callback function to create directories.
        excute_cmd_callback ('function'): Callback function to execute commands.

    Returns:
        None
    '''
    replace_text_in_file_callback(
        transform_path, 
        search_text = '(FinalBSplineInterpolationOrder 3)', 
        replacement_text =  '(FinalBSplineInterpolationOrder 0)')

    # Get the names of the fixed and moving images for the output directory, names without the file extensions
    reg_fixed_name  = fixed_path.replace("\\", "/").split("/")[-1].split(".")[0] 
    reg_moving_name = os.path.join(moving_path.replace("\\", "/").split("/")[0], moving_path.replace("\\", "/").split("/")[-1].split(".")[0])
        
    # create an output directory for the labels
    output_dir = f'output/labels/output_{reg_fixed_name}/{reg_moving_name}' # rem _float64

    # creates the output directory
    create_dir_callback(output_dir)
    
    # create transformix command line
    command_line = f'transformix -in "{input_label}" -tp "{transform_path}"  -out "{output_dir}"'
    
    # run transformix on all combinations
    excute_cmd_callback(command_line)

def control_points_transformix(
    fixed_path, 
    moving_path, 
    input_points,
    transform_path,
    replace_text_in_file_callback,
    create_dir_callback, 
    excute_cmd_callback
):
    replace_text_in_file_callback(
        transform_path, 
        search_text = '(FinalBSplineInterpolationOrder 3)', 
        replacement_text =  '(FinalBSplineInterpolationOrder 0)')
    
    # Get the names of the fixed and moving images for the output directory, names without the file extensions
    reg_fixed_name  = fixed_path.replace("\\", "/").split("/")[-1].split(".")[0] 
    reg_moving_name = os.path.join(moving_path.replace("\\", "/").split("/")[0], moving_path.replace("\\", "/").split("/")[-1].split(".")[0])

    # create an output directory for the labels
    output_dir = f'output/labels/output_{reg_fixed_name}/{reg_moving_name}' # rem _float64

    # creates the output directory
    create_dir_callback(output_dir)

    # create transformix command line
    command_line = f'transformix -def "{input_points}" -tp "{transform_path}"  -out "{output_dir}"'

    # run transformix on all combinations
    excute_cmd_callback(command_line)


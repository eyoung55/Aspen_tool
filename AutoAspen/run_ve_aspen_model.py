'''
This script calls the 2011 Aspen Ethanol Model APV10
as part of the Virtual Engineering workflow.
'''

# import argparse
import os
# from i_o import parse_config, save_simulation_results, plot_hist
# from utilities import extract_input_data, generate_input_data, simulate_using_aspen
from classes import Aspen, Excel
# from pythoncom import CoInitialize
# import win32com.client as win32

from vebio.Utilities import dict_to_yaml, yaml_to_dict

def run_ve_aspen_model(notebook_dir, params_filename, tea_options, verbose=True, dry_run=True):

    # Set the input and output files/directories
    aspenFile = os.path.abspath(tea_options['aspen_filename'])
    excelFile = os.path.abspath(tea_options['excel_filename'])

    outDir = 'output'
    os.makedirs(outDir, exist_ok = True)

    # ================================================================
    # Create Aspen Plus communicator
    # ================================================================
    print('Opening Aspen Plus model... ', end='')
    aspenModel = Aspen(aspenFile)
    print('Success!')

    # ================================================================
    # Write backup file with value updates/replacements
    # ================================================================
    # aspenPath: str, path in ASPEN tree
    # value: float or str, value to set
    # ifFortran: bool, whether it is a Fortran variable
    # ve_params['aspenPath'] = [value, ifFortran]

    path_to_input_file = os.path.join(notebook_dir, params_filename)
    tea_dict = yaml_to_dict(path_to_input_file)

    tea_replacements = {}
    tea_replacements['path/in/aspen/tree'] = [tea_dict['enzymatic_output']['rho_g'], False]
    tea_replacements['path/in/aspen/tree2'] = [tea_dict['enzymatic_output']['rho_x'], False]


    print('Changing values in model backup definition tree... ', end='')
    for key, val in tea_replacements.items():
        value = val[0]
        ifFortran = val[1]
        if not dry_run:
            aspenModel.set_value(key, value, ifFortran)
    print('Success!')

    # ================================================================
    # Run the Aspen Plus model
    # ================================================================
    print('Running Aspen Plus model... ', end='')
    aspenModel.run_model()
    print('Success!')

    # ================================================================
    # Save current model state
    # ================================================================
    print('Saving current model definition... ', end='')
    tmpFile = '%s/%s_bkup.bkp' % (outDir, tea_options['aspen_filename'].split('.')[0])
    aspenModel.save_model(tmpFile)
    print('Success!')

    # ================================================================
    # Create Excel communicator and run calculator
    # ================================================================

    print('Opening Excel calculator... ', end='')
    excelCalculator = Excel(excelFile)
    print('Success!')

    print('Running Excel analysis... ', end='')
    if not dry_run:
        excelCalculator.load_aspenModel(tmpFile)
        excelCalculator.run_macro('solvedcfror')
    print('Success!')

    # aspenModel.close()
    excelCalculator.close()


def main():

    # Ordinarily this would be set in the notebook
    notebook_dir = os.path.abspath('../../../')

    # Ordinarily this would be passed in from the notebook
    params_filename = 'tea_temp.yaml'

    # Ordinarily this would be set in the notebook via a widget collection
    # tea_options = widgetCollect()
    # tea_options = tea_options.export_widgets_to_dict()
    tea_options = {}
    tea_options['aspen_filename'] = 'DW1102A_AB.bkp'
    tea_options['excel_filename'] = 'DW1102A_2016UPDATES.xlsm'

    run_ve_aspen_model(notebook_dir, params_filename, tea_options)

if __name__ == "__main__":
    main()


'''
This script calls the an Aspen sugar model and excel calculation
as part of the Virtual Engineering workflow.
'''

import os
import numpy as np

from classes import Aspen, Excel
from vebio.Utilities import dict_to_yaml, yaml_to_dict


def _init_tea_replacements(enzyme_loading=10.0, glucose_conv=0.9630, xylose_conv=0.9881, arabinose_conv=0.9881):
    tea_replacements = {}

    max_digits = 4

    tea_replacements['enzyme_loading'] = [os.path.join('Data', 'Flowsheeting Options', 'Calculator', 'A400-ENZ',
                                          'Input', 'FORTRAN_EXEC', '#22'),
                                          np.round(enzyme_loading, max_digits), True]

    tea_replacements['glucose_conv'] = [os.path.join('Data', 'Blocks', 'A300', 'Data', 'Blocks', 'CEH', 'Data',
                                        'Flowsheeting Options', 'Calculator', 'CEH', 'Input', 'FORTRAN_EXEC', '#11'),
                                        np.round(glucose_conv, max_digits), True]

    tea_replacements['xylose_conv'] = [os.path.join('Data', 'Blocks', 'A300', 'Data', 'Blocks', 'CEH', 'Data',
                                       'Flowsheeting Options', 'Calculator', 'CEH', 'Input', 'FORTRAN_EXEC', '#12'),
                                       np.round(xylose_conv, max_digits), True]

    tea_replacements['arabinose_conv'] = [os.path.join('Data', 'Blocks', 'A300', 'Data', 'Blocks', 'CEH', 'Data',
                                          'Flowsheeting Options', 'Calculator', 'CEH', 'Input', 'FORTRAN_EXEC', '#13'),
                                          np.round(arabinose_conv, max_digits), True]

    return tea_replacements

def run_ve_aspen_model(aspenFile, notebook_dir, params_filename, tea_options, outDir):

    try:
        # ================================================================
        # Create Aspen Plus communicator
        # ================================================================
        print('Opening Aspen Plus model... ')
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

        tea_replacements = _init_tea_replacements(enzyme_loading=9.8)

        print('Changing values in model backup definition tree... ')
        for key, val in tea_replacements.items():
            path_to_value = val[0]
            value = val[1]
            ifFortran = val[2]
            aspenModel.set_value(path_to_value, value, ifFortran)
        print('Success!')

        # ================================================================
        # Run the Aspen Plus model
        # ================================================================
        print('Running Aspen Plus model... ')
        aspenModel.run_model()
        print('Success!')

        # ================================================================
        # Save current model state
        # ================================================================
        print('Saving current model definition... ')
        tmpFile = '%s/%s_bkup.bkp' % (outDir, tea_options['aspen_filename'].split('.')[0])
        aspenModel.save_model(tmpFile)
        print('Success!')

    finally:
        aspenModel.close()

    return tmpFile


def run_ve_excel_calc(excelFile, tmpFile):

    # ================================================================
    # Create Excel communicator and run calculator
    # ================================================================
    try:
        print('Opening Excel calculator... ')
        excelCalculator = Excel(excelFile)
        excelCalculator.load_aspenModel(tmpFile)
        print('Success!')

        power = excelCalculator.get_cell('OPEX', 'E40')
        print(f'Old Power: {power}')
        power += 10000
        excelCalculator.set_cell(power, 'OPEX', 'E40')
        power = excelCalculator.get_cell('OPEX', 'E40')
        print(f'New Power: {power}')

        print('Running Excel analysis... ')
        excelCalculator.run_macro('solvedcfror')
        print('Success!')
        
        mssp = excelCalculator.get_cell('DCFROR', 'B36')

    finally:
        excelCalculator.close()

    return mssp
    

def run_ve_tea(notebook_dir, params_filename, tea_options, verbose=True, dry_run=True):

    # Set the input and output files/directories
    aspenFile = os.path.abspath(tea_options['aspen_filename'])
    excelFile = os.path.abspath(tea_options['excel_filename'])

    outDir = 'output'
    os.makedirs(outDir, exist_ok = True)

    tmpFile = run_ve_aspen_model(aspenFile, notebook_dir, params_filename, tea_options, outDir)

    mssp = run_ve_excel_calc(excelFile, tmpFile)

    print(f'Selling price: {mssp}')


def main():

    # Ordinarily this would be set in the notebook
    notebook_dir = os.path.abspath('../../../')

    # Ordinarily this would be passed in from the notebook
    params_filename = 'tea_temp.yaml'

    # Ordinarily this would be set in the notebook via a widget collection
    # tea_options = widgetCollect()
    # tea_options = tea_options.export_widgets_to_dict()
    tea_options = {}
    tea_options['aspen_filename'] = 'bc1707a-sugars_CEH.bkp'
    tea_options['excel_filename'] = 've_bc1707a-sugars_CEH.xlsm'

    run_ve_tea(notebook_dir, params_filename, tea_options)


if __name__ == "__main__":
    main()

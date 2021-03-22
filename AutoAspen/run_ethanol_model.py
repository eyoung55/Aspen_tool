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


def main():

	# Set the input and output files/directories
	aspenFile = os.path.abspath('DW1102A_AB.bkp')
	excelFile = os.path.abspath('DW1102A_2016UPDATES.xlsm')

	outDir = 'ethanol_output'
	os.makedirs(outDir, exist_ok = True)

	# ================================================================
	# Create Aspen Plus and Excel communicators
	# ================================================================
	print('Opening Aspen Plus model... ', end='')
	aspenModel = Aspen(aspenFile)
	print('Success!')

	print('Opening Excel calculator... ', end='')
	excelModel = Excel(excelFile)
	print('Success!')

	# ================================================================
	# Write backup file with value updates/replacements
	# ================================================================
	# aspenPath: str, path in ASPEN tree
	# value: float or str, value to set
	# ifFortran: bool, whether it is a Fortran variable
	# ve_params['aspenPath'] = [value, ifFortran]
	ve_params = {}
	ve_params['path/in/aspen/tree'] = [0.75, False]
	ve_params['path/in/aspen/tree2'] = [0.01, False]

	DUMMY_OPERATION = True

	print('Changing values in model backup definition tree... ', end='')
	for key, value in ve_params.items():
		if not DUMMY_OPERATION:
			aspenModel.set_value(key, value[0], value[1])
		else:
			pass
	print('Success!')

	# ================================================================
	# Run the Aspen Plus model
	# ================================================================
	print('Running Aspen Plus model... ', end='')
	aspenModel.run_model()
	print('Success!')

	# ================================================================
	# Create Aspen Plus and Excel communicators
	# ================================================================
	print('Saving current model definition... ', end='')
	tmpFile = '%s/%s.bkp' % (outDir, 'temp_backup')
	aspenModel.save_model(tmpFile)
	print('Success!')

	# ================================================================
	# Create Aspen Plus and Excel communicators
	# ================================================================
	print('Running Excel analysis... ', end='')
	calculator.load_aspenModel(tmpFile)
	if not DUMMY_OPERATION:
		calculator.run_macro('solvedcfror')
	print('Success!')

	aspenModel.close()
	excelModel.close()


if __name__ == "__main__":
    main()


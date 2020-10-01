#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '8/27/2020'
__version__ = '1.0'


r'''
This script estimates response of output with respect to 2-3 Aspen variables

Example
python C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Scripts\response_AspenVars.py -o C:\Users\cwu\Desktop\Outputs\Aspen_automation\Results\Q4\enzyme_loading_and_deploy_and_solid_loading -c C:\Users\cwu\Desktop\Outputs\Aspen_automation\Data\Q4\enzyme_loading_and_deploy_and_solid_loading\resp_AspenVars_config.xlsx -a C:\Users\cwu\Desktop\Outputs\Aspen_automation\Data\Q4\enzyme_loading_and_deploy_and_solid_loading\PETase_Depoly_Base_v8.bkp -e C:\Users\cwu\Desktop\Outputs\Aspen_automation\Data\Q4\enzyme_loading_and_deploy_and_solid_loading\PETase_Depoly_Base_v8_corr.xlsm
'''


import argparse
import os
from i_o import parse_config, save_response_results, plot_aspenVar_or_nonAspenVar_response
from utilities import generate_input_data, response_using_aspen
from classes import Aspen, Excel




if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description = 'This script estimates response of output with respect to 2-3 variables in .xlsm')
	parser.add_argument('-o', '--outDir', type = str, required = True, help = 'output directory')
	parser.add_argument('-c', '--configFile', type = str, required = True, help = 'config file, .xlsx')
	parser.add_argument('-a', '--aspenFile', type = str, required = True, help = 'Aspen model file, .bkp')
	parser.add_argument('-e', '--calculatorFile', type = str, required = True, help = 'excel calculator file, .xlsm')
	args = parser.parse_args()
	
	outDir = args.outDir
	configFile = args.configFile
	aspenFile = args.aspenFile
	calculatorFile = args.calculatorFile
	
	os.makedirs(outDir, exist_ok = True)
	
	
	# parse inputs and outputs
	inputInfos, outputInfos = parse_config(configFile)
	
	inputData = generate_input_data(inputInfos)
	
	
	# run simulation with calculator
	try:
		aspenModel = Aspen(aspenFile)
		calculator = Excel(calculatorFile)
		
		simResults = response_using_aspen(aspenModel, calculator, inputData, outputInfos, outDir)
	
	finally:
		aspenModel.close()
		calculator.close()
	
	
	# plot results
	save_response_results(simResults, outDir)
	
	plot_aspenVar_or_nonAspenVar_response(simResults, outDir)



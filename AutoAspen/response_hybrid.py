#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '02/5/2020'
__version__ = '1.0'


r'''
This script estimates response of output with respect to 2 variables in .xlsm and Aspen

Example
python C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Scripts\response_hybrid.py -o C:\Users\cwu\Desktop\Outputs\Aspen_automation\Results\Sugars\resp_hybrid -c C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Sugars\resp_hybrid_config.xlsx -a C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Sugars\BC1707A_sugars_V10_mod-lite.bkp -e C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Sugars\BC1707A_sugars_V10_mod.xlsm
'''




import argparse
import os
from i_o import parse_config, save_response_results, plot_hybrid_response
from utilities import generate_input_data, response_using_aspen_and_calculator_2D
from classes import Aspen, Excel




if __name__ == '__main__':

	parser = argparse.ArgumentParser(description = 'This script estimates response of output with respect to 2 variables in .xlsm and Aspen')
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
	
	
	# run simulation with Aspen and calculator
	try:
		aspenModel = Aspen(aspenFile)
		calculator = Excel(calculatorFile)
		
		simResults = response_using_aspen_and_calculator_2D(aspenModel, calculator, inputData, outputInfos, outDir)
	
	finally:
		aspenModel.close()
		calculator.close()
	
	
	# plot results
	save_response_results(simResults, outDir)
	
	plot_hybrid_response(simResults, outDir)
	
	
	
	















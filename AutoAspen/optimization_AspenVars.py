#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '10/25/2019'
__version__ = '1.0'


r'''
This script optimizes outputs and get optimal inputs

Example
python C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Scripts\optimization_AspenVars.py -o C:\Users\cwu\Desktop\Outputs\Aspen_automation\Results\Sugars\opt -c C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Sugars\opt_config.xlsx -a C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Sugars\BC1707A_sugars_V10_mod-lite.bkp -e C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Sugars\BC1707A_sugars_V10_mod.xlsm
'''




import argparse
import os
from i_o import parse_config, save_optimization_results, plot_optimization_results
from classes import Aspen, Excel
from utilities import optimize




if __name__ == '__main__':

	parser = argparse.ArgumentParser(description = 'This script optimizes outputs and get optimal inputs')
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
	
	
	# optimize
	try:
		aspenModel = Aspen(aspenFile)
		calculator = Excel(calculatorFile)
	
		solutions = optimize(inputInfos, outputInfos, aspenModel, calculator, outDir)
	
	finally:
		aspenModel.close()
		calculator.close()
	
	
	# save and plot results 
	save_optimization_results(solutions, outDir)
	
	if solutions.columns.size == 3:   # plot if 2 inputs
		plot_optimization_results(outDir, solutions.index.tolist(), solutions.columns.tolist()[1:], outDir)
	
	
	
	
	






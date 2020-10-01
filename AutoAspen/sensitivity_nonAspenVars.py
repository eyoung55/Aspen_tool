#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '09/08/2020'
__version__ = '1.2'


r'''
This script estimates sensitivity of outputs with respect to varied variables in .xlsm, values are enumerated (discrete) or given in range (continuous)

Example
python C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Scripts\sensitivity_nonAspenVars.py -o C:\Users\cwu\Desktop\Outputs\Aspen_automation\Results\Sugars\sens_nonAspenVars -c C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Sugars\sens_nonAspenVars_config.xlsx -a C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Sugars\BC1707A_sugars_V10_mod-lite.bkp -e C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Sugars\BC1707A_sugars_V10_mod.xlsm -n 100
'''



import argparse
import os
from i_o import parse_config, save_simulation_results, plot_hist
from utilities import extract_input_data, generate_input_data, simulate_using_calculator
from classes import Aspen, Excel




if __name__ == '__main__':

	parser = argparse.ArgumentParser(description = 'This script estimates outputs according to varied variables in .xlsm, values are enumerated (discrete) or given in range (continuous)')
	parser.add_argument('-o', '--outDir', type = str, required = True, help = 'output directory')
	parser.add_argument('-c', '--configFile', type = str, required = True, help = 'config file, .xlsx')
	parser.add_argument('-a', '--aspenFile', type = str, required = True, help = 'Aspen model file, .bkp')
	parser.add_argument('-e', '--calculatorFile', type = str, required = True, help = 'excel calculator file, .xlsm')
	parser.add_argument('-d', '--varType', type = str, required = True, choices = ['dis', 'con'], help = 'input data type in config file, "dis" for discrete, "con" for continuous')
	parser.add_argument('-n', '--nruns', type = int, required = False, help = '# of simulation runs')
	args = parser.parse_args()
	
	outDir = args.outDir
	configFile = args.configFile
	aspenFile = args.aspenFile
	calculatorFile = args.calculatorFile
	varType = args.varType
	nruns = args.nruns
	
	os.makedirs(outDir, exist_ok = True)
	
	
	# parse inputs and outputs
	inputInfos, outputInfos = parse_config(configFile)
	
	if varType == 'dis':
		inputData = extract_input_data(inputInfos)
	else:
		inputData = generate_input_data(inputInfos)
	
	
	# run simulation with calculator
	try:
		aspenModel = Aspen(aspenFile)
		calculator = Excel(calculatorFile)
	
		simResults = simulate_using_calculator(aspenModel, calculator, inputData, outputInfos, nruns)
	
	finally:
		aspenModel.close()
		calculator.close()
	
	
	# save and plot results
	save_simulation_results(simResults, outDir)
	
	plot_hist(simResults, outputInfos[['Output', 'Unit']], outDir)
	
	
	
	
	
	
	
	



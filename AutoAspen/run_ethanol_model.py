'''
This script calls the 2011 Aspen Ethanol Model APV10
as part of the Virtual Engineering workflow.
'''

# import argparse
import os
# from i_o import parse_config, save_simulation_results, plot_hist
# from utilities import extract_input_data, generate_input_data, simulate_using_aspen
# from classes import Aspen, Excel
# from pythoncom import CoInitialize
import win32com.client as win32

def main():

	aspenFile = os.path.abspath('DW1102A_AB.bkp')
	outDir = 'ethanol_output'

	os.makedirs(outDir, exist_ok = True)


	# CoInitialize()
	aspen = win32.Dispatch('Apwn.Document')
	aspen.InitFromArchive2(aspenFile)

	# simResults = simulate_using_aspen(aspenModel
	COM.close()

if __name__ == "__main__":
    main()

# if __name__ == '__main__':

# 	# parser = argparse.ArgumentParser(description = 'This script estimates outputs according to varied variables in Aspen, values are enumerated (discrete) or given in range (continuous)')
# 	# parser.add_argument('-o', '--outDir', type = str, required = True, help = 'output directory')
# 	# parser.add_argument('-c', '--configFile', type = str, required = True, help = 'config file, .xlsx')
# 	# parser.add_argument('-a', '--aspenFile', type = str, required = True, help = 'Aspen model file, .bkp')
# 	# parser.add_argument('-e', '--calculatorFile', type = str, required = True, help = 'excel calculator file, .xlsm')
# 	# parser.add_argument('-d', '--varType', type = str, required = True, choices = ['dis', 'con'], help = 'input data type in config file, "dis" for discrete, "con" for continuous')
# 	# parser.add_argument('-n', '--nruns', type = int, required = False, help = '# of simulation runs')
# 	# args = parser.parse_args()
	
# 	outDir = args.outDir
# 	configFile = args.configFile
# 	aspenFile = args.aspenFile
# 	calculatorFile = args.calculatorFile
# 	varType = args.varType
# 	nruns = args.nruns
	
# 	os.makedirs(outDir, exist_ok = True)


# 	# parse inputs and outputs
# 	inputInfos, outputInfos = parse_config(configFile)
	
# 	if varType == 'dis':
# 		inputData = extract_input_data(inputInfos)
# 	else:
# 		inputData = generate_input_data(inputInfos)
	
	
# 	# run simulation with Aspen
# 	try:
# 		aspenModel = Aspen(aspenFile)
# 		calculator = Excel(calculatorFile)

# 		simResults = simulate_using_aspen(aspenModel, calculator, inputData, outputInfos, outDir, nruns)
	
# 	finally:
# 		aspenModel.close()
# 		calculator.close()

	
# 	# save and plot results
# 	save_simulation_results(simResults, outDir)
	
# 	plot_hist(simResults, outputInfos[['Output', 'Unit']], outDir)
	







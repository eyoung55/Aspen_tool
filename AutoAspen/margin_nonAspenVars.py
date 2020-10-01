#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '03/04/2020'
__version__ = '1.0'


r'''
This script calculates the margin of two models and facilitate comparison 

Example
python C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Scripts\margin_nonAspenVars.py -o C:\Users\cwu\Desktop\Outputs\Aspen_automation\Results\Q2\Corn_sugar_ethanol\without_rin -c C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Q2\Corn_sugar_ethanol\mar_nonAspenVars_config.xlsx -a sugar::C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Q2\Corn_sugar_ethanol\sugar\Corn_dry_mill_USDA_2008_(v10)_2002B.bkp,ethanol::C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Q2\Corn_sugar_ethanol\ethanol\LT1302A-corn_dry_mill_USDA_2008_v18_AspenV10_ZH.bkp -e sugar::C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Q2\Corn_sugar_ethanol\sugar\USDA_corn_dry_mill_DCFROR_2016$_SugarOnly.xlsm,ethanol::C:\Share_GoogleDrive\NREL\Software\Aspen_automation\Data\Q2\Corn_sugar_ethanol\ethanol\USDA_corn_dry_mill_DCFROR_2016$_with_corn_oil_updated_costs.xlsm -m sugar::C:\Users\cwu\Desktop\Outputs\Aspen_automation\Results\Q2\Corn_sugar_ethanol\sugar_price.tsv,ethanol::C:\Users\cwu\Desktop\Outputs\Aspen_automation\Results\Q2\Corn_sugar_ethanol\ethanol_price.tsv -p no -r C:\Users\cwu\Desktop\Outputs\Aspen_automation\Results\Q2\Corn_sugar_ethanol\rin_price.tsv
'''



import argparse
import os
from i_o import parse_config, save_margins, save_total_margins, plot_margins, plot_total_margins
from utilities import calculate_margin




if __name__ == '__main__':

	parser = argparse.ArgumentParser(description = 'This script calculates the margin of two models and facilitate comparison')
	parser.add_argument('-o', '--outDir', type = str, required = True, help = 'output directory')
	parser.add_argument('-c', '--configFile', type = str, required = True, help = 'config file, .xlsx')
	parser.add_argument('-a', '--aspenFiles', type = str, required = True, help = 'Aspen model files, in format of "modelname1::path1,modelname2::path2"')
	parser.add_argument('-e', '--calculatorFiles', type = str, required = True, help = 'excel calculator files, in format of "modelname1::path1,modelname2::path2"')
	parser.add_argument('-m', '--marketPriceFiles', type = str, required = True, help = 'market price files, in format of "modelname1::path1,modelname2::path2"')
	parser.add_argument('-p', '--capital', type = str, required = True, help = 'whether to include the capital investment, "yes" or "no"')
	parser.add_argument('-r', '--rinPriceFile', type = str, required = False, help = 'rin price file, None if no subtractor rin price')
	parser.add_argument('-d', '--credits', type = str, required = True, help = 'whether to include the by-product credits in sugar model, "yes" or "no"')
	args = parser.parse_args()
	
	outDir = args.outDir
	configFile = args.configFile
	aspenFiles = args.aspenFiles
	calculatorFiles = args.calculatorFiles
	marketPriceFiles = args.marketPriceFiles
	capital = args.capital
	rinPriceFile = args.rinPriceFile
	credits = args.credits
	
	os.makedirs(outDir, exist_ok = True)
	
	
	# parse inputs and outputs
	inputInfos, outputInfos = parse_config(configFile)
	
	aspenFiles = dict([aspenFile.split('::') for aspenFile in aspenFiles.split(',')])
	calculatorFiles = dict([calculatorFile.split('::') for calculatorFile in calculatorFiles.split(',')])
	marketPriceFiles = dict([priceFile.split('::') for priceFile in marketPriceFiles.split(',')])
		
	
	# calculate margin
	margins, totalMargins = calculate_margin(inputInfos, outputInfos, aspenFiles, calculatorFiles, marketPriceFiles, rinPriceFile, capital, credits)
	
	
	# save and plot results
	save_margins(margins, outDir)
	save_total_margins(totalMargins, outDir)
	
	plot_margins(margins, outDir)
	plot_total_margins(totalMargins, outDir)
	
	
	
	
	
	
	
	
	
	
	
	
	
	


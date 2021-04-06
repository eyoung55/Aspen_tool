#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '8/26/2020'
__version__ = '1.3'


import os
import re
import numpy as np
import pandas as pd
from pandas import IndexSlice as idx
from numpy.random import uniform, normal, choice
from scipy.stats import alpha, beta, triang, pareto
from pybobyqa import solve
from classes import Scaler
from logging import INFO, basicConfig
from classes import Aspen, Excel


def generate_distribution(distName, size, *params):
	'''
	Parameters
	distName: str, distribution name
	size: int, size of generated distribution
	params: lst, 
			lb,ub for 'uniform'; 
			lb,ub for 'linspace'; 
			mean,sd for 'normal'; 
			a,loc,scale for 'alpha';
			a,b,loc,scale for 'beta';
			c,loc,scale for 'triangular';
			b,loc,scale for 'pareto';
	
	Returns
	distValues: array, generated distribution
	'''
	
	if distName == 'uniform':
		lb, ub = params
		distValues = uniform(lb, ub, size)
	
	elif distName == 'linspace':
		lb, ub = params
		distValues = np.linspace(lb, ub, size)
	
	elif distName == 'normal':
		mean, sd = params
		distValues =  normal(mean, sd, size)
		
	else:
		if distName == 'alpha':
			dist = alpha
		
		elif distName == 'beta':
			dist = beta
		
		elif distName == 'triangular':
			dist = triang
		
		elif distName == 'pareto':
			dist = pareto
		
		*shapeParams, loc, scale = params
		distValues = dist.rvs(*shapeParams, loc = loc, scale = scale, size = size)


	return distValues


def generate_input_data(inputInfos):
	'''
	columns ['Distribution', 'Parameters', 'Size'] transformed into ['Data']
	
	Parameters
	inputInfos: df, input infos for 
	sensitivity_nonAspenVars_con, columns are ['Input', 'Location', 'Distribution', 'Parameters', 'Size'];
	sensitivity_AspenVars_con, columns are ['Input', 'Path', 'Fortran', 'Distribution', 'Parameters', 'Size'];
	response_hybrid, columns are ['Input', 'Unit', 'Location', 'Fortran', 'Distribution', 'Parameters', 'Size'];
	response_nonAspenVars, columns are ['Input', 'Unit', 'Location', 'Distribution', 'Parameters', 'Size'];
	response_AspenVars, columns are ['Input', 'Unit', 'Location', 'Fortran', 'Distribution', 'Parameters', 'Size']
	
	Returns
	inputData: df, input data for 
	sensitivity_nonAspenVars_con, columns are ['Input', 'Location', 'Data'];
	sensitivity_AspenVars_con, columns are ['Input', 'Path', 'Fortran', 'Data'];
	response_hybrid, columns are ['Input', 'Unit', 'Location', 'Fortran', 'Data'];
	response_nonAspenVars, columns are ['Input', 'Unit', 'Location', 'Data']
	response_AspenVars, columns are ['Input', 'Unit', 'Location', 'Fortran', 'Data']
	'''
	
	inputData = inputInfos.copy()
	inputData['Data'] = np.nan
	inputData = inputData.astype(object)
	
	for _, row in inputData.iterrows():
	
		distName, params, size = row[['Distribution', 'Parameters', 'Size']]
		params = list(map(float, params.split(',')))
		size = int(size)
		
		row['Data'] = generate_distribution(distName, size, *params)
		
	inputData.drop(columns = ['Distribution', 'Parameters', 'Size'], inplace = True)
	
	
	return inputData	


def extract_input_data(inputInfos):
	'''
	column ['Values'] transformed into ['Data']
	
	Parameters
	inputInfos: df, input infos 
	for sensitivity_AspenVars_dis, columns are ['Input', 'Path', 'Fortran', 'Values']
	or for sensitivity_nonAspenVars_dis, columns are ['Input', 'Location', 'Values']
	
	Returns
	inputData: df, input data 
	for sensitivity_AspenVars_dis, columns are ['Input', 'Path', 'Fortran', 'Data']
	or for sensitivity_nonAspenVars_dis, columns are ['Input', 'Location', 'Data']
	'''
	
	inputData = inputInfos.copy()
	inputData['Data'] = np.nan
	inputData = inputData.astype(object)
	
	for input, row in inputData.iterrows():
		row['Data'] = np.array(list(map(float, inputInfos.loc[input, 'Values'].split(','))))
	
	inputData.drop(columns = ['Values'], axis = 1)
	
	
	return inputData
	
	
def simulate_using_calculator(aspenModel, calculator, inputData, outputInfos, nruns = None):
	'''
	Parameters
	aspenModel: instance of Aspen class
	calculator: instance of Excel class
	inputData: df, input data for sensitivity_nonAspenVars, columns are ['Input', 'Location', 'Data']
	outputInfos: df, output infos, columns are ['Output', 'Unit', 'Location']
	nruns: int or None, # of runs, if None, nruns will be the size of each Data cell 
	
	Returns
	outputData: df, colunms are output variables, index are runs
	'''
	
	# setting
	inputSettings = inputData.copy()
	inputSettings[['Sheet', 'Cell']] = inputSettings['Location'].str.split('!', expand = True)
	
	if nruns:
		inputSettings['Choice'] = inputSettings.apply(lambda r: choice(r['Data'], size = nruns, replace = False), axis = 1)
	else:
		inputSettings['Choice'] = inputSettings['Data']
		nruns = inputSettings.loc[0, 'Choice'].size
	
	outputSettings = outputInfos.copy()
	outputSettings[['Sheet', 'Cell']] = outputSettings['Location'].str.split('!', expand = True)
	
	
	# simulation
	outputData = pd.DataFrame(index = range(nruns), columns = outputSettings['Output'])
	for i in range(nruns):
		
		# set calculator variable
		for _, row in inputSettings.iterrows():
			calculator.set_cell(row['Choice'][i], row['Sheet'], loc = row['Cell'])
		
		# run excel calculator
		calculator.load_aspenModel(aspenModel.file)
		calculator.run_macro('solvedcfror')
		
		
		for _, row in outputSettings.iterrows():
			outputData.loc[i, row['Output']] = calculator.get_cell(row['Sheet'], loc = row['Cell'])
	
	outputData = outputData.astype(np.float)
	
	
	return outputData
	
	
def simulate_using_aspen(aspenModel, calculator, inputData, outputInfos, outDir, nruns = None):
	'''
	Parameters
	aspenModel: instance of Aspen class
	calculator: instance of Excel class
	inputData: df, input data for sensitivity_AspenVars, columns are ['Input', 'Path', 'Fortran', 'Data']
	outputInfos: df, output infos, columns are ['Output', 'Unit', 'Location']
	nruns: int or None, # of runs
	outDir: str, output directory
	
	Returns
	outputData: df, colunms are output variables, index are runs
	'''
	
	tmpDir = outDir + '/tmp'
	os.makedirs(tmpDir, exist_ok = True)
	
	
	# setting
	inputSettings = inputData.copy()
	
	if nruns:
		inputSettings['Choice'] = inputSettings.apply(lambda r: choice(r['Data'], size = nruns, replace = False), axis = 1)
	else:
		inputSettings['Choice'] = inputSettings['Data']
		nruns = inputSettings.loc[0, 'Choice'].size
	
	outputSettings = outputInfos.copy()
	outputSettings[['Sheet', 'Cell']] = outputSettings['Location'].str.split('!', expand = True)
	
	
	# simulation
	outputData = pd.DataFrame(index = range(nruns), columns = outputSettings['Output'])
	count = 0
	for i in range(nruns):
		
		# set ASPEN model variables
		for _, row in inputSettings.iterrows():
			_, path, ifFortran = row[['Input', 'Path', 'Fortran']]
			
			aspenModel.set_value(path, row['Choice'][i], bool(ifFortran))
	
		# run ASPEN model
		aspenModel.run_model()
		
		count += 1
		tmpFile = '%s/%s.bkp' % (tmpDir, count)
		aspenModel.save_model(tmpFile)
		
		# run excel calculator
		calculator.load_aspenModel(tmpFile)
		calculator.run_macro('solvedcfror')
		
		
		for _, row in outputSettings.iterrows():
			outputData.loc[i, row['Output']] = calculator.get_cell(row['Sheet'], loc = row['Cell'])
		
	outputData = outputData.astype(np.float)
	
	
	return outputData
		

def response_using_calculator(aspenModel, calculator, inputData, outputInfos):
	'''
	Parameters
	aspenModel: instance of Aspen class
	calculator: instance of Excel class
	inputData: df, input data for sensitivity_AspenVars, columns are ['Input', 'Unit', 'Location', 'Data']
	outputInfos: df, output infos, columns are ['Output', 'Unit', 'Location']
	
	Returns
	simResults: dict, keys are 'output+unit', values are df,
	for 2 input variables, index are 1st var values, columns are 2nd var values, index.name is '1stVar+unit,2ndVar+unit'
	for 3 input variables, index are 1st var values, columns are multiIndex with 2nd and 3rd var values, index.name is '1stVar+unit,2ndVar+unit,3rdVar+unit'
	'''
	
	# setting
	inputSettings = inputData.copy()
	inputSettings[['Sheet', 'Cell']] = inputSettings['Location'].str.split('!', expand = True)
	inputSettings['Unit'].fillna('', inplace = True)
	
	outputSettings = outputInfos.copy()
	outputSettings[['Sheet', 'Cell']] = outputSettings['Location'].str.split('!', expand = True)
	outputSettings['Unit'].fillna('', inplace = True)
	
	# simulation
	simResults = {}
	for _, row in outputSettings.iterrows():
		outputID = row['Output'] + ' (%s)' % row['Unit']
		
		if inputSettings.shape[0] == 2:
			outputData = pd.DataFrame(index = inputSettings.loc[0, 'Data'], columns = inputSettings.loc[1, 'Data'])
		elif inputSettings.shape[0] == 3:
			mutiIdx = pd.MultiIndex.from_product([inputSettings.loc[1, 'Data'], inputSettings.loc[2, 'Data']])
			outputData = pd.DataFrame(index = inputSettings.loc[0, 'Data'], columns = mutiIdx)
		else:
			raise ValueError('Only 2-3 input variables are acceptable')
			
		outputData.index.name = ','.join(inputSettings['Input'] + ' (' + inputSettings['Unit'] + ')')
		
		simResults[outputID] = outputData
		
	for var1value in inputSettings.loc[0, 'Data']:
		var1sheet, var1cell = inputSettings.loc[0, ['Sheet', 'Cell']]
		calculator.set_cell(var1value, var1sheet, loc = var1cell)
		
		for var2value in inputSettings.loc[1, 'Data']:
			var2sheet, var2cell = inputSettings.loc[1, ['Sheet', 'Cell']]
			calculator.set_cell(var2value, var2sheet, loc = var2cell)
		
			if inputSettings.shape[0] == 3:
				for k in range(inputSettings.loc[2, 'Data'].size):
					var3value = inputSettings.loc[2, 'Data'][k]
					var3sheet, var3cell = inputSettings.loc[2, ['Sheet', 'Cell']]
					calculator.set_cell(var3value, var3sheet, loc = var3cell)
			
					calculator.load_aspenModel(aspenModel.file)
					calculator.run_macro('solvedcfror')
					
					for _, row in outputSettings.iterrows():
						outputID = row['Output'] + ' (%s)' % row['Unit']
						simResults[outputID].loc[idx[var1value], idx[var2value, var3value]] = \
						calculator.get_cell(row['Sheet'], loc = row['Cell'])
			
			else:
				calculator.load_aspenModel(aspenModel.file)
				calculator.run_macro('solvedcfror')
				
				for _, row in outputSettings.iterrows():
					outputID = row['Output'] + ' (%s)' % row['Unit']
					simResults[outputID].loc[var1value, var2value] = calculator.get_cell(row['Sheet'], loc = row['Cell'])
			
	
	return simResults
			
			
def response_using_aspen(aspenModel, calculator, inputData, outputInfos, outDir):
	'''
	Parameters
	aspenModel: instance of Aspen class
	calculator: instance of Excel class
	inputData: df, input data for sensitivity_AspenVars, columns are ['Input', 'Unit', 'Location', 'Fortran', 'Data']
	outputInfos: df, output infos, columns are ['Output', 'Unit', 'Location']
	outDir: str, output directory
	
	Returns
	simResults: dict, keys are 'output+unit', values are df,
	for 2 input variables, index are 1st var values, columns are 2nd var values, index.name is '1stVar+unit,2ndVar+unit'
	for 3 input variables, index are 1st var values, columns are multiIndex with 2nd and 3rd var values, index.name is '1stVar+unit,2ndVar+unit,3rdVar+unit'
	'''
	
	tmpDir = outDir + '/tmp'
	os.makedirs(tmpDir, exist_ok = True)
	
	# setting
	inputSettings = inputData.copy()
	inputSettings['Unit'].fillna('', inplace = True)
	
	outputSettings = outputInfos.copy()
	outputSettings[['Sheet', 'Cell']] = outputSettings['Location'].str.split('!', expand = True)
	outputSettings['Unit'].fillna('', inplace = True)
	
	# simulation
	simResults = {}
	for _, row in outputSettings.iterrows():
		outputID = row['Output'] + ' (%s)' % row['Unit']
		
		if inputSettings.shape[0] == 2:
			outputData = pd.DataFrame(index = inputSettings.loc[0, 'Data'], columns = inputSettings.loc[1, 'Data'])
		elif inputSettings.shape[0] == 3:
			mutiIdx = pd.MultiIndex.from_product([inputSettings.loc[1, 'Data'], inputSettings.loc[2, 'Data']])
			outputData = pd.DataFrame(index = inputSettings.loc[0, 'Data'], columns = mutiIdx)
		else:
			raise ValueError('Only 2-3 input variables are acceptable')
			
		outputData.index.name = ','.join(inputSettings['Input'] + ' (' + inputSettings['Unit'] + ')')
		
		simResults[outputID] = outputData
	
	count = 0
	for var1value in inputSettings.loc[0, 'Data']:
		var1path, var1ifFortran = inputSettings.loc[0, ['Location', 'Fortran']]
		aspenModel.set_value(var1path, var1value, bool(var1ifFortran))
		
		for var2value in inputSettings.loc[1, 'Data']:
			var2path, var2ifFortran = inputSettings.loc[1, ['Location', 'Fortran']]
			aspenModel.set_value(var2path, var2value, bool(var2ifFortran))
			
			if inputSettings.shape[0] == 3:
				for var3value in inputSettings.loc[2, 'Data']:
					var3path, var3ifFortran = inputSettings.loc[2, ['Location', 'Fortran']]
					aspenModel.set_value(var3path, var3value, bool(var3ifFortran))
					
					aspenModel.run_model()
					
					count += 1
					tmpFile = '%s/%s.bkp' % (tmpDir, count)
					aspenModel.save_model(tmpFile)
					
					calculator.load_aspenModel(tmpFile)
					calculator.run_macro('solvedcfror')
					
					for _, row in outputSettings.iterrows():
						outputID = row['Output'] + ' (%s)' % row['Unit']
						simResults[outputID].loc[idx[var1value], idx[var2value, var3value]] = \
						calculator.get_cell(row['Sheet'], loc = row['Cell'])
			
			else:
				aspenModel.run_model()
		
				count += 1
				tmpFile = '%s/%s.bkp' % (tmpDir, count)
				aspenModel.save_model(tmpFile)
				
				calculator.load_aspenModel(tmpFile)
				calculator.run_macro('solvedcfror')
		
				for _, row in outputSettings.iterrows():
					outputID = row['Output'] + ' (%s)' % row['Unit']
					simResults[outputID].loc[var1value, var2value] = calculator.get_cell(row['Sheet'], loc = row['Cell'])
	
	return simResults


def response_using_aspen_and_calculator_2D(aspenModel, calculator, inputData, outputInfos, outDir):
	'''
	Parameters
	aspenModel: instance of Aspen class
	calculator: instance of Excel class
	inputData: df, input data for sensitivity_AspenVars, columns are ['Input', 'Unit', 'Location', 'Fortran', 'Data']
	outputInfos: df, output infos, columns are ['Output', 'Unit', 'Location']
	outDir: str, output directory
	
	Returns
	simResults: dict, keys are 'output+unit', values are df, index are aspenVar values, columns are nonaspenVar values, index.name is 'nonaspenVar+unit,aspenVar+unit'
	'''
	
	tmpDir = outDir + '/tmp'
	os.makedirs(tmpDir, exist_ok = True)
	
	
	# setting
	if re.search(r'\\', inputData['Location'][0]):
		aspenVar, nonaspenVar = inputData['Input']
	else:
		nonaspenVar, aspenVar = inputData['Input']
	
	nonaspenVarValues, nonaspenVarUnit = inputData.loc[inputData['Input'] == nonaspenVar, ['Data', 'Unit']].squeeze()
	nonaspenVarUnit = '' if nonaspenVarUnit is np.nan else nonaspenVarUnit
	aspenVarValues, aspenVarUnit = inputData.loc[inputData['Input'] == aspenVar, ['Data', 'Unit']].squeeze()
	aspenVarUnit = '' if aspenVarUnit is np.nan else aspenVarUnit
	
	aspenPath, ifFortran = inputData.loc[inputData['Input'] == aspenVar, ['Location', 'Fortran']].squeeze()
	excelSheet, excelCell = inputData.loc[inputData['Input'] == nonaspenVar, 'Location'].str.split('!', expand = True).squeeze()

	outputSettings = outputInfos.copy()
	outputSettings[['Sheet', 'Cell']] = outputSettings['Location'].str.split('!', expand = True)
	outputSettings['Unit'].fillna('', inplace = True)
	
	
	# simulation
	simResults = {}
	for _, row in outputSettings.iterrows():
		outputID = row['Output'] + ' (%s)' % row['Unit']
		
		outputData = pd.DataFrame(0, index = aspenVarValues, columns = nonaspenVarValues)
		nonaspenVarID = nonaspenVar + (' (%s)' % nonaspenVarUnit if nonaspenVarUnit else '')
		aspenVarID = aspenVar + (' (%s)' % aspenVarUnit if aspenVarUnit else '')
		outputData.index.name = nonaspenVarID + ',' + aspenVarID
		
		simResults[outputID] = outputData
	
	count = 0
	for i in range(aspenVarValues.size):
	
		# set ASPEN model variable
		aspenVarValue = aspenVarValues[i]
		aspenModel.set_value(aspenPath, aspenVarValue, bool(ifFortran))
		
		# run ASPEN model
		aspenModel.run_model()

		count += 1
		tmpFile = '%s/%s.bkp' % (tmpDir, count)
		aspenModel.save_model(tmpFile)
		
		for j in range(nonaspenVarValues.size):
			
			# set calculator variable
			nonaspenVarValue = nonaspenVarValues[j]
			calculator.set_cell(nonaspenVarValue, excelSheet, loc = excelCell)
			
			# run excel calculator
			calculator.load_aspenModel(tmpFile)
			calculator.run_macro('solvedcfror')
			
			
			for _, row in outputSettings.iterrows():
				outputID = row['Output'] + ' (%s)' % row['Unit']
				simResults[outputID].iloc[i, j] = calculator.get_cell(row['Sheet'], loc = row['Cell'])
	
		
	return simResults	


def optimize(inputInfos, outputInfos, aspenModel, calculator, outDir):	
	'''
	Parameters
	inputInfos: df, input infos for optimization, columns are ['Input', 'Path', 'Range', 'Fortran']
	outputInfos: df, output infos, columns are ['Output', 'Unit', 'Location']
	aspenModel: instance of Aspen class
	calculator: instance of Excel class
	outDir: str, output directory
	
	Returns
	solutions: df, index are outputs, index are ['Objective'] + inputs
	'''
	
	tmpDir = outDir + '/tmp'
	os.makedirs(tmpDir, exist_ok = True)
	
	
	## setting
	inputSettings = inputInfos.copy()
	inputSettings[['LB', 'UB']] = inputSettings['Range'].str.split(',', expand = True).astype(np.float)
	
	outputSettings = outputInfos.copy()
	outputSettings[['Sheet', 'Cell']] = outputSettings['Location'].str.split('!', expand = True)
			
	
	## optimization
	lb = inputSettings['LB'].values
	ub = inputSettings['UB'].values
	
	nvars = inputSettings.shape[0]
	x0 = uniform(low = lb, high = ub, size = nvars)
	
	rhoend = 0.001   #!
	maxfun = 100   #!

				
	solutions = pd.DataFrame(columns = ['Objective'] + inputSettings['Input'].tolist())
	for idx, row in outputSettings.iterrows():
		output, sheet, cell = row[['Output', 'Sheet', 'Cell']]
		
		count = 0
		def f(x, aspenModel, calculator, inputSettings, tmpDir):
			
			# set ASPEN model variables
			for idx, row in inputSettings.iterrows():
				input, path, ifFortran = row[['Input', 'Path', 'Fortran']]
				
				aspenModel.set_value(path, x[idx], bool(ifFortran))
				
			# run ASPEN model
			aspenModel.run_model()
			
			nonlocal count
			count += 1
			tmpFile = '%s/%s.bkp' % (tmpDir, count)
			aspenModel.save_model(tmpFile)
			
			# run excel calculator
			calculator.load_aspenModel(tmpFile)
			
			calculator.run_macro('solvedcfror')
			
			res = np.float(calculator.get_cell(sheet, loc = cell))
			
			return res	
		
		
		basicConfig(filename = '%s/%s_opt.log' % (outDir, output), level = INFO, format = '%(message)s', filemode = 'w')
		
		res = solve(f, x0, args = (aspenModel, calculator, inputSettings, tmpDir), bounds = (lb, ub), rhoend = rhoend, maxfun = maxfun, scaling_within_bounds = True)
	
		solutions.loc[output, :] = [res.f] + res.x.tolist()
		
		
	return solutions	

	
def calculate_margin(inputInfos, outputInfos, aspenFiles, calculatorFiles, marketPriceFiles, rinPriceFile, capital, credits):
	'''
	Parameters
	inputInfos: df, input infos for optimization, columns are ['Model', 'Input', 'Location', 'InputPath']
	outputInfos: df, output infos, columns are ['Model', 'Output', 'Unit', 'Location'] 
	aspenFiles: dict, keys are model names, values are aspen model path
	calculatorFiles: dict, keys are model names, values are calculator path
	marketPriceFiles: dict, keys are model names, values are market price file path
	rinPriceFile: str or None, rin price file, None if no subtractor rin price
	capital: str, whether to include the capital investment
	credits: str, whether to include the by-product credits in sugar model
	
	Returns
	margins: dict, keys are model names, values are df (index are time, columns are ['output (unit)', 'market price (unit)', 'margin (unit)'])
	totalMargins: df, index are time, columns are models
	'''
	
	margins = {}
	totalMargins = {}
	for model in inputInfos['Model'].unique():
		if model is np.nan: continue
		
		inputInfo = inputInfos[inputInfos['Model'] == model]
		inputInfo.index = range(inputInfo.shape[0])
		
		inputData = pd.DataFrame(index = inputInfo.index, columns = ['Input', 'Location', 'Data'], dtype = object)
		for i, (input, location, inputPath) in inputInfo[['Input', 'Location', 'InputPath']].iterrows():
			inputData.loc[i, :] = [input, location, pd.read_csv(inputPath, sep = '\t', index_col = 0).values.reshape(-1)]
			
		if capital == 'no':
			inputData.loc[inputData.shape[0], :] = ['Capital', 'DCFROR!B18', np.zeros(inputData.loc[0, 'Data'].size)]
			
		if credits == 'no' and model == 'sugar':
			inputData.loc[inputData.shape[0], :] = ['Credits', 'OPEX!I48', np.zeros(inputData.loc[0, 'Data'].size)]
			
		
		outputInfo = outputInfos.loc[outputInfos['Model'] == model, ['Output', 'Unit', 'Location']]
		outputInfo.index = [0]   # index start from 0
		output, unit = outputInfo.loc[0, :][['Output', 'Unit']]
		
		###
		if output == 'MESP':
			outputInfo.loc[1, :] = ['Production', 'gal/yr', 'OPEX!B18']
		elif output == 'MSSP':
			outputInfo.loc[1, :] = ['Production', 'kg/yr', 'OPEX!B17']
		###
		
		
		aspenFile = aspenFiles[model]
		calculatorFile = calculatorFiles[model]
		
		
		aspenModel = Aspen(aspenFile)
		calculator = Excel(calculatorFile)

		simResults = simulate_using_calculator(aspenModel, calculator, inputData, outputInfo)
		
		aspenModel.close()
		calculator.close()
		
		
		priceFile = marketPriceFiles[model]
		marketPrices = pd.read_csv(priceFile, sep = '\t', index_col = 0)
		
		data = pd.DataFrame(index = marketPrices.index)
		if rinPriceFile:
			rinPrice = pd.read_csv(rinPriceFile, sep = '\t', index_col = 0).values.reshape(-1)
			data['%s (%s)' % (output, unit)] = simResults[output].values - rinPrice
		else:	
			data['%s (%s)' % (output, unit)] = simResults[output].values
		data['market price (%s)' % unit] = marketPrices
		data['margin (%s)' % unit] = data['market price (%s)' % unit] - data['%s (%s)' % (output, unit)]
		margins[model] = data
		
		###
		totalMargin = data['margin (%s)' % unit].values * simResults['Production'].values
		if output == 'MESP':
			totalMargin = totalMargin / 52
		elif output == 'MSSP':
			totalMargin = totalMargin / 52 * 2.2045
		totalMargins[model] = totalMargin
		
	totalMargins = pd.DataFrame(totalMargins, index = marketPrices.index)	
	###
	
	return margins, totalMargins
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	


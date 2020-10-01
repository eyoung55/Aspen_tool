#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '8/26/2020'
__version__ = '1.3'


import re
import numpy as np
import pandas as pd
from pandas import IndexSlice as idx
from itertools import product
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import warnings
warnings.filterwarnings("ignore")


def parse_config(configFile):
	'''
	Parameters
	configFile: str, config file
	
	Returns
	inputs: df, index are inputs, columns are 
			['Input', 'Location', 'Distribution', 'Parameters', 'Size'] for sensitivity_nonAspenVars_con
			['Input', 'Location', 'Values'] for sensitivity_nonAspenVars_dis
			['Input', 'Path', 'Fortran', 'Distribution', 'Parameters', 'Size'] for sensitivity_AspenVars_con
			['Input', 'Path', 'Fortran', 'Values'] for sensitivity_AspenVars_dis
			['Input', 'Path', 'Range', 'Fortran'] for optimization_AspenVars
			['Input', 'Unit', 'Location', 'Fortran', 'Distribution', 'Parameters', 'Size'] for response_hybrid
			['Input', 'Unit', 'Location', 'Distribution', 'Parameters', 'Size'] for response_nonAspenVars
			['Input', 'Unit', 'Location', 'Fortran', 'Distribution', 'Parameters', 'Size'] for response_AspenVars
	outputs: df, index are outputs, columns are ['Output', 'Unit', 'Location']
	'''
	
	config = pd.read_excel(configFile, sheet_name = ['Inputs', 'Outputs'])   # don't see # as comment because # could appear in Aspen path of Fortran variables
	
	inputs = config['Inputs'].dropna(how = 'all')
	outputs = config['Outputs'].dropna(how = 'all')
	
	
	return inputs, outputs
	
	
def save_simulation_results(results, outDir):
	'''
	Parameters
	results: df, colunms are output variables, index are runs
	outDir: str, output directory
	'''
	
	results.to_csv(outDir + '/sim_results.tsv', sep = '\t', index = False)
	
	
def plot_hist(data, units, outDir):
	'''
	Parameters
	data: df, columns are outputs to plot, index are runs
	units: df, columns are ['Output', 'Unit']
	outDir: str, output directory
	'''
	
	units = units.set_index('Output')['Unit']
	
	for output, outputData in data.items():
		
		#sns.set()
		fig, ax1 = plt.subplots()
		sns.distplot(outputData, rug = True, kde = False, hist = True, ax = ax1)
		ax1.set_xlabel('%s (%s)' % (output, units[output]))
		ax1.set_ylabel('Count')
		
		#sns.set(style = 'white')
		ax2 = ax1.twinx()
		sns.distplot(outputData, rug = True, kde = True, hist = False, ax = ax2)   # if plot kde, y axis can not be Count
		ax2.set_yticks([])
		ax2.spines['left'].set_visible(False)
		ax2.spines['right'].set_visible(False)
		ax2.spines['top'].set_visible(False)
		ax2.spines['bottom'].set_visible(False)
		
		fig.savefig('%s/%s.jpg' % (outDir, output), dpi = 300, bbox_inches = 'tight')   
	
	
def save_optimization_results(results, outDir):
	'''
	Parameters
	results: df, index are outputs, columns are ['Objective'] + inputs
	outDir: str, output directory
	'''
	
	results.to_csv(outDir + '/opt_results.tsv', sep = '\t')
	
	
def read_log(logFile, objName, varNames):
	'''
	Parameters:
	logFile: str, log file of pybobyqa
	objName: str, objective name
	varNames: lst, variable names
	
	Returns:
	points: df, columns are f, x, y, index are data points
	'''
	
	points = []
	with open(logFile) as f:
		for line in f:
		
			if re.match(r'^Function eval', line):
				f_str, xy_str = re.search(r'f = (.+) at x = \[(.+)\]', line).groups()
				xy_str = xy_str.strip().split()
				fxy_float = list(map(float, [f_str] + xy_str))
	
				points.append(fxy_float)
	
	points = pd.DataFrame(points, columns = [objName] + varNames)
	

	return points


def plot_3D_1(data, outDir):
	'''
	Parameters
	data: df, columns are f, x, y, index are data points
	outDir: str, output directory
	'''

	fig = plt.figure()
	ax = fig.add_subplot(111, projection = '3d')
	
	zLabel, xLabel, yLabel = data.columns
	
	ax.scatter(data[xLabel], data[yLabel], data[zLabel], c = data[zLabel])
	
	ax.set_xlabel(xLabel)
	ax.set_ylabel(yLabel)
	ax.set_zlabel(zLabel, labelpad = 15)
	ax.tick_params(axis = 'z', which = 'major', pad = 10, labelsize = 8)
	ax.tick_params(axis = 'both', labelsize = 8)
		
	fig.savefig('%s/%s_%s+%s.jpg' % (outDir, zLabel, xLabel, yLabel), dpi = 300, bbox_inches = 'tight')	
	

def plot_optimization_results(logDir, outputs, inputs, outDir):
	'''
	Parameters
	logDir: str, directory of log file
	outputs: lst, output objectives
	inputs: lst, input variables
	outDir: str, output directory
	'''
	
	for output in outputs:
		
		points = read_log('%s/%s_opt.log' % (logDir, output), output, inputs)
	
		plot_3D_1(points, outDir)
	
	
def save_response_results(simResults, outDir):
	'''
	Parameters
	Parameters
	simResults: dict, keys are outputs+unit, values are df, index are aspenVarValues, columns are nonaspenVarValues, index.name is nonaspenVar+unit,aspenVar+unit
	outDir: str, output directory
	'''
	
	for output, data in simResults.items():
		
		data.to_csv('%s/%s_res_results.tsv' % (outDir, output.split()[0]), sep = '\t')
	
	
def plot_hybrid_response(simResults, outDir):	
	'''
	Parameters
	simResults: dict, keys are outputs+unit, values are df, index are aspenVarValues, columns are nonaspenVarValues, 
	            index.name is nonaspenVar+unit,aspenVar+unit
				nonaspenVar in x axis, aspenVar in y axis
	outDir: str, output directory
	'''
	
	for zLabel, data in simResults.items():
		
		xLabel, yLabel = data.index.name.split(',')
		x = data.columns.astype(np.float)
		y = data.index.astype(np.float)
		X, Y = np.meshgrid(x, y)
		Z = data.values
		
		
		plt.figure()
		
		ctf = plt.contourf(X, Y, Z, 50, cmap = plt.cm.get_cmap('RdBu').reversed())
		
		plt.xlabel(xLabel)
		plt.ylabel(yLabel)
		
		cbar = plt.colorbar(ctf)
		cbar.set_label(zLabel, labelpad = 15, rotation = 270)
		
		if Z.max() - Z.min() > 0.001:	
			ct = plt.contour(X, Y, Z, ctf.levels[1::6], colors = 'dimgray', linewidths = 1, linestyles ='dashed')
			plt.clabel(ct, ctf.levels[1::6], inline = True, fontsize = 7, colors = 'k')
		
		plt.savefig('%s/%s_contour.jpg' % (outDir, zLabel.split()[0]), dpi = 300, bbox_inches = 'tight')
		

def plot_contour(output, data, outDir, suffix = ''):	
	'''
	Parameters
	output: str, in format of 'outputID (unit)'
	data: df, index are var1 values, columns are var2 values, index.name is in format of 'var1 (unit),var2 (unit)'
		  var1 in x axis, var2 in y axis 
	outDir: str, output directory
	'''
	
	xLabel, yLabel = data.index.name.split(',')
	x = data.index.astype(np.float)
	y = data.columns.astype(np.float)
	X, Y = np.meshgrid(x, y)
	Z = data.T.values   #!
	
	
	plt.figure()
	
	ctf = plt.contourf(X, Y, Z, 50, cmap = plt.cm.get_cmap('RdBu').reversed())
	
	plt.xlabel(xLabel)
	plt.ylabel(yLabel)
	
	cbar = plt.colorbar(ctf)
	cbar.set_label(output, labelpad = 15, rotation = 270)
	
	if Z.max() - Z.min() > 0.001:	
		ct = plt.contour(X, Y, Z, ctf.levels[1::6], colors = 'dimgray', linewidths = 1, linestyles ='dashed')
		plt.clabel(ct, ctf.levels[1::6], inline = True, fontsize = 7, colors = 'k')
	
	plt.savefig('%s/%s_contour%s.jpg' % (outDir, output.split()[0], '_'+suffix if suffix else ''), 
                dpi = 300, bbox_inches = 'tight')
		
		
def plot_3D_2(output, data, outDir):
	'''
	Parameters
	output: str, in format of 'outputID (unit)'
	data: df, index are var1 values, columns are multiIndex with 2nd and 3rd var values, 
		  index.name is in format of 'var1 (unit),var2 (unit),var3 (unit)'
	outDir: str, output directory
	'''
	
	xLabel, yLabel, zLabel = data.index.name.split(',')
	
	var1 = data.index
	var2 = data.columns.levels[0]
	var3 = data.columns.levels[1]

	xyz = np.array(list(product(var1, var2, var3)))
	x, y, z = xyz[:,0], xyz[:,1], xyz[:,2] 
	values = [data.loc[idx[i], idx[j, k]] for i, j, k in zip(x, y, z)]

	
	ax = plt.subplot(111, projection = '3d')
	
	splot = ax.scatter(x, y, z, s = 50, c = values, cmap = plt.cm.get_cmap('RdBu').reversed())
	
	ax.set_xlabel(xLabel)
	ax.set_ylabel(yLabel)
	ax.set_zlabel(zLabel)
	
	cbar = plt.colorbar(splot, pad = 0.08)
	cbar.set_label(output, labelpad = 15, rotation = 270)
	
	plt.savefig('%s/%s_3D.jpg' % (outDir, output.split()[0]), dpi = 300, bbox_inches = 'tight')
	
	
def plot_aspenVar_or_nonAspenVar_response(simResults, outDir):
	'''
	Parameters
	simResults: dict, keys are 'output+unit', values are df,
	for 2 input variables, index are 1st var values, columns are 2nd var values, index.name is '1stVar+unit,2ndVar+unit'
	for 2 input variables, index are 1st var values, columns are multiIndex with 2nd and 3rd var values, index.name is '1stVar+unit,2ndVar+unit,3rdVar+unit'
	outDir: str, output directory
	'''
	
	for output, data in simResults.items():
		
		if isinstance(data.columns, pd.MultiIndex):
			
			# plot 3D
			plot_3D_2(output, data, outDir)
			
			# plot three contours
			xLabel, yLabel, zLabel = data.index.name.split(',')
			
			var1 = data.index
			var2 = data.columns.levels[0]
			var3 = data.columns.levels[1]
			
			var1mid = var1[var1.size//2]
			var2mid = var2[var2.size//2]
			var3mid = var3[var3.size//2]
			
			data12 = data.loc[idx[:], idx[:, var3mid]].copy()
			data12.columns = data12.columns.levels[0]
			data12.index.name = ','.join([xLabel, yLabel])
			
			data13 = data.loc[idx[:], idx[var2mid, :]].copy()
			data13.columns = data13.columns.levels[1]
			data13.index.name = ','.join([xLabel, zLabel])
			
			data23 = data.loc[idx[var1mid], idx[:, :]].copy().unstack()
			data23.index.name = ','.join([yLabel, zLabel])
			
			plot_contour(output, data12, outDir, '%s+%s' % (xLabel, yLabel))
			plot_contour(output, data13, outDir, '%s+%s' % (xLabel, zLabel))
			plot_contour(output, data23, outDir, '%s+%s' % (yLabel, zLabel))
			
		else:
			plot_contour(output, data, outDir)
	
	
def save_margins(margins, outDir):
	'''
	Parameters
	margins: dict, keys are model names, values are df (index are time, columns are ['output (unit)', 'market price (unit)', 'margin (unit)'])
	outDir: str, output directory
	'''
	
	for model, margin in margins.items():
		margin.to_csv('%s/%s_margins.tsv' % (outDir, model), sep = '\t')
	
	
def save_total_margins(totalMargins, outDir):
	'''
	Parameters
	totalMargins: df, index are time, columns are models
	outDir: str, output directory
	'''
	
	totalMargins.to_csv('%s/total_margins.tsv' % outDir, sep = '\t')
	
	
def plot_margins(margins, outDir):	
	'''
	Parameters
	margins: dict, keys are model names, values are df (index are time, columns are ['output (unit)', 'market price (unit)', 'margin (unit)'])
	outDir: str, output directory
	'''
	
	fig, axs = plt.subplots(2, 1, sharex=True)
	
	for i, model in enumerate(margins.keys()):
		
		t = margins[model].index
		mxsp = margins[model].iloc[:, 0]
		marketPrice = margins[model].iloc[:, 1]
		
		axs[i].plot(t, mxsp, label = mxsp.name)
		axs[i].plot(t, marketPrice, label = marketPrice.name)
		
		axs[i].fill_between(t, mxsp, marketPrice, where = marketPrice > mxsp, alpha = 0.5)
		
		axs[i].plot(t, np.zeros(mxsp.size), color = 'gray', linestyle='--', alpha = 0.7)
		
		x = np.arange(t.size)
		axs[i].set_xticks(x)
		axs[i].set_xticklabels(t, size = 5, rotation = 90)
		axs[i].set_ylabel(model)
		
		axs[i].legend(loc = 'center', bbox_to_anchor = (1.2, 0.6))
	
	fig.savefig('%s/margins_plot.jpg' % outDir, dpi = 300, bbox_inches = 'tight')
	
	
def plot_total_margins(totalMargins, outDir):
	'''
	Parameters
	totalMargins: df, index are time, columns are models
	outDir: str, output directory
	'''
	
	t = totalMargins.index
	model1, model2 = totalMargins.columns
	data1 = totalMargins[model1]
	data2 = totalMargins[model2]
	
	
	fig, ax = plt.subplots()
	
	ax.plot(t, data1, label = model1)
	ax.plot(t, data2, label = model2)
	
	ax.fill_between(t, data1, data2, where = data1 > data2, alpha = 0.5)
	ax.fill_between(t, data1, data2, where = data1 < data2, alpha = 0.5)
	
	ax.plot(t, np.zeros(data1.size), color = 'gray', linestyle='--', alpha = 0.7)
	
	x = np.arange(t.size)
	ax.set_xticks(x)
	ax.set_xticklabels(t, size = 5, rotation = 90)
	ax.set_ylabel('total margin ($)')
	
	ax.legend(loc = 'center', bbox_to_anchor = (1.15, 0.5))
	
	fig.savefig('%s/total_margins_plot.jpg' % outDir, dpi = 300, bbox_inches = 'tight')
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	

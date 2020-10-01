#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '09/01/2020'
__version__ = '1.0'


r'''
This script identifies the distribution of a continuous variable by fitting to the following unimodal distributions: "alpha", "beta", "triangular", "normal", "gamma" and "pareto"

Example
python C:\Users\cwu\Desktop\Software\Aspen_automation\Scripts\identify_distribution.py -o C:\Users\cwu\Desktop\Software\Aspen_automation\Results\Q4\Monte_Carlo_feedstock -i C:\Users\cwu\Desktop\Software\Aspen_automation\Data\Q4\feedstock\Historical_PET_Bale_Prices.xlsx
'''




import argparse
import os
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import kstest
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")




if __name__ == '__main__':

	parser = argparse.ArgumentParser(description = 'This script identify the distribution of a continuous variable by fitting to the following unimodal distributions: "alpha", "beta", "triangular", "normal", "gamma" and "pareto"')
	parser.add_argument('-o', '--outDir', type = str, required = True, help = 'output directory')
	parser.add_argument('-i', '--inVarFile', type = str, required = True, help = '.xlsx file of input variable')
	args = parser.parse_args()
	
	outDir = args.outDir
	inVarFile = args.inVarFile
	
	os.makedirs(outDir, exist_ok = True)
	
	
	### read input variable
	data = pd.read_excel(inVarFile, header = 0, index_col = 0, squeeze = True)
	data = data*2000/100 + 0.19*2000   ###! $/dry ton
	
	
	### identify distribution
	distNames = ['alpha', 'gamma', 'beta', 'triang', 'norm', 'pareto']
	#['alpha', 'anglit', 'arcsine', 'beta', 'betaprime', 'bradford', 'burr', 'cauchy', 'chi', 'chi2', 'cosine', 'dgamma', 'dweibull', 'erlang', 'expon', 'exponweib', 'exponpow', 'f', 'fatiguelife', 'fisk', 'foldcauchy', 'foldnorm', 'frechet_r', 'frechet_l', 'genlogistic', 'genpareto', 'genexpon', 'genextreme', 'gausshyper', 'gamma', 'gengamma', 'genhalflogistic', 'gilbrat', 'gompertz', 'gumbel_r', 'gumbel_l', 'halfcauchy', 'halflogistic', 'halfnorm', 'hypsecant', 'invgamma', 'invgauss', 'invweibull', 'johnsonsb', 'johnsonsu', 'ksone', 'kstwobign', 'laplace', 'logistic', 'loggamma', 'loglaplace', 'lognorm', 'lomax', 'maxwell', 'mielke', 'nakagami', 'ncx2', 'ncf', 'nct', 'norm', 'pareto', 'pearson3', 'powerlaw', 'powerlognorm', 'powernorm', 'rdist', 'reciprocal', 'rayleigh', 'rice', 'recipinvgauss', 'semicircular', 't', 'triang', 'truncexpon', 'truncnorm', 'tukeylambda', 'uniform', 'vonmises', 'wald', 'weibull_min', 'weibull_max', 'wrapcauchy']
	#['alpha', 'gamma', 'beta', 'triang', 'norm', 'pareto']
	
	fitPDFs = {}
	for distName in distNames:
		
		# fit to known distribution
		dist = getattr(stats, distName)
		params = dist.fit(data)
		
		# Kolmogorov-Smirnov test for goodness of fit
		pvalue = kstest(data, distName, args = params)[1]
		
		*shapeParams, loc, scale = params
		
		print('%s pvalue: %.4f\nparams: %s, loc: %.4f, scale: %.4f' % (distName, pvalue, shapeParams, loc, scale))
		
		# generate PDF of fitted distribution
		xstart = dist.ppf(0.01, *shapeParams, loc = loc, scale = scale)
		xend = dist.ppf(0.99, *shapeParams, loc = loc, scale = scale)
		
		xs = np.linspace(xstart, xend, 1000)
		PDF = dist.pdf(xs, *params[:-2], loc = params[-2], scale = params[-1])
		
		fitPDFs[distName] = pd.Series(PDF, index = xs)
	
	
	### plot
	plt.hist(data, bins = 50, density = True)
	
	for distName, PDF in fitPDFs.items():
		plt.plot(PDF.index, PDF.values, label = distName)
	
	plt.xlabel('Feedstock price ($/dry ton)')
	plt.ylabel('Frequency (probability)')
	
	plt.legend()
	
	plt.savefig('%s/fitted_distributions.jpg' % outDir, dpi = 300, bbox_inches = 'tight')
	
	
	
	
	
	
	




#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '05/15/2021'
__version__ = '1.1'


r'''
This script identifies the distribution of a continuous variable by fitting to the following unimodal distributions: "alpha", "beta", "triangular", "normal", "gamma" and "pareto"

python C:\Users\cwu\Desktop\Software\Aspen_automation\Scripts\case\FY21_Q3\identify_distribution.py
'''



import os
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import kstest
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")



### setting
outDir = r'C:\Users\cwu\Desktop\Software\Aspen_automation\Results\FY2021_Q3\Identify_distribution_weekly'
dataFile = r'C:\Users\cwu\Desktop\Software\Aspen_automation\Results\FY2021_Q3\Identify_distribution_weekly\D3_table_export.xlsx'
xlabel = 'Weekly prices'

os.makedirs(outDir, exist_ok = True)


### read data
data = pd.read_excel(dataFile, header = 0, index_col = 0, squeeze = True)


### 
distNames = ['alpha', 'gamma', 'beta', 'triang', 'norm', 'pareto']
#['alpha', 'anglit', 'arcsine', 'beta', 'betaprime', 'bradford', 'burr', 'cauchy', 'chi', 'chi2', 'cosine', 'dgamma', 'dweibull', 'erlang', 'expon', 'exponweib', 'exponpow', 'f', 'fatiguelife', 'fisk', 'foldcauchy', 'foldnorm', 'frechet_r', 'frechet_l', 'genlogistic', 'genpareto', 'genexpon', 'genextreme', 'gausshyper', 'gamma', 'gengamma', 'genhalflogistic', 'gilbrat', 'gompertz', 'gumbel_r', 'gumbel_l', 'halfcauchy', 'halflogistic', 'halfnorm', 'hypsecant', 'invgamma', 'invgauss', 'invweibull', 'johnsonsb', 'johnsonsu', 'ksone', 'kstwobign', 'laplace', 'logistic', 'loggamma', 'loglaplace', 'lognorm', 'lomax', 'maxwell', 'mielke', 'nakagami', 'ncx2', 'ncf', 'nct', 'norm', 'pareto', 'pearson3', 'powerlaw', 'powerlognorm', 'powernorm', 'rdist', 'reciprocal', 'rayleigh', 'rice', 'recipinvgauss', 'semicircular', 't', 'triang', 'truncexpon', 'truncnorm', 'tukeylambda', 'uniform', 'vonmises', 'wald', 'weibull_min', 'weibull_max', 'wrapcauchy']
#['alpha', 'gamma', 'beta', 'triang', 'norm', 'pareto']

fitPDFs = {}
for distName in distNames:
	
	# fit to known distribution
	dist = getattr(stats, distName)
	params = dist.fit(data)
	
	pvalue = kstest(data, distName, args = params)[1]
	
	*shapeParams, loc, scale = params
	
	print('%s pvalue: %.4f\nparams: %s, loc: %.4f, scale: %.4f' % (distName, pvalue, shapeParams, loc, scale))
	
	# generate PDF of fitted distribution
	xstart = dist.ppf(0.01, *shapeParams, loc = loc, scale = scale)
	xend = dist.ppf(0.99, *shapeParams, loc = loc, scale = scale)
	xend = min(xend, data.max()*1.2)
	
	xs = np.linspace(xstart, xend, 1000)
	PDF = dist.pdf(xs, *params[:-2], loc = params[-2], scale = params[-1])
	fitPDFs[distName] = pd.Series(PDF, index = xs)


### plot
plt.hist(data, bins = 50 if data.size > 100 else 10)
plt.xlabel(xlabel)
plt.ylabel('Count')

ax = plt.twinx()
for distName, PDF in fitPDFs.items():
	ax.plot(PDF.index, PDF.values, label = distName)

ax.set_ylabel('Probability density function')
ax.legend()

plt.savefig('%s/fitted_distributions.jpg' % outDir, dpi = 300, bbox_inches = 'tight')
	
	

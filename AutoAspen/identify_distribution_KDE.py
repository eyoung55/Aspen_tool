#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '09/08/2020'
__version__ = '1.0'


r'''
This script identify the distribution of a continuous variable using kernel density estimation, and generates random samples from the model

Example
python C:\Users\cwu\Desktop\Software\Aspen_automation\Scripts\identify_distribution_KDE.py -o C:\Users\cwu\Desktop\Software\Aspen_automation\Results\Q4\Monte_Carlo_feedstock2 -i C:\Users\cwu\Desktop\Software\Aspen_automation\Data\Q4\feedstock\Historical_PET_Bale_Prices.xlsx -n 1000
'''




import argparse
import os
import numpy as np
import pandas as pd
from sklearn.neighbors import KernelDensity
import matplotlib.pyplot as plt




if __name__ == '__main__':

	parser = argparse.ArgumentParser(description = 'This script identify the distribution of a continuous variable using kernel density estimation, and generates random samples from the model')
	parser.add_argument('-o', '--outDir', type = str, required = True, help = 'output directory')
	parser.add_argument('-i', '--inVarFile', type = str, required = True, help = '.xlsx file of input variable')
	parser.add_argument('-n', '--nsamples', type = int, required = True, help = '# of random samples to generate')
	args = parser.parse_args()
	
	outDir = args.outDir
	inVarFile = args.inVarFile
	nsamples = args.nsamples
	
	os.makedirs(outDir, exist_ok = True)


	### read input variable
	data = pd.read_excel(inVarFile, header = 0, index_col = 0, squeeze = True).values
	data = data*2000/100 + 0.19*2000   ###! $/dry ton
	
	
	### fit distribution
	kde = KernelDensity(kernel = 'gaussian', bandwidth = 10).fit(data[:, np.newaxis])
	samples = kde.sample(nsamples).reshape(-1)
	
	
	### save and plot
	np.savetxt('%s/samples.txt' % outDir, X = samples, newline = ',', fmt = '%.4f')
	
	plt.hist(data, bins = 50, density = True)
	
	x = np.sort(data)
	prob = np.exp(kde.score_samples(x[:, np.newaxis]))
	plt.plot(x, prob, label = 'KDE')
	
	plt.xlabel('Input variable')
	plt.ylabel('Frequency (probability)')
	
	plt.legend()
	
	plt.savefig('%s/fitted_distributions.jpg' % outDir, dpi = 300, bbox_inches = 'tight')
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	





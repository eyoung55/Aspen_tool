#!/usr/bin/env pyhton
# -*- coding: UTF-8 -*-


__author__ = 'Chao Wu'
__date__ = '12/25/2019'
__version__ = '1.1'


import re
import numpy as np
from pythoncom import CoInitialize
from win32com.client import DispatchEx
import os


class Excel():

	def __init__(self, excelFile):
		'''
		Parameters
		file: str, excel file
		'''
		
		CoInitialize()
		self.excelCOM = DispatchEx('Excel.Application')
		self.excelBook = self.excelCOM.Workbooks.Open(excelFile)


	def get_cell(self, sheet, loc = None, row = None, col= None):
		'''
		Parameters
		sheet: str, sheet name
		loc: cell location, equivalent to col+row
		row: int or str, row index
		col: str, column index
		
		Returns
		cellValue: num or str, cell value (after calculation)
		'''
		
		sht = self.excelBook.Worksheets(sheet)
		
		if loc != None:
			cellValue = sht.Evaluate(loc).Value
		
		elif row != None and col != None:
			cellValue = sht.Cells(row, col).Value
		
		return cellValue

	
	def set_cell(self, value, sheet, loc = None, row = None, col= None):
		'''
		Parameters
		value: num or str, value to set
		sheet: str, sheet name
		loc: cell location, equivalent to col+row
		row: int or str, row index
		col: str, column index
		'''
		
		sht = self.excelBook.Worksheets(sheet)
		
		if loc != None:
			sht.Evaluate(loc).Value = value
		
		elif row != None and col != None:
			sht.Cells(row, col).Value = value
	
	
	def load_aspenModel(self, aspenFile):
		'''
		Parameters
		aspenFile: str, aspen file
		'''
		
		self.set_cell(aspenFile, 'Set-up', 'B1')
	
		self.run_macro('sub_ClearSumData_ASPEN')
		self.run_macro('sub_GetSumData_ASPEN')
		
		
	def run_macro(self, macro):
		'''
		Parameters
		macro: str, macro
		'''
			
		self.excelCOM.Run(macro)	
		
			
	def close(self):
		
		self.excelBook.Close(SaveChanges = 0)    
		
		
class Aspen():

	def __init__(self, aspenFile):
		'''
		Parameters
		file: str, excel file
		'''
		
		CoInitialize()
		self.file = aspenFile
		self.COM = DispatchEx('Apwn.Document')
		print('Found relative aspen file path: %s' % (self.file))
		abspath = os.path.abspath(self.file)
		print('Found absolute aspen file path: %s' % (abspath))
		self.COM.InitFromArchive2(abspath)
		
		
	def get_value(self, aspenPath):
		'''
		Parameters
		aspenPath: str, path in ASPEN tree
		
		Returns
		value: num or str, value in ASPEN tree node
		'''
		
		value = self.COM.Tree.FindNode(aspenPath).Value
		
		return value
		
		
	def set_value(self, aspenPath, value, ifFortran):
		'''
		Parameters
		aspenPath: str, path in ASPEN tree
		value: float or str, value to set
		ifFortran: bool, whether it is a Fortran variable
		'''
		
		if ifFortran:
			oldValue = self.COM.Tree.FindNode(aspenPath).Value
			
			self.COM.Tree.FindNode(aspenPath).Value = re.sub(r'(?<==).+', str(value), oldValue)
			
		else:
			self.COM.Tree.FindNode(aspenPath).Value = float(value)
		

	def run_model(self):
	
		self.COM.Reinit()
		self.COM.Engine.Run2()
		
		
	def save_model(self, saveFile):
		'''
		Parameters
		saveFile: str, file name to save (.bkp)
		'''
	
		self.COM.SaveAs(saveFile)
		
	
	def close(self):
		
		self.COM.Close()
	
		
class Scaler():
	
	def __init__(self, range = (-1, 1)):
		'''
		Parameters
		range: 2-tuple, range to standardize 
		'''
		
		self.lb, self.ub = range
		
	
	def transform(self, rawData):
		'''
		Parameters
		rawData: 2D array, raw data, columns are inputs
		
		Returns
		stdData: 2D array, standardized data, columns are inputs
		'''
		
		rawData = np.array(rawData)
		self.min = rawData.min(axis = 0)
		self.max = rawData.max(axis = 0)
		
		stdData = (rawData - self.min) / (self.max - self.min) * (self.ub - self.lb) + self.lb
		
		return stdData
		
		
	def back_transform(self, stdData):
		'''
		Parameters
		stdData: array, standardized data, columns are inputs
		
		Returns
		rawData: array, raw data, columns are inputs
		'''
		
		rawData = (stdData - self.lb) / (self.ub - self.lb) * (self.max - self.min) + self.min
		
		return rawData
		
		
		
		
		
		
		
		
		
		
		
		
		



		



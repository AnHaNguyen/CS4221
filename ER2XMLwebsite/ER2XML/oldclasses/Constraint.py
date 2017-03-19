from .ConstraintType import *

class Constraint:		#define each constraint
	def __init__(self,constraintType):			
		self.constraintType = constraintType 		#refer to constraintType enum class
		self.data = [] 					#a list contains table id and column id that this column refers to as foreign key

	def setConstraintType(self, constraintType):
		self.constraintType = constraintType

	def setData(self, data):
		self.data = data

	def getConstraintType(self):
		return self.constraintType

	def getData(self):
		return self.data

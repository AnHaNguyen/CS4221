from Type import *
from Constraint import *
class Column:
	def __init__(self, colId, name):
		self.id = colId				#column id as in xml file
		self.name = name 			#column name as in xml file
		self.datatype = Type.STRING   	#type from Type enum class(let default be STRING)
		self.constraintList = []			#a list of constraint objects for column

	def getId(self):
		return self.id;	
	
	def addConstraint(self, constraint):
		self.constraintList.append(constraint)
			
	def getName(self):
		return self.name

	def getDataType(self):
		return self.datatype

	def getConstraintList(self):
		return self.constraintList

	def setName(self, name):
		self.name = name

	def setDataType(self, datatype):
		self.datatype = datatype

	def setConstraintList(self, constraintList):
		self.constraintList = constraintList

	def isInPrimaryKey(self):
		for constraint in self.constraintList:
			if constraint.getConstraintType() == ConstraintType.PRIMARY_KEY:
				return True
		return False
from .Column import *
from .WeakEntity import *
from .ConstraintType import *
class Table:
	def __init__(self, tableId, name):
		self.id = tableId			#table id as in xml file
		self.name = name 			#table name as in xml file
		self.columnList = [] 		#list of columns in table
		self.weakEntityList = []

	def getId(self):
		return self.id

	def addColumn(self,column):
		self.columnList.append(column)

	def getName(self):
		return self.name

	def setName(self, name):
		self.name = name
			
	def getColumnList(self):
		return self.columnList

	def setColumnList(self, columnList):
		self.columnList = columnList

	def getPrimaryKey(self):
		primKey = []
		for column in self.columnList:
			if column.isInPrimaryKey():
				primKey.append(column)
		return primKey

	def getForeignKeyToTable(self, tableId):
		foreignKeys = []
		for column in self.columnList:
			constraintList = column.getConstraintList()
			for constraint in constraintList:
				if (constraint.getConstraintType() == ConstraintType.FOREIGN_KEY):
					data = constraint.getData()
					if (data[0] == tableId):
						foreignKeys.append(column.getName())			#now only need to return name
		for weakEntity in self.weakEntityList:
			if (weakEntity.getToEntity() == tableId):
				for foreignKey in weakEntity.getForeignKey():
					foreignKeys.append(foreignKey.split(".")[1])

		return foreignKeys

	def setWeakEntityList(self, weakEntityList):
		self.weakEntityList = weakEntityList

	def getWeakEntityList(self):
		return self.weakEntityList
		
	def toXML(self):
		return ""
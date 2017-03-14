from Column import *
from WeakEntity import *
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

	def setWeakEntityList(self, weakEntityList):
		self.weakEntityList = weakEntityList

	def getWeakEntityList(self):
		return self.weakEntityList
		
	def toXML(self):
		return ""
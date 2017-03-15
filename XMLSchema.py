from Table import *
from Column import *
from Constraint import *
from ConstraintType import *
from Type import *
from WeakEntity import *
import xml.dom.minidom

class XMLSchema:
	def __init__(self, tableEntityList, tableRelationshipList):
		self.tableEntityList = tableEntityList
		self.tableRelationshipList = tableRelationshipList

	def toString(self):
		tableList = []
		tableList.extend(self.tableEntityList)
		tableList.extend(self.tableRelationshipList)
		xml_string = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
		xml_string += "<xs:schema id=\"MyDataSet\" xmlns=\"\" "
		xml_string += "xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" "
		xml_string += "xmlns:msdata=\"urn:schemas-microsoft-com:xml-msdata\">"
		xml_string += "<xs:element name=\"NewDataSet\" msdata:IsDataSet=\"true\">"
		xml_string += "<xs:complexType>"
		xml_string += "<xs:choice maxOccurs=\"unbounded\">"

		for table in tableList:
			xml_string += self.convertEntity(table)
		
		xml_string += "</xs:choice>"
		xml_string += "</xs:complexType>"
		
		#convert keys
		primKeySet = []
		i = 1
		for table in self.tableEntityList:
			primKeys = table.getPrimaryKey()
			keyName = "NewDataSetKey"+str(i)
			i = i+1
			selector = ".//"+table.getName()
			xml_string += self.convertPrimKey(keyName, selector, primKeys)
			reference = []
			reference.append(keyName)
			reference.append(table.getName())
			reference.append(table.getId())
			primKeySet.append(reference)

		for table in self.tableRelationshipList:
			primKeys = table.getPrimaryKey()
			keyName = "NewDataSetKey"+str(i)
			i = i+1
			selector = ".//"+table.getName()
			xml_string += self.convertPrimKey(keyName, selector, primKeys)
		
		i = 0
		for i in range(len(primKeySet)):
			keyName, tableName, tableId = primKeySet[i][0:3]
			for table in tableList:
				foreignKeys = table.getForeignKeyToTable(tableId)
				if (len(foreignKeys) > 0):
					name = table.getName() + "to" +tableName + "Ref"
					selector = ".//"+table.getName()
					xml_string += self.convertForeignKey(name, keyName, selector, foreignKeys)
		
		xml_string += "</xs:element>"
		xml_string += "</xs:schema>"
		dom = xml.dom.minidom.parseString(xml_string)
		prettyString = dom.toprettyxml()
		return prettyString

	def convertEntity(self, table):
		tableName = table.getName()
		s = "<xs:element name=" + "\"" + tableName + "\">"
		s += "<xs:complexType>"
		s += "<xs:sequence>"
		columnList = table.getColumnList()
		for column in columnList:
			s += self.convertColumn(column)
		weakEntityList = table.getWeakEntityList()
		for weakEntity in weakEntityList:
			s += self.convertWeakEntity(weakEntity)

		s += "</xs:sequence>"
		s += "</xs:complexType>"
		s += "</xs:element>"
		return s

	def convertColumn(self, column):
		columnName = column.getName()
		columnType = column.getDataType()
		xType = self.getXMLType(columnType)
		constraintList = column.getConstraintList()
		isOptional = (len(constraintList) == 0)
		
		s = "<xs:element name=\"" + columnName + "\" type=\"" + xType + "\""
		if (isOptional):
			s += " minOccurs=\"0\"/>"
		else:
			s += "/>"
		return s

	def convertWeakEntity(self, weakEntity):
		foreignKeyList = weakEntity.getForeignKey()
		dataTypeList = weakEntity.getDataType()
		s = ""
		for i in range(len(foreignKeyList)):
			columnName = foreignKeyList[i].split(".")[1]
			columnType = dataTypeList[i]
			xType = self.getXMLType(columnType)
			s += "<xs:element name=\"" + columnName + "\" type=\"" + xType + "\"/>"
		return s

	def convertPrimKey(self, keyName, selector, primKeys):
		s = "<xs:key name=\""+keyName+"\" msdata:PrimaryKey=\"true\">"
		s += "<xs:selector xpath=\""+ selector+"\"/>"
		for column in primKeys:
			columnName = column.getName()
			s += "<xs:field xpath=\""+columnName+"\"/>"
		s += "</xs:key>"
		return s

	def convertForeignKey(self, name, referName, selector, foreignKeys):
		s = "<xs:keyref name=\"" + name + "\" refer=\"" + referName + "\">"
		s += "<xs:selector xpath=\"" + selector + "\"/>"
		for column in foreignKeys:
			s += "<xs:field xpath=\""+column+"\"/>"
		s += "</xs:keyref>"
		return s

	def getXMLType(self,columnType):
		if (columnType == Type.STRING):
			xType = "xs:string"
		elif (columnType == Type.NUMERIC):
			xType = "xs:decimal"
		elif (columnType == Type.DATE):
			xType = "xs:date"
		elif (columnType == Type.BOOLEAN):
			xType = "xs:boolean"
		elif (columnType == Type.INTEGER):
			xType = "xs:integer"
		return xType
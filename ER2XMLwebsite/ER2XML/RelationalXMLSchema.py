from .models import XSDType, ConstraintType, Table, Column
from xml.etree import ElementTree
import xml.dom.minidom

def generateXMLSchema(erModel):
	tableList = erModel.tables.all()

	xml_string = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
	xml_string += "<xs:schema id=\"MyDataSet\" xmlns=\"\" "
	xml_string += "xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" "
	xml_string += "xmlns:msdata=\"urn:schemas-microsoft-com:xml-msdata\">"
	xml_string += "<xs:element name=\"NewDataSet\" msdata:IsDataSet=\"true\">"
	xml_string += "<xs:complexType>"
	xml_string += "<xs:choice maxOccurs=\"unbounded\">"

	for table in tableList:
		xml_string += convertEntity(table)
	
	xml_string += "</xs:choice>"
	xml_string += "</xs:complexType>"
	
	#convert keys
	primKeySet = []
	i = 1
	for table in tableList:
		keySet = []
		primKeys = getPrimaryKey(table)
		keyName = "NewDataSetKey"+str(i)
		i = i+1
		selector = ".//"+table.name
		xml_string += convertPrimKey(keyName, selector, primKeys)
		if (table.isEntity == "1"):
			keySet.append(keyName)
			keySet.append(table.name)
			keySet.append(str(table.tableId))
			primKeySet.append(keySet)

	i = 0
	for i in range(len(primKeySet)):
		keyName, tableName, tableId = primKeySet[i][0:3]
		for table in tableList:
			foreignKeys = getForeignKeyToTable(table, tableId)
			if (len(foreignKeys) > 0):
				name = table.name + "To" +tableName + "Ref"
				selector = ".//"+table.name
				xml_string += convertForeignKey(name, keyName, selector, foreignKeys)
	
	xml_string += "</xs:element>"
	xml_string += "</xs:schema>"
	#if there is an error in xml.dom.minidom NoneType has no 'replace' function
	#go to python27/Lib/xml/dom/minidom.py and comment line 294 + 295
	dom = xml.dom.minidom.parseString(xml_string)
	prettyString = dom.toprettyxml()
	return prettyString

def convertEntity(table):
	tableName = table.name
	s = "<xs:element name=" + "\"" + tableName + "\">"
	s += "<xs:complexType>"
	s += "<xs:sequence>"
	columnList = table.columns.all()
	for column in columnList:
		s += convertColumn(column)

	s += "</xs:sequence>"
	s += "</xs:complexType>"
	s += "</xs:element>"
	return s

def convertColumn(column):
	columnName = column.name
	columnType = column.tp
	xType = getXMLType(columnType)
	constraintList = column.constr.all()
	minOccur = str(column.minOccur)
	maxOccur = str(column.maxOccur)

	s = "<xs:element name=\"" + columnName + "\" type=\"" + xType + "\""
	
	if (minOccur != "1"):
		s += " minOccurs=\"" + minOccur + "\""
	
	if (maxOccur != "1"):
		if (maxOccur == "2"):
			maxOccur = "unbounded"
		s += " maxOccurs=\"" + maxOccur + "\"/>"
	return s

def convertPrimKey(keyName, selector, primKeys):
	s = "<xs:key name=\""+keyName+"\" msdata:PrimaryKey=\"true\">"
	s += "<xs:selector xpath=\""+ selector+"\"/>"
	for column in primKeys:
		columnName = column.name
		s += "<xs:field xpath=\""+columnName+"\"/>"
	s += "</xs:key>"
	return s

def convertForeignKey(name, referName, selector, foreignKeys):
	s = "<xs:keyref name=\"" + name + "\" refer=\"" + referName + "\">"
	s += "<xs:selector xpath=\"" + selector + "\"/>"
	for column in foreignKeys:
		s += "<xs:field xpath=\""+column.name+"\"/>"
	s += "</xs:keyref>"
	return s

def getXMLType(columnType):
	if (columnType == XSDType.STRING):
		xType = "xs:string"
	elif (columnType == XSDType.NUMERIC):
		xType = "xs:decimal"
	elif (columnType == XSDType.DATE):
		xType = "xs:date"
	elif (columnType == XSDType.BOOLEAN):
		xType = "xs:boolean"
	elif (columnType == XSDType.INTEGER):
		xType = "xs:integer"
	return xType

def getPrimaryKey(table):
    primKey = []
    for column in table.columns.all():
        for constraint in column.constr.all():
            constraintType = constraint.constraintType
            if (constraintType == ConstraintType.PRIMARY_KEY):
                primKey.append(column)
    return primKey

def getForeignKeyToTable(table, tableId):
	foreignKeys = []
	for column in table.columns.all():
		constraintList = column.constr.all()
		for constraint in constraintList:
			if (constraint.constraintType == ConstraintType.FOREIGN_KEY):
				referredTableId = constraint.referredTable
				if (str(referredTableId) == tableId):
					foreignKeys.append(column)			
	return foreignKeys

class WeakEntity:
    def __init__(self, fromEntity, toEntity):
        self.fromEntity = fromEntity
        self.toEntity = toEntity
        
    def getFromEntity(self):
        return self.fromEntity;

    def getToEntity(self):
        return self.toEntity;


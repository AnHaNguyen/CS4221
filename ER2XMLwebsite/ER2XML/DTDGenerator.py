from .models import XSDType, ConstraintType, Table, Column

def generateDTD(erModel):
	tables = erModel.tables.all()
	dtdString = ""
	for table in tables:
		dtdString += convertTable(table)

	return dtdString

def convertTable(table):
	tableName = table.name
	
	elementList = getNotIdNotIdRef(table)
	idList = getIdNotIdRef(table)
	idRefList = getIdRef(table)

	s = "<!ELEMENT " + tableName + " "
	if (len(elementList) == 0):
		s+="EMPTY>\n"
	
	else:
		i= 0
		for i in range(len(elementList)):
			s += "("
			column = elementList[i]
			columnName = column.name
			occurence = getOccurence(column)
			s += columnName + occurence
			if (i < len(elementList) - 1):
				s += ", "
		s += ")>\n"

	
	for column in elementList:
		s += convertColumn(column)
	for column in idList:
		s += convertId(column, tableName)
	for column in idRefList:
		s += convertIdRef(column, tableName)
	return s

def convertColumn(column):
	columnName = column.name
	columnType = '#PCDATA'
	s = "<!ELEMENT " + columnName + " (" + columnType +")>\n"
	return s

def convertId(column, tableName):
	columnName = column.name
	s = "<!ATTLIST " + tableName + " " + columnName + " ID #REQUIRED>\n"
	return s

def convertIdRef(column, tableName):
	columnName = column.name
	s = "<!ATTLIST " + tableName + " " + columnName + " IDREF #IMPLIED>\n"
	return s

def getOccurence(column):
	minOccur = column.minOccur
	maxOccur = column.maxOccur
	if (minOccur == 1 and maxOccur == 1):
		return ''
	elif (minOccur == 1 and maxOccur == 2):
		return '+'
	elif (minOccur == 0 and maxOccur == 2):
		return '*'
	elif (minOccur == 0 and maxOccur == 1):
		return '?'

	return ''

def isPrimaryKey(column):
	for constraint in column.constr.all():
		if constraint.constraintType == ConstraintType.PRIMARY_KEY:
			return True
	return False

def getIdNotIdRef(table):
	columnList = []
	for column in table.columns.all():
		isIdRef = False
		isId = False
		for constraint in column.constr.all():
			if constraint.constraintType == ConstraintType.PRIMARY_KEY:
				isId = True
			elif constraint.constraintType == ConstraintType.FOREIGN_KEY:
				isIdRef = True
		if (isId and not isIdRef):
			columnList.append(column)
	return columnList

def getIdRef(table):
	columnList = []
	for column in table.columns.all():
		for constraint in column.constr.all():
			if constraint.constraintType == ConstraintType.FOREIGN_KEY:
				columnList.append(column)			
	return columnList

def getNotIdNotIdRef(table):
	columnList = []
	for column in table.columns.all():
		isIdRef = False
		isId = False
		for constraint in column.constr.all():
			if constraint.constraintType == ConstraintType.PRIMARY_KEY:
				isId = True
			elif constraint.constraintType == ConstraintType.FOREIGN_KEY:
				isIdRef = True
		if (not isId and not isIdRef):
			columnList.append(column)
	return columnList
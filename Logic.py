import xml.etree.ElementTree as ET
from Table import *
from ConstraintType import *

def processEntity(entityList):
	tableEntityList = []
	for entity in entityList:
		data = entity.items()
		for name,value in data:		#create table id and name based on an entry in entity
			if (name == "id"):
				tableId = value
			else:
				tableName = value
				
		columnList = []		
		attributeList = []
		keyList = []
		for child in entity:
			if (child.tag == "attribute"):
				attributeList.append(child.items())
			else:
				keyList.append(child.text)
		
		# for key in keyList:					#let user choose prim key in keyList, in the first time parsed, we use first key as prim
		# 	parsedKey = key.split(",")		


		for attribute in attributeList:
			isReferredAttribute = False;
			for name, value in attribute:
				if (name == "id"):
					columnId = value
				elif (name == "name"):
					columnName = value
				else:
					referredEntity = value			#need to handle weak entity
					isReferredAttribute = True

			if (not isReferredAttribute):
				column = Column(columnId, columnName)

				parsedKey = keyList[0].split(",")		#use tge first key as prim key
				if (columnId in parsedKey):								#handle prim key
					primKey = Constraint(ConstraintType.PRIMARY_KEY)
					column.addConstraint(primKey)

				columnList.append(column)

		table = Table(tableId, tableName)
		table.setColumnList(columnList)
		tableEntityList.append(table)	

	return tableEntityList


def processRelationship(relationshipList, tableEntityList):
	tableRelationshipList = []
	for relationship in relationshipList:
		data = relationship.items()
		for name,value in data:		#same as entity
			if (name == "id"):
				tableId = value
			else:
				tableName = value
		
		columnList = []		
		attributeList = []

		for child in relationship:
			attributeList.append(child.items())
		
		for attribute in attributeList:
			for name, value in attribute:
				if (name == "name"):  		#need to handle min/max participation and aggregation?
					columnName = value
					columnId = generateId(columnList)
					column = Column(columnId, columnName)
					columnList.append(column)
				
				elif (name == "entity_id"):
					referredColumns = getReferredColumn(value, tableEntityList, generateId(columnList))
					columnList.extend(referredColumns)

		table = Table(tableId, tableName)
		table.setColumnList(columnList)
		tableRelationshipList.append(table)	
	
	return tableRelationshipList

def getReferredColumn(entity_id, tableEntityList, nextId):
	referredColumns = []
	for table in tableEntityList:
		if table.getId() == entity_id:
			primKey = table.getPrimaryKey()
			for column in primKey:
				columnId = nextId
				nextId = str(int(nextId) + 1)
				columnName = column.getName()
				data = [table.getId(), column.getId()]
				constraint = Constraint(ConstraintType.FOREIGN_KEY)
				constraint.setData(data)
				column = Column(columnId, columnName)
				column.addConstraint(constraint)
				referredColumns.append(column)

	return referredColumns

def generateId(columnList):
	genId = 1
	for column in columnList:
		colId = int(column.getId())
		if colId >= genId:
			genId = colId + 1
	return str(genId)

tree = ET.parse("template.xml")
root = tree.getroot()
entityList = []
relationshipList = []

for child in root:
	if (child.tag == "entity"):
		entityList.append(child)
	else:
		relationshipList.append(child)

tableEntityList = processEntity(entityList)
for table in tableEntityList:
 	print("\nENTITY TABLE:"+ table.getId(), table.getName())
 	columnList = table.getColumnList()
 	for column in columnList:
 		print("\nColumn:"+column.getId(), column.getName(), column.getDataType())
 		constraintList = column.getConstraintList()
 		for constraint in constraintList:
 			print(constraint.getConstraintType())

tableRelationshipList = processRelationship(relationshipList, tableEntityList)	
for table in tableRelationshipList:
	print("\nRELATIONSHIP TABLE:"+ table.getId(), table.getName())
	columnList = table.getColumnList()
	for column in columnList:
		print("\nColumn:"+column.getId(), column.getName(), column.getDataType())
		constraintList = column.getConstraintList()
		for constraint in constraintList:
			print(constraint.getConstraintType(), constraint.getData()[0], constraint.getData()[1])
import xml.etree.ElementTree as ET
from Table import *
from ConstraintType import *
from XMLSchema import *
import argparse

def processEntity(entityList):
    tableEntityList = []
    for entity in entityList:
        data = entity.items()
        for name, value in data:        #create table id and name based on an entry in entity
            if (name == "id"):
                tableId = value
            else:
                tableName = value
                
        columnList = []     
        attributeList = []
        keyList = []
        weakEntityList = [] # list of weak entities
        for child in entity:
            if (child.tag == "attribute"):
                attributeList.append(child.items())
            else:
                keyList.append(child.text)
        
        # for key in keyList:                   #let user choose prim key in keyList, in the first time parsed, we use first key as prim
        #   parsedKey = key.split(",")      


        for attribute in attributeList:
            isReferredAttribute = False;
            for name, value in attribute:
                if (name == "id"):
                    columnId = value
                elif (name == "name"):
                    columnName = value
                else:
                    referredEntity = value          #need to handle weak entity
                    isReferredAttribute = True
                    weakEntityList.append(WeakEntity(tableId, value))

            if (not isReferredAttribute):
                column = Column(columnId, columnName)

                parsedKey = keyList[0].split(",")       #use tge first key as prim key
                if (columnId in parsedKey):                             #handle prim key
                    primKey = Constraint(ConstraintType.PRIMARY_KEY)
                    column.addConstraint(primKey)

                columnList.append(column)

        table = Table(tableId, tableName)
        table.setColumnList(columnList)
        table.setWeakEntityList(weakEntityList)
        tableEntityList.append(table)   

    return tableEntityList


def processRelationship(relationshipList, tableEntityList):
    tableRelationshipList = []
    for relationship in relationshipList:
        data = relationship.items()
        for name,value in data:     #same as entity
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
                if (name == "name"):        #need to handle min/max participation and aggregation?
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
                column = Column(columnId, columnName)
                
                foreignKeyConstraint = Constraint(ConstraintType.FOREIGN_KEY)
                foreignKeyConstraint.setData(data)
                column.addConstraint(foreignKeyConstraint)
                
                primKeyConstraint = Constraint(ConstraintType.PRIMARY_KEY)
                column.addConstraint(primKeyConstraint)
                
                referredColumns.append(column)

    return referredColumns

def generateId(columnList):
    genId = 1
    for column in columnList:
        colId = int(column.getId())
        if colId >= genId:
            genId = colId + 1
    return str(genId)

def generateXMLSchema(tableEntityList, tableRelationshipList):
	f = open('schema.xsd', 'w')
	schema = XMLSchema(tableEntityList, tableRelationshipList)
	f.write(schema.toString())
	f.close()
 
if __name__ == '__main__':
    # Environment Setting
    parser = argparse.ArgumentParser()
    parser.add_argument('inFileName', help='A required string as input file name')
    args = parser.parse_args()

    tree = ET.parse(args.inFileName)
    root = tree.getroot()
    entityList = []
    relationshipList = []

    for child in root:
        if (child.tag == "entity"):
            entityList.append(child)
        else:
            relationshipList.append(child)

    primaryKeys = [[]] * len(entityList)
    dataTypes = [[]] * len(entityList)	#datatypes of primary keys
    weakEntityList = []

    tableEntityList = processEntity(entityList)
    tableRelationshipList = processRelationship(relationshipList, tableEntityList)  

    for table in tableEntityList:
    	# Save primary key as TABLE_NAME.COLUMN_NAME
        keys = []
        dataType = []
        for key in table.getPrimaryKey():
            keys.append(table.getName() + "." + key.getName())
            dataType.append(key.getDataType())

        primaryKeys[int(table.getId()) - 1] = keys
        dataTypes[int(table.getId()) - 1] = dataType

        weakEntityList.append(table.getWeakEntityList())

    # Set weak entities foreign key(s)
    for weakEntities in weakEntityList:
        for weakEntity in weakEntities:
            weakEntity.setForeignKey(primaryKeys[int(weakEntity.getToEntity()) - 1])
            weakEntity.setDataType(dataTypes[int(weakEntity.getToEntity()) - 1])

    generateXMLSchema(tableEntityList, tableRelationshipList)


    #for debugging
    print(primaryKeys)
    print("\n--- Weak Entities ---")
    for weakEntities in weakEntityList:
        for weakEntity in weakEntities:
            print("Weak Entity: (From: " + weakEntity.getFromEntity() + ", To: " + weakEntity.getToEntity() + ")")
            print("Foreign Key: " + str(weakEntity.getForeignKey()))

    print("--- End Weak Entities ---")

    for table in tableEntityList:
        print("\nENTITY TABLE:"+ table.getId(), table.getName())    
        columnList = table.getColumnList()
        for column in columnList:
            print("\nColumn:"+column.getId(), column.getName(), column.getDataType())
            constraintList = column.getConstraintList()
            for constraint in constraintList:
                print(constraint.getConstraintType())


    for table in tableRelationshipList:
        print("\nRELATIONSHIP TABLE:"+ table.getId(), table.getName())
        columnList = table.getColumnList()
        for column in columnList:
            print("\nColumn:"+column.getId(), column.getName(), column.getDataType())
            constraintList = column.getConstraintList()
            for constraint in constraintList:
                if (constraint.getConstraintType() == ConstraintType.PRIMARY_KEY):
                    print(constraint.getConstraintType())
                else:
                    print(constraint.getConstraintType(), constraint.getData()[0], constraint.getData()[1])

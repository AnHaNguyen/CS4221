import xml.etree.ElementTree as ET
from .models import Table, XMLSchema, Column, Constraint, XSDType, ConstraintType
import argparse

def processEntity(entityList,erModel):
    tableEntityList = []
    weakEntityList = [] # list of weak entities
    for entity in entityList:
        data = entity.items()
        tableId = 0
        tableName = ""
        for name, value in data:        #create table id and name based on an entry in entity
            if (name == "id"):
                tableId = int(value)
            else:
                tableName = value
        table = Table(model = erModel, tableId = tableId, name = tableName, isEntity = True)
        table.save()
        
        attributeList = []
        keyList = []            

        for child in entity:
            if (child.tag == "attribute"):
                attributeList.append(child.items())
            else:
                keyList.append(child.text)          #can retrieve key List after here
        
        # for key in keyList:                   #let user choose prim key in keyList, in the first time parsed, we use first key as prim
        #   parsedKey = key.split(",")      

        for attribute in attributeList:
            isReferredAttribute = False;
            columnId = -1
            columnName = ""
            columnType = XSDType.STRING.value
            for name, value in attribute:
                if (name == "id"):
                    columnId = int(value)
                elif (name == "name"):
                    isReferredAttribute = False
                    columnName = value
                elif (name =="entity_id"):
                    referredEntity = value          #need to handle weak entity
                    isReferredAttribute = True
                    weakEntityList.append(WeakEntity(tableId, int(value)))
                elif (name == "type"):
                    columnType = parseType(value)

            if (not isReferredAttribute):
                column = Column(table = table, colId = columnId, name = columnName, tp=columnType)
                column.save()
                parsedKey = parsePrimaryKey(keyList, 0)      #use the first key as prim
                if str(columnId) in parsedKey:
                    primKey = Constraint(column = column, constraintType = ConstraintType.PRIMARY_KEY.value)
                    primKey.save()

        tableEntityList.append(table)   
    
    for weakEntity in weakEntityList:
        originTable = getTableById(weakEntity.getFromEntity(), tableEntityList)
        referredTable = getTableById(weakEntity.getToEntity(), tableEntityList)
        primKey = getPrimaryKey(referredTable)
        columnId = generateId(originTable.columns.all())
        for key in primKey:
            col = Column(table = originTable, colId = columnId, name = key.name, tp = key.tp)
            col.save()
            foreignKey = Constraint(column = col, constraintType = ConstraintType.FOREIGN_KEY.value, referredTable = referredTable.tableId, referredCol = key.colId)
            foreignKey.save()
            columnId = columnId + 1

    return tableEntityList

def getTableById(tableId, tableList):
    for table in tableList:
        if table.tableId == tableId:
            return table

def processRelationship(relationshipList, tableEntityList, erModel):
    tableRelationshipList = []
    for relationship in relationshipList:
        data = relationship.items()
        tableId = 0
        tableName = ""
        for name,value in data:     #same as entity
            if (name == "id"):
                tableId = int(value)
            else:
                tableName = value
        table = Table(model = erModel, tableId = tableId, name = tableName, isEntity = False)
        table.save()

        attributeList = []
        columnList = []

        for child in relationship:
            attributeList.append(child.items())
        
        for attribute in attributeList:
            columnId = -1
            columnName = ""
            columnType = XSDType.STRING.value
            isReferredAttribute = False
            isAggregate = False
            minOccur = 0
            maxOccur = 2
            for name, value in attribute:
                if (name == "name"):       
                    isReferredAttribute = False
                    isAggregate = False
                    columnName = value
                    columnId = generateId(columnList)
                elif (name == "type"):
                    columnType = parseType(value)
                elif (name == "entity_id"):
                    isReferredAttribute = True
                    referredId = int(value)
                elif (name == "relation_id"):
                    isAggregate = True              #need to handle aggregate
                elif (name == "min_participation"):
                    minOccur = int(value)
                elif (name == "max_participation"):
                    if (value == "N"):
                        maxOccur = 2
                    else:
                        maxOccur = int(value)

            if (not isReferredAttribute and not isAggregate):
                column = Column(table = table, colId = columnId, name = columnName, tp=columnType, minOccur = minOccur, maxOccur = maxOccur)
                column.save()
                columnList.append(column)
            elif (isReferredAttribute):
                columnList.extend(getReferredColumn(referredId, tableEntityList, generateId(columnList), table))
        
        tableRelationshipList.append(table) 
    
    return tableRelationshipList

def getReferredColumn(entity_id, tableEntityList, nextId, originTable):
    referredColumns = []
    for table in tableEntityList:
        if (table.tableId == entity_id):
            primKey = getPrimaryKey(table)
            for column in primKey:
                columnId = nextId
                nextId = nextId + 1
                columnName = column.name
                columnType = column.tp
                newColumn = Column(table = originTable, colId = columnId, name = columnName, tp = columnType)
                newColumn.save()

                foreignKeyConstraint = Constraint(column = newColumn, constraintType = ConstraintType.FOREIGN_KEY.value, referredTable = table.tableId, referredCol = column.colId)
                foreignKeyConstraint.save()

                primKeyConstraint = Constraint(column = newColumn, constraintType = ConstraintType.PRIMARY_KEY.value)
                primKeyConstraint.save()
                
                referredColumns.append(newColumn)
    return referredColumns

def getPrimaryKey(table):
    primKey = []
    for column in table.columns.all():
        for constraint in column.constr.all():
            constraintType = constraint.constraintType
            if (constraintType == ConstraintType.PRIMARY_KEY.value):
                primKey.append(column)
    return primKey

def parseType(tp):
    if (tp == 'string'):
        return XSDType.STRING.value
    elif(tp == 'date'):
        return XSDType.DATE.value
    elif (tp == 'integer'):
        return XSDType.INTEGER.value
    elif (tp == 'decimal'):
        return XSDType.DECIMAL.value
    elif (tp == 'boolean'):
        return XSDType.BOOLEAN.value
    elif (tp == 'short'):
        return XSDType.SHORT.value

def generateId(columnList):
    genId = 1
    for column in columnList:
        colId = column.colId
        if colId >= genId:
            genId = colId + 1
    return genId

def parsePrimaryKey(keyList, keyId):
    parsedKey = keyList[keyId].split(",")      
    return parsedKey

def exportXMLToFile(fileName, xmlString):
    f = open(fileName, 'w')
    f.write(xmlString)
    f.close()

def parseXMLString(erModel):
    xmlString = erModel.text
    root = ET.fromstring(xmlString)
    tables = parseAndConvertXML(root, erModel)
    return tables

def parseAndConvertXML(root, erModel):
    entityList = []
    weakEntityList = []
    relationshipList = []

    for child in root:
        if (child.tag == "entity"):
            entityList.append(child)
        else:
            relationshipList.append(child)

        entityList.extend(weakEntityList)

    primaryKeys = [[]] * len(entityList)
    dataTypes = [[]] * len(entityList)  #datatypes of primary keys
    weakEntityList = []

    tableEntityList = processEntity(entityList, erModel)
    tableRelationshipList = processRelationship(relationshipList, tableEntityList, erModel)  

    for table in tableEntityList:
        print("\nENTITY TABLE:"+ str(table.tableId), table.name)    
        columnList = table.columns.all()
        for column in columnList:
            print("\nColumn:"+ str(column.colId), column.name, column.tp)
            constraintList = column.constr.all()
            for constraint in constraintList:
                print(constraint.constraintType, constraint.referredTable, constraint.referredCol)


    for table in tableRelationshipList:
        print("\nRELATIONSHIP TABLE:"+ str(table.tableId), table.name)
        columnList = table.columns.all()
        for column in columnList:
            print("\nColumn:"+ str(column.colId), column.name, column.tp)
            constraintList = column.constr.all()
            for constraint in constraintList:
                print(constraint.constraintType, constraint.referredTable, constraint.referredCol)
    
    returnList = []
    returnList.extend(tableEntityList)
    returnList.extend(tableRelationshipList)
    return returnList

# if __name__ == '__main__':
#     # Environment Setting
#     parser = argparse.ArgumentParser()
#     parser.add_argument('inFileName', help='A required string as input file name')
#     args = parser.parse_args()

#     tree = ET.parse(args.inFileName)
#     root = tree.getroot()
#     parseAndConvertXML(root)

class WeakEntity:
    def __init__(self, fromEntity, toEntity):
        self.fromEntity = fromEntity
        self.toEntity = toEntity
        
    def getFromEntity(self):
        return self.fromEntity

    def getToEntity(self):
        return self.toEntity
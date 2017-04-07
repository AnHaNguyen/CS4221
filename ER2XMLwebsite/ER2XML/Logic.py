import xml.etree.ElementTree as ET
from .models import Table, XMLSchema, Column, Constraint, XSDType, ConstraintType, Key, Type
import argparse

def setKey(table, key):
    for column in table.columns.all():
        constrList = column.constr.all()
        for constraint in constrList:
            if constraint.constraintType == ConstraintType.PRIMARY_KEY:
                constraint.delete()
                column.save()

    idString = key.colIds
    columnIds = idString.split(",")
    for columnId in columnIds:
        column = getColumnById(columnId, table)
        constraint = Constraint(constraintType = ConstraintType.PRIMARY_KEY, column = column)
        constraint.save()


def processEntity(entityList,erModel):
    tableEntityList = []
    weakEntityList = [] # list of weak entities
    tableKeyList = []
    
    for entity in entityList:
        data = entity.items()
        tableId = 0
        tableName = ""
        for name, value in data:        #create table id and name based on an entry in entity
            if (name == "id"):
                tableId = int(value)
            else:
                tableName = value.replace(" ", "")
        table = Table(model = erModel, tableId = tableId, name = tableName, isEntity = True)
        table.save()
        
        attributeList = []
        keyList = []            

        for child in entity:
            if (child.tag == "attribute"):
                attributeList.append(child.items())
            else:
                keyList.append(child.text)          #can retrieve key List after here
        
        tableKeyList.append(keyList)

        for attribute in attributeList:
            isReferredAttribute = False;
            columnId = -1
            columnName = ""
            columnType = XSDType.STRING
            for name, value in attribute:
                if (name == "id"):
                    columnId = int(value)
                elif (name == "name"):
                    isReferredAttribute = False
                    columnName = value.replace(" ", "")
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
                    primKey = Constraint(column = column, constraintType = ConstraintType.PRIMARY_KEY)
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
            foreignKey = Constraint(column = col, constraintType = ConstraintType.FOREIGN_KEY, referredTable = referredTable.tableId, referredCol = key.colId)
            foreignKey.save()
            columnId = columnId + 1
     
    for i in range(len(tableKeyList)):
        table = tableEntityList[i]
        keyList = tableKeyList[i]
        for key in keyList:
            parsedKey = key.split(",")
            colNames = ""
            for columnId in parsedKey:
                print(table.name, columnId)
                column = getColumnById(columnId, table)     #each columnId in key must refer to an existed column
                colNames += column.name + ","
            colNames = colNames[:-1]
            newKey = Key(table = table, colIds = key, colNames = colNames)
            newKey.save()

    return tableEntityList

def getColumnById(columnId, table):
    for column in table.columns.all():
        if (column.colId == (columnId)):
            return column
    return ''

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
                tableName = value.replace(" ", "")
        table = Table(model = erModel, tableId = tableId, name = tableName, isEntity = False)
        table.save()

        attributeList = []
        columnList = []

        for child in relationship:
            attributeList.append(child.items())
        
        for attribute in attributeList:
            columnId = -1
            columnName = ""
            columnType = XSDType.STRING
            isReferredAttribute = False
            isAggregate = False
            minOccur = 1
            maxOccur = 1
            for name, value in attribute:
                if (name == "name"):       
                    isReferredAttribute = False
                    isAggregate = False
                    columnName = value.replace(" ", "")
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
                        maxOccur = -1
                    else:
                        maxOccur = int(value)

            if (not isReferredAttribute and not isAggregate):
                column = Column(table = table, colId = columnId, name = columnName, tp=columnType, minOccur = minOccur, maxOccur = maxOccur)
                column.save()
                columnList.append(column)
            elif (isReferredAttribute):
                columnList.extend(getReferredColumn(referredId, tableEntityList, generateId(columnList), table, minOccur, maxOccur))
        
        tableRelationshipList.append(table) 
    
    return tableRelationshipList

def getReferredColumn(entity_id, tableEntityList, nextId, originTable, minOccur=1, maxOccur=1):
    referredColumns = []
    for table in tableEntityList:
        if (table.tableId == entity_id):
            primKey = getPrimaryKey(table)
            for column in primKey:
                columnId = nextId
                nextId = nextId + 1
                columnName = column.name
                columnType = column.tp
                newColumn = Column(table = originTable, colId = columnId, name = columnName, tp = columnType, minOccur=minOccur, maxOccur=maxOccur)
                newColumn.save()

                foreignKeyConstraint = Constraint(column = newColumn, constraintType = ConstraintType.FOREIGN_KEY, referredTable = table.tableId, referredCol = column.colId)
                foreignKeyConstraint.save()

                primKeyConstraint = Constraint(column = newColumn, constraintType = ConstraintType.PRIMARY_KEY)
                primKeyConstraint.save()
                
                referredColumns.append(newColumn)
    return referredColumns

def getPrimaryKey(table):
    primKey = []
    for column in table.columns.all():
        for constraint in column.constr.all():
            constraintType = constraint.constraintType
            if (constraintType == ConstraintType.PRIMARY_KEY):
                primKey.append(column)
    return primKey

def parseType(tp):
    types = Type.objects.all()
    for _type in types:
        if (tp == _type.text):
            return _type.text

    if (tp == 'string'):
        return XSDType.STRING
    elif(tp == 'date'):
        return XSDType.DATE
    elif (tp == 'integer'):
        return XSDType.INTEGER
    elif (tp == 'decimal'):
        return XSDType.NUMERIC
    elif (tp == 'boolean'):
        return XSDType.BOOLEAN
    else:
        return XSDType.STRING #default
        
def generateId(columnList):
    genId = 1
    for column in columnList:
        colId = int(column.colId)
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

    # table0 = tableEntityList[0]
    # keys = table0.keys.all()
    # key1 = keys[1]
    # setKey(table0, key1)

    for table in tableEntityList:
        print("ENTITY TABLE:"+ str(table.tableId), table.name)    
        columnList = table.columns.all()
        for column in columnList:
            print("Column:"+ str(column.colId), column.name, column.tp)
            constraintList = column.constr.all()
            for constraint in constraintList:
                print(constraint.constraintType, constraint.referredTable, constraint.referredCol)
        for key in table.keys.all():
            print(str(key))

    # format: [[relationTableId, referredTableId...], [relationTableId, referredTableId...]]
    allNestedList = []
    for table in tableRelationshipList:
        # format: [relationTableId, referredTableId...]
        nestedList = []
        nestedList.append(table.tableId)
        
        print("RELATIONSHIP TABLE:"+ str(table.tableId), table.name)
        columnList = table.columns.all()
        for column in columnList:
            print("Column:"+ str(column.colId), column.name, column.tp)
            constraintList = column.constr.all()
            for constraint in constraintList:
                print(constraint.constraintType, constraint.referredTable, constraint.referredCol)
                nestedList.append(constraint.referredTable)

        allNestedList.append(nestedList)
    
    return allNestedList

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
from .models import XSDType, ConstraintType, Table, Column, Type
from xml.etree import ElementTree
from collections import deque
import xml.dom.minidom

# Global dictionary
tableDictionary = {}
relationDictionary = {}

def generateXMLSchema(erModel):
    tableList = erModel.tables.all()

    initial_xml_string = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    initial_xml_string += "<xs:schema xmlns=\"\" "
    initial_xml_string += "xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" "
    initial_xml_string += "xmlns:msdata=\"urn:schemas-microsoft-com:xml-msdata\">"
    initial_xml_string += "<xs:element name=\""+erModel.name+"\" msdata:IsDataSet=\"true\">"

    type_xml_string = addSimpleType(erModel)


    xml_string = "<xs:complexType>"
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
        #xml_string += "1" + len(primKeys)
        keyName = erModel.name+"Key"+str(i)
        i = i+1
        selector = ".//"+table.name
        xml_string += convertPrimKey(keyName, selector, primKeys)
        if (table.isEntity == True):
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
    dom = xml.dom.minidom.parseString(initial_xml_string + type_xml_string + xml_string)
    prettyString = dom.toprettyxml()
    return prettyString

def addSimpleType(erModel):
    xml = ""
    allTypes = Type.objects.all()
    tables = erModel.tables.all()
    for tp in allTypes:
        tpName = tp.text
        tpContent = tp.content
        for table in tables:
            for column in table.columns.all():
                columnTp = column.tp
                if columnTp == tpName:
                    xml += tpContent
    return xml

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
        s += " maxOccurs=\"" + maxOccur + "\""
    s += "/>"
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
    xType = columnType
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

# Indentation does not work because of Django rendering
def generateNestedXMLSchema(erModel, rootElements=None):
    tableList = erModel.tables.all()
    if (rootElements is None):
    	rootElements = []
    	rootElements.append(tableList[0])
    # store tables in tableDictionary with key as tableId and value as table
    # store tables in relationDictionary with key as relatedTableId and value as [relationTable(s)]
    for table in tableList:
        if (table.isEntity):
            tableDictionary[str(table.tableId)] = table
        else:
            createRelationshipDictionary(table)

    xml_string = ""
    xml_string += xmlDefinitionStart()
    xml_string += schemaOpen()

    xml_string += elementOpen(
        "NewDataSet",   # name 
        "true",
        "",             # type
        "",             # maxOccurs
        ""              # minOccurs
        )

    xml_string += addSimpleType(erModel)

    xml_string += complextypeOpen()
    xml_string += choiceOpen("unbounded")

    # # store tables in tableDictionary with key as tableId and value as table
    # for table in tableList:
    #     if (table.isEntity):
    #         tableDictionary[str(table.tableId)] = table

    # for table in tableList:
    #     if (not table.isEntity):
    #         # recreate relationships between tables
    #         relationships = createRelationships(table)

    #         xml_string += createNestedEntity(table, relationships)
    
    # Retrieve all root elements
    for rootElement in rootElements:
        if (not rootElement.isEntity):
            # Recreate relationships from the root element -- is relation table
            relationships = createRelationships(rootElement)
            xml_string += createNestedEntity(rootElement, relationships)
        else:
            # Recreate relationships from the root element -- is entity table
            relationshipList = relationDictionary[rootElement.tableId]
            xml_string += createNestedEntity2(rootElement, relationshipList)

    xml_string += choiceClose()
    xml_string += complextypeClose()
    
    xml_string += elementClose()
    xml_string += schemaClose()

    #if there is an error in xml.dom.minidom NoneType has no 'replace' function
    #go to python27/Lib/xml/dom/minidom.py and comment line 294 + 295
    dom = xml.dom.minidom.parseString(xml_string)
    prettyString = dom.toprettyxml()
    return prettyString

def xmlDefinitionStart():
    return "<?xml version=\"1.0\" encoding=\"utf-8\"?>"

def schemaOpen():
    return "<xs:schema xmlns=\"\" xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" xmlns:msdata=\"urn:schemas-microsoft-com:xml-msdata\">"

def schemaClose():
    return "</xs:schema>"

def sequenceOpen():
    return "<xs:sequence>"

def sequenceClose():
    return "</xs:sequence>"

def complextypeOpen():
    return "<xs:complexType>"

def complextypeClose():
    return "</xs:complexType>"

def choiceOpen(maxOccurs):
    return "<xs:choice maxOccurs=\"" + maxOccurs+ "\">"

def choiceClose():
    return "</xs:choice>"

def elementOpen(name, isDataSet, elementType, maxOccurs, minOccurs):
    element_tag = "<xs:element"

    if (name != ""):
        element_tag += " name=\"" + name + "\""

    if (isDataSet != ""):
        element_tag += " msdata:IsDataSet=\"" + isDataSet + "\""

    if (elementType != ""):
        element_tag += " type=\"" + elementType + "\""

    if (maxOccurs != ""):
        element_tag += " maxOccurs=\"" + maxOccurs + "\""

    if (minOccurs != ""):
        element_tag += " minOccurs=\"" + minOccurs + "\""

    element_tag += ">"

    return element_tag

def elementClose():
    return "</xs:element>"

def createRelationshipDictionary(relationTable):
    columnList = relationTable.columns.all()
    for column in columnList:
        constraintList = column.constr.all()
        for constraint in constraintList:
            if (constraint.constraintType == ConstraintType.FOREIGN_KEY):
                referredTableId = constraint.referredTable
                relationTableList = []
                if str(referredTableId) in relationDictionary:
                    # Merge list (extend) then add (append) relationTable
                    relationTableList = relationDictionary[str(referredTableId)]
                    add = True
                    for relationTableListItem in relationTableList:
                        if (relationTableListItem == relationTable):
                            add = False
                    if (add):
                        relationTableList.extend(relationDictionary[str(referredTableId)])
                else:
                    relationTableList.append(relationTable)
                    relationDictionary[str(referredTableId)] = relationTableList

def createRelationships(table):
    relationships = {}
    columnList = table.columns.all()
    for column in columnList:
        constraintList = column.constr.all()
        for constraint in constraintList:
            if (constraint.constraintType == ConstraintType.FOREIGN_KEY):
                referredTableId = constraint.referredTable
                relationships[str(referredTableId)] = tableDictionary[str(referredTableId)]

    return relationships

def getPrimaryKeys(table):
    xml = ""

    keyName = "NewDataSet" + "Key" + str(table.name)
    primKeys = getPrimaryKey(table)
    selector = ".//"+table.name
    xml += convertPrimKey(keyName, selector, primKeys)

    return xml

def getForeignKeys(table, otherTable):
    xml = ""
    foreignKeys = getPrimaryKey(otherTable)
    if (len(foreignKeys) > 0):
        name = table.name + "To" + otherTable.name + "Ref"
        selector = ".//" + table.name
        keyName =  "NewDataSet" + "Key" + str(otherTable.name)
        xml += convertForeignKey(name, keyName, selector, foreignKeys)

    return xml

# Modified - table = relation
def createNestedEntity(table, relationships):
    queue = deque([])
    queue.append(table)
    for key in relationships.keys():
        queue.append(relationships[key])

    return createEntity(queue, 0)

# table = entity
def createNestedEntity2(table, relationshipList):
    #table = queue[index]
    tableName = table.name

    xml = elementOpen(tableName, "", "", "", "")
    xml += complextypeOpen()
    xml += sequenceOpen()

    columnList = table.columns.all()
    for column in columnList:
        xml += convertColumn(column)

    # add nested element here
    for relationship in relationshipList:
        relationships = createRelationships(relationship)
        del relationships[str(table.tableId)]
        queue = deque([])
        queue.append(relationship)
        for key in relationships.keys():
            queue.append(relationships[key])
        xml += createEntity2(queue, 0)

    xml += sequenceClose()
    xml += complextypeClose()

    # Set primary keys
    xml += getPrimaryKeys(table)
        
    xml += elementClose()

    return xml

# Modified - for if the first in queue is a relation table
def createEntity(queue, index):
    table = queue[index]
    tableName = table.name

    xml = elementOpen(tableName, "", "", "", "")
    xml += complextypeOpen()
    xml += sequenceOpen()

    columnList = table.columns.all()
    for column in columnList:
        xml += convertColumn(column)

    xml += sequenceClose()
    xml += complextypeClose()

    # add nested element here
    # since index 1 will be a relationship table,
    # all other tables more than 1 will be nested within table index 1 
    if (index + 1 < len(queue) and index + 1 < 2):
        xml += createEntity(queue, index + 1)

    # Set primary keys
    xml += getPrimaryKeys(table)
        
    xml += elementClose()

     # add nested element here
    # since index 1 will be a relationship table,
    # all other tables more than 1 will be nested within table index 1 
    if (index + 1 < len(queue) and index + 1 >= 2):
        xml += createEntity(queue, index + 1)

    return xml

# Modified - for if the first in queue is an entity table
def createEntity2(queue, index):
    table = queue[index]
    tableName = table.name

    xml = elementOpen(tableName, "", "", "", "")
    xml += complextypeOpen()
    xml += sequenceOpen()

    columnList = table.columns.all()
    for column in columnList:
        xml += convertColumn(column)

    # add nested element here
    if (index + 1 < len(queue) and index + 1 < 2):
        xml += createEntity2(queue, index + 1)

    xml += sequenceClose()
    xml += complextypeClose()

    # add nested element here
    # since index 1 will be a relationship table,
    # all other tables more than 1 will be nested within table index 1 
    if (index + 1 < len(queue) and index + 1 >= 2):
        xml += createEntity2(queue, index + 1)

    # Set primary keys
    xml += getPrimaryKeys(table)
        
    xml += elementClose()

    return xml






# def createNestedEntity(table, relationships):
#     queue = deque([])
#     index = 0
#     for key in sorted(relationships.keys()):
#         queue.append(relationships[key])
#         if (index == 0):
#             queue.append(table)
#         index = index + 1

#     return createEntity(queue, 0)

# def createEntity(queue, index):
#     table = queue[index]
#     tableName = table.name

#     xml = elementOpen(tableName, "", "", "", "")
#     xml += complextypeOpen()
#     xml += sequenceOpen()

#     columnList = table.columns.all()
#     for column in columnList:
#         xml += convertColumn(column)

#     # add nested element here
#     if (index + 1 < len(queue) and index + 1 < 3):
#         xml += createEntity(queue, index + 1)

#     xml += sequenceClose()
#     xml += complextypeClose()

#     # add nested element here
#     # since index 1 will be a relationship table,
#     # all other tables more than 1 will be nested within table index 1 
#     if (index + 1 < len(queue) and index + 1 >= 3):
#         xml += createEntity(queue, index + 1)

#     # Set primary keys
#     xml += getPrimaryKeys(table)

#     # Set foreign keys
#     if (not table.isEntity and index - 1 > -1):
#         xml += getForeignKeys(table, queue[index - 1])
#     if (not table.isEntity and index + 1 < len(queue)):
#         xml += getForeignKeys(table, queue[index + 1])
        
#     xml += elementClose()

#     return xml
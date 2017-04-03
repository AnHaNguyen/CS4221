from .models import XSDType, ConstraintType, Table, Column, Type
from xml.etree import ElementTree
from collections import deque
import xml.dom.minidom

# Global dictionary
tableDictionary = {}

def generateXMLSchema(erModel):
    tableList = erModel.tables.all()

    initial_xml_string = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
    initial_xml_string += "<xs:schema id=\"MyDataSet\" xmlns=\"\" "
    initial_xml_string += "xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" "
    initial_xml_string += "xmlns:msdata=\"urn:schemas-microsoft-com:xml-msdata\">"
    initial_xml_string += "<xs:element name=\"NewDataSet\" msdata:IsDataSet=\"true\">"

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

# Indentation does not work because of Django rendering
def generateNestedXMLSchema(erModel):
    tableList = erModel.tables.all()

    xml_string = ""
    xml_string += xmlDefinitionStart()
    xml_string += schemaOpen("MyDataSet")

    xml_string += elementOpen(
        "NewDataSet",   # name 
        "true",
        "",             # type
        "",             # maxOccurs
        ""              # minOccurs
        )

    # type_xml_string = addSimpleType(erModel)


    xml_string += complextypeOpen()
    xml_string += choiceOpen("unbounded")

    # store tables in tableDictionary with key as tableId and value as table
    for table in tableList:
        if (table.isEntity):
            tableDictionary[str(table.tableId)] = table

    for table in tableList:
        if (not table.isEntity):
            # recreate relationships between tables
            relationships = createRelationships(table)

            xml_string += createNestedEntity(table, relationships)
    
    xml_string += choiceClose()
    xml_string += complextypeClose()
    
    # #convert keys
    # primKeySet = []
    # i = 1
    # for table in tableList:
    #     keySet = []
    #     primKeys = getPrimaryKey(table)
    #     keyName = "NewDataSetKey"+str(i)
    #     i = i+1
    #     selector = ".//"+table.name
    #     xml_string += convertPrimKey(keyName, selector, primKeys)
    #     if (table.isEntity == "1"):
    #         keySet.append(keyName)
    #         keySet.append(table.name)
    #         keySet.append(str(table.tableId))
    #         primKeySet.append(keySet)

    # i = 0
    # for i in range(len(primKeySet)):
    #     keyName, tableName, tableId = primKeySet[i][0:3]
    #     for table in tableList:
    #         foreignKeys = getForeignKeyToTable(table, tableId)
    #         if (len(foreignKeys) > 0):
    #             name = table.name + "To" +tableName + "Ref"
    #             selector = ".//"+table.name
    #             xml_string += convertForeignKey(name, keyName, selector, foreignKeys)
    
    xml_string += elementClose()
    xml_string += schemaClose()

    #if there is an error in xml.dom.minidom NoneType has no 'replace' function
    #go to python27/Lib/xml/dom/minidom.py and comment line 294 + 295
    dom = xml.dom.minidom.parseString(xml_string)
    prettyString = dom.toprettyxml()
    return prettyString

def xmlDefinitionStart():
    return "<?xml version=\"1.0\" encoding=\"utf-8\"?>"

def schemaOpen(id):
    return "<xs:schema id=\"" + id + "\" xmlns=\"\" xmlns:xs=\"http://www.w3.org/2001/XMLSchema\" xmlns:msdata=\"urn:schemas-microsoft-com:xml-msdata\">"

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

def createRelationships(table):
    # tableName = table.name
    relationships = {}
    columnList = table.columns.all()
    for column in columnList:
        constraintList = column.constr.all()
        for constraint in constraintList:
            if (constraint.constraintType == ConstraintType.FOREIGN_KEY):
                referredTableId = constraint.referredTable
                relationships[str(referredTableId)] = tableDictionary[str(referredTableId)]

    return relationships

def createNestedEntity(table, relationships):
    queue = deque([])
    index = 0
    for key in sorted(relationships.keys()):
        queue.append(relationships[key])
        if (index == 0):
            queue.append(table)
        index = index + 1

    return createEntity(queue)

def createEntity(queue):
    table = queue.popleft()
    tableName = table.name

    xml = ""
    xml = elementOpen(tableName, "", "", "", "")
    xml += complextypeOpen()
    xml += sequenceOpen()

    columnList = table.columns.all()
    for column in columnList:
        xml += convertColumn(column)

    # add nested element here
    if (len(queue) > 0):
        queue.popleft
        xml += createEntity(queue)

    xml += sequenceClose()
    xml += complextypeClose()
    xml += elementClose()
    return xml
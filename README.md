# CS4221 - ER Model to XML Schema Generator
## Logic module functions:
  + setKey(table, key): set the primary key of this table with this candidate key (refer to Key model in models.py)
  (to retrieve all the candidate keys of a table: call "table.keys.all().colNames", output is a list of column names as string 
  (composite key has each column separated by a comma) eg: ["UName,SName", "Matric,SName", ...])
  + exportXMLToFile(fileName, xmlString): create a file with name as fileName and content as xmlString
  + parseXMLString(erModel): create the tables in the erModel using the erModel.text (ie: input template xml)
 
## RelationalXMLSchema module functions:
  + generateXMLSchema(erModel): create the xmlSchema of this erModel (relational type)
  + generateNestedXMLSchema(erModel, re): create the xmlSchema of this erModel (nested type), re contains all root elements for the nested XML schema

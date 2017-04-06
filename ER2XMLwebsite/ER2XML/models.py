from django.db import models
from enum import Enum

class ConstraintType(Enum): 
    NOT_NULL = "NN"
    UNIQUE = "UNI"
    PRIMARY_KEY = "PK"
    FOREIGN_KEY = "FK"

class XSDType(Enum):
    STRING = "xs:string"
    DATE = "xs:date"
    NUMERIC = "xs:decimal"
    BOOLEAN = "xs:boolean"
    INTEGER = "xs:integer"
    # Pid = "empid"

class Type(models.Model):
    name = models.CharField(max_length=200)
    text = models.CharField(max_length=16)
    content = models.TextField(null=True)

    def __str__(self):
        return self.name

class ERModel(models.Model):
    name = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.name

class Table(models.Model):
    isEntity = models.BooleanField()
    name = models.CharField(max_length=16)
    model = models.ForeignKey('ER2XML.ERModel',related_name='tables')
    tableId = models.CharField(max_length=3)

    def __str__(self):
        return self.name

class XMLSchema(models.Model):
    model = models.ForeignKey('ER2XML.ERModel',related_name='schema')
    text = models.TextField(null=True)

    def __str__(self):
        return self.text

class Column(models.Model):
    TYPE = (
        (XSDType.STRING,"STRING"),
        (XSDType.INTEGER, "INTEGER"),
        (XSDType.DATE, "DATE"),
        (XSDType.BOOLEAN, "BOOLEAN"),
        (XSDType.NUMERIC, "DECIMAL"),
    )
    table = models.ForeignKey('ER2XML.Table',related_name='columns')
    name = models.CharField(max_length=16)
    tp = models.CharField(max_length = 10, default = XSDType.STRING)
    minOccur = models.IntegerField(null=True, default = 1)
    maxOccur = models.IntegerField(null=True, default = 1)
    colId = models.CharField(max_length=3)
    def __str__(self):
        return self.name

class Constraint(models.Model):     #define each constraint
    CONSTRAINT_TYPE = (
        (ConstraintType.NOT_NULL,"NOT_NULL"),
        (ConstraintType.UNIQUE,"UNIQUE"),
        (ConstraintType.PRIMARY_KEY,"PRIMARY_KEY"),
        (ConstraintType.FOREIGN_KEY,"FOREIGN_KEY"),
    )
    constraintType = models.CharField(
        max_length = 3,
        choices = CONSTRAINT_TYPE,
        default = ConstraintType.NOT_NULL,
    )
    column = models.ForeignKey('ER2XML.Column', related_name='constr')
    #table = models.ForeignKey('ER2XML.Table', related_name='constraints')
    #only use for foreignkey constr
    referredTable = models.IntegerField(default = 0)
    referredCol = models.IntegerField(default = 0)

class Key(models.Model):
    table = models.ForeignKey('ER2XML.Table', related_name='keys')
    colIds = models.CharField(max_length=10)    #for single key: "1", for composite key: "1,2"
    colNames = models.CharField(max_length=50)  #for single key: "SName", for composite key: "SName,Matric"
    def __str__(self):
        return self.colNames

# class XMLAttribute(models.Model):
#     xElement
#     name
#     type
#     use

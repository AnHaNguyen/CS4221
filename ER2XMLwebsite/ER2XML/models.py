from django.db import models
from enum import Enum

# class Document(models.Model):
#     docfile = models.FileField(upload_to='documents/')

class ConstraintType(Enum): 
    NOT_NULL = "NN"
    UNIQUE = "UNI"
    PRIMARY_KEY = "PK"
    FOREIGN_KEY = "FK"

class XSDType(Enum):
    STRING = "xs:string"
    DATE = "xs:date"
    INTEGER = "xs:integer"
    DECIMAL = "xs:decimal"
    BOOLEAN = "xs:boolean"
    SHORT = "xs:short"
    # Pid = "empid"

class ERModel(models.Model):
    name = models.CharField(max_length=200)
    text = models.TextField()

    def __str__(self):
        return self.name

class Table(models.Model):
    name = models.CharField(max_length=16)
    model = models.ForeignKey('ER2XML.ERModel',related_name='tables')

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
        (XSDType.INTEGER, "NUMERIC"),
        (XSDType.DATE, "DATE"),
        (XSDType.BOOLEAN, "BOOLEAN"),
        (XSDType.DECIMAL, "DECIMAL"),
        (XSDType.SHORT, "SHORT"),
    )
    table = models.ForeignKey('ER2XML.Table',related_name='columns')
    name = models.CharField(max_length=16)
    tp = models.CharField(max_length = 10, choices = TYPE, default = XSDType.STRING)
    minOccur = models.IntegerField(null=True)
    maxOccur = models.IntegerField(null=True)
    
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
    column = models.ForeignKey('ER2XML.Column')
    table = models.ForeignKey('ER2XML.Table', related_name='constraints')

# class XMLAttribute(models.Model):
#     xElement
#     name
#     type
#     use
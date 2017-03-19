from .Type import *
class WeakEntity:
    def __init__(self, fromEntity, toEntity):
        self.fromEntity = fromEntity
        self.toEntity = toEntity
        self.foreignKey = []
        self.datatype = []    

    def getFromEntity(self):
        return self.fromEntity;

    def getToEntity(self):
        return self.toEntity;

    def setForeignKey(self, key):
        self.foreignKey = key;

    def getForeignKey(self):
        return self.foreignKey;

    def setDataType(self, datatype):
        self.datatype = datatype

    def getDataType(self):
        return self.datatype
class WeakEntity:
    def __init__(self, fromEntity, toEntity):
        self.fromEntity = fromEntity
        self.toEntity = toEntity
        
    def getFromEntity(self):
        return self.fromEntity;

    def getToEntity(self):
        return self.toEntity;


from Type import *
class WeakEntity:
    def __init__(self, id):
        self.id = id             #id as in xml file
        self.datatype = Type.STRING     #type from Type enum class(let default be STRING)

    def getId(self):
        return self.id; 
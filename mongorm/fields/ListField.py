from mongorm.fields.BaseField import BaseField

class ListField(BaseField):
	_resyncAtSave = True
	
	def __init__( self, documentClass, *args, **kwargs ):
		super(ListField, self).__init__( *args, **kwargs )
		
		self.itemClass = documentClass
	
	def getDefault( self ):
		return []
	
	def fromPython( self, pythonValue ):
		return [ self.itemClass.fromPython(value) for value in pythonValue ]
	
	def toPython( self, bsonValue ):
		if bsonValue is None:
			bsonValue = []
		return [ self.itemClass.toPython(value) for value in bsonValue ]

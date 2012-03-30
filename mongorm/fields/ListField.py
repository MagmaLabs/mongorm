from mongorm.fields.BaseField import BaseField

class ListField(BaseField):
	_resyncAtSave = True
	
	def __init__( self, documentClass, *args, **kwargs ):
		super(ListField, self).__init__( *args, **kwargs )
		
		self.itemClass = documentClass
	
	def getDefault( self ):
		return []
	
	def toQuery( self, pythonValue, dereferences=[] ):
		if not isinstance(pythonValue, (list, set)):
			return self.itemClass.fromPython( pythonValue )
		return self.fromPython( pythonValue )
	
	def fromPython( self, pythonValue ):
		return [ self.itemClass.fromPython(value) for value in pythonValue ]
	
	def toPython( self, bsonValue ):
		if bsonValue is None:
			bsonValue = []
		if not isinstance(bsonValue, list):
			# if someone upgrades a field from a singular to a list, let them do it if possible
			return [ self.itemClass.toPython(bsonValue) ]
		return [ self.itemClass.toPython(value) for value in bsonValue ]

	def setOwnerDocument( self, ownerDocument ):
		super(ListField, self).setOwnerDocument( ownerDocument )
		self.itemClass.setOwnerDocument( ownerDocument )
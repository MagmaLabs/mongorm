from mongorm.fields.BaseField import BaseField

class DictField(BaseField):
	_resyncAtSave = True

	def __init__( self, *args, **kwargs ):
		super(DictField, self).__init__( *args, **kwargs )

	def getDefault( self ):
		return {}

	def fromPython( self, pythonValue ):
		if pythonValue is None:
			pythonValue = {}
		return pythonValue

	def toPython( self, bsonValue ):
		if bsonValue is None:
			bsonValue = {}
		return bsonValue
	
	def toQuery( self, pythonValue, dereferences=[] ):
		return {
			'.'.join( dereferences ): pythonValue
		}
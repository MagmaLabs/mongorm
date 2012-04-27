from mongorm.fields.BaseField import BaseField

class BooleanField(BaseField):
	def fromPython( self, pythonValue, dereferences=[] ):
		return bool(pythonValue)
	
	def toPython( self, bsonValue ):
		return bool(bsonValue)

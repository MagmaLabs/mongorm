from mongorm.fields.BaseField import BaseField

class IntegerField(BaseField):
	def fromPython( self, pythonValue ):
		return int(pythonValue)
	
	def toPython( self, bsonValue ):
		return int(bsonValue)
IntField = IntegerField

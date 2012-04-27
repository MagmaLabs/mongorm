from mongorm.fields.BaseField import BaseField

class StringField(BaseField):
	def fromPython( self, pythonValue, dereferences=[] ):
		return unicode(pythonValue)
	
	def toPython( self, bsonValue ):
		return unicode(bsonValue)
	
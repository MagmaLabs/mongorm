from mongorm.fields.BaseField import BaseField

class StringField(BaseField):
	def fromPython( self, pythonValue ):
		return unicode(pythonValue)
	
	def toPython( self, bsonValue ):
		return unicode(bsonValue)
	
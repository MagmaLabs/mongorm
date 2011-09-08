from mongorm.fields.BaseField import BaseField

from datetime import datetime

class DateTimeField(BaseField):
	def fromPython( self, pythonValue ):
		if not isinstance(pythonValue, datetime):
			raise ValueError, "Value must be a datetime object"
		return pythonValue
	
	def toPython( self, bsonValue ):
		return bsonValue
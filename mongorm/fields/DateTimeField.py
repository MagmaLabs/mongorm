from mongorm.fields.BaseField import BaseField

from datetime import datetime

class DateTimeField(BaseField):
	def fromPython( self, pythonValue, dereferences=[], modifier=None ):
		if pythonValue is not None and not isinstance(pythonValue, datetime):
			raise ValueError, "Value must be a datetime object not %r" % (pythonValue,)
			
		return pythonValue
	
	def toPython( self, bsonValue ):
		return bsonValue
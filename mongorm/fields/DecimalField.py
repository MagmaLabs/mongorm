from mongorm.fields.BaseField import BaseField

from decimal import Decimal

from datetime import datetime

class DecimalField(BaseField):
	def fromPython( self, pythonValue, dereferences=[], modifier=None ):
		if isinstance(pythonValue, (basestring, int, float)):
			pythonValue = Decimal(pythonValue)
		if not isinstance(pythonValue, Decimal):
			raise ValueError, "Value (%s: %s) must be a Decimal object, or must be able to be passed to the Decimal constructor" % (type(pythonValue), pythonValue,)
		return str(pythonValue)
	
	def toPython( self, bsonValue ):
		return Decimal(bsonValue)
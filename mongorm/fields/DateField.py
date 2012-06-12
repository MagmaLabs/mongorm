from mongorm.fields.BaseField import BaseField

import time
from datetime import datetime, date

class DateField(BaseField):
	def fromPython( self, pythonValue, dereferences=[], modifier=None ):
		# convert datetime objects to just a date
		if isinstance(pythonValue, datetime):
			pythonValue = pythonValue.date( )
		
		# convert string dates to a date object
		if isinstance(pythonValue, basestring):
			try:
				pythonValue = date.fromtimestamp( time.mktime( time.strptime( pythonValue, '%Y-%m-%d' ) ) )
			except:
				raise ValueError, "String format of date must be YYYY-MM-DD"
		
		# make sure we ended up with a date() object
		if not isinstance(pythonValue, date):
			raise ValueError, "Value must be a date object"
		
		# convert it to a string since mongo doesn't have a date-only type and datetime
		# searches would be wrong. this format should still allow sorting, etc.
		return pythonValue.strftime( '%Y-%m-%d' )
	
	def toPython( self, bsonValue ):
		if bsonValue is None or bsonValue == '':
			return None
		if isinstance(bsonValue, datetime):
			return bsonValue.date( )
		if isinstance(bsonValue, date):
			return basonValue
		return date.fromtimestamp( time.mktime( time.strptime( bsonValue, '%Y-%m-%d' ) ) )
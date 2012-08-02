try:
	from pymongo import objectid
except ImportError:
	from bson import objectid

from mongorm.fields.BaseField import BaseField

class ObjectIdField(BaseField):
	def fromPython( self, pythonValue, dereferences=[], modifier=None ):
		if pythonValue is not None:
			return objectid.ObjectId( unicode(pythonValue) )
		else:
			return None
	
	def toPython( self, bsonValue ):
		return bsonValue
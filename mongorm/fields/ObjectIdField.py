import pymongo.objectid

from mongorm.fields.BaseField import BaseField

class ObjectIdField(BaseField):
	def fromPython( self, pythonValue, dereferences=[] ):
		if pythonValue is not None:
			return pymongo.objectid.ObjectId( unicode(pythonValue) )
		else:
			return None
	
	def toPython( self, bsonValue ):
		return bsonValue
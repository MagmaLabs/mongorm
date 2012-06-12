class BaseField(object):
	_resyncAtSave = False
	
	def __init__( self, default=None, unique=False, dbField=None, primaryKey=False ):
		self.default = default
		self.unique = unique
		self.dbField = dbField
		self.primaryKey = primaryKey
		if primaryKey:
			self.dbField = '_id'
	
	def fromPython( self, pythonValue, dereferences=[], modifier=None ):
		raise NotImplementedError

	def toPython( self, bsonValue ):
		raise NotImplementedError
	
	def toQuery( self, pythonValue, dereferences=[] ):
		return self.fromPython( pythonValue )
	
	def getDefault( self ):
		return self.default
	
	def setOwnerDocument( self, ownerDocument ):
		self.ownerDocument = ownerDocument
	
	def optimalIndex( self ):
		return self.dbField
from mongorm.connection import getDatabase
from mongorm.queryset.QuerySet import QuerySet

class QuerySetManager(object):
	def __init__( self ):
		self.collection = None
	
	def __get__( self, instance, owner ):
		if instance is not None:
			# Document class being accessed, not an object
			return self
		
		if self.collection is None:
			database = getDatabase( )
			self.collection = database[owner._collection]
		
		return QuerySet( owner, self.collection )
	
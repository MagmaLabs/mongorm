from mongorm.connection import getDatabase
from .Aggregation import Aggregation

class AggregationManager(object):
	def __init__( self ):
		self.collection = None
	
	def __get__( self, instance, owner ):
		if instance is not None:
			# Document class being accessed, not an object
			return self
		
		# this should be fast, it's just a thin wrapper to get a collection?
		groupName = getattr(owner, 'database_group', 'default')
		database = getDatabase( groupName )
		self.collection = database[owner._collection]
		
		return Aggregation( owner, self.collection )

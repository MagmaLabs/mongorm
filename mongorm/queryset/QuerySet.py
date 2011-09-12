from mongorm.queryset.Q import Q

class QuerySet(object):
	def __init__( self, document, collection, query=None ):
		self.document = document
		self.collection = collection
		self.orderBy = []
		if query is None:
			self.query = Q( )
		else:
			self.query = query
	
	def get( self, query=None, **search ):
		if query is None:
			query = Q( **search )
		newQuery = self.query & query
		#self._mergeSearch( search )
		#print 'get:', newQuery.toMongo( self.document )
		result = self.collection.find( newQuery.toMongo( self.document ), limit=1 )
		if result.count() == 0:
			raise self.document.DoesNotExist( )
		elif result.count() > 1:
			raise self.document.MultipleObjectsReturned( )
		else:
			result = result[0]
		
		return self.document( )._fromMongo( result )
	
	def all( self ):
		return self
	
	def filter( self, query=None, **search ):
		if query is None:
			query = Q( **search )
		newQuery = self.query & query
		#print 'filter:', newQuery.toMongo( self.document )
		return QuerySet( self.document, self.collection, query=newQuery )
	
	def count( self ):
		return self.collection.find( self.query.toMongo( self.document ) ).count( )
	
	def delete( self ):
		self.collection.remove( self.query.toMongo( self.document ) )
	
	def update( self, upsert=False, safeUpdate=False, **actions ):
		updates = {}
		
		for action, value in actions.iteritems( ):
			assert '__' in action, 'Action "%s" not legal for update' % (action,)
			modifier, fieldName = action.split( '__', 1 )
			assert modifier in ['set', 'inc', 'dec']
			
			if '$'+modifier not in updates:
				updates['$'+modifier] = {}
			
			updates['$'+modifier].update( {
				fieldName.replace( '__', '.' ): value
			} )
		
		if '$set' not in updates:
			updates['$set'] = {}
		
		updates['$set'].update( self.query.toMongo( self.document, forUpdate=True ) )

		#print 'query:', self.query.toMongo( self.document )
		#print 'update:', updates
		
		ret = self.collection.update( self.query.toMongo( self.document ), updates, upsert=upsert, safe=safeUpdate )
		if 'n' in ret:
			return ret['n']
	
	def order_by( self, *fields ):
		self.orderBy.extend( fields )
		return self
	
	def __iter__( self ):
		#print 'iter:', self.query.toMongo( self.document ), self.collection
		items = self.collection.find( self.query.toMongo( self.document ) )
		for item in items:
			yield self.document( )._fromMongo( item )
	
	def __getitem__( self, index ):
		if isinstance(index, int):
			getOne = True
			skip = index
			limit = 1
		elif isinstance(index, slice):
			getOne = False
			skip = index.start or 0
			limit = index.stop - skip
			assert index.step is None, "Slicing with step not supported by mongorm"
		else:
			assert False, "item not an index"
		
		print self.query.toMongo( self.document )
		items = self.collection.find( self.query.toMongo( self.document ), skip=skip, limit=limit )
		
		if getOne:
			try:
				item = items[0]
			except IndexError:
				raise IndexError # re-raise our own index error
			document = self.document( )._fromMongo( item )
			return document
		else:
			def _yieldItems():
				for item in items:
					document = self.document( )._fromMongo( item )
					yield document
			return _yieldItems( )
	
	def first( self ):
		try:
			return self[0]
		except IndexError:
			return None
	
	def __call__( self, **search ):
		return self.filter( **search )
from mongorm.queryset.Q import Q

class QuerySet(object):
	def __init__( self, document, collection, query=None ):
		self.document = document
		self.collection = collection
		self.orderBy = []
		self._savedCount = None
		self._savedItems = None
		self._savedBuiltItems = None
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
		
		# limit of 2 so we know if multiple matched without running a count()
		result = self.collection.find( newQuery.toMongo( self.document ), limit=2 )
		
		try:
			result = result[0]
		except (KeyError, IndexError):
			raise self.document.DoesNotExist( )
	
		try:
			shouldntExist = result[1]
			raise self.document.MultipleObjectsReturned( )
		except (KeyError, IndexError):
			pass # we actually EXPECT this should happen, ignore
		
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
		if self._savedCount is None:
			if self._savedItems is None:
				self._savedCount = self.collection.find( self.query.toMongo( self.document ) ).count( )
			else:
				self._savedCount = self._savedItems.count( )
		
		return self._savedCount
	
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
		if self._savedItems is None:
			self._savedItems = self.collection.find( self.query.toMongo( self.document ) )
			self._savedBuiltItems = []
		for i,item in enumerate(self._savedItems):
			if i >= len(self._savedBuiltItems):
				self._savedBuiltItems.append( self.document( )._fromMongo( item ) )
			
			yield self._savedBuiltItems[i]
	
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
import pymongo

from mongorm.BaseDocument import BaseDocument
from mongorm.connection import getDatabase

from mongorm.errors import OperationError

class Document(BaseDocument):
	__internal__ = True
	__needs_primary_key__ = True
	
	def __eq__(self, other):
		if isinstance(other, self.__class__) and hasattr(other, self._primaryKeyField):
			assert self._primaryKeyField == other._primaryKeyField
			if getattr(self, self._primaryKeyField) == getattr(other, other._primaryKeyField):
				return True
		return False
	
	def __ne__(self, other):
		return not (self == other)
	
	def __init__( self, **kwargs ):
		super(Document, self).__init__( **kwargs )
	
	def save( self, forceInsert=False, safe=True ):
		database = getDatabase( )
		collection = database[self._collection]
		
		self._resyncFromPython( )
		
		if '_id' in self._data and self._data['_id'] is None:
			del self._data['_id']
		try:
			if forceInsert:
				newId = collection.insert( self._data, safe=safe )
			else:
				newId = collection.save( self._data, safe=safe )
		except pymongo.errors.OperationFailure, err:
			message = 'Could not save document (%s)'
			if u'duplicate key' in unicode(err):
				message = u'Tried to save duplicate unique keys (%s)'
			raise OperationError( message % unicode(err) )
		if newId is not None:
			setattr(self, self._primaryKeyField, newId)
		
		return self

	def __repr__( self ):
		return '<%s id=%s>' % (self.__class__.__name__, getattr(self, self._primaryKeyField))
from mongorm.fields.BaseField import BaseField
from mongorm.queryset.QuerySetManager import QuerySetManager
from mongorm.aggregation.AggregationManager import AggregationManager
from mongorm.DocumentRegistry import DocumentRegistry
from mongorm.util import sortListToPyMongo

from mongorm.fields.ObjectIdField import ObjectIdField

from mongorm.errors import DoesNotExist, MultipleObjectsReturned

from mongorm.connection import getDatabase

import sys

if sys.version_info < (2, 5):
	# Prior to Python 2.5, Exception was an old-style class
	def subclassException( name, parents, unused ):
		return types.ClassType(name, parents, {} )
else:
	def subclassException( name, parents, module ):
		return type( name, parents, {'__module__': module} )

class DocumentMetaclass(type):
	@staticmethod
	def __new__( cls, name, bases, attrs ):
		if DocumentRegistry.hasDocument( name ):
			return DocumentRegistry.getDocument( name )
			
		# don't do anything if we're the class that defines the metaclass
		#metaclass = attrs.get( '__metaclass__' )
		superNew = super(DocumentMetaclass, cls).__new__
		#if metaclass and issubclass(metaclass, DocumentMetaclass):
		#	return superNew( cls, name, bases, attrs )
		
		fields = {}
		collection = name.lower()
		needsPrimaryKey = False
		primaryKey = None
		
		# find all inherited fields and record them
		for base in bases:
			if hasattr(base, '_fields'):
				fields.update( base._fields )
			if hasattr(base, '_collection'):
				collection = base._collection
			if hasattr(base, '__needs_primary_key__'):
				needsPrimaryKey = True
		
		if not '__internal__' in attrs:
			attrs['_collection'] = collection
		
		# find all fields and add them to our field list
		for attrName, attrValue in attrs.items( ):
			if hasattr(attrValue, '__class__') and \
				issubclass(attrValue.__class__, BaseField):
				field = attrValue
				field.name = attrName
				if not hasattr(field, 'dbField') or field.dbField is None:
					field.dbField = attrName
				fields[attrName] = field
				del attrs[attrName]
		
		for field,value in fields.iteritems( ):
			if value.primaryKey:
				assert primaryKey is None, "Can only have one primary key per document"
				primaryKey = field
		
		# add a primary key if none exists and one is required
		if needsPrimaryKey and primaryKey is None:
			fields['id'] = ObjectIdField( primaryKey=True, dbField='_id' )
			primaryKey = 'id'
		
		attrs['_primaryKeyField'] = primaryKey
		
		# make sure we have all indexes that are specified
		if 'meta' in attrs:
			meta = attrs['meta']
			if 'indexes' in meta:
				indexes = meta['indexes']
				
				groupName = attrs.get('database_group', 'default')
				_database = getDatabase( groupName)
				_collection = _database[collection]
				
				for index in indexes:
					if not isinstance(index, (list,tuple)):
						index = [index]
					def indexConverter( fieldName ):
						if fieldName in fields:
							return fields[fieldName].optimalIndex( )
						return fieldName
					pyMongoIndexKeys = sortListToPyMongo( index, indexConverter )
					_collection.ensure_index( pyMongoIndexKeys )
		
		# add a query set manager if none exists already
		if 'objects' not in attrs:
			attrs['objects'] = QuerySetManager( )
		
		# add an aggregation manager if none exists
		if 'aggregate' not in attrs:
			attrs['aggregate'] = AggregationManager( )
		
		# construct the new class
		attrs['_is_lazy'] = False
		attrs['_fields'] = fields
		attrs['_data'] = None
		attrs['_values'] = None
		newClass = superNew( cls, name, bases, attrs )
		
		# record the document in the fields
		for field in newClass._fields.values( ):
			#field.ownerDocument = newClass
			field.setOwnerDocument( newClass )
		
		# add DoesNotExist and MultipleObjectsReturned exceptions
		module = attrs.get('__module__')
		newClass._addException( 'DoesNotExist', bases,
								defaultBase=DoesNotExist,
								module=module )
		newClass._addException( 'MultipleObjectsReturned', bases,
								defaultBase=MultipleObjectsReturned,
								module=module )
		
		# register the document for name-based reference
		DocumentRegistry.registerDocument( name, newClass )
		
		return newClass
	
	def _addException( self, name, bases, defaultBase, module ):
		baseExceptions = tuple( getattr(base, name) \
								for base in bases if hasattr(base, name)
							  ) or (defaultBase,)
		exception = subclassException( name, baseExceptions, module )
		setattr( self, name, exception )
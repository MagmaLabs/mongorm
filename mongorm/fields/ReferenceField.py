try:
	from pymongo import objectid, dbref
except ImportError:
	from bson import objectid, dbref
from mongorm.types import InvalidId

from mongorm.fields.BaseField import BaseField
from mongorm.DocumentRegistry import DocumentRegistry

from mongorm.blackMagic import serialiseTypesForDocumentType

class ReferenceField(BaseField):
	def __init__( self, documentClass, *args, **kwargs ):
		cached_fields = None
		if 'cached_fields' in kwargs:
			cached_fields = kwargs['cached_fields']
			del kwargs['cached_fields']
		
		super(ReferenceField, self).__init__( *args, **kwargs )
		
		self.inputDocumentClass = documentClass
		self.cached_fields = cached_fields
	
	def _getClassInfo( self ):
		if hasattr(self, 'documentName'): return
		
		documentClass = self.inputDocumentClass
		
		if isinstance(documentClass, basestring):
			if documentClass == 'self':
				self.documentName = self.ownerDocument.__name__
				self.documentClass = self.ownerDocument
			else:
				self.documentName = documentClass
				self.documentClass = DocumentRegistry.getDocument( self.documentName )
		else:
			self.documentClass = documentClass
			self.documentName = documentClass.__name__
	
	def fromPython( self, pythonValue, dereferences=[], modifier=None ):
		self._getClassInfo( )
		
		if pythonValue is None:
			return None
		
		if len(dereferences) > 0:
			return pythonValue # can't do any value checking here.. we actually need to recurse to our referenced class's fromPython
		
		if not isinstance(pythonValue, self.documentClass):
			# try mapping to an objectid
			try:
				objectId = objectid.ObjectId( str( pythonValue ) )
			except InvalidId:
				pass # if it's not a valid ObjectId, then pass through and allow the assert to fail
			else:
				return {
					'_ref': dbref.DBRef( self.documentClass._collection, objectId ),
				}
		
		assert isinstance(pythonValue, self.documentClass), \
				"Referenced value must be a document of type %s" % (self.documentName,)
		assert pythonValue.id is not None, "Referenced Document must be saved before being assigned"
		
		data = {
			'_types': serialiseTypesForDocumentType(pythonValue.__class__),
			'_ref': dbref.DBRef( pythonValue.__class__._collection, pythonValue.id ),
		}
		
		if self.cached_fields is not None:
			for field in self.cached_fields:
				if field.startswith('_'): continue
				data[field] = getattr(pythonValue, field)
		
		return data
	
	def toQuery( self, pythonValue, dereferences=[] ):
		if pythonValue is None:
			return None
		
		qVal = self.fromPython( pythonValue, dereferences=dereferences )
		
		if len(dereferences) > 0:
			return {
				'.'.join( dereferences ): qVal,
			}
		
		return {
			'_ref': qVal['_ref']
		}
	
	def toPython( self, bsonValue ):
		self._getClassInfo( )
		
		if bsonValue is None:
			return None
		
		if isinstance(bsonValue, dbref.DBRef):
			# old style (mongoengine)
			dbRef = bsonValue
			documentClass = self.documentClass
			documentName = self.documentName
			initialData = {
				'_id': bsonValue.id,
			}
		else:
			# new style (dict with extra info)
			dbRef = bsonValue['_ref']
			if '_cls' in bsonValue:
				# mongoengine GenericReferenceField compatibility
				documentName = bsonValue['_cls']
			else:
				documentName = bsonValue['_types'][0]
			documentClass = DocumentRegistry.getDocument( documentName )
			initialData = {
				'_id': dbRef.id,
			}
			if self.cached_fields is not None:
				for field in self.cached_fields:
					if field in bsonValue:
						initialData[field] = bsonValue[field]
		
		return documentClass( )._fromMongo( initialData )
	
	def optimalIndex( self ):
		return self.dbField + '._ref'
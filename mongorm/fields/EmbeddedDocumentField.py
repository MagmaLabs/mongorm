from mongorm.fields.BaseField import BaseField

from mongorm.EmbeddedDocument import EmbeddedDocument

class EmbeddedDocumentField(BaseField):
	_resyncAtSave = True
	
	def __init__( self, documentType, *args, **kwargs ):
		self.documentType = documentType
		self.defaultInstanceType = documentType
		if 'defaultInstanceType' in kwargs:
			self.defaultInstanceType = kwargs['defaultInstanceType']
			del kwargs['defaultInstanceType']
		
		super(EmbeddedDocumentField, self).__init__( *args, **kwargs )
		
		assert issubclass(self.documentType, EmbeddedDocument), \
			"EmbeddedDocumentField can only contain EmbeddedDocument instances"
	
	def fromPython( self, pythonValue, dereferences=[], modifier=None ):
		if len(dereferences) > 0:
			return {
				'.'.join( dereferences ): pythonValue,
			} # FIXME: this should be validated against the embedded document's fields
		
		if hasattr(self.documentType, 'fromPython'):
			pythonValue = self.documentType.fromPython( pythonValue )
		
		if pythonValue is None:
			return None
		assert isinstance(pythonValue, self.documentType), \
			"Instance for EmbeddedDocumentField must be an instance of %s or a subclass" \
			% self.documentType.__name__
		
		# before we go any further, re-sync from python values where needed
		pythonValue._resyncFromPython( )
		
		return pythonValue._data
	
	def toPython( self, bsonValue ):
		if bsonValue is not None:
			return self.defaultInstanceType( )._fromMongo( bsonValue )
		else:
			return None
	
	def toQuery( self, pythonValue, dereferences=[] ):
		# FIXME: this doesn't consider converting the value to/from python
		# should check the types of the fields the whole way down the chain
		return {
			'.'.join( dereferences ): pythonValue
		}
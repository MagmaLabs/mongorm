from mongorm.fields.BaseField import BaseField

from mongorm.EmbeddedDocument import EmbeddedDocument

class EmbeddedDocumentField(BaseField):
	_resyncAtSave = True
	
	def __init__( self, documentType, *args, **kwargs ):
		super(EmbeddedDocumentField, self).__init__( *args, **kwargs )
		self.documentType = documentType
		assert issubclass(self.documentType, EmbeddedDocument), \
			"EmbeddedDocumentField can only contain EmbeddedDocument instances"
	
	def fromPython( self, pythonValue ):
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
			return self.documentType( )._fromMongo( bsonValue )
		else:
			return None
	
	def toQuery( self, pythonValue, dereferences=[] ):
		# FIXME: this doesn't consider converting the value to/from python
		# should check the types of the fields the whole way down the chain
		return {
			'.'.join( dereferences ): pythonValue
		}
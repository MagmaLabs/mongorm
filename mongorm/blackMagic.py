
def serialiseTypesForDocumentType( documentType ):
	return [ cls.__name__ for cls in documentType.mro() if cls != object \
			 and cls.__name__ not in ['Document', 'BaseDocument', 'EmbeddedDocument'] ]

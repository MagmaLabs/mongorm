class DocumentRegistry(object):
	documentTypes = {}
	
	@classmethod
	def registerDocument( cls, name, document ):
		assert name not in cls.documentTypes, "Attempt to register the same document name twice"
		cls.documentTypes[name] = document
	
	@classmethod
	def getDocument( cls, name ):
		return cls.documentTypes[name]
	
	@classmethod
	def hasDocument( cls, name ):
		return name in cls.documentTypes
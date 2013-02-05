from mongorm.queryset.Q import Q
from mongorm.util import sortListToPyMongo
import pymongo

from mongorm.DocumentRegistry import DocumentRegistry

from mongorm.blackMagic import serialiseTypesForDocumentType

class Aggregation(object):
	def __init__( self, document, collection, pipeline=None ):
		self.document = document
		self.collection = collection
		
		if pipeline is None:
			pipeline = []
		
		self.pipeline = pipeline
	
	def __iter__( self ):
		return self.collection.aggregate( self.pipeline )['result'].__iter__( )
	
	def _extend( self, newStep ):
		return Aggregation( self.document, self.collection, self.pipeline + [newStep] )
	
	def match( self, **search ):
		query = Q( **search ).toMongo( self.document )
		
		return self._extend( { '$match': query } )
	
	def project( self, **projection ):
		return self._extend( { '$project': projection } )
	
	def group( self, **group ):
		return self._extend( { '$group': group } )
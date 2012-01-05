from mongorm import *
from pymongo.dbref import DBRef

def teardown_module(module):
	DocumentRegistry.clear( )
	
def test_update_dictfield( ):
	"""Tests to make sure updates are calculated correctly by dictfields"""
	class TestA(Document):
		data = DictField( )

	assert Q( { 'data__123': 'test' } ).toMongo( TestA, forUpdate=True ) == { 'data.123': 'test' }

	# children of a dictfield shouldn't be motified
	fieldName = 'data__123'
	value = {"XXX": "YYY"}
	assert Q( { fieldName: value } ).toMongo( TestA, forUpdate=True )[fieldName.replace('__', '.')] \
		== value
	value = ['test']
	assert Q( { fieldName: value } ).toMongo( TestA, forUpdate=True )[fieldName.replace('__', '.')] \
		== value
	
def test_update_types( ):
	"""Tests to make sure updates work with different types"""
	connect( 'test_mongorm' )
	
	class TestB(Document):
		dictval = DictField( )
		boolval = BooleanField( )
		stringval = StringField( )
		listval = ListField( StringField() )
		genericval = GenericReferenceField( )
	
	doc = TestB( )
	doc.save( )
	
	assert TestB.objects._prepareActions(
		set__boolval=True,
		set__stringval='test'
	) == {'$set': {'boolval': True, 'stringval': 'test'}}

	assert TestB.objects._prepareActions(
		set__listval=['a','b','c']
	) == {'$set': {'listval': ['a', 'b', 'c']}}
	
	assert TestB.objects._prepareActions(
		set__dictval__subkeybool=True,
		set__dictval__subkeystring='testing',
		set__dictval__subkeydict={'a':'b'},
	) == {'$set': { 'dictval.subkeybool': True,
	                'dictval.subkeydict': {'a': 'b'},
	                'dictval.subkeystring': 'testing'}}
	
	assert TestB.objects._prepareActions(
		set__genericval=doc
	) == {'$set': {'genericval': {'_types': ['TestB'], '_ref': DBRef('testb', doc.id)}}}
	
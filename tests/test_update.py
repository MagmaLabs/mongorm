from mongorm import *

def teardown_module(module):
	DocumentRegistry.clear( )
	
def test_update_dictfield( ):
	"""Tests to make sure updates are calculated correctly by dictfields"""
	class TestA(Document):
		data = DictField( )
	
	assert Q( { 'data__123': 'test' } ).toMongo( TestA, forUpdate=False ) == { 'data.123': 'test' }
	
	# children of a dictfield shouldn't be motified
	fieldName = 'data__123'
	value = {"XXX": "YYY"}
	assert Q( { fieldName: value } ).toMongo( TestA, forUpdate=False )[fieldName.replace('__', '.')] \
		== value
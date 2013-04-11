from mongorm import *

def teardown_module(module):
	DocumentRegistry.clear( )

def test_equality( ):
	"""Tests to make sure comparisons work. Equality compares database
	identity, not value similarity."""
	connect( 'test_mongorm' )
	
	class TestDocument(Document):
		s = StringField( )
	
	a = TestDocument( s="Hello" )
	a.save( )
	
	b = TestDocument( s="Hello" )
	b.save( )

	assert not (a == b)
	assert a != b
	
	c = TestDocument.objects.get(pk=a.id)

	assert c == a
	assert not (c != a)
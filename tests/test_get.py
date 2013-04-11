from mongorm import *

from pytest import raises

def teardown_module(module):
	DocumentRegistry.clear( )

def test_equality( ):
	"""Tests to make sure comparisons work. Equality compares database
	identity, not value similarity."""
	connect( 'test_mongorm' )
	
	class TestDocument(Document):
		s = StringField( )
	
	TestDocument.objects.delete()
	
	with raises(TestDocument.DoesNotExist):
		TestDocument.objects.get(s="hello")
	
	item = TestDocument(s="hello")
	item.save()
	
	assert item == TestDocument.objects.get(s="hello")
	
	item2 = TestDocument(s="hello")
	item2.save()
	
	with raises(TestDocument.MultipleObjectsReturned):
		TestDocument.objects.get(s="hello")
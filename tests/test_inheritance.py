from mongorm import *

def setup_module(module):
	DocumentRegistry.clear( )

def test_inheritance_magic( ):
	"""Make sure inherited documents instantiate the correct subclass"""
	connect( 'test_mongorm' )

	class BaseThing(Document):
		name = StringField( )

	class ExtendedThing(BaseThing):
		extended = StringField( )

	class AnotherThing(BaseThing):
		another = StringField( )
	
	BaseThing.objects.delete( )
	
	b = BaseThing( name='basey' ).save( )
	e = ExtendedThing( name='extendy', extended='extension foo' ).save( )
	a = AnotherThing( name='another', another='another bar' ).save( )
	
	bOut = BaseThing.objects.get( name='basey' )
	assert isinstance( bOut, BaseThing )
	assert not isinstance( bOut, (ExtendedThing, AnotherThing) )
	assert bOut.name == 'basey'
	
	eOut = BaseThing.objects.get( name='extendy' )
	assert isinstance( eOut, BaseThing )
	assert isinstance( eOut, ExtendedThing )
	assert not isinstance( eOut, AnotherThing )
	assert eOut.name == 'extendy'
	assert eOut.extended == 'extension foo'
	
	aOut = BaseThing.objects.get( name='another' )
	assert isinstance( aOut, BaseThing )
	assert isinstance( aOut, AnotherThing )
	assert not isinstance( aOut, ExtendedThing )
	assert aOut.name == 'another'
	assert aOut.another == 'another bar'
	
	aOutSet = AnotherThing.objects.filter( another='another bar' )
	assert aOutSet.count( ) == 1
	aOut2 = aOutSet[0]
	assert isinstance( aOut2, BaseThing )
	assert isinstance( aOut2, AnotherThing )
	assert not isinstance( aOut2, ExtendedThing )
	assert aOut2.name == 'another'
	assert aOut2.another == 'another bar'
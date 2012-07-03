from mongorm import *

from pymongo.objectid import ObjectId

def setup_module(module):
	DocumentRegistry.clear( )

def test_inheritance_magic( ):
	"""Make sure inherited documents instantiate the correct subclass"""
	DocumentRegistry.clear( )
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
	
	# test backwards compatability
	assert BaseThing.objects._getNewInstance( {
		"_id" : ObjectId("4f72c55402ac3601db000000"),
		"name": "foo",
	} ) is not None

def test_inheritance_upsert( ):
	DocumentRegistry.clear( )
	connect( 'test_mongorm' )
	
	class BaseThingUpsert(Document):
		name = StringField( )
		value = IntegerField( )
	
	class ExtendedThingUpsert(BaseThingUpsert):
		extended = StringField( )
	
	BaseThingUpsert.objects.delete( )
	
	assert BaseThingUpsert.objects.count( ) == 0
	
	for i in range( 2 ):
		BaseThingUpsert.objects.filter( name='upsert1' ).update(
			upsert=True,
			set__name='upsert1',
			set__value=42,
		)
	
	item = BaseThingUpsert.objects.get( name='upsert1' )
	
	assert BaseThingUpsert.objects.count( ) == 1
	assert item.value == 42
	
	for i in range( 2 ):
		ExtendedThingUpsert.objects.filter( name='upsert2' ).update(
			upsert=True,
			set__name='upsert2',
			set__extended='ext',
			set__value=42,
		)
	
	item = ExtendedThingUpsert.objects.get( name='upsert2' )
	
	assert len( list( ExtendedThingUpsert.objects.all( ) ) ) == 1
	assert len( list( BaseThingUpsert.objects.all( ) ) ) == 2
	assert ExtendedThingUpsert.objects.count( ) == 1
	assert BaseThingUpsert.objects.count( ) == 2

def test_inheritance_backwards( ):
	DocumentRegistry.clear( )
	connect( 'test_mongorm' )

	class BaseThingBackwards(Document):
		name = StringField( )
		value = IntegerField( )

	class ExtendedThingBackwards(BaseThingBackwards):
		extended = StringField( )

	BaseThingBackwards.objects.delete( )
	
	BaseThingBackwards.objects.collection.insert( { 'name': 'test', 'value': 43 } )
	
	assert BaseThingBackwards.objects.count( ) == 1
	assert len( list( BaseThingBackwards.objects.all( ) ) ) == 1
	assert ExtendedThingBackwards.objects.count( ) == 0
	assert len( list( ExtendedThingBackwards.objects.all( ) ) ) == 0

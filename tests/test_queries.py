from mongorm import *

def teardown_module(module):
	DocumentRegistry.clear( )

def test_basic_equality( ):
	"""Tests field equality and nested field equality"""
	class Test(Document):
		data = DictField( )
		name = StringField( )
	
	# equality
	assert Q( name='c' ).toMongo( Test ) \
		== {'name': 'c'}
	assert Q( data__attributes__course__name='c' ).toMongo( Test ) \
		== {'data.attributes.course.name': 'c'}

def test_basic_comparisons( ):
	"""Tests field and nested field comparisons"""
	class Test(Document):
		data = DictField( )
		name = StringField( )
	
	# simple comparisons
	assert Q( name__lte='c' ).toMongo( Test ) \
		== {'name': {'$lte': 'c'}}
	assert Q( data__attributes__course__name__lte='c' ).toMongo( Test ) \
		== {'data.attributes.course.name': {'$lte': 'c'}}

def test_regex_comparisons( ):
	"""Tests field and nested field regex comparisons"""
	class Test(Document):
		data = DictField( )
		name = StringField( )
	
	# regex comparisons
	assert Q( data__attributes__course__name__icontains='c' ).toMongo( Test ) \
		== {'data.attributes.course.name': {'$options': 'i', '$regex': u'c'}}
	assert Q( name__icontains='c' ).toMongo( Test ) \
		== {'name': {'$options': 'i', '$regex': u'c'}}
		
def test_embedded_basic_comparisons( ):
	"""Tests nested field regex comparisons over an EmbeddedDocument boundary"""
	class Data(EmbeddedDocument):
		attributes = DictField( )
	class TestPage(Document):
		data = EmbeddedDocumentField(Data)

	# regex comparisons
	assert Q( data__attributes__course__name__lte='c' ).toMongo( TestPage ) \
		== {'data.attributes.course.name': {'$lte': 'c'}}
		
def test_embedded_regex_comparisons( ):
	"""Tests nested field regex comparisons over an EmbeddedDocument boundary"""
	class Data(EmbeddedDocument):
		attributes = DictField( )
	class TestPage(Document):
		data = EmbeddedDocumentField(Data)

	# regex comparisons
	assert Q( data__attributes__course__name__icontains='c' ).toMongo( TestPage ) \
		== {'data.attributes.course.name': {'$options': 'i', '$regex': u'c'}}

def test_multiple_or( ):
	class Test(Document):
		data = DictField( )
	
	query = '123'
	queryFilter = (
		Q(data__a__icontains=query) |
		Q(data__b__icontains=query) |
		Q(data__c__icontains=query)
	)
	
	assert queryFilter.toMongo( Test ) == {
		'$or': [
			{'data.a': {'$options': 'i', '$regex': '123'}},
			{'data.b': {'$options': 'i', '$regex': '123'}},
			{'data.c': {'$options': 'i', '$regex': '123'}}
		]
	}

def test_regex_escape( ):
	"""Tests to make sure regex matches work with values containing regex special characters"""
	class Test(Document):
		name = StringField( )
	
	# equality
	assert Q( name__icontains='test.test' ).toMongo( Test ) \
		== {'name': {'$options': 'i', '$regex': u'test\\.test'}}
	assert Q( name__iexact='test.test' ).toMongo( Test ) \
		== {'name': {'$options': 'i', '$regex': u'^test\\.test$'}}
	assert Q( name__iexact='test\\' ).toMongo( Test ) \
		== {'name': {'$options': 'i', '$regex': u'^test\\\\$'}}
	assert Q( name__iexact='test[abc]test' ).toMongo( Test ) \
		== {'name': {'$options': 'i', '$regex': u'^test\\[abc\\]test$'}}

def test_and_or( ):
	"""Tests to make sure 'or's can be embedded in 'and's"""
	connect( 'test_mongorm' )
	
	class TestAndOr(Document):
		name = StringField( )
		path = StringField( )
		index = ListField( StringField( ) )
	
	# using consecutive .filter calls
	assert TestAndOr.objects.filter( 
			Q( name__icontains='t' ) | Q( name__icontains='e' )
		).filter( name='123' ).query.toMongo( TestAndOr ) \
		== {'$or': [{'name': {'$options': 'i', '$regex': 't'}},
					{'name': {'$options': 'i', '$regex': 'e'}}],
			'name': u'123'}
	
	# using Q objects
	assert TestAndOr.objects.filter( 
			( Q( name__icontains='t' ) | Q( name__icontains='e' ) ) & Q( name='123' )
		).query.toMongo( TestAndOr ) \
		== {'$or': [{'name': {'$options': 'i', '$regex': 't'}},
					{'name': {'$options': 'i', '$regex': 'e'}}],
			'name': u'123'}
	
	# test ANDs
	assert TestAndOr.objects.filter(
		Q(index='123') &
		Q(index='456')
	).query.toMongo( TestAndOr ) \
	== {'$and': [
		{'index': '123'},
		{'index': '456'},
		]}
	
	# multiple ORs with embedded ANDs
	assert TestAndOr.objects.filter(
		Q(name__icontains='abc') |
		Q(path__icontains='def') |
		(
			Q(index='123') &
			Q(index='456')
		)
	).query.toMongo( TestAndOr ) \
	== {'$or': [{'name': {'$options': 'i', '$regex': 'abc'}},
				{'path': {'$options': 'i', '$regex': 'def'}},
				{'$and': [
					{'index': '123'},
					{'index': '456'},
					]},
				]}

def test_referencefield_none( ):
	"""Make sure ReferenceField can be searched for None"""
	connect( 'test_mongorm' )

	class TestRef(Document):
		name = StringField( )

	class TestHolder(Document):
		ref = ReferenceField( TestRef )
	
	TestHolder.objects.delete( )
	TestHolder( ref=None ).save( )
	ref = TestRef( name='123' )
	ref.save( )
	TestHolder( ref=ref ).save( )
	
	assert TestHolder.objects.filter( ref=None ).query.toMongo( TestHolder ) \
		== {'ref': None}
	
	assert TestHolder.objects.filter( ref=None ).count( ) == 1
	assert TestHolder.objects.filter( ref=ref ).count( ) == 1
	assert TestHolder.objects.get( ref=ref ).ref.name == ref.name
	assert TestHolder.objects.count( ) == 2
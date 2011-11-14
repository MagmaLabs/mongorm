
class Q(object):
	def __init__( self, _query=None, **search ):
		if _query is None:
			if 'pk' in search:
				search['id'] = search['pk']
				del search['pk']
			
			self.query = search
		else:
			self.query = _query
	
	def toMongo( self, document, forUpdate=False ):
		newSearch = {}
		for (name, value) in self.query.iteritems( ):
			if name in ['$or', '$and']:
				# mongodb logic operator - value is a list of Qs
				newSearch[name] = [ value.toMongo( document ) for value in value ]
				continue
			
			fieldName = name
			
			MONGO_COMPARISONS = ['gt', 'lt', 'lte', 'gte']
			REGEX_COMPARISONS = {
				'contains': ( '%s', '' ),
				'icontains': ( '%s', 'i' ),

				'iexact': ( '^%s$', 'i' ),

				'startswith': ( '^%s', '' ),
				'istartswith': ( '^%s', 'i' ),
				
				'endswith': ( '%s$', '' ),
				'iendswith': ( '%s$', 'i' ),
			}
			ALL_COMPARISONS = MONGO_COMPARISONS + REGEX_COMPARISONS.keys()

			comparison = None
			dereferences = []
			if '__' in fieldName:
				chunks = fieldName.split( '__' )
				fieldName = chunks[0]

				comparison = chunks[-1]

				if comparison in ALL_COMPARISONS:
					dereferences = chunks[1:-1]
				else:
					# not a comparison operator
					dereferences = chunks[1:]
					comparison = None
			
			field = document._fields[fieldName]
			if not forUpdate:
				searchValue = field.toQuery( value, dereferences=dereferences )
			else:
				searchValue = field.fromPython( value )
			
			targetSearchKey = field.dbField
			
			valueMapper = lambda value: value
			
			
			if comparison is not None:
				if comparison in REGEX_COMPARISONS:
					regex,options = REGEX_COMPARISONS[comparison]
					regexReserved = [ '\\', '.', '*', '+' ,'^', '$', '[', ']', '?', '(', ')' ]
					safeValue = value
					for reserved in regexReserved:
						safeValue = safeValue.replace( reserved, '\\' + reserved )
					valueMapper = lambda value: { '$regex': regex % safeValue, '$options': options }
					#pattern = regex % searchValue
					#print comparison, searchValue, targetSearchKey, pattern, options
					#newSearch[targetSearchKey] = { '$regex': pattern, '$options': options }
				else:
					valueMapper = lambda value: { '$'+comparison: value }
					#newSearch[targetSearchKey] = { '$'+comparison: searchValue }

			if isinstance(searchValue, dict):
				if not forUpdate:
					for name,value in searchValue.iteritems( ):
						key = targetSearchKey + '.' + name
						newSearch[key] = valueMapper(value)
				else:
					newSearch[targetSearchKey] = valueMapper(searchValue)
			else:
				newSearch[targetSearchKey] = valueMapper(searchValue)

		return newSearch
	
	def __or__( self, other ):
		return self.do_merge( other, '$or' )
	
	def __and__( self, other ):
		return self.do_merge( other, '$and' )
	
	def do_merge( self, other, op ):
		if len(self.query) == 0: return other
		if len(other.query) == 0: return self
		
		if op in self.query:
			items = self.query[op] + [other]
		elif op in other.query:
			items = other.query[op] + [self]
		else:
			items = [ self, other ]
		
		newQuery = { op: items }
		return Q( _query=newQuery )
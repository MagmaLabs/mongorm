import pymongo

def sortListToPyMongo( sortList, keyMap=None, convertUnderscoreNotation=True ):
	sorting = []
	
	for sortField in sortList:
		direction = pymongo.ASCENDING
		
		if sortField.startswith( '+' ):
			sortField = sortField[1:]
		elif sortField.startswith( '-' ):
			sortField = sortField[1:]
			direction = pymongo.DESCENDING
		
		if keyMap is not None:
			sortField = keyMap( sortField )
		
		if convertUnderscoreNotation:
			sortField = sortField.replace( '__', '.' )
		
		sorting.append( (sortField,direction) )
	
	return sorting
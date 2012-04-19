import pymongo

def sortListToPyMongo( sortList, keyMap=None ):
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
		
		sorting.append( (sortField,direction) )
	
	return sorting
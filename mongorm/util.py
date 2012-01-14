import pymongo

def sortListToPyMongo( sortList ):
	sorting = []
	
	for sortField in sortList:
		direction = pymongo.ASCENDING
		
		if sortField.startswith( '+' ):
			sortField = sortField[1:]
		elif sortField.startswith( '-' ):
			sortField = sortField[1:]
			direction = pymongo.DESCENDING
		
		sorting.append( (sortField,direction) )
	
	return sorting
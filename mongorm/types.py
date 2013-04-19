try:
	from pymongo.objectid import ObjectId
except ImportError:
	from bson.objectid import ObjectId

try:
	from pymongo.dbref import DBRef
except ImportError:
	from bson.dbref import DBRef

try:
	from pymongo.objectid import InvalidId
except ImportError:
	from bson.errors import InvalidId
from mongorm.fields.ReferenceField import ReferenceField

from mongorm.Document import Document


class GenericReferenceField(ReferenceField):
	def __init__( self, *args, **kwargs ):
		super(GenericReferenceField, self).__init__( Document, *args, **kwargs )
from wtforms import Form, StringField, SelectField, TextField
from wtforms import DateTimeField, IntegerField, validators
from wtforms_components import TimeField

class ItemForm(Form):
	type = SelectField('Element type', default='image',
		choices=[('message', 'Message'), ('image', 'Image'),
		('video', 'Video'), ('website', 'Website')])
	message = TextField('Message')
	url = StringField('URL')
	display_time = IntegerField('Display time', validators=[validators.optional()])
	valid_since = DateTimeField('Valid since', validators=[validators.optional()])
	valid_until = DateTimeField('Valid until', validators=[validators.optional()])
	display_after = TimeField('Display after', validators=[validators.optional()])
	display_before = TimeField('Display before', validators=[validators.optional()])

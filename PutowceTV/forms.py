# -*- encoding: utf-8 -*-
from wtforms import Form, StringField, SelectField
from wtforms import DateTimeField, IntegerField, validators
from wtforms_components import TimeField


class SafeStringField(StringField):

	def process_formdata(self, valuelist):
		super(SafeStringField, self).process_formdata(valuelist)
		# Klein ffs
		self.data = self.data.decode('utf-8')


class ItemForm(Form):
	type = SelectField('Element type', default='image',
		choices=[('message', 'Message'), ('image', 'Image'),
		('video', 'Video'), ('website', 'Website')])
	message = SafeStringField('Message')
	url = SafeStringField('URL')
	display_time = IntegerField('Display time', validators=[validators.optional()])
	valid_since = DateTimeField('Valid since', validators=[validators.optional()])
	valid_until = DateTimeField('Valid until', validators=[validators.optional()])
	display_after = TimeField('Display after', validators=[validators.optional()])
	display_before = TimeField('Display before', validators=[validators.optional()])

	def validate_message(form, field):
		if form.type.data == 'message':
			if not field.data:
				raise validators.ValidationError("Message is required")
		elif field.data:
			raise validators.ValidationError("Message cannot be set if type is not 'message'")

	def validate_url(form, field):
		if form.type.data != 'message':
			if not field.data:
				raise validators.ValidationError("URL is required")
			validators.URL()(form, field)
		elif field.data:
			raise validators.ValidationError("URL cannot be set if type is 'message'")

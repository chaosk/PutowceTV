# -*- encoding: utf-8 -*-
from wtforms import Form, StringField, SelectField, SelectMultipleField
from wtforms import DateTimeField, IntegerField, validators, widgets
from wtforms_components import TimeField


class SafeStringField(StringField):

	def process_formdata(self, valuelist):
		super(SafeStringField, self).process_formdata(valuelist)
		# Klein ffs
		self.data = self.data.decode('utf-8')


class MultiCheckboxField(SelectMultipleField):
	"""
	A multiple-select, except displays a list of checkboxes.

	Iterating the field will produce subfields, allowing custom rendering of
	the enclosed checkbox fields.
	"""
	widget = widgets.ListWidget(prefix_label=False)
	option_widget = widgets.CheckboxInput()

date_format = '%Y-%m-%dT%H:%M'

class ItemForm(Form):
	type = SelectField('Typ elementu', default='image',
		choices=[('message', u'Wiadomość'), ('image', 'Plik graficzny'),
		('video', 'Plik video'), ('website', 'Strona internetowa')])
	message = SafeStringField(u'Wiadomość')
	url = SafeStringField('Adres URL')
	display_time = IntegerField('Display time', validators=[validators.optional()], default=20)
	valid_since = DateTimeField('Valid since', format=date_format,
		validators=[validators.optional()])
	valid_until = DateTimeField('Valid until', format=date_format,
		validators=[validators.optional()])
	display_after = TimeField('Display after', validators=[validators.optional()])
	display_before = TimeField('Display before', validators=[validators.optional()])
	week_days = MultiCheckboxField(
		choices=[('mon', "pon."), ('tue', "wt."), ('wed', u"śr."),
		('thu', "czw."), ('fri', u"pt."), ('sat', "sob."), ('sun', "niedz.")])

	def validate_message(form, field):
		if form.type.data == 'message':
			if not field.data:
				raise validators.ValidationError(u"Wiadomość jest wymagana")
		elif field.data:
			raise validators.ValidationError(u"Wiadomość nie może zostać ustawiona, gdy element nie jest typu 'message'")

	def validate_url(form, field):
		if form.type.data != 'message':
			if not field.data:
				raise validators.ValidationError("Adres URL jest wymagany")
			validators.URL()(form, field)
		elif field.data:
			raise validators.ValidationError(u"Adres URL nie może zostać ustawiony, gdy element jest typu 'message'")

from odoo import api, models, fields 
from odoo.exceptions import UserError, ValidationError
import re


EM = (r"[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")

def emailvalidation(email):
	"""Check valid email."""
	if email:
		email_regex = re.compile(EM)
		if not email_regex.match(email):
			raise ValidationError(_("""This seems not to be valid email.
Please enter email in correct format!"""))

class StudentParent(models.Model):
	_name = 'student.parent'
	_inherit = ["mail.thread","mail.activity.mixin"]
	_description = 'Parents Detail'

	name = fields.Char(string="Parents Name", required=True)
	image = fields.Binary(string="Parent(s) Photo", required=True)
	email = fields.Char(string="Parents Email", required=True) 
	gender = fields.Selection([
		('male', 'Male'),
		('female', 'Female')], string="Gender", required=True)
	phone = fields.Char(string="Parents Phone", size=10, required=True) 
	relation = fields.Selection([
		('father', 'Father'),
		('mother', 'Mother'),
		('brother', 'Brother'),
		('sister', 'Sister'),
		('other', 'Other')], string='Relation With Student')
	student_ids = fields.Many2many('student.student', string='Student')
	active = fields.Boolean(default=True,string='Activate Student', tracking=True)

	@api.model
	def create(self,vals):
		if vals['phone'] and len(vals['phone']) != 10:
			raise ValidationError("Phone number must have 10 digits.")
		if vals['email']:
			email_regex = re.compile(EM)
			if not email_regex.match(vals['email']):
				raise ValidationError(_("""This seems not to be valid email. Please enter email in correct format!"""))
		return super(StudentParent, self).create(vals)   
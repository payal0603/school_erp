from odoo import api, models, fields , _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import re

EM = (r"[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")

# def emailvalidation(email):
# 	"""Check valid email."""
# 	if email:
# 		email_regex = re.compile(EM)
# 		if not email_regex.match(email):
# 			raise ValidationError(_("""This seems not to be valid email.
# Please enter email in correct format!"""))

class StudentAdmission(models.Model):
	_name = 'student.admission'
	_inherit = ["mail.thread","mail.activity.mixin"]
	_description = 'Student'
	# _inherits = {"res.partner": "partner_id"}
	# _order  = 'grno,name'
	
	@api.model
	def default_get(self, fields):
		res = super(StudentAdmission, self).default_get(fields)
		res['gender'] = 'male'
	   # res['age'] = 5
		return res

	grno = fields.Char(string='GR Number', required=True, copy=False, readonly=True, default=lambda self: _('New'))
	photo = fields.Image(string="Student Photo", required=True)
	name = fields.Char(string='Student Name', required=True)
	last_name = fields.Char(string="Student Last Name")
	is_student = fields.Boolean(default=True,string='Activate Student', tracking=True)

	# school_id = fields.Char(string='School Details', tracking=True)
	medium_id = fields.Many2one('student.department',string='Educational Medium', tracking=True)
	standard_id = fields.Many2one('student.class')
	division_id = fields.Many2one('student.division', string='Student Division')
	# division_id_domain = fields.Char(compute="_compute_division_id_domain", readonly=True, store=False)
	
	street = fields.Char(string="Street Address")
	street2 = fields.Char(string="Street Address 2")
	country = fields.Char(string="Country Name", default="India")
	states = fields.Char(string="State Name")
	city = fields.Char(string="City Name")
	zipcode = fields.Char(string="Zip/Postal Code")

	phone = fields.Char(string='Phone', size=10) # , compute="_compute_phone", inverse="_inverse_phone"
	mobile = fields.Char(string='Mobile', size=10, required=True)
	email = fields.Char(string='Email', required=True)

	gender = fields.Selection([
		('male', 'Male'), 
		('female', 'Female')],
		string='Student Gender')
	date_of_birth = fields.Date(string='Date Of Birth')
	age = fields.Integer(string='Student Age', compute="_compute_age") #

	admission_date = fields.Date(string='Student Admission Date',default=fields.Date.today())
	mother_tongue = fields.Selection([
		('gujarati','Gujarati'),
		('english','English'),
		('hindi','Hindi'),
		('other','Other')],string='Mother Tongue')
	
	
	parent = fields.Char(string='Student Parents ID')
	fname = fields.Char(string='Father Name', required=True)
	mname = fields.Char(string='Mother Name')
	fdesignation = fields.Char(string='Father Designation')
	mdesignation = fields.Char(string='Mother Designation')
	fphone = fields.Char(string='Father Phone No.', required=True, size=10)
	mphone = fields.Char(string='Mother Phone No.', required=True, size=10)
	
	
	previous_school_ids = fields.Char(string='Student Previous School Details')
	registration_no = fields.Char(string="GR No.")
	admission_date = fields.Date(string="Admission Date")
	exit_date = fields.Date(string="Exit Date")

	roll_no = fields.Integer(readonly=True,string='student roll no.')
	category = fields.Selection([
		('general', 'General'),
		('obc', 'OBC'),
		('sc', 'SC'),
		('st', 'ST'),
		('other', 'Other')], string='Category')

	subject_ids = fields.Many2many('student.subject',string="Subject")
	
	user_id = fields.Many2one('res.users', string="User ID", ondelete="cascade")
	partner_id = fields.Many2one('res.partner', string='Partner')
	
	state = fields.Selection([
		('draft', 'Draft'), 
		('done', 'Done'),
		('terminate', 'Terminate'), 
		('cancel', 'Cancel')], default="draft",
		tracking=True, string='Status Of Admission')
	certificate = fields.Char(string='student certificates')
	description = fields.Char(string='Description')
	stu_name = fields.Char(string='student first name', tracking=True)
	required_age = fields.Integer(string="Required Age", default=5)
	academic_year_id = fields.Many2one('academic.year', string="Academic Year")
	
	# standard_ids = fields.Many2many('student.class', string="Standard")
	
	# @api.onchange('standard_id')
	# def onchange_standard_id(self):
	#     for rec in self:
	#         print("Standard: ",rec.standard_id.division_id)
	#         aaaaaaaaa
	# 		rec.division_id_domain = json.dumps([('standard_id.id', '=', rec.standard_id.id)])
	# 		print("Standard iddddddddddd:",rec.division_id_domain)

	def name_get(self):
		result = []
		for rec in self:
			# name = "[" + rec.grno +"]" +" "+ rec.name
			name =  rec.name + "  " + rec.last_name 
			result.append((rec.id, name))
		return result

	@api.depends('date_of_birth')
	def _compute_age(self):
		for record in self:
			if record.date_of_birth:
				today = date.today()
				dob = record.date_of_birth	#.strptime("%Y-%m-%d").date()
				age = relativedelta(today, dob).years
				record.age = age
			else:
				record.age = 0

	def set_terminate(self):
		self.state = 'draft'

	def cancel_admission(self):
		self.state = 'cancel'

	def admission_done(self):
		if self.age < self.required_age:
			raise ValidationError("Age of student should be greater than 6 years!")
		if (self.phone and len(self.phone) != 10) or (self.mobile and len(self.mobile) != 10) or (self.fphone and len(self.fphone) != 10) or (self.mphone and len(self.mphone) != 10):
			raise ValidationError("Phone number must have 10 digits.")
		if self.email:
			email_regex = re.compile(EM)
			if not email_regex.match(self.email):
				raise ValidationError(_("""This seems not to be valid email. Please enter email in correct format!"""))
		address = self.street +" , " + self.city +"  " + self.zipcode
		vals = {
			'grno' : self.grno,
			'name' : self.name + " " + self.last_name,
			'image' : self.photo,
			'gender' : self.gender,
			'dob' : self.date_of_birth,
			'age' : self.age,
			'address' : address,
			'mobile' : self.mobile,
			'email' : self.email, 
			'standard_id' : self.standard_id.id,
			'division_id' : self.division_id.id,
			'active' : self.is_student,
			'admission_date' : self.admission_date,
			'father' : self.fname,
			'mother' : self.mname,
			'fphone' : self.fphone,
			'student_id': self.id,
			'department_id' : self.medium_id.id,
			'academic_year_id' : self.academic_year_id.id
		}
		stud = self.env['student.student'].create(vals)
		self.state = 'done'

	@api.model
	def create(self,vals):
		if vals['phone'] and len(vals['phone']) != 10:
			raise ValidationError("Phone number must have 10 digits.")
		if vals['email']:
			email_regex = re.compile(EM)
			if not email_regex.match(vals['email']):
				raise ValidationError(_("""This seems not to be valid email. Please enter email in correct format!"""))
		if vals.get('grno', _('New')) == _('New'):
			vals['grno'] = self.env['ir.sequence'].next_by_code('student.admission') or _('New')
		return super(StudentAdmission, self).create(vals)   

	def unlink(self):
		if self.state == 'done':
			raise ValidationError("You Cannot Delete %s As It In Done State"%self.grno)
		return super(StudentAdmission, self).unlink()

	# @api.constrains('phone','email')
	# def check_phone(self):
	# 	for rec in self:
	# 		students = self.env['student.admission'].search([('phone', '=', rec.phone), ('id', '!=', rec.id)])
	# 		if students:
	# 			raise ValidationError("Student Already Exist")

	@api.constrains('age')
	def check_age(self):
		for rec in self:
			if rec.age == 0:
				raise ValidationError("Age Cannot Be Zero")
			if rec.age >= 18:
				raise ValidationError("Age Cannot Be Greater Than 18")

	@api.constrains('date_of_birth')
	def _check_birthdate(self):
		for record in self:
			if record.date_of_birth > fields.Date.today():
				raise ValidationError(_(
					"Birth Date can't be greater than current date!"))	

	# @api.depends('phone','mobile','fphone','fphone')
	# def _compute_phone(self):
	# 	for record in self:
	# 		record.phone = record.phone.strip()  # Remove leading/trailing spaces
	# 		if record.phone and not record.phone.isdigit():
	# 			raise ValidationError('Phone number must contain only digits')
	
	# def _inverse_phone(self):
	# 	for record in self:
	# 		if record.phone and len(record.phone) != 10:
	# 			raise ValidationError('Phone number must contain 10 digits')		


class ResPartner(models.Model):
	_inherit = "res.partner"


	def create(self, vals):
		print ("vals", vals)
		res = super(ResPartner, self).create(vals)
		return res

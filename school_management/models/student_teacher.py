from odoo import api,models, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import re 


EM = (r"[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")

def emailvalidation(email):
	"""Check valid email."""
	if email:
		email_regex = re.compile(EM)
		if not email_regex.match(email):
			raise ValidationError(_("""This seems not to be valid email.
Please enter email in correct format!"""))

class StudentTeacher(models.Model):
	_name = 'student.teacher'
	_inherit = ["mail.thread","mail.activity.mixin"]
	_description = 'Student Teacher'
	
	empid = fields.Char(string='Employee ID', required=True, copy=False, readonly=True, default=lambda self: _('New'))
	photo = fields.Image(string="Photo", required=True) 
	name = fields.Char(string='Name', required=True)
	date_of_birth = fields.Date(string="Date Of birth", required=True)
	age = fields.Integer(string='Age', compute="_compute_age")
	gender = fields.Selection([
		('male', 'Male'), 
		('female', 'Female')], string='Gender', required=True, default='male')
	address = fields.Text(string='Address', required=True)
	phone = fields.Char(string='Phone', size=10, required=True)
	email = fields.Char(string='Email', required=True)
	marital_status = fields.Selection([
		('married','Married'),
		('unmarried','Unmarried'),
		('divorced','Divorced'),
		('widower','Widower')],string="Marital Status", required=True)
	mobile = fields.Char(string="Work Phone", size=10, required=True)
	qualifications = fields.Selection([
		('graduate','Graduate'),
		('post-graduate','Post-Graduate'),
		('doctor', 'Doctor(Ph.D)')], string='Qualifications', required=True)
	experience = fields.Integer(string='Experience In Years', required=True)
	joined_date = fields.Date(string='Date Joined', required=True, default=fields.Date.today())
	required_age = fields.Integer(string="Required Age", default=20, required=True)
	salary = fields.Monetary(string='Salary', currency_field='currency_id', required=True)
	currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
	teacher_subject_ids = fields.Many2many('student.subject', string='Subject')
	user_id = fields.Many2one('res.users', string="User ID", ondelete="cascade")
	partner_id = fields.Many2one('res.partner', string="Partner", ondelete="cascade")
	active = fields.Boolean(default=True,string='Activate ', tracking=True)
	department_id = fields.Many2one('student.department', string="Department", required=True)
	standard_id = fields.Many2one('student.class', string="Standard", required=True)
	session_ids = fields.One2many('student.timetable', 'teacher_id', string='Sessions')
	session_count = fields.Integer(compute='_compute_session_details')

	@api.depends('date_of_birth')
	def _compute_age(self):
		for record in self:
			if record.date_of_birth:
				today = date.today()
				print(">>>>>>>>>>>TODAY",today)
				dob = record.date_of_birth	#.strptime("%Y-%m-%d").date()
				print("??????????",dob)
				age = relativedelta(today, dob).years
				print("AGEEEEEEEEEEEEEEEEEEEEEEEE",age)
				record.age = age
			else:
				record.age = 0

	@api.depends('session_ids')
	def _compute_session_details(self):
		today = date.today().strftime('%Y-%m-%d')                               #%m-%d-%Y
		for session in self:
			session_count = 0
			session_count = self.env['student.timetable'].search_count([('teacher_id', '=', self.id), ('start_time', '>=', today), ('start_time', '<=', today + ' 23:59:59')])
			session.session_count = session_count

	def count_sessions_details(self):
		return {
			'type': 'ir.actions.act_window',
			'name': 'Sessions',
			'view_mode': 'tree,form',
			'res_model': 'student.timetable',
			'domain': [('teacher_id', '=', self.id)],
			'target': 'current',
			'teacher_id' : self.id
		}


	def create_teacher_user(self):
		user_group = self.env.ref("school_management.group_school_teacher") or False
		users_res = self.env['res.users']
		for record in self:
			if not record.user_id:
				user_id = users_res.create({
					'name': record.name,
					# 'partner_id': record.partner_id.id,
					'login': record.email,
					'groups_id': user_group,
					'password' : 'Emp@123',
					'tz': self._context.get('tz'),
					'teacher_id' : record.id
				})
				record.user_id = user_id

	@api.model
	def create(self,vals):
		if self.age < self.required_age:
			raise ValidationError("Age of Teacher should be greater than 20 years!")

		if (vals['phone'] and len(vals['phone']) != 10) or (vals['mobile'] and len(vals['mobile']) != 10):
			raise ValidationError("Phone number must have 10 digits.")

		if vals['email']:
			email_regex = re.compile(EM)
			if not email_regex.match(vals['email']):
				raise ValidationError(_("""This seems not to be valid email. Please enter email in correct format!"""))
				
		for record in self:
			vals = {
				'name': record.name,
				'gender': record.gender,
				'address_home_id': record.address
			}
			emp_id = self.env['hr.employee'].create(vals)
			# record.write({'emp_id': emp_id.id})

		if vals.get('empid', _('New')) == _('New'):
			vals['empid'] = self.env['ir.sequence'].next_by_code('student.teacher') or _('New')
		return super(StudentTeacher, self).create(vals)

	@api.constrains('age')
	def check_age(self):
		for rec in self:
			if rec.age == 0:
				raise ValidationError("Age Cannot Be Zero")
			if rec.age >= 60:
				raise ValidationError("Age Cannot Be Greater Than 60")

	def copy(self, default=None):
		if default is None:    
			default = {}
		if not default.get('name'):
			default['name'] = _("%s (copy)", self.name)
		return super(StudentTeacher, self).copy(default)

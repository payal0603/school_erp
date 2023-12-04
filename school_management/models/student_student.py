from odoo import api,models, fields, _
import re

EM = (r"[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")

# def emailvalidation(email):
# 	"""Check valid email."""
# 	if email:
# 		email_regex = re.compile(EM)
# 		if not email_regex.match(email):
# 			raise ValidationError(_("""This seems not to be valid email.
# Please enter email in correct format!"""))

class StudentStudent(models.Model):
	_name = 'student.student'
	_inherit = ["mail.thread","mail.activity.mixin"]
	_description = 'Student'
	# _inherits = {"res.partner": "partner_id"}
	#_order = "grno asc/desc"
	
	student_id = fields.Many2one('student.admission',string="Admission ID", ondelete="cascade")
	grno = fields.Char(string='GR Number',required=True)
	image = fields.Binary(string="Student Photo", required=True)
	name = fields.Char(string='Student Name', required=True)
	gender = fields.Selection(
			[('male','Male'),('female','Female')], string="Gender", required=True)
	dob = fields.Date(string='Date Of Birth', required=True)
	age = fields.Integer(string='Age', required=True)
	address = fields.Text(string='Address', required=True)
	mobile =fields.Char(string='Mobile Number', required=True, size=10)
	email = fields.Char(string='Email ID', required=True)
	user_id = fields.Many2one('res.user', string="Student", ondelete="cascade", required=True)
	# partner_id = fields.Many2one('res.partner', string="Partner")
	standard_id = fields.Many2one('student.class', string="Standard", required=True)
	division_id = fields.Many2one('student.division', string="Division", required=True)
	active = fields.Boolean(string='Active',default=True, required=True)
	admission_date = fields.Date(string='Admission Date', required=True)
	department_id = fields.Many2one('student.department',string='Educational Medium', tracking=True, required=True)
	father = fields.Char(string='Father Name', required=True)
	fphone = fields.Char(string="Father Phone", size=10, related="student_id.fphone", required=True)
	mother = fields.Char(string='Mother name', required=True)
	state = fields.Selection([
		('draft', 'Draft'),
		('done', 'Done')], string="Status", default="draft")
	# certificate = fields.Image(string='Certificate')
	user_id = fields.Many2one('res.users', 'User', ondelete="cascade")
	assignment_count = fields.Integer(string="Assignment Count", compute="compute_count_assignment")
	academic_year_id = fields.Many2one('academic.year', string="Academic Year")
	partner_id = fields.Many2one('res.Partner')
	# time_in  = fields.Datetime(string='Time In')s
	# time_out = fields.Datetime(string='Time Out')

	


	def create(self, vals):
		print ("vals", vals)
		if vals['mobile'] and len(vals['mobile']) != 10:
			raise ValidationError("Phone number must have 10 digits.")
		if vals['email']:
			email_regex = re.compile(EM)
			if not email_regex.match(vals['email']):
				raise ValidationError(_("""This seems not to be valid email. Please enter email in correct format!"""))
		return super(StudentStudent, self).create(vals)

	@api.model
	def change_standard(self):
		students = self.search([])
		for student in students:
			academic_year_end_date = student.academic_year_id.end_date
			if academic_year_end_date and academic_year_end_date < fields.Date.today() and student.active:
				next_standard = student.standard_id.next_standard_id
				student.standard_id = next_standard
				student.active = False
				new_student = student.copy(default={'standard_id': next_standard.id, 'active': True})
				new_student.write({'grno': self.env['ir.sequence'].next_by_code('student.student')})

	def name_get(self):
		result = []
		for rec in self:
			# name = "[" + rec.grno +"]" +" "+ rec.name
			name = rec.name +" [ Std - "+ rec.standard_id.name + " Div - " + rec.division_id.name +" ]"
			result.append((rec.id, name))
		return result	

	def create_student_user(self):
		user_group = self.env.ref("school_management.group_school_student") or False              # base.group_portal
		users_res = self.env['res.users']
		for record in self:
			if not record.user_id:
				user_id = users_res.create({
					'name': record.name,
					# 'partner_id': record.partner_id.id,
					'login': record.email,
					'groups_id': user_group,
					'password' : 'Stud@123',
					'tz': self._context.get('tz'),
					'student_id' : record.id
				})
				record.user_id = user_id
				record.partner_id = self.id

	def get_parent(self):
		action = self.env.ref('school_management.action_student_parent').read()[0]
		action['domain'] = [('student_ids', 'in', self.ids)]
		return action

	def get_assignment(self):
		action = self.env.ref('school_management.action_school_student_assignment').read()[0]
		action['domain'] = [('student_id', '=', self.id)]
		return action

	def compute_count_assignment(self):
		for record in self:
			record.assignment_count = self.env['school.student.assignment'].search_count(
				[('student_id', '=', self.id)])

	@api.model
	def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
		print("calllllllllledddddddddd", self._context,self)
		if 'standard_id' in self._context:
			standard_id = self._context.get('standard_id')
			if standard_id:
				print (">>>>>>>>>>>>>>>>>>>>>>", standard_id)
				standard_id = self.env['student.class'].search([('id', '=', standard_id)])
				stud_ids = standard_id.subject_ids.ids
				print ("stud_ids", stud_ids)
				args = [('id', 'in', stud_ids)]
		res = super(StudentStudent, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=None)
		return res

	def _get_report_base_filename(self):
		return self.name
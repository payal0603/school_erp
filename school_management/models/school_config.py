from odoo import api, models, fields , _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class StudentSubject(models.Model):
	_name = 'student.subject'
	_inherit = ["mail.thread"]
	_description = 'Student Subject'
	

	name = fields.Char(string='Name', required=True)
	# code = fields.Char(string="Subject Code")
	type = fields.Selection([
		('theory', 'Theory'), 
		('practical', 'Practical'),
		('both', 'Both')], string='Type', required=True)
	subject_type = fields.Selection([
		('compulsory', 'Compulsory'), 
		('elective', 'Elective')], string='Subject Type')
	subject_id = fields.Many2one('student.admission')
	teacher_id = fields.Many2one('student.teacher')
	active = fields.Boolean(default=True,string='Activate ', tracking=True)

	@api.model
	def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
		if 'standard_id' in self._context:
			standard_id = self._context.get('standard_id')
			if standard_id:
				print (">>>>>>>>>>>>>>>>>>>>>>", standard_id)
				standard_id = self.env['student.class'].search([('id', '=', standard_id)])
				sub_ids = standard_id.subject_ids.ids
				print ("sub_ids", sub_ids)
				args = [('id', 'in', sub_ids)]
		res = super(StudentSubject, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=None)
		return res

	# @api.model
	# def search(self, args, offset=0, limit=None, order=None, count=False):
	# 	if 'standard_id' in self._context:
	# 		standard_id = self._context.get('standard_id')
	# 		if standard_id:
	# 			print (">>>>>>>>>>>>>>>>>>>>>>", standard_id)
	# 			standard_id = self.env['student.class'].search([('id', '=', standard_id)])
	# 			sub_ids = standard_id.subject_ids.ids
	# 			print ("sub_ids", sub_ids)
	# 			args += [('id', 'in', sub_ids)]
	# 	return super(StudentSubject, self).search(args, offset=offset, limit=limit, order=order, count=count)

	

class StudentClass(models.Model):
	_name = 'student.class'
	_inherit = ["mail.thread"]
	_description = 'Student Standard'

	name = fields.Char(string='Standard', required=True)
	code = fields.Char(string="Code")
	subject_ids = fields.Many2many('student.subject', string='Subject')
	division_id = fields.Many2many('student.division', string="Division")
	department_id = fields.Many2one('student.department', string='Department')
	active = fields.Boolean(default=True,string='Activate ', tracking=True)
	

class StudentDivision(models.Model):
	_name = 'student.division'
	_inherit = ["mail.thread"]
	_description = 'Division Details'

	name = fields.Char(string="Division")
	active = fields.Boolean(default=True,string='Activate ', tracking=True)

	@api.model
	def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
		if 'standard_id' in self._context:
			standard_id = self._context.get('standard_id')
			if standard_id:
				print (">>>>>>>>>>>>>>>>>>>>>>", standard_id)
				standard_id = self.env['student.class'].search([('id', '=', standard_id)])
				div_ids = standard_id.division_id.ids
				print ("div_ids", div_ids)
				args = [('id', 'in', div_ids)]
		res = super(StudentDivision, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=None)
		return res


class StudentDepartment(models.Model):
	_name = 'student.department'
	_inherit = ["mail.thread"]
	_description = 'Department Details'

	name = fields.Char(string="Department name")
	code = fields.Char(string="Code")
	active = fields.Boolean(default=True)

	@api.model
	def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
		if 'standard_id' in self._context:
			standard_id = self._context.get('standard_id')
			if standard_id:
				standard_id = self.env['student.class'].search([('id', '=', standard_id)])
				dep_ids = standard_id.department_id.ids
				print ("dep_ids", dep_ids)
				args += [('id', 'in', dep_ids)]
		res = super(StudentDepartment, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=None)
		return res
	

class StudentClassroom(models.Model):
	_name = 'student.classroom'
	_inherit = ["mail.thread"]
	_description = 'Classroom Details'

	name = fields.Char(string="Classroom No.")
	capacity = fields.Integer(string="No. Of Person")
	standard_id = fields.Many2one('student.class', string="Standard")
	division_id = fields.Many2one('student.division', string="Division")
	active = fields.Boolean(string="Active",  default=True)
	
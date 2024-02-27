from odoo import models, fields, api


# class StudentAttendenceType(models.Model):
# 	_name = "student.attendence.type"
# 	_inherit = ["mail.thread"]
# 	_description = "Attendence Type"

# 	name = fields.Char(string="Name", required=True, tracking=True)
# 	active = fields.Boolean(default=True)
# 	present = fields.Boolean(string="Present", tracking=True)
# 	absent = fields.Boolean(string="Absent", tracking=True)
# 	late = fields.Boolean(string="Late", tracking=True)


class StudentAttendenceSheet(models.Model):
	_name = "student.attendence.sheet"
	_inherit = ["mail.thread"]
	_description = "Attendence Sheet"
	_order = "attendence_date desc"

	name = fields.Char(string='Name', size=32, required=True)
	register_id = fields.Many2one('student.attendence.register', string='Register', required=True, tracking=True)
	standard_id = fields.Many2one('student.class', related='register_id.standard_id', store=True, readonly=True)
	division_id = fields.Many2one('student.division', string='Batch', related='register_id.division_id', store=True, readonly=True)
	attendence_date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today(),tracking=True)
	attendence_line = fields.One2many('student.attendence.line', 'attendence_id', string='Attendence Line')
	teacher_id = fields.Many2one('student.teacher', 'Faculty')
	active = fields.Boolean(default=True)
	state = fields.Selection(
		[('draft', 'Draft'), ('start', 'Attendence Start'),
		 ('done', 'Attendence Taken'), ('cancel', 'Cancelled')], string='Status', default='draft', tracking=True)

	def attendence_draft(self):
		self.state = 'draft'

	def attendence_start(self):
		self.state = 'start'

	def attendence_done(self):
		self.state = 'done'

	def attendence_cancel(self):
		self.state = 'cancel'

	@api.model
	def create(self, vals):
		sheet = self.env['ir.sequence'].next_by_code('student.attendence.sheet')
		register = self.env['student.attendence.register']. \
			browse(vals['register_id']).code
		vals['name'] = register # str(register+" {}").format(sheet)
		return super(StudentAttendenceSheet, self).create(vals)
		
	@api.model
	def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
		if 'standard_id' in self._context:
			standard_id = self._context.get('standard_id')
			if standard_id:
				print (">>>>>>>>>>>>>>>>>>>>>>", standard_id)
				standard_id = self.env['student.class'].search([('id', '=', standard_id)])
				stud_ids = standard_id.subject_ids.ids
				print ("stud_ids", stud_ids)
				args += [('id', 'in', stud_ids)]
		res = super(StudentAttendenceSheet, self)._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=None)
		return res


class StudentAttendenceRegister(models.Model):
	_name = "student.attendence.register"
	_inherit = ["mail.thread"]
	_description = "Attendence Register"
	_order = "id DESC"

	name = fields.Char(string="Name", required=True, tracking=True, compute="_compute_name")
	code = fields.Char(string="Code", required=True, tracking=True)
	standard_id = fields.Many2one('student.class', string="Standard", required=True, tracking=True)
	division_id = fields.Many2one('student.division', string="Division", required=True, tracking=True)
	subject_id = fields.Many2one('student.subject', string="Subject",tracking=True)
	active = fields.Boolean(default=True)

	@api.depends('standard_id')
	def onchange_standard(self):
		if not self.standard_id:
			self.division_id = False

	@api.depends('standard_id', 'division_id')
	def _compute_name(self):
		for rec in self:
			if rec.standard_id and rec.division_id:
				name = "Standard : " + str(rec.standard_id.name) + " Division : " + str(rec.division_id.name)
				rec.name = name
			else:
				rec.name = ''

class StudentAttendenceLine(models.Model):
	_name = "student.attendence.line"
	_inherit = ["mail.thread"]
	_rec_name = "attendence_id"
	_description = "Attendence Lines"
	_order = "attendence_date desc"

	attendence_id = fields.Many2one('student.attendence.sheet', string="Attendence Sheet", required=True, tracking=True, ondelete="cascade")
	student_id = fields.Many2one('student.student', string="Student", required=True, tracking=True)
	present = fields.Boolean(string="Present", default=True, tracking=True)
	absent = fields.Boolean(string="Absent", tracking=True)
	late = fields.Boolean(string="Late", tracking=True)
	standard_id = fields.Many2one('student.class', string="Standard", related="attendence_id.register_id.standard_id", store=True, readonly=True)
	division_id = fields.Many2one('student.division', string="Division", related="attendence_id.register_id.division_id", store=True, readonly=True)
	attendence_date = fields.Date(string="Date", related="attendence_id.attendence_date", store=True, readonly=True, tracking=True)
	register_id = fields.Many2one(related="attendence_id.register_id", store=True)
	remark = fields.Char(string="Remark")
	active = fields.Boolean(default=True)
	
	@api.onchange('present')
	def onchange_present(self):
		if self.present:
			self.absent = False 
			self.late = False 

	@api.onchange('absent')
	def onchange_absent(self):
		if self.absent:
			self.present = False 
			self.late = False 

	@api.onchange('late')
	def onchange_late(self):
		if self.late:
			self.absent = False 
			self.present = False 

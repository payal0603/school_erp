import calendar
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class StudentTiming(models.Model):
	_name = 'student.timing'
	_inherit = ["mail.thread"]
	_description = 'Timetable Timing'

	name = fields.Char(string="Name", required=True)
	hour = fields.Selection([
		('1', '1'),('2', '2'),('3', '3'),('4', '4'),
		('5', '5'),('6', '6'),('7', '7'),('8', '8'),
		('9', '9'),('10', '10'),('11', '11'),('12', '12')], string="Starting Hour", required=True)
	minute = fields.Selection([
		('00', '00'),('15', '15'),
		('30', '30'),('45', '45')], string="Minute", required=True)
	duration = fields.Float(string="Duration")
	am_pm = fields.Selection([
		('am', 'AM'),('pm', 'PM')], string="AM/PM", required=True)
	sequence = fields.Integer(string="Sequence")
	active = fields.Boolean(default=True,string='Activate ', tracking=True)


class StudentTimetable(models.Model):
	_name = 'student.timetable'
	_inherit = ["mail.thread"]
	_description = 'Student Timetable'

	week_days = [(calendar.day_name[0], _(calendar.day_name[0])),
			 (calendar.day_name[1], _(calendar.day_name[1])),
			 (calendar.day_name[2], _(calendar.day_name[2])),
			 (calendar.day_name[3], _(calendar.day_name[3])),
			 (calendar.day_name[4], _(calendar.day_name[4])),
			 (calendar.day_name[5], _(calendar.day_name[5])),
			 (calendar.day_name[6], _(calendar.day_name[6]))]

	# name = fields.Char(string="Name")
	name = fields.Char( string="Name", compute="_compute_name", required=True, tracking=True)
	timing_id = fields.Many2one('student.timing', string="Timing", required=True)
	start_time = fields.Datetime(string="Start Time", required=True, default=lambda self: fields.Datetime.now())
	end_time = fields.Datetime(string="End Time", required=True)
	duration = fields.Float(string="Duration", related="timing_id.duration")
	standard_id = fields.Many2one('student.class', string="Standard", required=True)
	division_id = fields.Many2one('student.division', string="Division", required=True)
	subject_id = fields.Many2one('student.subject', string="Subject Name", required=True)
	classroom_id = fields.Many2one('student.classroom', string="Classroom")
	teacher_id = fields.Many2one('student.teacher', string="Teacher Name", required=True)
	type = fields.Char(compute="_compute_day", string="Day")
	state = fields.Selection([
		('draft', 'Draft'),('confirm', 'Confirm'),
		('done', 'Done'),('cancel', 'Cancel')], string="Status", default="draft")
	active = fields.Boolean(default=True,string='Activate ', tracking=True)

	@api.depends('teacher_id', 'subject_id', 'start_time')
	def _compute_name(self):
		for rec in self:
			if rec.standard_id and rec.division_id and rec.start_time:
				name = ' Timing : ' + str(rec.timing_id.name) + " Standard : " + str(rec.standard_id.name) + ' ::  ' + str(rec.division_id.name) 
				rec.name = name
			else:
				rec.name = ''

	# For record rule on student and teacher dashboard
	@api.depends('division_id', 'teacher_id')
	def _compute_batch_users(self):
		student_obj = self.env['student.student']
		for timetable in self:
			student_ids = student_obj.search(
				[('standard_detail_ids.division_id', '=', timetable.division_id.id)])
			user_list = [student_id.id for student_id
						 in student_ids if student_id]
			if timetable.teacher_id:
				user_list.append(timetable.teacher_id.id)
			
	@api.depends('start_time')
	def _compute_day(self):
		for rec in self:
			rec.type = fields.Datetime.from_string(
				rec.start_time).strftime("%A")

	def lec_confirm(self):
		self.state = 'confirm'

	def lec_done(self):
		self.state = 'done'

	def lec_draft(self):
		self.state = 'draft'

	def lec_cancel(self):
		self.state = 'cancel'

	@api.constrains('teacher_id', 'timing_id', 'start_time', 'classroom_id',
					'division_id', 'subject_id')
	def check_timetable_fields(self):
		res_param = self.env['ir.config_parameter'].sudo()
		teacher_constraint = res_param.search([('key', '=', 'timetable.is_teacher_constraint')])
		classroom_constraint = res_param.search([('key', '=', 'timetable.is_classroom_constraint')])
		batch_and_subject_constraint = res_param.search([('key', '=', 'timetable.is_batch_and_subject_constraint')])
		batch_constraint = res_param.search([('key', '=', 'timetable.is_batch_constraint')])
		is_teacher_constraint = teacher_constraint.value
		is_classroom_constraint = classroom_constraint.value
		is_batch_and_subject_constraint = batch_and_subject_constraint.value
		is_batch_constraint = batch_constraint.value
		sessions = self.env['student.timetable'].search([])
		for session in sessions:
			if self.id != session.id:
				if is_teacher_constraint:
					if self.teacher_id.id == session.teacher_id.id and \
							self.timing_id.id == session.timing_id.id and \
							self.start_time.date() == session.start_time.date():
						raise ValidationError(_(
							'You cannot create a session with same teacher on same date '
							'and time'))
				if is_classroom_constraint:
					if self.classroom_id.id == session.classroom_id.id and \
							self.timing_id.id == session.timing_id.id and \
							self.start_time.date() == session.start_time.date():
						raise ValidationError(_(
							'You cannot create a session with same classroom on same date'
							' and time'))
				if is_batch_and_subject_constraint:
					if self.division_id.id == session.division_id.id and \
							self.timing_id.id == session.timing_id.id and \
							self.start_time.date() == session.start_time.date() \
							and self.subject_id.id == session.subject_id.id:
						raise ValidationError(_(
							'You cannot create a session for the same batch on same time '
							'and for same subject'))
				if is_batch_constraint:
					if self.division_id.id == session.division_id.id and \
							self.timing_id.id == session.timing_id.id and \
							self.start_time.date() == session.start_time.date():
						raise ValidationError(_(
							'You cannot create a session for the same batch on same time '
							'even if it is different subject'))

	@api.model
	def create(self, values):
		res = super(StudentTimetable, self).create(values)
		mfids = res.message_follower_ids
		partner_val = []
		partner_ids = []
		for val in mfids:
			partner_val.append(val.partner_id.id)
		if res.teacher_id and res.teacher_id.user_id:
			partner_ids.append(res.teacher_id.user_id.partner_id.id)
		if res.division_id and res.standard_id:
			standard_val = self.env['student.student'].search([
				('division_id', '=', res.division_id.id),
				('standard_id', '=', res.standard_id.id)
			])
			for val in standard_val:
				if val.student_id.user_id:
					partner_ids.append(val.student_id.user_id.partner_id.id)
		subtype_id = self.env['mail.message.subtype'].sudo().search([
			('name', '=', 'Discussions')])
		if partner_ids and subtype_id:
			mail_followers = self.env['mail.followers'].sudo()
			for partner in list(set(partner_ids)):
				if partner in partner_val:
					continue
				mail_followers.create({
					'res_model': res._name,
					'res_id': res.id,
					'partner_id': partner,
					'subtype_ids': [[6, 0, [subtype_id[0].id]]]
				})
		return res

	@api.onchange('standard_id')
	def onchange_standard(self):
		self.division_id = False
		if self.standard_id:
			subject_ids = self.env['student.student'].search([
				('id', '=', self.standard_id.subject_ids.ids)])
			return {'domain': {'subject_id': [('id', 'in', subject_ids.ids)]}}

	def notify_user(self):
		template = ''
		for session in self:
			template = self.env.ref(
				'school_management.session_details_changes',
				raise_if_not_found=False)
			template.send_mail(session.id)

	def get_emails(self, follower_ids):
		email_ids = ''
		for user in follower_ids:
			if email_ids:
				email_ids = email_ids + ',' + str(user.sudo().partner_id.email)
			else:
				email_ids = str(user.sudo().partner_id.email)
		return email_ids

	
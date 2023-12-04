from odoo import models, api, fields


class studentHeldExam(models.TransientModel):
	_name = "student.held.exam"
	_description = "Held Exam"

	standard_id = fields.Many2one('student.class', string='class')
	division_id = fields.Many2one('student.division', string='Division')
	exam_id = fields.Many2one('student.exam', 'Exam')
	subject_id = fields.Many2one('student.subject', 'Subject')
	attendees_line = fields.Many2many(
		'student.exam.attendees', string='Attendees')

	@api.model
	def default_get(self, fields):
		res = super(studentHeldExam, self).default_get(fields)
		active_id = self.env.context.get('active_id', False)
		exam = self.env['student.exam'].browse(active_id)
		session = exam.session_id
		res.update({
			# 'division_id': session.division_id.id,
			'standard_id': session.standard_id.id,
			'exam_id': active_id,
			'subject_id': exam.subject_id.id
		})
		return res

	def held_exam(self):
		for record in self:
			if record.attendees_line:
				for attendee in record.attendees_line:
					if attendee.status == 'present':
						attendee.status = 'present'
					else:
						attendee.status = 'absent'	
			record.exam_id.state = 'held'
			return True

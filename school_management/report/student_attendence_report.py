import time
from odoo import models, api


class StudentAttendenceReport(models.AbstractModel):
	_name = "report.school_management.student_attendence_report"
	_description = "Attendence Report"

	def get_student_name(self, data):
		student = self.env['student.student'].browse(data['student_id'])
		if student:
			return student.name

	def get_data(self, data):
		sheet_search = self.env['student.attendence.sheet'].search(
			[('attendence_date', '>=', data['from_date']),
			 ('attendence_date', '<=', data['to_date'])],
			order='attendence_date asc')

		lst = []
		for sheet in sheet_search:
			for line in sheet.attendence_line:
				dic = {}
				if data['student_id'] == line.student_id.id and \
						not line.present:
					dic = {
						'absent_date': sheet.attendence_date,
						'remark': line.remark
					}
					lst.append(dic)
		return [{'total': len(lst),
				 'line': lst}]

	@api.model
	def _get_report_values(self, docids, data):
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_id'))
		docargs = {
			'doc_ids': self.ids,
			'doc_model': model,
			'docs': docs,
			'time': time,
			'from_date': data['from_date'],
			'to_date': data['to_date'],
			'get_student_name': self.get_student_name(data),
			'get_data': self.get_data(data),
		}
		return docargs

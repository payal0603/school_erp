import time
from odoo import models, fields, api


class ReportTicket(models.AbstractModel):
	_name = "report.school_management.student_hall_ticket_report"  
	_description = "Exam Ticket Report"

	def get_date(self, exam_line):
		timestamp = fields.Datetime.context_timestamp
		dt = fields.Datetime
		schedule_start = timestamp(self, dt.from_string(exam_line.start_time))
		schedule_end = timestamp(self, dt.from_string(exam_line.end_time))
		schedule_start = fields.Datetime.to_string(schedule_start)
		schedule_end = fields.Datetime.to_string(schedule_end)

		return schedule_start[11:] + ' To ' + schedule_end[11:]

	def get_subject(self, exam_session):
		lst = []
		for exam_line in exam_session['exam_ids']:
			res1 = {
				'subject': exam_line.subject_id.name,
				'date': fields.Datetime.to_string(exam_line.start_time)[:10],
				'time': self.get_date(exam_line),
				'sup_sign': ''
			}
			lst.append(res1)
		return lst

	def get_data(self, data):
		print(">>>>>>>>>>>>>>>DATA 111111>>>>>>>>>>>",data)
		final_lst = []
		exam_session = self.env['student.exam.session'].browse(data['exam_session_id'][0])
		print(">>>>>>>>>>>>>>>DATA >>>>>>>>>>>",data)
		student_search = self.env['student.student'].search([('standard_id', '=', exam_session.standard_id.id)])
		for student in student_search:
			print("STUDNT>>>>>>>>>>>>>",student)
			res = {
				'exam': exam_session.name,
				'code': exam_session.code,
				'standard': exam_session.standard_id.id,
				'student': student.name,
				'image': student.image,
				'line': self.get_subject(exam_session),
			}
			final_lst.append(res)
			print("<<<<<<<<<<<Final LST>>>>>>>>>", final_lst)
		return final_lst

	@api.model
	def _get_report_values(self, docids, data):
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_id'))
		docargs = {
			'doc_ids': self.ids,
			'doc_model': 'student.exam.session',
			'docs': docs,
			'time': time,
			'get_data': self.get_data(data),
		}
		return docargs

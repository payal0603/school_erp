import calendar
import pytz
import time
from datetime import datetime
from odoo import models, api, _, fields, tools


class ReportTimetableStudentGenerate(models.AbstractModel):
	_name = "report.school_management.report_timetable_student_generate"
	_description = "Timetable Student Report"

	def _convert_to_local_timezone(self, time):
		if time:
			timezone = pytz.timezone(self._context['tz'] or 'UTC')
			utc_in_time = pytz.UTC.localize(fields.Datetime.from_string(time))
			local_time = utc_in_time.astimezone(timezone)
			return local_time

	def sort_tt(self, data_list):
		main_list = []
		f = []
		for d in data_list:
			if d['period'] not in f:
				f.append(d['period'])
				main_list.append({
					'name': d['period'],
					'line': {d['day']: d}
				})
			else:
				for m in main_list:
					if m['name'] == d['period']:
						m['line'][d['day']] = d
		return main_list

	def get_heading(self):
		dayofWeek = [_(calendar.day_name[0]),
					 _(calendar.day_name[1]),
					 _(calendar.day_name[2]),
					 _(calendar.day_name[3]),
					 _(calendar.day_name[4]),
					 _(calendar.day_name[5])]
		return dayofWeek

	def get_object(self, data):
		data_list = []
		for timetable_obj in self.env['student.timetable'].browse(
				data['time_table_ids']):
			oldDate = pytz.UTC.localize(
				fields.Datetime.from_string(timetable_obj.start_time))
			day = datetime.weekday(oldDate)
			timetable_data = {
				'period': timetable_obj.timing_id.name,
				'sequence': timetable_obj.timing_id.sequence,
				'start_time': self._convert_to_local_timezone(
					timetable_obj.start_time).strftime(
					tools.DEFAULT_SERVER_DATETIME_FORMAT),
				'day': str(day),
				'subject': timetable_obj.subject_id.name,
			}
			data_list.append(timetable_data)
		ttdl = sorted(data_list, key=lambda k: k['sequence'])
		final_list = self.sort_tt(ttdl)
		return final_list

	@api.model
	def _get_report_values(self, docids, data):
		model = self.env.context.get('active_model')
		docs = self.env[model].browse(self.env.context.get('active_id', False))
		docargs = {
			'doc_ids': self.ids,
			'doc_model': model,
			'docs': docs,
			'data': data,
			'time': time,
			'get_object': self.get_object,
			'get_heading': self.get_heading,
		}
		return docargs

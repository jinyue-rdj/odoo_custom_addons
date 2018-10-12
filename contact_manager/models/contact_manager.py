from odoo import models, api, fields
import base64
import logging
import os

_logger = logging.getLogger("ContactManager")


class ContactManager(models.Model):

    _name = "contact.manager"

    name = fields.Char('Contact Name', required=True)
    address = fields.Char('Address')
    phone = fields.Char('Mobile')
    age = fields.Integer()


class ContactImporter(models.Model):

    _name = "contact.importer"

    csv_data = fields.Binary('CSV File', default='')

    @api.multi
    def do_import(self):
        file_content = base64.decodebytes(self.csv_data)
        file_content_string = file_content.decode("utf-8")

        _logger.info("file content is %s", file_content_string)

        csv_manager = self.env['csv.import.manager']

        csv_manager.initialize(
            import_operation='contact_import',
            import_data=file_content_string,
            validation_method='import_validator',
            caller_class=self._name,
            db_cols_count=4,
            debug=True
        )
        csv_manager.start_import()

    def import_validator(self, csv_import_data, task_id=None):
        with api.Environment.manage():
            # new_cr = db_connect( self.env.cr.dbname ).cursor()
            # self.env = api.Environment( new_cr, self.env.uid, self.env.context )
            total_records = 0

            is_validate, message = self.invalidate_check_data(csv_import_data)
            if not is_validate:
                return False, message

            obj_csv_manager = self.env['contact.manager']
            csv_holder = self.env['csv.import.holder']

            for row in csv_import_data:
                total_records += 1
                data = {
                            'name': row[0],
                            'age': int(row[1]),
                            'address': row[2],
                            'phone': row[3]
                      }
                obj_csv_manager.create(data)
                csv_holder.update_task_progress(task_id, total_records, "")
                self.env.cr.commit()
            '''if not self.env.cr.closed:
                self.env.cr.close()'''
            return True, str(total_records) + "  records inserted"

    def invalidate_check_data(self, csv_import_data):
        message = "Success checked data"
        for row in csv_import_data:
            try:
                age = int(row[1])
            except Exception:
                message = "cann't convert %s to int" % (row[2])
                _logger.info(message)
                return False, message
        return True, message


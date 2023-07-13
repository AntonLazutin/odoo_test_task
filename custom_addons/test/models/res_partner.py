from odoo import api, models, fields
import re

from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    name = fields.Char(index=True, default_export_compatible=True, required=False) #doesn't work :(
    department = fields.Char()
    first_name = fields.Char()
    surname = fields.Char()
    origin_country = fields.Selection([('us', 'United States'),
                                       ('uk', 'United Kingdom')])
    experience = fields.Float()

    @api.model
    def create(self, vals_list):
        if vals_list['company_type'] == 'person':
            vals_list['name'] = f'{vals_list["first_name"]} {vals_list["surname"]}'
        print(vals_list)
        return super(ResPartner, self).create(vals_list) #поле имя не пропускает пробел между именем и фамилией

    @api.constrains('experience')
    def _check_experience(self):
        """
        Validation for experience field
        Examples:
        1. User tries to save form with negative experience number -> field is set to 0 anyway
        2. User tries to save form with experience number higher, than 70 -> too unrealistic, error is raised
        """
        if self.experience < 0:
            self.experience = 0
        elif self.experience > 70:
            raise ValidationError('Unrealistic experience number')

    @api.constrains('name')
    def _check_company_name(self):
        for record in self:
            if re.match('^[a-zA-Z0-9 ]*$', record.name) is None:
                raise ValidationError('Non alphanumeric characters are not allowed')

    @api.constrains('company_name')
    def _check_company_name_individual(self):
        for record in self:
            if record.company_name:
                if re.match('^[a-zA-Z0-9_]+$', record.company_name) is None:
                    raise ValidationError('Non alphanumeric characters are not allowed on company name field')

    @api.constrains('department')
    def _check_department(self):
        for record in self:
            if record.department:
                if re.match('^[a-zA-Z]+$', record.department) is None:
                    raise ValidationError('Only alphabetical characters on department field are allowed')

    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            print(f'phone {record.phone}')
            if len(record.phone.replace(' ', '')) == 0:
                raise ValidationError('Blank string for phone field is not allowed')
            elif re.match("^\\+?[1-9][0-9]{7,14}$", record.phone) is None:
                raise ValidationError('Invalid phone format')

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            print(f'email {record.email}')
            regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
            if not re.fullmatch(regex, record.email):
                raise ValidationError('Invalid email format')

    _sql_constraints = [
        ('check_name', 'CHECK(1=1)', ""),
    ]


    # перенастроить create метод
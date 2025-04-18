# forms.py
from wtforms import Form, StringField, SelectField, DecimalField, DateField, validators

class PolicyForm(Form):
    policy_number = StringField('Policy Number', [validators.Length(min=5, max=20)])
    customer_id = StringField('Customer ID', [validators.InputRequired()])
    insurance_type = SelectField('Type', choices=[('Auto', 'Auto'), ('Home', 'Home'), ('Life', 'Life')])
    premium = DecimalField('Premium', [validators.NumberRange(min=0)])
    start_date = DateField('Start Date', format='%Y-%m-%d')
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[validators.Optional()])

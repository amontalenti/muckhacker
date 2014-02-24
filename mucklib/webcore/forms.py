# Post/Put Validation logic and some forms
import re

import bleach
from wtforms import Form, TextField, PasswordField, ValidationError
from wtforms.validators import Required, Length
import wtforms_json

wtforms_json.init()

class MarkdownField(TextField):
    def process_formdata(self, value):
        super(MarkdownField, self).process_formdata(value)
        pre = self.data
        self.data = bleach.clean(pre)

class PostEditForm(Form):
    title = TextField('title', [Length(min=0, max=500), 
                                Required()])
    body = MarkdownField('body', [Length(min=0, max=9000)])

class LoginForm(Form):
    username = TextField('Username', [Length(min=5, max=50),
                                      Required()])
    password = PasswordField('Password', [Required()])

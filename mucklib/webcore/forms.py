# Post/Put Validation logic and some forms
from lxml.html import clean
from wtforms import Form, TextField, PasswordField, ValidationError
from wtforms.validators import Required, Length
import wtforms_json

wtforms_json.init()

def clean_html_field(allowed, field):
    """Only accepts tags described in allowed w/o any attrs"""
    cleaner = clean.Cleaner(allow_tags=allowed,  # TODO this removes all &nbsp;s prevents whitespace...
                            remove_unknown_tags=False,
                            safe_attrs_only=True, 
                            safe_attrs=[],
                           )
    preproc = "<div>{}</div>".format(field.data) #quick hack that worries me
    cleaned = cleaner.clean_html(preproc)
    if cleaned == preproc:
        return True
    else:
        raise ValidationError("Invalid html provided")

def check_body_content(form, field):
    allowed = ["a", "p", "h4", "h3", "em", "br", "blockquote", "b", "u", "code"]
    return clean_html_field(allowed, field)

def check_title_content(form, field):
    allowed = ["p", "em", "b", "quote"]
    return clean_html_field(allowed, field)


class PostEditForm(Form):
    title = TextField('title', [check_title_content,
                                Length(min=0, max=500), 
                                Required()])
    body = TextField('body', [check_body_content,
                              Length(min=0, max=9000)])

class LoginForm(Form):
    username = TextField('Username', [Length(min=5, max=50),
                                      Required()])
    password = PasswordField('Password', [Required()])

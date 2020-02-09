from wtforms import Form, StringField


class UrlForm(Form):
    original_url = StringField('')

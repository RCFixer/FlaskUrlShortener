from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from flask_admin import Admin, BaseView, expose
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flask_security import SQLAlchemyUserDatastore
from flask_security import Security
from flask_security import current_user

from flask import redirect, url_for, request

from config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)

db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

from models import *


class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


class BaseModelView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    @expose('/', methods=('GET', 'POST'))
    def admin_stats(self):
        page = request.args.get('page')
        if page and page.isdigit():
            page = int(page)
        else:
            page = 1
        links = Link.query.order_by(Link.id.desc())
        pages = links.paginate(page=page, per_page=15)
        return self.render('admin_stats.html', pages=pages)


admin = Admin(app, 'CutURL', url='/', index_view=HomeAdminView(name='Stats'))
admin.add_view(BaseModelView(Link, db.session))
admin.add_view(BaseModelView(User, db.session))
admin.add_view(BaseModelView(Role, db.session))
### Security

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

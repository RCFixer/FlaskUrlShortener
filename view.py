from flask import render_template, request, redirect, flash, url_for
from flask_security import current_user, login_required

from app import app, db
from models import Link
from forms import UrlForm


@app.route('/<short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    link.visits = link.visits + 1
    db.session.commit()
    return redirect(link.original_url)


@app.route('/', methods=['POST', 'GET'])
def index():
    form = UrlForm()
    if request.method == "POST":
        original_url = request.form['original_url']
        link = Link(original_url=original_url, user=current_user)
        db.session.add(link)
        db.session.commit()
        short = link.short_url
        flash(short, "success")
        return redirect(url_for('index'))
    return render_template('index.html', form=form)


@app.route('/stats')
@login_required
def stats():
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    links = current_user.links.order_by(Link.id.desc())
    pages = links.paginate(page=page, per_page=15)
    return render_template('stats.html', pages=pages)


@app.errorhandler(404)
def page_not_found(e):
    return '<h1>404</h1>', 404

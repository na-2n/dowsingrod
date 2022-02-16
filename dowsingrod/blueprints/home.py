from flask import Blueprint, render_template

from dowsingrod.app import rod, app
from dowsingrod.forms import ReportForm


mod = Blueprint('home', __name__)

@mod.route('/')
def index():
    treasure = rod.find_treasure()

    src = treasure.source if treasure.source_type != 'other' and treasure.source else f'https://danbooru.donmai.us/posts/{treasure.id}'

    sitekey = app.config['HCAPTCHA'].get('sitekey')
    form = ReportForm()

    return render_template('index.html',
                           treasure=treasure,
                           src=src, form=form,
                           hcaptcha={'sitekey': sitekey})

@mod.route('/report', methods=('POST',))
def report():
    form = ReportForm()

    if form.validate():
        print(form.reason.data)
        print(form.info.data)

        return {'success': True}

    return {'success': False}


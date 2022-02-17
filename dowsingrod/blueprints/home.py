from flask import Blueprint, render_template, request

from dowsingrod.app import rod, app
from dowsingrod.models import Report, ReportReason
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

REASON_MAP = {
    'unrelated': ReportReason.UNRELATED,
    'nsfw': ReportReason.NSFW,
    'other': ReportReason.OTHER
}

@mod.route('/report', methods=('POST',))
def report():
    form = ReportForm()

    if form.validate():
        ip = request.remote_addr
        reason = form.reason.data
        info = form.info.data

        print(ip)

        Report.create(
            ip_address=ip,
            report_reason=REASON_MAP[reason],
            report_info=reason or None
        )

        return {'success': True}

    return {'success': False, 'errors': form.errors}, 400


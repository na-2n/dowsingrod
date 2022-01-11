from datetime import datetime
from peewee import *

from dowsingrod.app import db


class User(db.Model):
    id = AutoField()
    created_at = DateTimeField(default=datetime.utcnow)

    username = CharField(max_length=32, unique=True)
    email = CharField()
    password = CharField(60)

    permissions = BitField()
    can_review = permissions.flag(0b01000000)
    is_admin = permissions.flag(0b10000000)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return f'<User {self.username}>'


class ReportStatus:
    PENDING = 0
    ACCEPTED = 1
    REJECTED = 2


class ReportReason:
    OTHER = 0
    NSFW = 1
    UNRELATED = 2


class Report(db.Model):
    id = AutoField()
    created_at = DateTimeField(default=datetime.utcnow)
    reviewed_at = DateTimeField(null=True)
    status = SmallIntegerField(default=ReportStatus.PENDING)
    rejected_reason = CharField(max_length=2048, null=True)
    ip_address = CharField(max_length=15)
    report_reason = SmallIntegerField()
    report_info = CharField(max_length=2048, null=True)


class BanType:
    REPORTS = 0
    API = 1
    FULL = 2


class BannedAddresses(db.Model):
    id = AutoField()
    banned_at = DateTimeField(default=datetime.utcnow)
    ban_type = SmallIntegerField(default=BanType.FULL)
    reason = CharField(max_length=2048)
    appealed = BooleanField(default=False)
    appealed_at = DateTimeField(null=True)
    ip_address = CharField(max_length=15)


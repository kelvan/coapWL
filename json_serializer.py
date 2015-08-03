import datetime


def default(obj):
    if isinstance(obj, (datetime.datetime, datetime.time, datetime.date)):
        return obj.isoformat()

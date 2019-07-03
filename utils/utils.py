import json
import collections
from datetime import timezone
from datetime import datetime
from datetime import timedelta

def datetime_to_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def payload_time_to_str(payload_time):
    return post_time_to_datetime(payload_time).strftime("%Y-%m-%d")


def post_time_to_datetime(post_time: str) -> datetime:
    """将POST数据中的时间转换为datetime格式"""
    return datetime.strptime(post_time, "%Y-%m-%dT%H:%M:%S.000")


def time_with_Z_to_datetime(z_time: str) -> datetime:
    return datetime.strptime(z_time, "%Y-%m-%dT%H:%M:%S.000Z") + \
           timedelta(hours=8)


def init_data_for_PDF(days_interval: int) -> collections.defaultdict:
    # 初始化图数据，初始list中元素数量为 end_time - start_time + 1
    return collections.defaultdict(lambda: [0] * (days_interval + 1))


def datetime_z_convert(dt, fmt="%Y-%m-%dT%H:%M:%S.%fZ"):
    d = datetime.strptime(dt, fmt)
    return str(d.replace(tzinfo=timezone.utc).astimezone(tz=None))[:10]
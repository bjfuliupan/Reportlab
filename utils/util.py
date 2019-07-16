import collections
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import json
import requests
from utils import constant
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


def init_data_for_pdf_with_interval(days_interval: int) -> collections.defaultdict:
    # 初始化图数据，初始list中元素数量为 end_time - start_time + 1
    return collections.defaultdict(lambda: [0 for _ in range(days_interval+1)])


def init_data_for_pdf_with_default_int() -> collections.defaultdict:
    # 初始化图数据，默认value为 int， default 0
    return collections.defaultdict(lambda: 0)


def datetime_z_convert(dt, fmt="%Y-%m-%dT%H:%M:%S.%fZ"):
    d = datetime.strptime(dt, fmt)
    return str(d.replace(tzinfo=timezone.utc).astimezone(tz=None))[:10]


def pretty_print(data):
    if isinstance(data, dict):
        print(json.dumps(data, indent=4, ensure_ascii=False))
    else:
        print(data)


def payload_time_to_datetime(payload_time: str) -> datetime:
    return datetime.strptime(payload_time, constant.LogConstant.PAYLOAD_TIME_FORMAT)


def log_format_to_detail(log_format: str) -> str:
    # 将日志类型转化为中文名称
    return constant.LogConstant.FORMAT_DETAIL_MAPPING.get(log_format, "未定义日志")


def datetime_to_category_time(target_time: datetime) -> str:
    # 将 datetime 格式时间转换为 折线图横坐标时间格式(%Y-%m-%d)
    return target_time.strftime(constant.LogConstant.CATAEGORY_TIME_FORMAT)


def adjust_es_log_time_to_datetime(log_time: str) -> datetime:
    # 从ES获取的日志格式形如： 2019-07-03T16:00:00.000Z， 且时间滞后8小时，需要重新格式化和校准
    return datetime.strptime(log_time, constant.LogConstant.ES_LOG_TIME_FORMAT) + timedelta(hours=8)


def cal_time_interval(base_time: datetime, target_time, target_time_format=None) -> int:
    # 计算两个时间的差值（天数差）
    # 将target_time转换为datetime类型
    if isinstance(target_time, str):
        target_time = datetime.strptime(target_time, target_time_format)

    return (target_time - base_time).days


def post_mrule(payload: dict, url="http://192.168.8.60:8002") -> dict:
    response = requests.post(url, data=json.dumps(payload))
    status_code = response.status_code
    content = response.content
    assert status_code == 200, \
        RuntimeError(f"request mrule: {payload} fail, errcode: {status_code}, reason: {content}")
    return json.loads(content)
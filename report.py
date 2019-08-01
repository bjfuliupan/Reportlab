import functools
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from utils import util
from urllib.parse import urlparse
from urllib.parse import parse_qs

from template_table3 import ReportSenHost
from template_table3 import ReportSenSafe
from template_table3 import ReportSenNetwork
from template_table3 import ReportFileOperation
from template_table3 import ReportSenPort
from template_table3 import ReportSenTrust
from template_table3 import ReportSenFile
from template_table3 import PDFReport

REPORT_PAGE_CLASS_MAPPING = {
        "主机运行日志": ReportSenHost,
        "违规定义日志": ReportSenSafe,
        "违规详情日志": ReportSenSafe,
        "其他安全日志": ReportSenSafe,
        "访问管控策略日志": ReportSenNetwork,
        "流量管控策略日志": ReportSenNetwork,
        "平均流量统计": ReportSenNetwork,
        # "open_port": ReportSenPort,
        "trust": ReportSenTrust,
        "critical_file": ReportSenFile,
        "file_operate": ReportFileOperation,
    }


PAYLOAD_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000"


class Report(object):
    pass


def validate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for kw in ["report_name", "data_scope",
                   "sensor_ids", "sensor_id_group_mapping",
                   "page_info", "send_mail"]:
            assert kwargs.get(kw) is not None, f"Require {kw}!"
        return func(*args, **kwargs)

    return wrapper


def gen_date_scope(data_scope: str) -> tuple:
    """#获取时间范围
    :param data_scope: 发送频率 week/month
    :return: 开始时间、结束时间
    """
    end_time_datetime = datetime.now()
    if data_scope == "week":
        start_time_datetime = end_time_datetime - relativedelta(weeks=1)
    elif data_scope == "month":
        start_time_datetime = end_time_datetime - relativedelta(months=1)
    else:
        raise ValueError(f"Not support data_scope=>{data_scope}")
    payload_start_time = start_time_datetime.strftime(PAYLOAD_TIME_FORMAT)
    payload_end_time = end_time_datetime.strftime(PAYLOAD_TIME_FORMAT)

    return payload_start_time, payload_end_time


def parse_url(url: str):
    """
    :param url: http url 包含页面资源路径和参数
    :return:
    """
    ret = {}

    url_obj = urlparse(url)
    params = parse_qs(url_obj.query)

    util.pretty_print(params)

    if params.get("tab"):
        ret["tab"] = params["tab"]

    if params.get("type"):
        ret["type"] = params["type"][0].split(",")

    return ret


@validate
def gen_report(*args, **kwargs):
    """生成report参数"""
    data_scope = kwargs["data_scope"]
    sensor_ids = kwargs["sensor_ids"]
    sensor_id_group_mapping = kwargs["sensor_id_group_mapping"]
    page_info = kwargs["page_info"]

    send_mail = kwargs["send_mail"]
    report_name = kwargs["report_name"]

    payload_start_time, payload_end_time = gen_date_scope(data_scope)

    for page in page_info:
        custom_name = page["custom_name"]
        page_source_name = page["page_source_name"]
        page_source_url = page["page_source_url"]
        sort_number = page["sort_number"]

        params = parse_url(page_source_url)
        util.pretty_print(params)

        _cls = REPORT_PAGE_CLASS_MAPPING[page_source_name]()
        _cls.indicate_date_scope(payload_start_time, payload_end_time)
        _cls.indicate_groups(sensor_id_group_mapping)
        _cls.indicate_sensors(sensor_ids)
        _cls.indicate_page_name(custom_name)
        _cls.indicate_sort_number(sort_number)
        _cls.add_items(params)

        _cls.draw_page()

    PDFReport().draw()






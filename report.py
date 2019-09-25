import functools
import os
from datetime import datetime
from urllib.parse import parse_qs
from urllib.parse import urlparse
import traceback

from dateutil.relativedelta import relativedelta

from pdflib.PDFTemplateR import PDFTemplateR
from template_table3 import ReportFileOperation
from template_table3 import ReportRunLog
from template_table3 import ReportSenFile
from template_table3 import ReportSenHost
from template_table3 import ReportSenNetwork
from template_table3 import ReportSenSafe
from template_table3 import ReportSenTrust
from template_table3 import ReportSetTimeOfCover
from template_table3 import ReportVm
from utils import util
from utils import constant

REPORT_PAGE_CLASS_MAPPING = {
    "主机运行日志": ReportSenHost,
    "违规定义日志": ReportSenSafe,
    "违规详情日志": ReportSenSafe,
    "其他安全日志": ReportSenSafe,
    "访问管控策略日志": ReportSenNetwork,
    "流量管控策略日志": ReportSenNetwork,
    "平均流量统计": ReportSenNetwork,
    "端口开放管理日志": ReportSenTrust,
    "应用安全基线日志": ReportSenTrust,
    "关键文件分析日志": ReportSenFile,
    "文件出入日志": ReportFileOperation,
    "运行日志": ReportRunLog,
    "策略变更日志": ReportRunLog,
    "容器和虚机日志": ReportVm,
}


def validate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for kw in ["report_name", "data_scope",
                   "sensor_ids", "sensor_id_group_mapping",
                   "page_info", "report_format"]:
            assert kwargs.get(kw) is not None, f"Require {kw}!"
        return func(*args, **kwargs)

    return wrapper


def gen_date_scope(data_scope: str) -> tuple:
    """获取时间范围
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
    payload_start_time = start_time_datetime.strftime(constant.LogConstant.PAYLOAD_TIME_FORMAT)
    payload_end_time = end_time_datetime.strftime(constant.LogConstant.PAYLOAD_TIME_FORMAT)

    return payload_start_time, payload_end_time


def parse_url(url: str):
    """
    :param url: http url 包含页面资源路径和参数
    :return:
    """
    print(f"url: {url}")
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
    print("start gen report")
    data_scope = kwargs["data_scope"]
    sensor_ids = kwargs["sensor_ids"]
    sensor_id_group_mapping = kwargs["sensor_id_group_mapping"]
    page_info = kwargs["page_info"]

    send_mail = kwargs["send_mail"]
    report_name = kwargs["report_name"]
    report_format = kwargs["report_format"]

    if report_format != "pdf":
        raise ValueError("Only support 'pdf' report format")

    payload_start_time, payload_end_time = gen_date_scope(data_scope)

    template_path = os.path.join(os.getcwd(), "templates", "template_charts.xml")
    print(template_path)
    assert os.path.exists(template_path) is True
    report_template = PDFTemplateR(template_path)
    report_template.set_pdf_file(".".join([report_name, report_format]))
    report_template.set_header_text(report_name)
    # 设置封面时间
    ReportSetTimeOfCover(report_template)

    for page in page_info:

        # if page["page_source_name"] != "主机运行日志":
        #     continue
        try:
            custom_name = page["custom_name"]
            page_source_name = page["page_source_name"]
            page_source_url = page["page_source_url"]
            sort_number = page["sort_number"]
            # 关键文件分析日志pdf图需要该字段
            rule_uuid = page.get("rule_uuid")

            params = parse_url(page_source_url)
            params.update(
                {
                    "rule_uuid": rule_uuid
                }
            )
            util.pretty_print(params)

            _cls = REPORT_PAGE_CLASS_MAPPING[page_source_name](report_template)
            print(f"++++++++++++++++++{page_source_name}++++++++++++++++++")
            _cls.indicate_date_scope(payload_start_time, payload_end_time)
            _cls.indicate_groups(sensor_id_group_mapping)
            _cls.indicate_sensors(sensor_ids)
            _cls.indicate_page_name(custom_name)
            _cls.indicate_sort_number(sort_number)
            _cls.add_items(params)

            _cls.draw_page()
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    report_template.draw()
    print("report draw done")

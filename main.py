import tornado
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from apscheduler.schedulers.background import BackgroundScheduler
from tornado.options import define
from tornado.options import options
from report import gen_report
from apscheduler.triggers.cron import CronTrigger
from utils import util

define("port", default=21001, help="run on the given port", type=int)


class DefaultErrorHandler(tornado.web.ErrorHandler):
    def data_received(self, chunk):
        pass

    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)
        self.write("<h1>404 Error!</h1>")
        self.finish()


class ReportHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        tornado.web.RequestHandler.__init__(*args, **kwargs)

    def data_received(self, chunk):
        pass

    async def post(self, *args, **kwargs):
        pass

    async def put(self, *args, **kwargs):
        pass

    async def delete(self, *args, **kwargs):
        pass


routes = [
            ()
        ]


class ReportApp(tornado.web.Application):
    def __init__(self, scheduler):
        settings = dict(
            default_handler_class=DefaultErrorHandler,
            default_handler_args={"status_code": 404},
            gzip=True,
            debug=False,
            cookie_secret='3hJxpjy/T/0JHy0P7eCgt/zhDUbLEUwImtdmKT9i8RU=',
            scheduler=scheduler
        )

        tornado.web.Application.__init__(self, routes, **settings)


sensor_id_group_mapping = {'LNX0001': '无分组',
 'LNX0002': '无分组',
 'LNX0003': '无分组',
 'LNX0004': '无分组',
 'LNX0005': '无分组',
 'LNX0006': '无分组',
 'LNX0007': '无分组',
 'LNX0008': '无分组',
 'LNX0009': '无分组',
 'LNX0010': '无分组',
 'LNX0011': '无分组',
 'LNX0012': '无分组',
 'LNX0013': '无分组',
 'LNX0014': '无分组',
 'LNX0015': '无分组',
 'LNX0016': '无分组',
 'LNX0017': '无分组',
 'LNX0018': '无分组',
 'LNX0019': '无分组',
 'LNX0021': '无分组',
 'LNX0023': '无分组',
 'LNX0024': '无分组',
 'LNX0025': '无分组',
 'LNX0026': '无分组',
 'LNX0027': '无分组',
 'LNX0028': '无分组',
 'WIN0003': '无分组',
 'WIN0075': '无分组',
 'WIN0116': '无分组',
 'WIN0117': '无分组',
 'WIN0118': '无分组',
 'WIN0119': '无分组',
 'WIN0120': '无分组',
 'WIN0121': '无分组',
 'WIN0122': '无分组',
 'WIN0123': '无分组',
 'WIN0124': '无分组',
 'WIN0125': '无分组',
 'WIN0126': '无分组',
 'WIN0127': '无分组',
 'WIN0128': '无分组',
 'WIN0129': '无分组',
 'WIN0130': '无分组',
 'WIN0131': '无分组',
 'WIN0132': '无分组',
 'WIN0133': '无分组',
 'WIN0135': '无分组',
 'WIN0136': '无分组',
 'WIN0137': '无分组',
 'WIN0138': '无分组',
 'WIN0139': '无分组',
 'WIN0140': '无分组',
 'WIN0141': '无分组',
 'WIN0142': '无分组',
 'WIN0143': '无分组',
 'WIN0144': '无分组',
 'WIN0145': '无分组',
 'WIN0146': '无分组',
 'WIN0147': '无分组',
 'WIN0148': '无分组',
 'WIN0149': '无分组',
 'WIN0150': '无分组',
 'WIN0151': '无分组',
 'WIN0152': '无分组',
 'WIN0153': '无分组',
 'WIN0154': '无分组',
 'WIN0155': '无分组',
 'WIN0156': '无分组',
 'WIN0157': '无分组',
 'WIN0158': '无分组',
 'WIN0159': '无分组',
 'WIN0160': '无分组',
 'WIN0161': '无分组',
 'WIN0162': '无分组',
 'WIN0163': '无分组',
 'WIN0164': '无分组',
 'WIN0165': '无分组',
 'WIN0166': '无分组',
 'WIN0167': '无分组',
 'WIN0168': '无分组',
 'WIN0169': '无分组',
 'WIN0170': '无分组',
 'WIN0171': '无分组',
 'WIN0172': '无分组',
 'WIN0173': '无分组',
 'WIN0174': '无分组',
 'WIN0175': '无分组',
 'WIN0176': '无分组',
 'WIN0177': '无分组',
 'WIN0178': '无分组',
 'WIN0179': '无分组',
 'WIN0180': '无分组',
 'WIN0181': '无分组',
 'WIN0182': '无分组',
 'WIN0183': '无分组',
 'WIN0184': '无分组',
 'WIN0186': '无分组',
 'WIN0188': '无分组',
 'WIN0189': '无分组',
 'WIN0190': '无分组',
 'WIN0191': '无分组',
 'WIN0192': '无分组',
 'WIN0193': '无分组',
 'WIN0194': '无分组',
 'WIN0195': '无分组',
 'WIN0196': '无分组',
 'WIN0197': '无分组',
 'WIN0198': '无分组',
 'WIN0199': '无分组',
 'WIN0200': '无分组',
 'WIN0201': '无分组',
 'WIN0202': '无分组',
 'WIN0203': '无分组',
 'WIN0204': '无分组',
 'WIN0205': '无分组',
 'WIN0206': '无分组',
 'WIN0207': '无分组',
 'WIN0208': '无分组',
 'WIN0209': '无分组',
 'WIN0210': '无分组',
 'WIN0211': '无分组',
 'WIN0212': '无分组',
 'WIN0213': '无分组',
 'WIN0214': '无分组',
 'WIN0215': '无分组',
 'WIN0216': '无分组',
 'WIN0217': '无分组',
 'WIN0218': '无分组',
 'WIN0219': '无分组',
 'WIN0220': '无分组',
 'WIN0221': '无分组',
 'WIN0222': '无分组',
 'WIN0223': '无分组',
 'WIN0224': '无分组',
 'WIN0225': '无分组',
 'WIN0226': '无分组',
 'WIN0227': '无分组',
 'WIN0228': '无分组',
 'WIN0229': '无分组',
 'WIN0230': '无分组',
 'WIN0231': '无分组',
 'WIN0232': '无分组',
 'WIN0233': '无分组',
 'WIN0234': '无分组',
 'WIN0235': '无分组',
 'WIN0236': '无分组',
 'WIN0237': '无分组',
 'WIN0238': '无分组',
 'WIN0239': '无分组',
 'WIN0240': '无分组',
 'WSR0001': '无分组',
 'WSR0002': '无分组',
 'WSR0003': '无分组',
 'WSR0004': '无分组',
 'WSR0005': '无分组',
 'WSR0006': '无分组',
 'WSR0007': '无分组',
 'WSR0008': '无分组',
 'WIN0014': '测试部',
 'WIN0015': '测试部',
 'WIN0016': '测试部',
 'WIN0017': '测试部',
 'WIN0019': '测试部',
 'WIN0020': '测试部',
 'WIN0022': '测试部',
 'WIN0023': '测试部',
 'WIN0024': '测试部',
 'WIN0025': '测试部',
 'WIN0026': '售前部',
 'WIN0027': '售前部',
 'WIN0028': '售前部',
 'WIN0029': '售前部',
 'WIN0035': '售前部',
 'WIN0042': '售前部',
 'WIN0061': '售前部',
 'WIN0018': '产品部',
 'WIN0045': '产品部',
 'WIN0046': '产品部',
 'WIN0047': '产品部',
 'WIN0001': '售后交付部',
 'WIN0013': '售后交付部',
 'WIN0034': '售后交付部',
 'WIN0036': '售后交付部',
 'WIN0037': '售后交付部',
 'WIN0038': '售后交付部',
 'WIN0039': '售后交付部',
 'WIN0040': '售后交付部',
 'WIN0041': '售后交付部',
 'WIN0074': '售后交付部',
 'WIN0077': '售后交付部',
 'WIN0030': '市场部',
 'WIN0031': '市场部',
 'WIN0033': '市场部',
 'WIN0049': '销售部',
 'WIN0054': '销售部',
 'WIN0057': '销售部',
 'WIN0079': '销售部',
 'WIN0095': '销售部',
 'WIN0096': '销售部',
 'WIN0044': '事业部',
 'WIN0051': '事业部',
 'WIN0055': '事业部',
 'WIN0056': '事业部',
 'WIN0058': '事业部',
 'WIN0060': '事业部',
 'WIN0032': '行政部',
 'WIN0062': '行政部',
 'WIN0064': '行政部',
 'WIN0065': '行政部',
 'WIN0066': '行政部',
 'WIN0067': '行政部',
 'WIN0068': '行政部',
 'WIN0021': '至安盾部',
 'WIN0063': '至安盾部',
 'WIN0078': '至安盾部',
 'WIN0080': '至安盾部',
 'WIN0081': '至安盾部',
 'WIN0082': '至安盾部',
 'WIN0086': '至安盾部',
 'WIN0090': '至安盾部',
 'WIN0091': '至安盾部',
 'WIN0092': '至安盾部',
 'WIN0093': '至安盾部',
 'WIN0094': '至安盾部',
 'WIN0043': '安全探针部',
 'WIN0048': '安全探针部',
 'WIN0050': '安全探针部',
 'WIN0053': '安全探针部',
 'WIN0105': '安全探针部',
 'WIN0107': '安全探针部',
 'WIN0108': '安全探针部',
 'WIN0110': '安全探针部',
 'WIN0111': '安全探针部',
 'WIN0112': '安全探针部',
 'WIN0009': '至察盾部',
 'WIN0011': '至察盾部',
 'WIN0070': '至察盾部',
 'WIN0073': '至察盾部',
 'WIN0083': '至察盾部',
 'WIN0085': '至察盾部',
 'WIN0087': '至察盾部',
 'WIN0088': '至察盾部',
 'WIN0089': '至察盾部',
 'WIN0097': '至察盾部',
 'WIN0098': '至察盾部',
 'WIN0099': '至察盾部',
 'WIN0101': '至察盾部',
 'WIN0102': '至察盾部',
 'WIN0103': '至察盾部',
 'WIN0109': '至察盾部',
 'WIN0113': '至察盾部',
 'WIN0115': '至察盾部',
 'WIN0002': '研发组',
 'WIN0005': '研发组',
 'WIN0006': '研发组',
 'WIN0007': '研发组',
 'WIN0008': '研发组',
 'WIN0010': '研发组',
 'WIN0012': '研发组',
 'WIN0069': '研发组',
 'WIN0071': '研发组',
 'WIN0072': '研发组',
 'WIN0004': 'QA组',
 'WIN0052': '技术支持部',
 'WIN0059': '技术支持部',
 'WIN0076': '技术支持部',
 'WIN0084': '技术支持部',
 'WIN0100': '技术支持部',
 'WIN0106': '技术支持部',
 'WIN0114': 'demo',
 'WIN0134': '日语操作系统',
 'LNX0020': '产品测试-test',
 'WIN0187': '产品测试-test',
 'WIN0104': 'hjn-演示专用',
 'LNX0022': '苏1',
 'WIN0185': 'cnwang_laptop'}
sensors = [
    _
    for _ in sensor_id_group_mapping
    if sensor_id_group_mapping[_] == "无分组"
]


def init_scheduler_infomation(sch, case_class):
    """
    :param sch:
    :param case_class:
    :return:
    """
    for uuid, report_info in case_class.report.items():
        page_info = case_class.report_detail[uuid]
        cron = report_info["send_date"]
        _report_params = {
            "report_name": report_info["report_name"],
            "data_scope": report_info["data_scope"],
            "sensor_ids": sensors,
            "sensor_id_group_mapping": sensor_id_group_mapping,
            "page_info": page_info,
            "send_mail": report_info["send_mail"],
        }

        trigger = CronTrigger.from_crontab(cron)

        gen_report(**_report_params)

        # sch.add_job(gen_report, trigger=trigger, kwargs=_report_params, id=uuid)


class Case:
    report = {
        "eb318a1caeb411e9b4740242edef7f35": {
            "report_name": "test",
            "report_format": "pdf",
            "timed": 1,
            "send_date": "0 * * * 1",
            "data_scope": "week",
            "sensor_group_ids": "",
            "send_mail": "",
            "update_time": "2019-07-26 11:05:33",
            "create_time": "2019-07-26 11:05:33"
        }
    }

    report_detail = {
        "eb318a1caeb411e9b4740242edef7f35": [
            {
                "custom_name": "host",
                "page_source_name": "主机运行日志",
                "page_source_url": "/host_log?"
                                   "tab=1&"
                                   "type=SENSOR_MULTIPLE_OS_BOOT,SENSOR_VM_INSTALLED,SENSOR_INFO_WORK_TIME,"
                                   "SENSOR_SOFTWARE_CHANGE,SENSOR_HARDWARE_CHANGE,SENSOR_SERVICECHANGE,"
                                   "SENSOR_SAFEMODE_BOOT",
                "sort_number": 0,
            },
            {
                "custom_name": "123",
                "page_source_name": "违规定义日志",
                "page_source_url": "/host_security_log?tab=1",
                "sort_number": 1,
            },
            {
                "custom_name": "111",
                "page_source_name": "违规详情日志",
                "page_source_url": "/host_security_log?tab=2",
                "sort_number": 2,
            },
            {
                "custom_name": "222",
                "page_source_name": "其他安全日志",
                "page_source_url": "/host_security_log?tab=3",
                "sort_number": 3,
            },
            {
                "custom_name": "访问管控策略日志",
                "page_source_name": "访问管控策略日志",
                "page_source_url": "/network_isolation_log?tab=1",
                "sort_number": 4,
            },
            {
                "custom_name": "流量管控策略日志",
                "page_source_name": "流量管控策略日志",
                "page_source_url": "/network_isolation_log?tab=2",
                "sort_number": 5,
            },
            {
                "custom_name": "平均流量统计",
                "page_source_name": "平均流量统计",
                "page_source_url": "/network_isolation_log?tab=3&type=1",
                "sort_number": 5,
            },
            {
                "custom_name": "平均流量统计",
                "page_source_name": "平均流量统计",
                "page_source_url": "/network_isolation_log?tab=3&type=2",
                "sort_number": 6,
            },
            {
                "custom_name": "端口开放管理日志",
                "page_source_name": "端口开放管理日志",
                "page_source_url": "/port_log?",
                "sort_number": 6,
            },
        ]
    }


if __name__ == "__main__":
    back_scheduler = BackgroundScheduler()
    # back_scheduler.start()

    init_scheduler_infomation(back_scheduler, Case)

    # tornado.options.parse_command_line()
    # http_server = tornado.httpserver.HTTPServer(
    #     ReportApp(back_scheduler),
    #     xheaders=True
    # )
    #
    # http_server.listen(options.port, address="127.0.0.1")
    # tornado.ioloop.IOLoop.instance().start()

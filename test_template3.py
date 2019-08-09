from utils import util
from pdflib import PDFTemplate
from datetime import timedelta
import os
import json
import traceback
import requests

typ_mapping = {
    "SENSOR_INFO_WORK_TIME": "开关机记录日志",
    "SENSOR_INFO_SYS_LOG": "探针系统日志",
    "SENSOR_USER": "用户信息日志",
    "SENSOR_FILESYSTEM": "文件访问日志",
    "SENSOR_REGISTRY": "注册表访问日志",
    "SENSOR_NETIO": "网络访问日志",
    "SENSOR_IO": "外设操作日志",
    "SENSOR_INPUT_ACTIVITY": "探针绩效日志",
    "SENSOR_OUTLOOK": "邮件审计日志",
    "SENSOR_PRINT": "打印审计日志",
    "SENSOR_CDBURN": "光盘刻录审计日志",
    "SENSOR_SERVICERUN": "服务项运行日志",
    "SENSOR_USER_INFO": "用户信息采集日志",
    "SENSOR_ACCOUNT_AUDIT": "系统账户监控与审计日志",
    "SENSOR_NET_SHARE": "网络共享日志",
    "SENSOR_RESOURCE_MONITOR": "系统资源监控日志",
    "SENSOR_SAFEMODE_BOOT": "安全模式登陆日志",
    "SENSOR_MULTIPLE_OS_BOOT": "多操作系统安装日志",
    "SENSOR_VM_INSTALLED": "虚拟机安装日志",
    "SENSOR_PORT_MONITOR": "开放端口监控日志",
    "SENSOR_AUTORUN": "自启动项变更日志",
    "SENSOR_CURRENT_AUTORUN": "当前自启动项日志",
    "SENSOR_CURRENT_SERVICE": "当前系统服务项日志",
    "SENSOR_ARP_SCAN": "ARP扫描日志",
    "SENSOR_PC_FRACTION": "PC得分日志",
    "SENSOR_RECEPTION_PROCESS": "前台进程活动日志",
    "SENSOR_SERVICECHANGE": "服务变更日志",
    "SENSOR_WORK_TIME": "工作时间日志",
    "SENSOR_HARDWARE_CHANGE": "硬件变更日志",
    "SENSOR_SOFTWARE_CHANGE": "软件变更日志",
    "SENSOR_PORT_CONNECT": "常用端口连接日志",
    "SENSOR_SERVICE_FULL_LOAD": "服务程序满负荷运行日志",
    "SENSOR_NET_CONNECTION": "网络访问违规日志",
    "SENSOR_RESOURCE_OVERLOAD": "资源使用超负荷日志",
    "SENSOR_ANTIVIRUS_OUTDATE": "杀毒软件未安装未更新日志",
    "SENSOR_ANTIVIRUS_STATUS": "杀毒软件状态日志",
    "SENSOR_SERVICE_STOP": "关键服务未启动日志",
    "SENSOR_REG_MODIFY": "注册表关键位置被修改日志",
    "SENSOR_TIME_ABNORMAL": "客户端时间异常日志",
    "SENSOR_FLOW_ABNORMAL": "进程流量异常日志",
    "SENSOR_HOTFIX_STATUS": "补丁更新状态日志",
    "SENSOR_NETWORK_ABNORMAL": "服务器/程序网络使用异常日志",
    "SENSOR_NETWORK_FLOW": "服务器/程序流量使用异常日志",
    "SENSOR_ALARM_MSG": "违规定义日志",
    "SENSOR_CURRENT_AUTORUN_DAILY": "主机服务运行日志",


}


GROUP_SENSORS_MAPPING = {
    "无分组": [
        "WIN0001",
        "WIN0002",
        "WIN0004",
        "WIN0005",
        "WIN0006",
        "WIN0008",
        "WIN0011",
        "WIN0012",
        "WIN0013",
        "WIN0014",
        "WIN0015",
        "WIN0016",
        "WIN0017",
        "WIN0018",
        "WIN0019",
        "WIN0020",
        "WIN0021",
        "WIN0022",
        "WIN0023",
        "WIN0024",
        "WIN0025",
        "WIN0026",
        "WSR0001",
    ],
    "cnwang_laptop": ["WIN0010"],
    "FAE": ["WIN0003"],
    "demo": ["WIN0009"],
    "hjn-demo": ["WIN0007"],
}


SENSOR_GROUP_MAPPING = {
                        "WIN0001": "无分组",
                        "WIN0002": "无分组",
                        "WIN0004": "无分组",
                        "WIN0005": "无分组",
                        "WIN0006": "无分组",
                        "WIN0008": "无分组",
                        "WIN0011": "无分组",
                        "WIN0012": "无分组",
                        "WIN0013": "无分组",
                        "WIN0014": "无分组",
                        "WIN0015": "无分组",
                        "WIN0016": "无分组",
                        "WIN0017": "无分组",
                        "WIN0018": "无分组",
                        "WIN0019": "无分组",
                        "WIN0020": "无分组",
                        "WIN0021": "无分组",
                        "WIN0022": "无分组",
                        "WIN0023": "无分组",
                        "WIN0024": "无分组",
                        "WIN0025": "无分组",
                        "WIN0026": "无分组",
                        "WSR0001": "无分组",
                        "WIN0010": "cnwang_laptop",
                        "WIN0003": "FAE",
                        "WIN0009": "demo",
                        "WIN0007": "hjn-demo"
                    }

class DrawSensorHostLogPDF(object):
    """
    1. 运行趋势与探针组无关，是LOG FORMAT 和 time 的对应关系
    """

    TITLE = "探针主机日志-运行趋势"
    url = "http://192.168.8.60:8002"

    def __init__(self, payload: dict):
        self.payload = payload
        # datetime type
        self.start_time = util.post_time_to_datetime(payload["start_time"])
        # datetime type
        self.end_time = util.post_time_to_datetime(payload["end_time"])
        self.days_interval = (self.end_time - self.start_time).days
        self.data_for_drawing = util.init_data_for_pdf_with_interval(self.days_interval)
        self.time_list = [
            (self.start_time + timedelta(hours=8, days=int(_))).\
            strftime("%Y%m%d")
            for _ in range(self.days_interval + 1)
        ]

    def parse_log(self, logs):
        for format_time_list, value, *_ in logs:
            log_format = format_time_list[0]["FORMAT.raw"]
            log_time = util.time_with_Z_to_datetime(format_time_list[1]["TIME"])
            value_index = (log_time - self.start_time).days + 1
            self.data_for_drawing[log_format][value_index] += value

        print(json.dumps(dict(self.data_for_drawing), indent=4))

    def draw(self, template_path):


        template = PDFTemplate.PDFTemplate.read_template(template_path)
        if not template:
            raise RuntimeError("读取模板文件失败！")

        try:
            items = template["items"]

            PDFTemplate.PDFTemplate.set_text_data(
                items["title"],
                self.TITLE
            )

            description = (
                f"{self.TITLE},"
                f"从{util.datetime_to_str(self.start_time)} 至 "
                f"{util.datetime_to_str(self.end_time)},"
                f"探针组: {list(GROUP_SENSORS_MAPPING.keys())}"
            )

            PDFTemplate.PDFTemplate.set_paragraph_data(
                items["description"],
                description
            )

            log_formats = []
            value_lists = []
            for key, value in self.data_for_drawing.items():
                print(f"value: {value}, type: {type(value)}")
                log_formats.append(key)
                value_lists.append(value)

            PDFTemplate.PDFTemplate.set_line_chart_data(
                items["line_chart"],
                value_lists,
                self.time_list,
                legend_names=log_formats
            )

            PDFTemplate.PDFTemplate.draw(template)

        except Exception as e:
            print(f"Error Occur: {e}")
            print(traceback.format_exc())

    def post_log_rule(self, url, data) -> tuple:

        response = requests.post(url, data=json.dumps(data))
        return response.status_code, json.loads(response.content)

    def run(self):
        status, content = self.post_log_rule(self.url, self.payload)
        print(f"status: {status},\n"
              f"content: {json.dumps(content, indent=4)}")

        self.parse_log(content["result"])
        tpl = os.path.join(os.getcwd(), "templates", "template3.xml")
        self.draw(tpl)


def main(start, end):
    data = {
        "start_time": start,
        "end_time": end,
        "page_name": "log_classify",
        "item_id": 0,
        "rule_id": "00",
        "search_index": "log*",
        "data_scope": {
            "FORMAT.raw": [
                "SENSOR_SAFEMODE_BOOT",
                "SENSOR_MULTIPLE_OS_BOOT",
                "SENSOR_VM_INSTALLED",
                "SENSOR_SERVICECHANGE",
                "SENSOR_HARDWARE_CHANGE"
            ],
            "SENSOR_ID.raw": [
                "WIN0001",
                "WIN0002",
                "WIN0004",
                "WIN0005",
                "WIN0006",
                "WIN0008",
                "WIN0011",
                "WIN0012",
                "WIN0013",
                "WIN0014",
                "WIN0015",
                "WIN0016",
                "WIN0017",
                "WIN0018",
                "WIN0019",
                "WIN0020",
                "WIN0021",
                "WIN0022",
                "WIN0023",
                "WIN0024",
                "WIN0025",
                "WIN0026",
                "WSR0001",
                "WIN0010",
                "WIN0003",
                "WIN0009",
                "WIN0007"
            ]
        }
    }
    draw_sensor_host_log = DrawSensorHostLogPDF(data)
    draw_sensor_host_log.run()


if __name__ == '__main__':

    main("2019-06-26T00:00:00.000",
         "2019-07-04T00:00:00.000")


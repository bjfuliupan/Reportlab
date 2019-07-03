from example import utils
from pdflib import PDFTemplate
import json
import datetime
import traceback


class DrawSensorHostLogPDF(object):
    """
    1. 运行趋势与探针组无关，是LOG FORMAT 和 time 的对应关系
    """

    TITLE = "探针主机日志-运行趋势"

    def __init__(self, payload: dict):
        self.payload = payload
        # datetime type
        self.start_time = utils.post_time_to_datetime(payload["start_time"])
        # datetime type
        self.end_time = utils.post_time_to_datetime(payload["end_time"])
        self.days_interval = (self.end_time - self.start_time).days
        self.data_for_drawing = utils.init_data_for_PDF(self.days_interval)
        self.time_list = [
            (self.start_time + datetime.timedelta(hours=8, days=int(_))).\
            strftime("%Y%m%d")
            for _ in range(self.days_interval + 1)
        ]

    def parse_log(self, logs):
        for format_time_list, value, *_ in logs:
            log_format = format_time_list[0]["FORMAT.raw"]
            log_time = utils.time_with_Z_to_datetime(format_time_list[1]["TIME"])
            value_index = (log_time - self.start_time).days + 1
            self.data_for_drawing[log_format][value_index] += value

        print(json.dumps(dict(self.data_for_drawing), indent=4))

    def draw(self):
        template = PDFTemplate.PDFTemplate.read_template("sensor_log_host.xml")
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
                f"从{utils.datetime_to_str(self.start_time)} 至 "
                f"{utils.datetime_to_str(self.end_time)},"
                f"探针组: {list(utils.GROUP_SENSORS_MAPPING.keys())}"
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

    def run(self):
        status, content = utils.post_log_rule(self.payload)
        print(f"status: {status},\n"
              f"content: {json.dumps(content, indent=4)}")

        self.parse_log(content["result"])
        self.draw()


if __name__ == "__main__":
    data = {
        "start_time": "2019-06-26T00:00:00.000",
        "end_time": "2019-07-04T00:00:00.000",
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
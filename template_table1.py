from utils import collect_line_data
from utils import collect_pie_data
from utils import collect_sensor_group_bar_data
from utils import collect_sensor_bar_data
import os
from pdflib.PDFTemplate import PDFTemplate


class TemplateTable():

    def __init__(self, payloads: dict, template_path: str,
                 sensor_id_group_mapping: dict):
        self.payloads = payloads
        self.template_path = template_path
        self.sensor_id_group_mapping = sensor_id_group_mapping
        self.log_formats_for_bar = payloads["log_formats"]
        self.template = None
        self.pages = None

    def init_template(self):
        self.template = PDFTemplate.read_template(self.template_path)
        assert self.template, \
            RuntimeError(f"读取模板失败！模板路径 ==> {self.template_path}")

        # 模板中的所有页
        self.pages = self.template["pages"]

        # # 设置标题显示内容
        # PDFTemplate.set_text_data(self.pages, 1, "title", "探针主机日志")

    def produce_line_chart(self):
        datas, legend_names, category_names = \
            collect_line_data.collect_line_data_for_draw(self.payloads["line_chart"])

        # 设置描述说明
        description = (
            f"探针主机日志报告，包含：运行趋势、运行日志分布展示、探针组Top10、探针Top10,"
            f"包含日志类型: {legend_names},"
            f"时间范围: {category_names[0]} 至 {category_names[-1]}"
        )
        PDFTemplate.set_paragraph_data(
            self.pages,
            1,
            "section_desc2",
            description
        )

        PDFTemplate.set_line_chart_data(
            self.pages,
            1,
            "section_operation_trend_line_chart",
            data=datas,
            category_names=category_names,
            legend_names=legend_names
        )

    def produce_pie_chart(self):
        datas, category_names = collect_pie_data.collect_pie_data_for_draw(self.payloads["pie_chart"])

        description = (
            f"运行日志分布展示图,"
            f"包含日志类型: {category_names}"
        )

        PDFTemplate.set_paragraph_data(
            self.pages,
            1,
            "section_heading1",
            description
        )

        PDFTemplate.set_pie_chart_data(
            self.pages,
            1,
            "section_log_distribution_pie_chart",
            data=datas,
            category_names=category_names
        )

    def produce_sensor_group_bar_chart(self):
        bar_chart_data_dict = collect_sensor_group_bar_data.collect_bar_data_for_draw(
            self.payloads["bar_chart"],
            self.log_formats_for_bar,
            self.sensor_id_group_mapping
        )

        for log_format, bar_chart_data in bar_chart_data_dict.items():
            category_names = bar_chart_data["category_names"]
            legend_names = bar_chart_data["legend_names"]

            PDFTemplate.set_bar_chart_data(
                self.pages,
                1,
                f"sensor_group_top_{log_format}",
                data=bar_chart_data["data"],
                category_names=category_names,
                legend_names=legend_names
            )

    def produce_sensor_bar_chart(self):
        bar_chart_data_dict = collect_sensor_bar_data.collect_bar_data_for_draw(
            self.payloads["bar_chart"],
            self.log_formats_for_bar,
            self.sensor_id_group_mapping,
        )

        for log_format, bar_chart_data in bar_chart_data_dict.items():
            print(log_format, "\n", bar_chart_data)
            category_names = bar_chart_data["category_names"]
            legend_names = bar_chart_data["legend_names"]

            PDFTemplate.set_bar_chart_data(
                self.pages,
                1,
                f"sensor_top_{log_format}",
                data=bar_chart_data["data"],
                category_names=category_names,
                legend_names=legend_names,
            )

    def produce_bar_chart(self):
        self.produce_sensor_group_bar_chart()
        self.produce_sensor_bar_chart()

    def main(self):
        self.init_template()
        self.produce_line_chart()
        self.produce_pie_chart()
        self.produce_bar_chart()

        PDFTemplate.draw(self.template)


def test_case():
    payload = {
        "line_chart": {
    "start_time": "2019-07-04T00:00:00.000",
    "end_time": "2019-07-12T00:00:00.000",
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
            "WIN0027",
            "WSR0001",
            "WIN0010",
            "WIN0003",
            "WIN0009",
            "WIN0007"
        ]
    }
},
        "pie_chart": {
            "start_time": "2019-07-05T00:00:00.000",
            "end_time": "2019-07-13T00:00:00.000",
            "page_name": "log_classify",
            "item_id": 1,
            "rule_id": "00",
            "search_index": "log*",
            "data_scope": {
                "FORMAT.raw": [
                    "SENSOR_SAFEMODE_BOOT",
                    "SENSOR_MULTIPLE_OS_BOOT",
                    "SENSOR_VM_INSTALLED",
                    "SENSOR_SERVICECHANGE",
                    "SENSOR_HARDWARE_CHANGE",
                    "SENSOR_SOFTWARE_CHANGE",
                    "SENSOR_INFO_WORK_TIME"
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
                    "WIN0027",
                    "WIN0028",
                    "WSR0001",
                    "WIN0010",
                    "WIN0003",
                    "WIN0009",
                    "WIN0007"
                ]
            }
        },
        "bar_chart": {
    "start_time": "2019-07-05T00:00:00.000",
    "end_time": "2019-07-13T00:00:00.000",
    "page_name": "log_classify",
    "item_id": 2,
    "rule_id": "00",
    "search_index": "log*",
    "data_scope": {
        "FORMAT.raw": [
            "SENSOR_SAFEMODE_BOOT"
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
            "WIN0027",
            "WIN0028",
            "WSR0001",
            "WIN0010",
            "WIN0003",
            "WIN0009",
            "WIN0007"
        ]
    }
},
        "log_formats": [
            "SENSOR_SERVICECHANGE",
            "SENSOR_HARDWARE_CHANGE",
            "SENSOR_MULTIPLE_OS_BOOT",
            "SENSOR_SAFEMODE_BOOT",
            "SENSOR_VM_INSTALLED",
            "SENSOR_SOFTWARE_CHANGE",
            "SENSOR_INFO_WORK_TIME"
        ]
    }
    sensor_id_group_mapping = {
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
                        "WIN0028": "无分组",
                        "WIN0010": "cnwang_laptop",
                        "WIN0003": "FAE",
                        "WIN0009": "demo",
                        "WIN0007": "hjn-demo",

                    }
    template_path = os.path.join(os.getcwd(), "templates", "template_charts.xml")
    tt = TemplateTable(payload, template_path, sensor_id_group_mapping)
    tt.main()


if __name__ == "__main__":
    test_case()
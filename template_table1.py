from utils import collect_line_data
import os
from pdflib.PDFTemplate import PDFTemplate


class TemplateTable():

    def __init__(self, payload: dict, template_path: str):
        self.payload = payload
        self.template_path = template_path
        self.pages = None

    def init_template(self):
        print(os.path.exists(self.template_path))
        self.template = PDFTemplate.read_template(self.template_path)
        assert self.template, \
            RuntimeError(f"读取模板失败！模板路径 ==> {self.template_path}")

        # 模板中的所有页
        self.pages = self.template["pages"]

        # # 设置标题显示内容
        # PDFTemplate.set_text_data(self.pages, 1, "title", "探针主机日志")

    def produce_line_chart(self):
        datas, legend_names, category_names = \
            collect_line_data.collect_line_data_for_draw(self.payload)

        # 设置描述说明
        description = (
            f"探针主机日志报告，包含：运行趋势、运行日志分布展示、探针组Top10、探针Top10,"
            f"包含日志类型: {legend_names},"
            f"时间范围: {legend_names[0]} 至 {legend_names[-1]}"
        )
        PDFTemplate.set_paragraph_data(
            self.pages,
            1,
            "section_desc2",
            description
        )


    # def get_line_chart_data(self):
    #     datas, legend_names, category_names = \
    #         collect_line_data.collect_line_data_for_draw(self.payload)

    def main(self):
        self.init_template()
        self.produce_line_chart()

        PDFTemplate.draw(self.template)


def test_case():
    payload = {
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
}
    template_path = os.path.join(os.getcwd(), "templates", "template_charts.xml")
    tt = TemplateTable(payload, template_path)
    tt.main()


if __name__ == "__main__":
    test_case()
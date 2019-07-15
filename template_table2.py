import os
import logging
import json
import requests
import collections
import copy

from datetime import timedelta
from utils import util
from utils import constant
from utils import collect_line_data
from utils import collect_pie_data
from utils import collect_sensor_group_bar_data
from utils import collect_sensor_bar_data

from pdflib.PDFTemplate import PDFTemplate


class DummyOb(object):
    """
    process original data class
    """

    ruleng_url = "http://192.168.8.60:8002"

    def __init__(self):
        # 探针& 探针组关系表
        self.sensor_group_map = {}

    def indicate_sen_group_map(self, sensor_group_map):
        """
        设置探针与探针组之间的关系表
        :param sensor_group_map:
        :return:
        """
        self.sensor_group_map = sensor_group_map

    def cook_line_data(self, payload:dict):
        """
        translate es return data to pdflib line chart data
        :param payload:
        :return:
        """

        begin_t = util.payload_time_to_datetime(payload["start_time"])
        end_t = util.payload_time_to_datetime(payload["end_time"])
        interval = (end_t - begin_t).days

        # 通过payload及时间参数，获取ES日志，并清洗
        # 返回折线图横坐标、纵坐标、折线标签数据
        data = json.dumps(payload)
        es_log_data = self.ruleng_url_post(data)

        chart_data = util.init_data_for_pdf_with_interval(interval)
        for key_list, value, *_ in es_log_data["result"]:
            log_format, log_time = None, None
            for key_dict in key_list:
                if key_dict.get("FORMAT.raw"):
                    log_format = key_dict["FORMAT.raw"]
                elif key_dict.get("TIME"):
                    log_time = key_dict["TIME"]
                else:
                    continue

            if not log_time:
                print("No TIME exist")
                continue

            log_time_datetime = util.adjust_es_log_time_to_datetime(log_time)
            value_index = (log_time_datetime - begin_t).days

            # 折线图 多条线， 每条线单独请求
            if log_format is None:
                log_format = "UNKNOW_FORMAT"

            chart_data[log_format][value_index] += value

        # 获取折线图横坐标数据
        category_names = [
            util.datetime_to_category_time(begin_t + timedelta(int(_)))
            for _ in range(interval + 1)
        ]

        # 获取折线标签
        legend_format_names = list(chart_data.keys())
        legend_names = [
            constant.LogConstant.FORMAT_DETAIL_MAPPING[_]
            for _ in legend_format_names
        ]

        # 获取折线图纵坐标数据
        datas = [
            chart_data[_]
            for _ in legend_format_names
        ]
        return datas, legend_names, category_names

    def cook_pie_data(self, payload:dict):
        # 通过payload及时间参数，获取ES日志，并清洗
        # 返回饼图日志类别、日志数量
        data = json.dumps(payload)
        es_log_data = self.ruleng_url_post(data)
        # util.pretty_print(es_log_data)

        # 统计数据
        pie_data = util.init_data_for_pdf_with_format()
        for format_dict, value, *_ in es_log_data["result"]:
            log_format = format_dict[0]["FORMAT.raw"]
            pie_data[log_format] += value

        # 获取饼图日志类型
        log_formats = list(pie_data.keys())
        category_names = [
            constant.LogConstant.FORMAT_DETAIL_MAPPING[_]
            for _ in log_formats
        ]

        # 获取饼图日志数量
        datas = [
            pie_data[_]
            for _ in log_formats
        ]
        return datas, category_names

    def cook_bar_data(self, payload:dict, sort=True, limit=10):
        """
        通过payload获取日志，进行清洗并返回
        :param payload: payload的FORMAT缺省，使用log_formats字段顺序填充
        :param sort: 是否排序，支持倒序
        :param limit: 最大展示数量
        :return:
        """
        ret = {}

        _fmt = payload["data_scope"]["FORMAT.raw"]
        formats = copy.deepcopy(_fmt)

        for log_format in formats:
            # 生成payload
            payload["data_scope"]["FORMAT.raw"] = [log_format]

            # 获取数据
            raw_data = json.dumps(payload)
            es_log_data = self.ruleng_url_post(raw_data)
            # 请求结果为空
            if not es_log_data["result"]:
                continue

            # 数据统计
            data_for_draw_with_sensor = util.init_data_for_pdf_with_format()
            for sensor_id_dict, value, *_ in es_log_data["result"]:
                sensor_id = sensor_id_dict[0]["SENSOR_ID.raw"]
                data_for_draw_with_sensor[sensor_id] += value

            if sort:
                data_for_draw_with_sensor_ordered = \
                    sorted(
                        data_for_draw_with_sensor.items(),
                        key=lambda sensor_value: sensor_value[1],
                        reverse=True
                    )
                data_for_draw_with_sensor = \
                    collections.OrderedDict(data_for_draw_with_sensor_ordered)

            # 获取柱状图横坐标（如探针）
            category_names = list(data_for_draw_with_sensor.keys())

            # 获取柱状图纵坐标
            data = [
                [data_for_draw_with_sensor[_]
                 for _ in category_names]
            ]

            # 获取柱状图日志类型
            legend_names = [
                constant.LogConstant.FORMAT_DETAIL_MAPPING[log_format]
            ]

            ret[log_format] = {
                "data": data,
                "category_names": category_names,
                "legend_names": legend_names,
            }
        return ret


    def cook_group_bar_data(self, payload:dict, sort=True, limit=10):
        """
        通过payload获取日志，进行清洗并返回
        :param payload: payload的FORMAT缺省，使用log_formats字段顺序填充
        :param sensor_id_group_mapping: 探针-探针组映射关系
        :param sort: 是否排序，支持倒序
        :param limit: 最大展示数量
        :return:
        """
        ret = {}

        _fmt = payload["data_scope"]["FORMAT.raw"]
        formats = copy.deepcopy(_fmt)

        for log_format in formats:
            # 生成payload
            payload["data_scope"]["FORMAT.raw"] = [log_format]
            # 获取数据
            raw_data = json.dumps(payload)
            es_log_data = self.ruleng_url_post(raw_data)
            # 请求结果为空
            if not es_log_data["result"]:
                continue
            # util.pretty_print(es_log_data)

            # 数据统计
            data_for_draw_with_group = util.init_data_for_pdf_with_format()
            for sensor_id_dict, value, *_ in es_log_data["result"]:
                sensor_id = sensor_id_dict[0]["SENSOR_ID.raw"]
                sensor_gorup = self.sensor_group_map[sensor_id]
                data_for_draw_with_group[sensor_gorup] += value

            if sort:
                data_for_draw_with_group_ordered = \
                    sorted(
                        data_for_draw_with_group.items(),
                        key=lambda group_value: group_value[1],
                        reverse=True
                    )
                data_for_draw_with_group = \
                    collections.OrderedDict(data_for_draw_with_group_ordered)

            # 获取柱状图横坐标（如探针组）
            category_names = list(data_for_draw_with_group.keys())

            # 获取柱状图纵坐标
            datas = [
                [data_for_draw_with_group[_] for _ in category_names]
            ]

            # 获取柱状图日志类型
            legend_names = [constant.LogConstant.FORMAT_DETAIL_MAPPING[log_format]]

            # print(groups, "\n", datas)
            ret[log_format] = {
                "data": datas,
                "category_names": category_names,
                "legend_names": legend_names
            }
        return ret

    def ruleng_url_post(self, data):
        ret = requests.post(self.ruleng_url, data=data)
        status_code = ret.status_code
        content = ret.content
        assert status_code == 200, \
            RuntimeError(f"request mrule: {payload} fail, errcode: {status_code}, reason: {content}")
        return json.loads(content)


class PDFReport(DummyOb):
    """
    generate report class.
    making pdf and translate data
    """

    def __init__(self, payloads: dict, template_path: str,
                 sensor_id_group_mapping: dict):

        super(PDFReport, self).__init__()
        if not os.path.exists(template_path):
            raise ValueError(f"reportlib template not found. {template_path}")

        self.report_tpl = PDFTemplate.read_template(template_path)
        self.report_tpl_pgs = self.report_tpl["pages"]
        self.report_tpl_pg_num = 0

        #
        self.indicate_sen_group_map(sensor_id_group_mapping)


        # self.payloads = payloads
        # self.template_path = template_path
        # self.sensor_id_group_mapping = sensor_id_group_mapping
        # self.log_formats_for_bar = payloads["log_formats"]

    def get_page_idx(self):
        return self.report_tpl_pg_num

    def set_page_idx(self, pg_num):
        self.report_tpl_pg_num = pg_num

    def set_title(self, content, page_idx=0, element_name="title"):
        """
        设置标题, must
        :return:
        """
        PDFTemplate.set_text_data(self.report_tpl_pgs, page_idx,
                                  element_name,
                                  content)

    def set_intro(self, content, page_idx=0, element_name="Introduction"):
        """
        设置文章内容描述
        :return:
        """
        PDFTemplate.set_text_data(self.report_tpl_pgs, page_idx,
                                  element_name,
                                  content)


    def making_data(self, begin_t, end_t,
                  fmts, sids, chart_typ,
                  page_name="log_classify", item_id=0, rule_id="00", search_index="log*"):
        """
        生成数据并进行翻译
        :param begin_t: 查询开始时间
        :param end_t: 查询结束时间
        :param fmts: array 查询功能列表
        :param sids: array 查询探针列表
        :param chart_typ: 需要生成图例类型 pie 饼图 line 线图 bar 柱图，看是否根据图例进行内容清洗
        :param page_name: rule engine param *
        :param item_id: rule engine param *
        :param rule_id: rule engine param *
        :param search_index: rule engine param *
        :return: cooked data
        """

        ret = None

        content = {
            "start_time": begin_t,
            "end_time": end_t,
            "page_name": page_name,
            "item_id": item_id,
            "rule_id": rule_id,
            "search_index": search_index,
            "data_scope": {
                "FORMAT.raw": fmts,
                "SENSOR_ID.raw": sids
            }
        }

        if chart_typ == "line":
            ret = self.cook_line_data(content)
        elif chart_typ == "bar":
            ret = self.cook_bar_data(content)
        elif chart_typ == "pie":
            ret = self.cook_pie_data(content)
        elif chart_typ == "group_bar":
            ret = self.cook_group_bar_data(content)
        else:
            raise ValueError("chart type error, not in ['line', 'bar', 'pie', 'group_bar']")

        return ret

    def report_draw_line(self, page_idx, elname, datas, legend_names,
                         category_names, has_description=False, description_elname=""):
        """
        自定义报告画线图
        :param page_idx: 当前操作页面的page index
        :param elname: 线图template对应element name
        :param datas: 图数据
        :param legend_names: 线图的legend names
        :param category_names: 线图的分类名称
        :param has_description: 该图是否有描述？
        :param description_elname: 描述对应template的element name
        :return:
        """

        if has_description:
            # 设置描述说明
            desc = (
                f"探针主机日志报告，包含：运行趋势、运行日志分布展示、探针组Top10、探针Top10,"
                f"包含日志类型: {legend_names},"
                f"时间范围: {cateogry_names[0]} 至 {category_names[-1]}"
            )
            PDFTemplate.set_paragraph_data(
                self.report_tpl_pgs,
                page_idx,
                description_elname,
                desc
            )

        PDFTemplate.set_line_chart_data(
            self.report_tpl_pgs,
            page_idx,
            elname,
            data=datas,
            category_names=category_names,
            legend_names=legend_names
        )

    def report_draw_pie(self, page_idx, elname, datas, category_names,
                        has_description=False, description_elname=""):
        """
        自定义报告饼图
        :param page_idx: 当前操作页面的page index
        :param elname: 图template对应element name
        :param datas: 图数据
        :param category_names: 图的分类名称
        :param has_description: 该图是否有描述
        :param description_elname: 描述对应template的element name
        :return:
        """

        if has_description:
            description = (
                f"运行日志分布展示图,"
                f"包含日志类型: {category_names}"
            )

            PDFTemplate.set_paragraph_data(
                self.report_tpl_pgs,
                page_idx,
                description_elname,
                description
            )

        PDFTemplate.set_pie_chart_data(
            self.report_tpl_pgs,
            page_idx,
            elname,
            data=datas,
            category_names=category_names
        )

    def report_draw_bar(self, page_idx, elname_prefix:str, bar_infos:dict,
                        has_description=False, description_elname=""):
        """

        :param page_idx: page number
        :param elname_prefix: 生成柱图会通过组批量产生，提供前缀
        :param bar_infos:
        :param has_description:
        :param description_elname:
        :return:
        """

        if has_description:
            description = (
                f"运行日志分布展示图,"
                f"包含日志类型: {category_names}"
            )

            PDFTemplate.set_paragraph_data(
                self.report_tpl_pgs,
                page_idx,
                description_elname,
                description
            )

        for log_format, bar_chart_data in bar_infos.items():
            category_names = bar_chart_data["category_names"]
            legend_names = bar_chart_data["legend_names"]

            PDFTemplate.set_bar_chart_data(
                self.report_tpl_pgs,
                page_idx,
                f"{elname_prefix}{log_format}",
                data=bar_chart_data["data"],
                category_names=category_names,
                legend_names=legend_names
            )


    def main(self):
        PDFTemplate.draw(self.report_tpl)


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
    tt = PDFReport(payload, template_path, sensor_id_group_mapping)
    tt.main()


if __name__ == "__main__":
    test_case()
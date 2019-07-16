import os
import logging
import json
import requests
import collections
import copy
import traceback

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
    sensor_group_map = {}

    def __init__(self):
        pass

    def indicate_sen_group_map(self, sensor_group_map):
        """
        设置探针与探针组之间的关系表
        :param sensor_group_map:
        :return:
        """
        self.sensor_group_map = sensor_group_map

    def cook_line_data(self, payload: dict):
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

        chart_datas = util.init_data_for_pdf_with_interval(interval)
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

            chart_datas[log_format][value_index] += value

        # 获取折线图横坐标数据
        category_names = [
            util.datetime_to_category_time(begin_t + timedelta(int(_)))
            for _ in range(interval + 1)
        ]

        # 获取折线标签
        legend_format_names = list(chart_datas.keys())
        legend_names = [
            constant.LogConstant.FORMAT_DETAIL_MAPPING[_]
            for _ in legend_format_names
        ]

        # 获取折线图纵坐标数据
        chart_data = [
            chart_datas[_]
            for _ in legend_format_names
        ]

        ret = {
            "datas": chart_data,
            "legend_names": legend_names,
            "category_names": category_names
        }

        return ret

    def cook_pie_data(self, payload: dict, page_name=None):
        # 通过payload及时间参数，获取ES日志，并清洗
        # 返回饼图日志类别、日志数量
        data = json.dumps(payload)
        es_log_data = self.ruleng_url_post(data)
        # util.pretty_print(es_log_data)

        # 统计数据
        pie_data = util.init_data_for_pdf_with_default_int()
        for format_dict, value, *_ in es_log_data["result"]:
            category_dict = format_dict[0]
            if "FORMAT.raw" in category_dict:
                category = format_dict[0]["FORMAT.raw"]
            elif "RULENAME.raw" in category_dict:
                category = format_dict[0]["RULENAME.raw"]
            else:
                continue
            pie_data[category] += value

        # 获取饼图日志类型
        log_formats = list(pie_data.keys())
        # 违规定义日志的类型为'规则名称'
        if page_name == "violation_define":
            category_names = list(pie_data.keys())
        else:
            category_names = [
                constant.LogConstant.FORMAT_DETAIL_MAPPING[_]
                for _ in log_formats
            ]

        # 获取饼图日志数量
        datas = [
            pie_data[_]
            for _ in log_formats
        ]

        ret = {
            "datas": datas,
            "category_names": category_names,
        }

        return ret

    def cook_bar_data(self, payload: dict, sort=True, limit=10, grouping=False):
        """
        通过payload获取日志，进行清洗并返回
        :param payload: payload的FORMAT缺省，使用log_formats字段顺序填充
        :param sort: 是否排序，支持倒序
        :param limit: 最大展示数量
        :param grouping: 是否分组
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
            # util.pretty_print(es_log_data)
            # 请求结果为空
            if not es_log_data["result"]:
                continue

            # 数据统计
            data_for_draw = util.init_data_for_pdf_with_default_int()
            for sensor_id_dict, value, *_ in es_log_data["result"]:
                sensor_id = sensor_id_dict[0]["SENSOR_ID.raw"]
                data_for_draw[sensor_id] += value

            if grouping:
                data_for_draw_tmp = util.init_data_for_pdf_with_default_int()
                for sensor_id, value in data_for_draw.items():
                    data_for_draw_tmp[self.sensor_group_map[sensor_id]] += value
                data_for_draw = data_for_draw_tmp

            if sort:
                data_for_draw_ordered = \
                    sorted(
                        data_for_draw.items(),
                        key=lambda key_value: key_value[1],
                        reverse=True
                    )
                data_for_draw = \
                    collections.OrderedDict(data_for_draw_ordered)

            # 获取柱状图横坐标（如探针）
            category_names = list(data_for_draw.keys())[:limit]

            # 获取柱状图纵坐标
            datas = [
                [data_for_draw[_]
                 for _ in category_names]
            ]

            # 获取柱状图日志类型
            legend_names = [
                constant.LogConstant.FORMAT_DETAIL_MAPPING[log_format]
            ]

            ret[log_format] = {
                "datas": datas,
                "category_names": category_names,
                "legend_names": legend_names,
            }
        return ret

    def cook_group_bar_data(self, payload: dict, sort=True, limit=10):
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
            data_for_draw_with_group = util.init_data_for_pdf_with_default_int()
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
            category_names = list(data_for_draw_with_group.keys())[:limit]

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
            RuntimeError(f"request mrule: {data} fail, errcode: {status_code}, reason: {content}")
        return json.loads(content)


template_path = os.path.join(os.getcwd(), "templates", "template_charts.xml")
assert os.path.exists(template_path) is True
report_template = PDFTemplate.read_template(template_path)


class PDFReport(DummyOb):
    """
    generate report class.
    making pdf and translate data
    """

    report_tpl = report_template

    def __init__(self):
        """
        init
        """

        super(PDFReport, self).__init__()

        self.report_tpl_pgs = self.report_tpl["pages"]
        self.report_tpl_pg_num = None

        # self.indicate_sen_group_map(sensor_id_group_mapping)

        # self.report_tpl = PDFTemplate.read_template(template_path)
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
        PDFTemplate.set_text_data(self.report_tpl_pgs,
                                  page_idx,
                                  element_name,
                                  content)

    def set_intro(self, content, page_idx=0, element_name="Introduction"):
        """
        设置文章内容描述
        :return:
        """
        PDFTemplate.set_text_data(self.report_tpl_pgs,
                                  page_idx,
                                  element_name,
                                  content)

    def making_data(self, begin_t: str, end_t: str, sids, chart_typ, fmts=None,
                    page_name="log_classify", item_id=0, rule_id="00", search_index="log*",
                    grouping=False):
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
        :param grouping: 是否按探针组对数据进行分组
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
                # 探针安全日志-违规定义日志分布展示 不需要此参数
                # "FORMAT.raw": fmts,
                "SENSOR_ID.raw": sids
            }
        }

        if fmts:
            content["data_scope"]["FORMAT.raw"] = fmts

        if chart_typ == "line":
            ret = self.cook_line_data(content)
        elif chart_typ == "bar":
            ret = self.cook_bar_data(content, grouping=grouping)
        elif chart_typ == "pie":
            ret = self.cook_pie_data(content, page_name=page_name)
        elif chart_typ == "group_bar":
            ret = self.cook_group_bar_data(content)
        else:
            raise ValueError("chart type error, not in ['line', 'bar', 'pie', 'group_bar']")

        return ret

    def report_draw_line(self, page_idx, elname,
                         datas, legend_names, category_names,
                         has_description=False, description_elname="",
                         description_intro=""):
        """
        自定义报告画线图
        :param page_idx: 当前操作页面的page index
        :param elname: 线图template对应element name
        :param datas: 图数据
        :param legend_names: 线图的legend names
        :param category_names: 线图的分类名称
        :param has_description: 该图是否有描述？
        :param description_elname: 描述对应template的element name
        :param description_intro: 图描述
        :return:
        """

        if has_description:
            # 设置描述说明
            PDFTemplate.set_paragraph_data(
                self.report_tpl_pgs,
                page_idx,
                description_elname,
                description_intro
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
                        has_description=False, description_elname="",
                        description_intro=""):
        """
        自定义报告饼图
        :param page_idx: 当前操作页面的page index
        :param elname: 图template对应element name
        :param datas: 图数据
        :param category_names: 图的分类名称
        :param has_description: 该图是否有描述
        :param description_elname: 描述对应template的element name
        :param description_intro: 图描述
        :return:
        """

        if has_description:
            PDFTemplate.set_paragraph_data(
                self.report_tpl_pgs,
                page_idx,
                description_elname,
                description_intro
            )

        PDFTemplate.set_pie_chart_data(
            self.report_tpl_pgs,
            page_idx,
            elname,
            data=datas,
            category_names=category_names
        )

    def report_draw_bar(self, page_idx, elname_prefix:str, bar_infos:dict,
                        has_description=False, description_elname="",
                        description_intro=""):
        """

        :param page_idx: page number
        :param elname_prefix: 生成柱图会通过组批量产生，提供前缀
        :param bar_infos:
        :param has_description:
        :param description_elname:
        :param description_intro: 图描述
        :return:
        """

        if has_description:

            PDFTemplate.set_paragraph_data(
                self.report_tpl_pgs,
                page_idx,
                description_elname,
                description_intro
            )

        for log_format, bar_chart_data in bar_infos.items():
            category_names = bar_chart_data["category_names"]
            legend_names = bar_chart_data["legend_names"]
            # 触发隔离违规定义TOP10 不需要后缀
            item_name = elname_prefix if log_format == "SENSOR_ALARM_MSG" \
                else f"{elname_prefix}{log_format}"

            PDFTemplate.set_bar_chart_data(
                self.report_tpl_pgs,
                page_idx,
                item_name,
                data=bar_chart_data["datas"],
                category_names=category_names,
                legend_names=legend_names
            )

    def draw(self):
        PDFTemplate.draw(self.report_tpl)


class ReportSenHost(PDFReport):
    """
    探针主机日志生成
    """
    # report_tpl_pg_num = 1
    all_fmts = [
        "SENSOR_SAFEMODE_BOOT",
        "SENSOR_MULTIPLE_OS_BOOT",
        "SENSOR_VM_INSTALLED",
        "SENSOR_SERVICECHANGE",
        "SENSOR_HARDWARE_CHANGE"
    ]

    def __init__(self):
        super(ReportSenHost, self).__init__()
        self.set_page_idx(1)

    def draw_page(self, begin_t, end_t, sensors, sensor_id_group_mapping, **kwargs):
        """
        :param begin_t: 日志起始时间
        :param end_t:  日志截止时间
        :param sensors: 目标探针
        :param sensor_id_group_mapping: 探针与探针组映射关系
        :param kwargs: 其他参数，如日志类型（fmts）
        :return:
        """
        self.indicate_sen_group_map(sensor_id_group_mapping)
        fmts = kwargs["fmts"]

        # 折线图
        line_ret = self.making_data(begin_t, end_t, sensors, chart_typ="line", fmts=fmts)
        desc = (
            f"探针主机日志报告，包含：运行趋势、运行日志分布展示、探针组Top10、探针Top10,"
            f"包含日志类型: {line_ret['legend_names']},"
            f"时间范围: {line_ret['category_names'][0]} 至 {line_ret['category_names'][-1]}"
        )
        self.report_draw_line(self.report_tpl_pg_num,
                              "section_operation_trend_line_chart",
                              line_ret['datas'], line_ret['legend_names'], line_ret['category_names'],
                              True,
                              "section_desc2",
                              desc)

        # 饼图
        pie_ret = self.making_data(begin_t, end_t, sensors, chart_typ="pie", fmts=self.all_fmts, item_id=1)
        self.report_draw_pie(self.report_tpl_pg_num,
                             "section_log_distribution_pie_chart",
                             pie_ret["datas"], pie_ret["category_names"]
                             )

        # 柱状图（探针）
        sensor_bar_ret = self.making_data(begin_t, end_t, sensors, chart_typ="bar", fmts=fmts, item_id=2)
        self.report_draw_bar(
            self.report_tpl_pg_num,
            "sensor_top_",
            sensor_bar_ret
        )

        # 柱状图（探针组）
        sensor_group_bar_ret = self.making_data(begin_t, end_t, sensors, chart_typ="bar", fmts=fmts, item_id=2,
                                                grouping=True)
        self.report_draw_bar(
            self.report_tpl_pg_num,
            "sensor_group_top_",
            sensor_group_bar_ret
        )


class ReportSenSafe(PDFReport):
    """
    探针安全日志
    """
    # report_tpl_pg_num = 2
    ALL_HOST_SAFE_FMTS = [
        "SENSOR_ALARM_MSG"
    ]
    ALL_VIOLATION_DETAIL_FMTS = [
        "SENSOR_SAFEMODE_BOOT",
        "SENSOR_MULTIPLE_OS_BOOT",
        "SENSOR_VM_INSTALLED",
        "SENSOR_SERVICECHANGE",
        "SENSOR_HARDWARE_CHANGE"
    ]
    ALL_VIOLATION_OTHER_FMTS = [
        "SENSOR_AUTORUN",
        "SENSOR_NET_SHARE"
    ]

    def __init__(self):
        super(ReportSenSafe, self).__init__()
        self.set_page_idx(2)

    def draw_page(self, begin_t, end_t, sensors, sensor_id_group_mapping, **kwargs):
        """
        :param begin_t: 日志起始时间
        :param end_t:  日志截止时间
        :param sensors: 目标探针
        :param sensor_id_group_mapping: 探针与探针组映射关系
        :param kwargs: 其他参数，如日志类型（fmts）
        :return:
        """
        self.indicate_sen_group_map(sensor_id_group_mapping)

        violation_detail_fmts = kwargs["violation_detail_fmts"]
        violation_other_fmts = kwargs["violation_other_fmts"]

        # 违规定义日志
        self.draw_violation_triggered(begin_t, end_t, sensors)
        # 违规详情日志
        self.draw_violation_detail(begin_t, end_t, sensors, violation_detail_fmts)
        # 其他安全日志
        self.draw_violation_other(begin_t, end_t, sensors, violation_other_fmts)

    def draw_violation_triggered(self, begin_t, end_t, sensors):
        # 违规定义日志-折线图
        line_ret = self.making_data(begin_t, end_t, sensors, chart_typ="line", fmts=self.ALL_HOST_SAFE_FMTS)
        self.report_draw_line(self.report_tpl_pg_num,
                              "violation_triggered_trend_line_chart",
                              line_ret['datas'],
                              line_ret['legend_names'],
                              line_ret['category_names'])

        # 违规定义日志-饼图
        pie_ret = self.making_data(begin_t, end_t, sensors, chart_typ="pie", item_id=2, page_name="violation_define")
        self.report_draw_pie(self.report_tpl_pg_num,
                             "violation_triggered_distrbution",
                             pie_ret["datas"],
                             pie_ret["category_names"]
                             )

        # 违规定义日志-柱图（探针）
        bar_ret = self.making_data(begin_t, end_t, sensors, chart_typ="bar",
                                   fmts=self.ALL_HOST_SAFE_FMTS, item_id=3,
                                   page_name="violation_define")
        self.report_draw_bar(
            self.report_tpl_pg_num,
            "violation_triggered_sensor_top",
            bar_ret
        )

        # 违规定义日志-柱图（探针组）
        bar_ret = self.making_data(begin_t, end_t, sensors, chart_typ="bar",
                                   fmts=[self.ALL_HOST_SAFE_FMTS], item_id=3,
                                   page_name="violation_define", grouping=True)
        self.report_draw_bar(
            self.report_tpl_pg_num,
            "violation_triggered_sensor_group_top",
            bar_ret
        )

    def draw_violation_detail(self, begin_t, end_t, sensors, violation_detail_fmts):
        # 违规详情日志运行趋势
        line_ret = self.making_data(begin_t, end_t, sensors, chart_typ="line",
                                    fmts=violation_detail_fmts, item_id=0,
                                    page_name="log_classify")
        self.report_draw_line(self.report_tpl_pg_num,
                              "violation_detail_trend_line_chart",
                              line_ret['datas'],
                              line_ret['legend_names'],
                              line_ret['category_names'])

        # 违规详情日志分布展示
        pie_ret = self.making_data(begin_t, end_t, sensors, chart_typ="pie",
                                   fmts=self.ALL_VIOLATION_DETAIL_FMTS,
                                   item_id=1, page_name="log_classify")
        self.report_draw_pie(self.report_tpl_pg_num,
                             "violation_detail_distrbution",
                             pie_ret["datas"],
                             pie_ret["category_names"]
                             )

        # 违规详情-探针组Top10
        sensor_group_bar_ret = self.making_data(begin_t, end_t, sensors, chart_typ="bar", fmts=violation_detail_fmts,
                                                item_id=2,grouping=True)
        self.report_draw_bar(
            self.report_tpl_pg_num,
            "violation_detail_distrbution_sensor_group_top_",
            sensor_group_bar_ret
        )

        # 违规详情-探针Top10
        sensor_group_bar_ret = self.making_data(begin_t, end_t, sensors, chart_typ="bar", fmts=violation_detail_fmts,
                                                item_id=2)
        self.report_draw_bar(
            self.report_tpl_pg_num,
            "violation_detail_distrbution_sensor_top_",
            sensor_group_bar_ret
        )

    def draw_violation_other(self, begin_t, end_t, sensors, violation_other_fmts):
        # 其他安全日志分析图-主机安全趋势
        line_ret = self.making_data(begin_t, end_t, sensors, chart_typ="line",
                                    fmts=violation_other_fmts, item_id=0,
                                    page_name="log_classify")
        self.report_draw_line(self.report_tpl_pg_num,
                              "violation_others_trend_line_chart",
                              line_ret['datas'],
                              line_ret['legend_names'],
                              line_ret['category_names'])

        # 其他安全日志分析图-分布展示
        pie_ret = self.making_data(begin_t, end_t, sensors, chart_typ="pie",
                                   fmts=self.ALL_VIOLATION_OTHER_FMTS,
                                   item_id=1, page_name="log_classify")
        self.report_draw_pie(self.report_tpl_pg_num,
                             "violation_others_distrbution",
                             pie_ret["datas"],
                             pie_ret["category_names"]
                             )

        # 其他安全日志-探针组Top10
        sensor_group_bar_ret = self.making_data(begin_t, end_t, sensors, chart_typ="bar", fmts=violation_other_fmts,
                                                item_id=2, grouping=True)
        self.report_draw_bar(
            self.report_tpl_pg_num,
            "violation_others_sensor_group_top_",
            sensor_group_bar_ret
        )

        # 其他安全日志-探针Top10
        sensor_bar_ret = self.making_data(begin_t, end_t, sensors, chart_typ="bar", fmts=violation_other_fmts,
                                                item_id=2)
        self.report_draw_bar(
            self.report_tpl_pg_num,
            "violation_others_sensor_top_",
            sensor_bar_ret
        )


def test_case():
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
        "WIN0027": "无分组",

    }
    sensors = [
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

    report_page_class_mapping = {
        "log_search": ReportSenHost,
        "violation_define": ReportSenSafe
    }

    case = {
        "begin_t": "2019-06-01T00:00:00.000",
        "end_t": "2019-07-17T00:00:00.000",
        "sensor_id_group_mapping": sensor_id_group_mapping,
        "report_pages": [
                {
                    "page_name": "log_search",
                    "kwargs":{
                        "fmts": [
                            "SENSOR_SAFEMODE_BOOT",
                            "SENSOR_MULTIPLE_OS_BOOT",
                            "SENSOR_VM_INSTALLED",
                            "SENSOR_SERVICECHANGE",
                            "SENSOR_HARDWARE_CHANGE"
                        ]
                    }
                },
                {
                    "page_name": "violation_define",
                    "kwargs": {
                        "violation_detail_fmts": [
                            "SENSOR_IO",
                            "SENSOR_RESOURCE_OVERLOAD",
                            "SENSOR_SERVICE_FULL_LOAD",
                            "SENSOR_TIME_ABNORMAL"
                        ],
                        "violation_other_fmts": [
                            "SENSOR_AUTORUN",
                            "SENSOR_NET_SHARE"
                        ]
                    }
                }
        ]
    }

    begin_t = case["begin_t"]
    end_t = case["end_t"]
    sensor_id_group_mapping = case["sensor_id_group_mapping"]

    for report_page in case["report_pages"]:
        try:
            prt = report_page_class_mapping[report_page["page_name"]]()
            prt.draw_page(begin_t, end_t, sensors, sensor_id_group_mapping, **report_page["kwargs"])
        except Exception as e:
            print(f"errmsg: {e}")
            print(traceback.format_exc())

    PDFReport().draw()


if __name__ == "__main__":

    test_case()

    # begin_time = "2019-07-04T00:00:00.000"
    # end_time = "2019-07-12T00:00:00.000"
    # sensor_id_group_map = {
    #     "WIN0001": "无分组",
    #     "WIN0002": "无分组",
    #     "WIN0004": "无分组",
    #     "WIN0005": "无分组",
    #     "WIN0006": "无分组",
    #     "WIN0008": "无分组",
    #     "WIN0011": "无分组",
    #     "WIN0012": "无分组",
    #     "WIN0013": "无分组",
    #     "WIN0014": "无分组",
    #     "WIN0015": "无分组",
    #     "WIN0016": "无分组",
    #     "WIN0017": "无分组",
    #     "WIN0018": "无分组",
    #     "WIN0019": "无分组",
    #     "WIN0020": "无分组",
    #     "WIN0021": "无分组",
    #     "WIN0022": "无分组",
    #     "WIN0023": "无分组",
    #     "WIN0024": "无分组",
    #     "WIN0025": "无分组",
    #     "WIN0026": "无分组",
    #     "WSR0001": "无分组",
    #     "WIN0028": "无分组",
    #     "WIN0010": "cnwang_laptop",
    #     "WIN0003": "FAE",
    #     "WIN0009": "demo",
    #     "WIN0007": "hjn-demo",
    #
    # }
    #
    # report_page_class_mapping = {
    #     "log_search": ReportSenHost,
    #     "violation_define": ReportSenSafe
    # }
    #
    # test_case = {
    #     "begin_t": "2019-07-04T00:00:00.000",
    #     "end_t": "2019-07-12T00:00:00.000",
    #     "sensor_id_group_map": sensor_id_group_map
    #     "report_pages": [
    #         "log_search",
    #         "violation_define",
    #     ]
    # }
    #
    #
    #
    # prt = ReportSenHost(begin_time, end_time, sensor_id_group_map)
    # prt.draw_page()
    #
    # prt1 = ReportSenSafe(begin_time, end_time, sensor_id_group_map)
    # prt1.draw_page()
    #
    # # final
    # PDFReport().draw()
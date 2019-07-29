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

    ruleng_url = "http://192.168.11.200:8002"
    # sensor_group_map = {}
    # begin_t = None
    # end_t = None
    # sensors = []

    def __init__(self):
        self.sensor_group_map = {}
        self.begin_t = None
        self.end_t = None
        self.sensors = []

    def indicate_parameters(self, **kwargs):
        if kwargs.get("sensor_id_group_map"):
            self.sensor_group_map = kwargs["sensor_id_group_map"]

        if kwargs.get("begin_t"):
            self.begin_t = kwargs["begin_t"]

        if kwargs.get("end_t"):
            self.end_t = kwargs["end_t"]

        if kwargs.get("sensors"):
            self.sensors = kwargs["sensors"]

    # def indicate_sen_group_map(self, sensor_group_map: dict):
    #     """
    #     设置探针与探针组之间的关系表
    #     :param sensor_group_map:
    #     :return:
    #     """
    #     self.sensor_group_map = sensor_group_map

    def indicate_date_scope(self, begin_t: str, end_t: str):
        self.begin_t = begin_t
        self.end_t = end_t

    def indicate_sensors(self, sensors: list):
        self.sensors = sensors

    def indicate_groups(self, group: dict):
        self.sensor_group_map = group

    def init_group_data(self) -> collections.defaultdict:
        # 初始化图数据，默认value为 int， default 0
        _default = {}
        for k, v in self.sensor_group_map.items():
            _default[v] = 0

        return _default

    def cook_line_data(self, payload: dict, grouping=False):
        """
        translate es return data to pdflib line chart data
        :param payload:
        :return:
        """
        begin_t = util.payload_time_to_datetime(payload["start_time"])
        end_t = util.payload_time_to_datetime(payload["end_time"])
        interval = (end_t - begin_t).days

        payload_log_format = payload["data_scope"].get("FORMAT.raw")

        if payload["page_name"] == "file_operate":
            payload_log_format = payload["data_scope"].get("ACCESS_FORMAT.raw")

        if payload_log_format is None:
            payload_log_format = [""]

        # 通过payload及时间参数，获取ES日志，并清洗
        # 返回折线图横坐标、纵坐标、折线标签数据
        data = json.dumps(payload)
        es_log_data = self.ruleng_url_post(data)

        chart_datas = util.init_data_for_pdf_with_interval(interval)
        for key_list, value, *_ in es_log_data["result"]:
            log_format, log_time, sensor_id = None, None, None
            for key_dict in key_list:
                if key_dict.get("FORMAT.raw"):
                    log_format = key_dict["FORMAT.raw"]
                elif key_dict.get("ACCESS_FORMAT.raw"):
                    log_format = key_dict["ACCESS_FORMAT.raw"]

                elif key_dict.get("TIME"):
                    log_time = key_dict["TIME"]
                elif key_dict.get("DAY_TIME"):
                    log_time = key_dict["DAY_TIME"]

                elif key_dict.get("SENSOR_ID.raw"):
                    sensor_id = key_dict["SENSOR_ID.raw"]
                else:
                    continue

            if not log_time:
                print("No TIME exist")
                continue

            log_time_datetime = util.adjust_es_log_time_to_datetime(log_time)
            value_index = (log_time_datetime - begin_t).days

            # 违规定义日志折线图 多条线， 每条线单独请求
            if log_format is None:
                log_format = "UNKNOW_FORMAT"
            if sensor_id:
                chart_datas[sensor_id][value_index] += int(value)
            else:
                chart_datas[log_format][value_index] += int(value)

        # 获取折线图横坐标数据
        category_names = [
            util.datetime_to_category_time(begin_t + timedelta(int(_)))
            for _ in range(interval + 1)
        ]

        # 获取折线标签
        if grouping:
            chart_datas_tmp = util.init_data_for_pdf_with_interval(interval)
            for key, value_list in chart_datas.items():
                for index in range(len(value_list)):
                    chart_datas_tmp[self.sensor_group_map[key]][index] += value_list[index]
            chart_datas = chart_datas_tmp

            legend_names = list(chart_datas.keys())
        else:
            legend_names = payload_log_format if payload_log_format == ["SENSOR_ALARM_MSG"] \
                else [constant.LogConstant.FORMAT_DETAIL_MAPPING[_] for _ in payload_log_format]

        # 获取折线图纵坐标数据
        if grouping:
            chart_data = [
                chart_datas[_]
                for _ in legend_names
            ]
        else:
            chart_data = [
                chart_datas[_]
                for _ in payload_log_format
            ]

        ret = {
            "datas": chart_data,
            "legend_names": legend_names,
            "category_names": category_names
        }

        return ret

    def cook_pie_data(self, payload: dict):
        """通过payload及时间参数，获取ES日志，并清洗,返回饼图日志类别、日志数量
        :param payload:
        :return:
        """
        payload_log_format = payload["data_scope"]["FORMAT.raw"]

        data = json.dumps(payload)
        es_log_data = self.ruleng_url_post(data)

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
        category_names = payload_log_format if payload_log_format == ["SENSOR_ALARM_MSG"] \
            else [constant.LogConstant.FORMAT_DETAIL_MAPPING[_] for _ in payload_log_format]

        # 获取饼图日志数量
        datas = [
            pie_data[_]
            for _ in payload_log_format
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

        data_access = "FORMAT.raw"
        if payload["page_name"] == "file_operate":
            data_access = "ACCESS_FORMAT.raw"

        _fmt = payload["data_scope"][data_access]

        formats = copy.deepcopy(_fmt)

        for log_format in formats:
            # 生成payload
            # if log_format == "SENSOR_NETWORK_ABNORMAL":
            #     del payload["data_scope"]["FORMAT.raw"]
            # else:
            payload["data_scope"][data_access] = [log_format]

            # 获取数据
            raw_data = json.dumps(payload)
            es_log_data = self.ruleng_url_post(raw_data)
            # 请求结果为空
            if not es_log_data["result"]:
                continue

            # 数据统计
            data_for_draw = util.init_data_for_pdf_with_default_int()
            for key_dict, value, *_ in es_log_data["result"]:
                if key_dict[0].get("SENSOR_ID.raw"):
                    key = key_dict[0]["SENSOR_ID.raw"]
                elif key_dict[0].get("TARGET_NAME.raw"):
                    key = key_dict[0]["TARGET_NAME.raw"]
                elif key_dict[0].get("RULENAME.raw"):
                    key = key_dict[0]["RULENAME.raw"]
                else:
                    continue
                data_for_draw[key] += int(value)

            if grouping:
                # data_for_draw_tmp = util.init_data_for_pdf_with_default_int()
                data_for_draw_tmp = self.init_group_data()
                for sensor_id, value in data_for_draw.items():
                    _id = self.sensor_group_map[sensor_id]
                    data_for_draw_tmp[_id] += value
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

    def making_data(self, chart_typ: str, fmts=None, resolved=None, access_fmts=None,
                    page_name="log_classify", item_id=0, rule_id="00", search_index="log*",
                    grouping=False, opt1=None, **kwargs):
        """
        生成数据并进行翻译
        # :param begin_t: 查询开始时间
        # :param end_t: 查询结束时间
        # :param fmts: array 查询功能列表
        # :param sids: array 查询探针列表
        :param chart_typ: 需要生成图例类型 pie 饼图 line 线图 bar 柱图，看是否根据图例进行内容清洗
        :param page_name: rule engine param *
        :param resolved: 日志报警是否已解决，用于'违规定义日志'
        :param item_id: rule engine param *
        :param rule_id: rule engine param *
        :param search_index: rule engine param *
        :param grouping: 是否按探针组对数据进行分组
        :param opt1: 主机网络管控payload关键字
        :return: cooked data
        """

        ret = None

        content = {
            "start_time": self.begin_t,
            "end_time": self.end_t,
            "page_name": page_name,
            "item_id": item_id,
            "rule_id": rule_id,
            "search_index": search_index,
            "data_scope": {
                # 探针安全日志-违规定义日志分布展示 不需要此参数
                # "FORMAT.raw": fmts,
                "SENSOR_ID.raw": self.sensors
            }
        }

        if fmts:
            content["data_scope"]["FORMAT.raw"] = fmts
        if resolved:
            content["data_scope"]["RESOLVED"] = resolved
        if access_fmts:
            content["data_scope"]["ACCESS_FORMAT.raw"] = access_fmts

        if opt1:
            content["opt1"] = opt1

        if chart_typ == "line":
            ret = self.cook_line_data(content, grouping=grouping)
        elif chart_typ == "bar":
            ret = self.cook_bar_data(content, grouping=grouping)
        elif chart_typ == "pie":
            ret = self.cook_pie_data(content)
        # 合入 cook_bar_data
        # elif chart_typ == "group_bar":
        #     ret = self.cook_group_bar_data(content)
        else:
            raise ValueError("chart type error, not in ['line', 'bar', 'pie']")

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

    def report_draw_bar(self, page_idx, elname_prefix:str, bar_infos:dict, elname=None,
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
            item_name = elname_prefix \
                if log_format in ["SENSOR_ALARM_MSG",
                                  "SENSOR_NETWORK_ABNORMAL",
                                  "SENSOR_NETWORK_FLOW"] \
                else f"{elname_prefix}{log_format}"

            PDFTemplate.set_bar_chart_data(
                self.report_tpl_pgs,
                page_idx,
                item_name,
                data=bar_chart_data["datas"],
                category_names=category_names,
                legend_names=legend_names
            )

    def report_draw_bar1(self, page_idx, elname_prefix=None, bar_infos=None, elname=None,
                        has_description=False, description_elname="",
                        description_intro="", group_bar=False):
        """
        draw group bar

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
        # barinfo不同类，可能存在category datas不相同的状况
        # 算出category_names的并集

        max_c = set()
        for _, value in bar_infos.items():
            _ax = value["category_names"]
            max_c = max_c.union(set(_ax))


        # 准备工作完成，开始数据补全
        for key, value in bar_infos.items():
            _max_c = list(max_c)
            for i in range(len(_max_c)):
                _ik = _max_c[i]
                if _ik not in value["category_names"]:
                    value["category_names"].append(_ik)
                    value["datas"][0].append(0)


        # max_k = "" # 数据最多的key
        # max_c = [] # 数据最多的category
        # max_v = [] # 数据最多的value
        # max_l = 0
        # p_same = True
        # for key, value in bar_infos.items():
        #     if max_l == 0:
        #         max_l = len(value["category_names"])
        #         max_k = key
        #     elif max_l < len(value["category_names"]):
        #         max_l = len(value["category_names"])
        #         max_k = key
        #
        #     if max_l != len(value["category_names"]):
        #         p_same = False
        #
        # # 此处表示barinfo中有数据格式不对齐
        # # 处理数据时需要使用最大的category对齐数据，没有的补0
        # if not p_same:
        #     print(f"{p_same}:{max_k}: {bar_infos[max_k]}")
        #
        # # 如果最大category为0，这个返回结果无法使用直接返回
        # if max_l == 0:
        #     return
        #
        # max_c = bar_infos[max_k]["category_names"]
        # max_v = bar_infos[max_k]["datas"][0]
        #
        # # 准备工作完成，开始数据补全
        # for key, value in bar_infos.items():
        #     if key == max_k:
        #         continue
        #
        #     if max_k != value["category_names"]:
        #         for i in range(len(max_c)):
        #             _ik, _iv = max_c[i], max_v[i]
        #             if _ik not in value["category_names"]:
        #                 value["category_names"].append(_ik)
        #                 value["datas"][0].append(0)


        if not group_bar:
            for log_format, bar_chart_data in bar_infos.items():
                category_names = bar_chart_data["category_names"]
                legend_names = bar_chart_data["legend_names"]

                if elname_prefix is not None:
                    # 触发隔离违规定义TOP10 不需要后缀
                    item_name = elname_prefix \
                        if log_format in ["SENSOR_ALARM_MSG",
                                          "SENSOR_NETWORK_ABNORMAL",
                                          "SENSOR_NETWORK_FLOW"] \
                        else f"{elname_prefix}{log_format}"
                elif elname is not None:
                    item_name = elname
                else:
                    raise ValueError("template element name prefix or name must be set.")

                PDFTemplate.set_bar_chart_data(
                    self.report_tpl_pgs,
                    page_idx,
                    item_name,
                    data=bar_chart_data["datas"],
                    category_names=category_names,
                    legend_names=legend_names
                )
        else:
            # 设置多bar的柱图
            datas = []
            category_names = []

            legend_names = []

            if elname_prefix:
                """不支持前缀element name"""
                raise NotImplemented

            for log_format, bar_chart_data in bar_infos.items():
                c = bar_chart_data["category_names"]
                l = bar_chart_data["legend_names"]


                _catelog = dict(zip(c, bar_chart_data["datas"][0]))
                _category = sorted(_catelog)
                _temp_arr = []

                for i in _category:
                    _temp_arr.append(_catelog[i])

                # fill data
                # tp = tuple(bar_chart_data["datas"][0])
                datas.append(tuple(_temp_arr))

                # legend names
                legend_names.extend(l)

                # category
                category_names = _category


            PDFTemplate.set_bar_chart_data(
                self.report_tpl_pgs,
                page_idx,
                elname,
                data=datas,
                category_names=category_names,
                legend_names=legend_names
            )


    def draw(self):
        PDFTemplate.draw(self.report_tpl)


class ReportSenHost(PDFReport):
    """
    探针主机日志生成
    """
    PG_NUM = 1
    ALL_FMTS = [
        "SENSOR_SAFEMODE_BOOT",
        "SENSOR_MULTIPLE_OS_BOOT",
        "SENSOR_VM_INSTALLED",
        "SENSOR_SERVICECHANGE",
        "SENSOR_HARDWARE_CHANGE"
    ]

    def __init__(self):
        super(ReportSenHost, self).__init__()
        self.set_page_idx(self.PG_NUM)
        self.items = {}

    def add_items(self, items, **kwargs):
        self.indicate_parameters(**kwargs)

        self.items["pages"] = [
            {
                "page_name": "log_classify",
                "rule_id": "00",
                "search_index": "log*",
                "fmts": items["kwargs"]["fmts"],
                "all_fmts": self.ALL_FMTS,
                "item_id": {
                    "line": 0,
                    "pie": 1,
                    "bar": 2
                },
                "elname": {
                    "line": "section_operation_trend_line_chart",
                    "pie": "section_log_distribution_pie_chart",
                    "bar": "sensor_top_",
                    "bar_group": "sensor_group_top_"
                },
                "description_elname": {
                    "line": "section_desc2"
                }
            },
        ]

    def draw_page(self):
        """
        """
        for page in self.items["pages"]:
            # 折线图
            line_ret = self.making_data(chart_typ="line", fmts=page["fmts"],
                                        page_name=page["page_name"],
                                        item_id=page["item_id"]["line"])
            desc = (
                f"探针主机网络管控报告报告，包含：运行趋势、运行日志分布展示、探针组Top10、探针Top10,"
                f"包含日志类型: {line_ret['legend_names']},"
                f"时间范围: {line_ret['category_names'][0]} 至 {line_ret['category_names'][-1]}"
            )
            self.report_draw_line(self.report_tpl_pg_num,
                                  page["elname"]["line"],
                                  line_ret['datas'],
                                  line_ret['legend_names'],
                                  line_ret['category_names'],
                                  has_description=True,
                                  description_elname=page["description_elname"]["line"],
                                  description_intro=desc)

            # 饼图
            pie_ret = self.making_data(chart_typ="pie", fmts=page["all_fmts"],
                                       page_name=page["page_name"],
                                       item_id=page["item_id"]["pie"])
            self.report_draw_pie(self.report_tpl_pg_num,
                                 "section_log_distribution_pie_chart",
                                 pie_ret["datas"], pie_ret["category_names"]
                                 )

            # 柱状图（探针）
            sensor_bar_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                              page_name=page["page_name"],
                                              item_id=page["item_id"]["bar"])
            self.report_draw_bar(
                self.report_tpl_pg_num,
                page["elname"]["bar"],
                sensor_bar_ret
            )

            # 柱状图（探针组）
            sensor_group_bar_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                                    page_name=page["page_name"],
                                                    item_id=page["item_id"]["bar"], grouping=True)
            if sensor_group_bar_ret:
                self.report_draw_bar(
                    self.report_tpl_pg_num,
                    page["elname"]["bar_group"],
                    sensor_group_bar_ret
                )


class ReportSenSafe(PDFReport):
    """
    探针安全日志
    """
    # report_tpl_pg_num = 2
    ALL_VIOLATION_TRIGGERED_FMTS = [
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
        # 设置 page num
        self.set_page_idx(2)
        self.items = {}

    def add_items(self, items, **kwargs):
        self.indicate_parameters(**kwargs)

        self.items["pages"] = [
            {
                "page_name": "violation_define",
                "rule_id": "00",
                "search_index": "log*",
                "all_fmts": self.ALL_VIOLATION_TRIGGERED_FMTS,
                "fmts": self.ALL_VIOLATION_TRIGGERED_FMTS,
                "item_id": {
                    "line": 0,
                    "line_with_resolved": 1,
                    "pie": 2,
                    "bar": 3
                },
                "elname": {
                    "line": "violation_triggered_trend_line_chart",
                    "pie": "violation_triggered_distrbution",
                    "bar": "violation_triggered_sensor_top",
                    "bar_group": "violation_triggered_sensor_group_top"
                },
            },
            {
                "page_name": "log_classify",
                "rule_id": "00",
                "search_index": "log*",
                "all_fmts": self.ALL_VIOLATION_DETAIL_FMTS,
                "fmts": items["kwargs"]["violation_detail_fmts"],
                "item_id": {
                    "line": 0,
                    "pie": 1,
                    "bar": 2
                },
                "elname": {
                    "line": "violation_detail_trend_line_chart",
                    "pie": "violation_detail_distrbution",
                    "bar": "violation_detail_distrbution_sensor_top_",
                    "bar_group": "violation_detail_distrbution_sensor_group_top_"
                }
            },
            {
                "page_name": "log_classify",
                "rule_id": "00",
                "search_index": "log*",
                "all_fmts": self.ALL_VIOLATION_OTHER_FMTS,
                "fmts": items["kwargs"]["violation_other_fmts"],
                "item_id": {
                    "line": 0,
                    "pie": 1,
                    "bar": 2
                },
                "elname": {
                    "line": "violation_others_trend_line_chart",
                    "pie": "violation_others_distrbution",
                    "bar": "violation_others_sensor_top_",
                    "bar_group": "violation_others_sensor_group_top_"
                }
            }
        ]

    def draw_page(self):
        """
        遍历item，获取数据并生成图
        """
        for page in self.items["pages"]:
            # 折线图
            if page["page_name"] == "violation_define":
                self.draw_violation_define_line_chart(page)
                # 违规定义日志-折线图
            else:
                # page_name 为 违规详情日志、其他安全日志
                # self.draw_line_chart()
                line_ret = self.making_data(chart_typ="line", fmts=page["fmts"],
                                            item_id=page["item_id"]["line"],
                                            page_name=page["page_name"])
                self.report_draw_line(
                    self.report_tpl_pg_num,
                    page["elname"]["line"],
                    line_ret["datas"],
                    line_ret["legend_names"],
                    line_ret["category_names"]
                )

            # 饼图
            pie_ret = self.making_data(chart_typ="pie", fmts=page["all_fmts"],
                                       item_id=page["item_id"]["pie"],
                                       page_name=page["page_name"])
            self.report_draw_pie(
                self.report_tpl_pg_num,
                elname=page["elname"]["pie"],
                datas=pie_ret["datas"],
                category_names=pie_ret["category_names"]
            )

            # 柱状图(探针组)
            bar_group_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                             item_id=page["item_id"]["bar"],
                                             page_name=page["page_name"], grouping=True)
            if bar_group_ret:
                self.report_draw_bar(
                    self.report_tpl_pg_num,
                    page["elname"]["bar_group"],
                    bar_infos=bar_group_ret,
                    elname=page["elname"]["bar_group"]
                )

            # 柱状图(探针)
            bar_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                       item_id=page["item_id"]["bar"],
                                       page_name=page["page_name"])
            if bar_ret:
                self.report_draw_bar(
                    self.report_tpl_pg_num,
                    page["elname"]["bar"],
                    bar_infos=bar_ret,
                    elname=page["elname"]["bar"]
                )

    def draw_line_chart(self):
        pass

    def draw_violation_define_line_chart(self, page):
        """添加探针安全日志-违规定义日志 折线图，
        该图需要请求四次ES，分别获取未解决、已解决日志和违规定义触发次数、触发员工次数
        """
        datas = []
        legend_names = []

        line_triggered_ret = self.making_data(chart_typ="line", fmts=page["fmts"],
                                              item_id=page["item_id"]["line"],
                                              page_name=page["page_name"])
        category_names = line_triggered_ret["category_names"]
        datas.append(line_triggered_ret["datas"][0])
        legend_names.append("触发员工次数")

        for resolved in ["0", "1", None]:
            line_with_resolved_ret = self.making_data(chart_typ="line", fmts=page["fmts"],
                                                      resolved=resolved,
                                                      page_name=page["page_name"],
                                                      item_id=page["item_id"]["line_with_resolved"])
            datas.append(line_with_resolved_ret["datas"][0])
            if resolved == "0":
                legend_names.append("未解决")
            elif resolved == "1":
                legend_names.append("已解决")
            else:
                legend_names.append("违规定义触发次数")

        self.report_draw_line(self.report_tpl_pg_num,
                              page["elname"]["line"],
                              datas,
                              legend_names,
                              category_names)


class ReportSenNetwork(PDFReport):
    """
    探针主机日志生成
    """
    PG_NUM = 3

    def __init__(self):
        super(ReportSenNetwork, self).__init__()
        self.set_page_idx(self.PG_NUM)
        self.items = {}

    def add_items(self, items, **kwargs):
        self.indicate_parameters(**kwargs)

        self.items["pages"] = [
            {
                "page_name": "network_violation",
                "rule_id": "00",
                "search_index": "datamap_precompute*",
                "fmts": items["kwargs"]["network_violation_fmts"],
                "item_id": {
                    "line": 0,
                    "bar": 1,
                    "bar_group": 1,
                    "bar_dest": 2,
                    "bar_rule": 3
                },
                "elname": {
                    "line": "network_violation_trend_line_chart",
                    "bar_group": "network_violation_sensor_group_top10",
                    "bar_sensor": "network_violation_sensor_top10",
                    "bar_dest": "network_violation_dest_top10",
                    "bar_rule": "network_violation_rule_top10",
                },
                "description_elname": {
                    "line": "network_violation_desc",
                },
                "opt1": {
                    "line_user": 0,
                    "line_sensor": 1,
                    "bar_user": 0,
                    "bar_sensor": 1,
                }
            },
            {
                "page_name": "netflow_violation",
                "rule_id": "00",
                "search_index": "log*",
                "fmts": items["kwargs"]["netflow_violation_fmts"],
                "item_id": {
                    "line": 0,
                    "bar": 1,
                    "bar_group": 1,
                    "bar_dest": 2,
                    "bar_rule": 3
                },
                "elname": {
                    "line": "netflow_violation_trend_line_chart",
                    "bar_group": "netflow_violation_sensor_group_top10",
                    "bar_sensor": "netflow_violation_sensor_top10",
                    "bar_dest": "netflow_violation_dest_top10",
                    "bar_rule": "netflow_violation_rule_top10",
                },
                "description_elname": {
                    "line": "netflow_violation_desc",
                },
                "opt1": {
                    "line_user": 0,
                    "line_sensor": 1,
                    "bar_user": 0,
                    "bar_sensor": 1,
                }
            },
        ]

    def draw_page(self):
        """
        """
        for page in self.items["pages"]:
            # 折线图
            line_ret = self.making_data(chart_typ="line", fmts=page["fmts"],
                                        page_name=page["page_name"],
                                        item_id=page["item_id"]["line"],
                                        search_index=page["search_index"],
                                        opt1=page["opt1"]["line_sensor"],
                                        grouping=True)
            desc = (
                f"探针主机网络管控报告，包含：访问管控策略日志、流量管控日志、平均流量统计"
                f"包含日志类型: {line_ret['legend_names']},"
                f"时间范围: {line_ret['category_names'][0]} 至 {line_ret['category_names'][-1]}"
            )
            self.report_draw_line(self.report_tpl_pg_num,
                                  page["elname"]["line"],
                                  line_ret['datas'],
                                  line_ret['legend_names'],
                                  line_ret['category_names'],
                                  has_description=True,
                                  description_elname=page["description_elname"]["line"],
                                  description_intro=desc)

            # 柱状图（探针组）
            sensor_group_bar_ret = self.making_data(chart_typ="bar",
                                                    fmts=page["fmts"],
                                                    page_name=page["page_name"],
                                                    item_id=page["item_id"]["bar_group"],
                                                    search_index=page["search_index"],
                                                    grouping=True, opt1=page["opt1"]["bar_sensor"])
            if sensor_group_bar_ret:
                self.report_draw_bar(
                    self.report_tpl_pg_num,
                    page["elname"]["bar_group"],
                    sensor_group_bar_ret
                )

            # 柱状图(探针)
            sensor_bar_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                              page_name=page["page_name"],
                                              item_id=page["item_id"]["bar"],
                                              search_index=page["search_index"],
                                              opt1=page["opt1"]["bar_sensor"])
            if sensor_bar_ret:
                self.report_draw_bar(
                    self.report_tpl_pg_num,
                    page["elname"]["bar_sensor"],
                    sensor_bar_ret
                )

            # 柱状图(目的地)
            dest_bar_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                            page_name=page["page_name"],
                                            item_id=page["item_id"]["bar_dest"],
                                            search_index=page["search_index"])
            if dest_bar_ret:
                self.report_draw_bar(
                    self.report_tpl_pg_num,
                    page["elname"]["bar_dest"],
                    dest_bar_ret
                )

            # 柱状图(违规规则)
            rule_bar_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                            page_name=page["page_name"],
                                            item_id=page["item_id"]["bar_rule"],
                                            search_index=page["search_index"])
            if rule_bar_ret:
                self.report_draw_bar(
                    self.report_tpl_pg_num,
                    page["elname"]["bar_rule"],
                    rule_bar_ret
                )


class ReportFileOperation(PDFReport):
    """
    文件出入日志
    """

    PG_NUM = 4

    def __init__(self):
        super(ReportFileOperation, self).__init__()
        self.set_page_idx(self.PG_NUM)
        self.items = {}

    def add_items(self, items, **kwargs):
        self.indicate_parameters(**kwargs)

        self.items["pages"] = [
            {
                "page_name": "file_operate",
                "rule_id": "00",
                "search_index": "datamap_precompute*",
                "fmts": [],
                "item_id": {
                    "line": 0,          # 文件出入日志 - 统计数量
                    "bar_sensors": 2,   # 文件出入日志 - 出入数量top10
                    "bar_groups": 3,    # 文件出入日志 - 出入流量top10
                },
                "elname": {
                    "file_operate_num_line_chart_USB": {
                        "chart_type": "line",
                        "item_id": 0,
                        "access_format": ["USB_OUT","USB_IN",
                                          "SEC_USB_IN","SEC_USB_OUT"],
                    },
                    "file_operate_flow_line_chart_USB": {
                        "chart_type": "line",
                        "item_id": 1,
                        "access_format": ["USB_OUT","USB_IN",
                                          "SEC_USB_IN","SEC_USB_OUT"],
                    },
                    "file_operate_sensor_group_num_top_USB": {
                        "chart_type": "bar",
                        "item_id": 2,
                        "access_format": [["SEC_USB_IN", "USB_IN"],
                                          ["SEC_USB_OUT", "USB_OUT"]],
                        "group": True,
                        "split_request": True,
                    },
                    "file_operate_sensor_group_flow_top_USB": {
                        "chart_type": "bar",
                        "item_id": 3,
                        "access_format": [["SEC_USB_IN", "USB_IN"],
                                          ["SEC_USB_OUT", "USB_OUT"]],
                        "group": True,
                        "split_request": True,
                    },
                    "file_operate_sensor_num_top_USB":{
                        "chart_type": "bar",
                        "item_id": 2,
                        "access_format": [["SEC_USB_IN", "USB_IN"],
                                          ["SEC_USB_OUT", "USB_OUT"]],
                        "split_request": True,
                    },
                    "file_operate_sensor_flow_top_USB":{
                        "chart_type": "bar",
                        "item_id": 3,
                        "access_format": [["SEC_USB_IN", "USB_IN"],
                                          ["SEC_USB_OUT", "USB_OUT"]],
                        "split_request": True,
                    },

                },
                "description_elname": {
                    "line": "network_violation_desc",
                },
                "opt1": {
                    "line_user": 0,
                    "line_sensor": 1,
                    "bar_user": 0,
                    "bar_sensor": 1,
                }
            },
        ]

    def draw_page(self):
        """
        draw 文件出入
        :return:
        """

        for page in self.items["pages"]:
            # Todo: init title or description
            elements = page["elname"]

            for element_name, v in elements.items():
                # Todo: indentify chart type.

                merged_data = {}

                _group = True if v.get("group") else False

                if v.get("split_request") is not None and \
                    v.get("split_request") is True:
                    for _af in v["access_format"]:

                        _fmts = v.get("fmts")
                        _resovled = v.get("resolved")
                        _item_id = v.get("item_id")
                        _chart_typ = v.get("chart_type")

                        r = self.making_data(_chart_typ, fmts=_fmts, resolved=_resovled,
                                             access_fmts=_af,
                                             item_id=_item_id,
                                             page_name=page["page_name"],
                                             search_index=page["search_index"],
                                             grouping=_group)
                        # merge data
                        merged_data.update(r)
                else:

                    _fmts = v.get("fmts")
                    _resovled = v.get("resolved")
                    _access_fmt = v.get("access_format")
                    _item_id = v.get("item_id")
                    _chart_typ = v.get("chart_type")

                    r = self.making_data(_chart_typ, fmts=_fmts, resolved=_resovled,
                                         access_fmts=_access_fmt,
                                         item_id=_item_id,
                                         page_name=page["page_name"],
                                         search_index=page["search_index"],
                                         grouping=_group)
                    merged_data = r


                if v["chart_type"] == "line":
                    # drawline
                    datas, legend_names, category_names = r['datas'], r['legend_names'], r['category_names']
                    self.report_draw_line(self.report_tpl_pg_num, element_name, datas,
                                          legend_names=legend_names,
                                          category_names=category_names)
                elif v["chart_type"] == "bar":
                    # drawbar

                    _group = True if len(merged_data.keys()) > 1 else False
                    self.report_draw_bar1(self.report_tpl_pg_num,
                                          elname=element_name,
                                          bar_infos=merged_data,
                                          group_bar=_group)

                elif v["chart_type"] == "pie":
                    # drawpie
                    raise NotImplemented
                else:
                    raise ValueError("chart type not in [line, bar, pie].")


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
        # "log_search": ReportSenHost,
        # "violation_define": ReportSenSafe,
        # "network_violation": ReportSenNetwork,
        "file_operate": ReportFileOperation
    }

    case = {
        "begin_t": "2019-06-01T00:00:00.000",
        "end_t": "2019-07-18T00:00:00.000",
        "report_pages": {
            "log_search": {
                "kwargs": {
                    "fmts": [
                        "SENSOR_SAFEMODE_BOOT",
                        "SENSOR_MULTIPLE_OS_BOOT",
                        "SENSOR_VM_INSTALLED",
                        "SENSOR_SERVICECHANGE",
                        "SENSOR_HARDWARE_CHANGE"
                    ]
                }
            },
            "violation_define": {
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
            },
            "network_violation": {
                "kwargs": {
                    "network_violation_fmts": [
                        "SENSOR_NETWORK_ABNORMAL"
                    ],
                    "netflow_violation_fmts": [
                        "SENSOR_NETWORK_FLOW"
                    ],
                }
            },
            "file_operate": {
                "kwargs": {

                }
            }
        }

    }

    begin_t = case["begin_t"]
    end_t = case["end_t"]

    kwargs = {
        "sensor_id_group_map": sensor_id_group_mapping,
        "begin_t": begin_t,
        "end_t": end_t,
        "sensors": sensors
    }

    # for report_page in case["report_pages"]:
    #     try:
    #         prt = report_page_class_mapping[report_page["page_name"]]()
    #         prt.add_items(report_page, **kwargs)
    #         prt.draw_page()
    #     except Exception as e:
    #         print(f"errmsg: {e}")
    #         print(traceback.format_exc())

    for pgname, cls in report_page_class_mapping.items():
        _cls = cls()

        try:
            _begin_t = case["begin_t"]
            _end_t = case["end_t"]
            args = case["report_pages"][pgname]
            _cls.indicate_groups(sensor_id_group_mapping)
            _cls.indicate_sensors(sensors)
            _cls.indicate_date_scope(_begin_t, _end_t)
            _cls.add_items(args)
            _cls.draw_page()

        except Exception as e:
            traceback.print_exc()




    PDFReport().draw()


if __name__ == "__main__":

    import time

    pf1 = time.perf_counter()
    test_case()
    print(time.perf_counter() - pf1)

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
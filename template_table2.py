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
    post_time_out = 10000  # 秒
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

    def cook_line_data(self, payload: dict, grouping=False, need_second=False):
        """
        translate es return data to pdflib line chart data
        :param payload:
        :param grouping:
        :param need_second:
        :return:
        """
        begin_t = util.payload_time_to_datetime(payload["start_time"])
        end_t = util.payload_time_to_datetime(payload["end_time"])
        interval = (end_t - begin_t).days

        # payload_log_format = payload["data_scope"].get("FORMAT.raw")

        if payload["page_name"] == "sensor_netio":
            payload_log_format = ["SENSOR_NETIO"]
        elif payload["page_name"] == "critical_file":
            payload_log_format = ["SENSOR_FILESYSTEM"]
        elif payload["page_name"] == "file_operate":
            payload_log_format = payload["data_scope"].get("ACCESS_FORMAT.raw")
        else:
            payload_log_format = payload["data_scope"].get("FORMAT.raw")

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
                # log_format = "UNKNOW_FORMAT"
                log_format = payload_log_format[0]
            if sensor_id:
                chart_datas[sensor_id][value_index] += int(value)
            else:
                chart_datas[log_format][value_index] += int(value)

            if need_second:
                chart_datas["SECOND"][value_index] += int(_[0])

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

        if need_second:
            ret["second_datas"] = chart_datas["SECOND"]

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
                elif key_dict[0].get("FILE_NAME.raw"):
                    key = key_dict[0]["FILE_NAME.raw"]
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
            if log_format == "SENSOR_FILEPARSE_LOG":
                legend_names = []
            else:
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

    @util.timeit
    def ruleng_url_post(self, data):
        print(f"TIMEOUT={self.post_time_out}")
        ret = requests.post(self.ruleng_url, data=data, timeout=self.post_time_out)
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
                    grouping=False, opt1=None, need_second=False, level=None, limit=10,
                    rule_uuid=None, top=None, **kwargs):
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
        :param need_second:
        :param rule_uuid:
        :param top:
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
        if level:
            content["data_scope"]["LEVEL.raw"] = level
        if rule_uuid:
            content["data_scope"]["UUID.raw"] = rule_uuid


        if opt1:
            content["opt1"] = opt1
        if top:
            content["top"] = top

        if chart_typ == "line":
            ret = self.cook_line_data(content, grouping=grouping, need_second=need_second)
        elif chart_typ == "bar":
            ret = self.cook_bar_data(content, grouping=grouping, limit=limit)
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
                                  "SENSOR_NETWORK_FLOW",
                                  "SENSOR_OPEN_PORT",
                                  "SENSOR_CREDIBLE_APP",
                                  "SENSOR_CREDIBLE_NETWORK",
                                  "SENSOR_CREDIBLE_PORT",
                                  "SENSOR_CREDIBLE_DATA",
                                  "SENSOR_PSYSTEM_FILE",
                                  "SENSOR_FILEPARSE_LOG",
                                  ] \
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

    def report_draw_table(self, page_idx, elname, datas, category_names,
                          has_description=False, description_elname="",
                          description_intro=""):
        """
        自定义报告表格
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
        data = [category_names] + datas
        PDFTemplate.set_table_data(
            self.report_tpl_pgs,
            page_idx,
            elname,
            data=data
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
            if line_ret:
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
            if pie_ret:
                self.report_draw_pie(self.report_tpl_pg_num,
                                     "section_log_distribution_pie_chart",
                                     pie_ret["datas"], pie_ret["category_names"]
                                     )

            # 柱状图（探针）
            sensor_bar_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                              page_name=page["page_name"],
                                              item_id=page["item_id"]["bar"])
            if sensor_bar_ret:
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
                if line_ret:
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
            if pie_ret:
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

        if all(datas) and all((legend_names, category_names)):
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
            {
                "page_name": "sensor_netio",
                "rule_id": "00",
                "search_index": "log*",
                "fmts": "SENSOR_NETIO",
                "item_id": {
                    "download": 0,
                    "upload": 1,
                },
                "elname": {
                    "upload": "sensor_netio_aver_upload_flow_line_chart",
                    "download": "sensor_netio_aver_download_flow_line_chart"
                }
            }
        ]

    def draw_page(self):
        """
        """
        for page in self.items["pages"]:

            if page["page_name"] == "sensor_netio":
                self.draw_netio_chart(page)
            else:
                self.draw_network_control_flow_chart(page)

    def draw_netio_chart(self, page):
        for direction in ["upload", "download"]:
            upload_line_ret = self.making_data(chart_typ="line",
                                               page_name=page["page_name"],
                                               item_id=page["item_id"][direction],
                                               search_index=page["search_index"],
                                               need_second=True)
            if upload_line_ret:
                datas = [[util.trans_bit_to_mb(_) for _ in upload_line_ret["datas"][0]],
                         [util.trans_bit_to_mb(_) for _ in upload_line_ret["second_datas"]]]
                # datas.append([util.trans_bit_to_mb(_) for _ in upload_line_ret["second_datas"]])
                legend_names = ["文件访问总量", "网络平均访问量"]
                self.report_draw_line(
                    self.report_tpl_pg_num,
                    elname=page["elname"][direction],
                    datas=datas,
                    legend_names=legend_names,
                    category_names=upload_line_ret["category_names"]
                )

    def draw_network_control_flow_chart(self, page):
        # 折线图
        line_ret = self.making_data(chart_typ="line", fmts=page["fmts"],
                                    page_name=page["page_name"],
                                    item_id=page["item_id"]["line"],
                                    search_index=page["search_index"],
                                    opt1=page["opt1"]["line_sensor"],
                                    grouping=True)
        if all((line_ret.values())):
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


class ReportSenTrust(PDFReport):
    """
    端口开放管理日志生成
    """
    OPEN_PORT_PG_NUM = 4
    SAFE_BASE_PG_NUM = 5

    def __init__(self):
        super(ReportSenTrust, self).__init__()
        # self.set_page_idx(self.PG_NUM)
        self.items = {}

    def add_items(self, items, **kwargs):
        self.indicate_parameters(**kwargs)

        self.items["pages"] = [
            {
                "page": "open_port",
                "page_name": "trust",
                "rule_id": "00",
                "search_index": "log*",
                "fmts": items["kwargs"]["port_fmts"],
                "item_id": {
                    "line": 0,
                    "bar": 1,
                },
                "elname": {
                    "line_deny": "open_port_deny_trend_line_chart",
                    "line_alarm": "open_port_alarm_trend_line_chart",
                    "bar_deny_sensor": "open_port_deny_sensor_top10",
                    "bar_alarm_sensor": "open_port_alarm_sensor_top10",
                    "bar_deny_group": "open_port_deny_sensor_group_top10",
                    "bar_alarm_group": "open_port_alarm_sensor_group_top10",
                },
                "description_elname": {
                    "line": "open_port_desc",
                },
                "level": {
                    "deny": "DENY",
                    "alarm": "ALARM",
                }
            },
            {
                "page": "safe_base",
                "page_name": "trust",
                "rule_id": "00",
                "search_index": "log*",
                "fmts": items["kwargs"]["trust_fmts"],
                "item_id": {
                    "line": 0,
                    "bar": 1,
                    "app": 2,
                },
                "elname": {
                    "line_deny": "trust_deny_trend_line_chart",
                    "line_alarm": "trust_alarm_trend_line_chart",
                    "bar_deny_sensor": "trust_deny_sensor_top10",
                    "bar_alarm_sensor": "trust_alarm_sensor_top10",
                    "bar_deny_group": "trust_deny_sensor_group_top10",
                    "bar_alarm_group": "trust_alarm_sensor_group_top10",
                    "bar_alarm_app": "trust_app_alarm_sensor_top10",
                    "bar_deny_app": "trust_app_deny_sensor_top10",
                },
                "description_elname": {
                    "line": "trust_desc",
                },
                "level": {
                    "deny": "DENY",
                    "alarm": "ALARM",
                }
            },
        ]

    def draw_page(self):
        for page in self.items["pages"]:
            if page["page"] == "open_port":
                self.set_page_idx(self.OPEN_PORT_PG_NUM)
            elif page["page"] == "safe_base":
                self.set_page_idx(self.SAFE_BASE_PG_NUM)
            else:
                raise ValueError("Wrong page")

            for level in ["deny", "alarm"]:
                line_ret = self.making_data(chart_typ="line", fmts=page["fmts"],
                                            page_name=page["page_name"],
                                            item_id=page["item_id"]["line"],
                                            search_index=page["search_index"],
                                            level=page["level"][level])

                if line_ret:
                    self.report_draw_line(
                        self.report_tpl_pg_num,
                        elname=page["elname"][f"line_{level}"],
                        datas=line_ret["datas"],
                        category_names=line_ret["category_names"],
                        legend_names=line_ret["legend_names"]
                    )

                bar_sensor_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                                  page_name=page["page_name"],
                                                  item_id=page["item_id"]["bar"],
                                                  search_index=page["search_index"],
                                                  level=page["level"][level])
                if bar_sensor_ret:
                    self.report_draw_bar(
                        self.report_tpl_pg_num,
                        elname_prefix=page["elname"][f"bar_{level}_sensor"],
                        bar_infos=bar_sensor_ret,
                    )

                bar_group_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                                 page_name=page["page_name"],
                                                 item_id=page["item_id"]["bar"],
                                                 search_index=page["search_index"],
                                                 level=page["level"][level], grouping=True)
                if bar_group_ret:
                    self.report_draw_bar(
                        self.report_tpl_pg_num,
                        elname_prefix=page["elname"][f"bar_{level}_group"],
                        bar_infos=bar_group_ret
                    )

                if page["page"] == "safe_base":
                    bar_app_ret = self.making_data(chart_typ="bar", fmts=page["fmts"],
                                                   page_name=page["page_name"],
                                                   item_id=page["item_id"]["app"],
                                                   search_index=page["search_index"],
                                                   level=page["level"][level])
                    if bar_app_ret:
                        self.report_draw_bar(
                            self.report_tpl_pg_num,
                            elname_prefix=page["elname"][f"bar_{level}_app"],
                            bar_infos=bar_group_ret
                        )


class ReportSenFile(PDFReport):
    """
    端口开放管理日志生成
    """
    PG_NUM = 6
    LIMIT_NUM = 5

    def __init__(self):
        super(ReportSenFile, self).__init__()
        self.set_page_idx(self.PG_NUM)
        self.items = {}

    def add_items(self, items, **kwargs):
        self.indicate_parameters(**kwargs)

        self.items["pages"] = [
            {
                "page_name": "critical_file",
                "rule_id": "00",
                "search_index": {
                    "normal": "logstash*",
                    "spe": "datamap*",
                },
                "fmts": items["kwargs"]["fmts"],
                "fmts_sensor_parse_file": items["kwargs"]["sensor_parse_file"],
                "item_id": {
                    "line_all_file": 0,
                    "line_rule_file": 1,
                    "bar_file_top5": 2,
                    "table_key_heat_top10": 3,
                    "bar_sensor_group": 4,
                    "bar_sensor": 4
                },
                "elname": {
                    "line_deny": "key_file_trend_line_chart",
                    "bar_all_file": "file_name_top5",
                    "bar_sensor_group": "key_file_sensor_group_top10",
                    "bar_sensor": "key_file_sensor_top10",
                    "table_key_heat_top10": "file_content_key_heat_top5",
                },
                "description_elname": {
                },
                "uuid": {
                    "line_rule_file": items["kwargs"]["rule_file_uuid"]
                },
                "top": {
                    "file_name_top5": "5",
                }
            },
        ]

    def draw_page(self):
        for page in self.items["pages"]:
            line_all_file = self.making_data(chart_typ="line", fmts=page["fmts"],
                                             page_name=page["page_name"],
                                             item_id=page["item_id"]["line_all_file"],
                                             search_index=page["search_index"]["normal"])
            line_rule_file = self.making_data(chart_typ="line",
                                              page_name=page["page_name"],
                                              item_id=page["item_id"]["line_rule_file"],
                                              search_index=page["search_index"]["spe"],
                                              rule_uuid=page["uuid"]["line_rule_file"])

            line_ret = {
                "datas": line_all_file["datas"] + line_rule_file["datas"],
                "category_names": line_all_file["category_names"],
                "legend_names": ["所有文件总量", "命中选中策略的文件总量"]
            }

            self.report_draw_line(
                self.report_tpl_pg_num,
                elname=page["elname"]["line_deny"],
                datas=line_ret["datas"],
                category_names=line_ret["category_names"],
                legend_names=line_ret["legend_names"]
            )

            table_file_top5 = self.making_data(chart_typ="bar", fmts=page["fmts_sensor_parse_file"],
                                             page_name=page["page_name"],
                                             item_id=page["item_id"]["bar_file_top5"],
                                             search_index=page["search_index"]["normal"],
                                             limit=self.LIMIT_NUM,
                                             rule_uuid=page["uuid"]["line_rule_file"],
                                             top=page["top"]["file_name_top5"])
            if table_file_top5:
                self.report_draw_table(
                    self.report_tpl_pg_num,
                    elname=page["elname"]["bar_all_file"],
                    datas=table_file_top5["SENSOR_FILEPARSE_LOG"]["datas"],
                    category_names=table_file_top5["SENSOR_FILEPARSE_LOG"]["category_names"],
                )

            # table_key_heat_top10 = self.making_data(chart_typ="bar",
            #                                         fmts=page["fmts_sensor_parse_file"],
            #                                         page_name=page["page_name"],
            #                                         item_id=page["item_id"]["table_key_heat_top10"],
            #                                         search_index=page["search_index"]["spe"],
            #                                         rule_uuid=page["uuid"]["line_rule_file"],
            #                                         )

            bar_group_ret = self.making_data(chart_typ="bar", fmts=page["fmts_sensor_parse_file"],
                                             page_name=page["page_name"],
                                             item_id=page["item_id"]["bar_sensor_group"],
                                             search_index=page["search_index"]["normal"],
                                             rule_uuid=page["uuid"]["line_rule_file"],
                                             top=page["top"]["file_name_top5"],
                                             grouping=True)
            self.report_draw_bar(
                self.report_tpl_pg_num,
                page["elname"]["bar_sensor_group"],
                bar_group_ret
            )

            bar_group_ret = self.making_data(chart_typ="bar", fmts=page["fmts_sensor_parse_file"],
                                             page_name=page["page_name"],
                                             item_id=page["item_id"]["bar_sensor"],
                                             search_index=page["search_index"]["normal"],
                                             rule_uuid=page["uuid"]["line_rule_file"],
                                             top=page["top"]["file_name_top5"])
            self.report_draw_bar(
                self.report_tpl_pg_num,
                page["elname"]["bar_sensor"],
                bar_group_ret
            )


class ReportFileOperation(PDFReport):
    """
    文件出入日志
    """

    PG_NUM = 7

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
    #    sensors = ['LNX0001',
 # 'LNX0002',
 # 'LNX0003',
 # 'LNX0004',
 # 'LNX0005',
 # 'LNX0006',
 # 'LNX0007',
 # 'LNX0008',
 # 'LNX0009',
 # 'LNX0010',
 # 'LNX0011',
 # 'LNX0012',
 # 'LNX0013',
 # 'LNX0014',
 # 'LNX0015',
 # 'LNX0016',
 # 'LNX0017',
 # 'LNX0018',
 # 'LNX0019',
 # 'LNX0020',
 # 'LNX0021',
 # 'LNX0022',
 # 'LNX0023',
 # 'LNX0024',
 # 'LNX0025',
 # 'LNX0026',
 # 'LNX0027',
 # 'LNX0028',
 # 'WIN0001',
 # 'WIN0002',
 # 'WIN0003',
 # 'WIN0004',
 # 'WIN0005',
 # 'WIN0006',
 # 'WIN0007',
 # 'WIN0008',
 # 'WIN0009',
 # 'WIN0010',
 # 'WIN0011',
 # 'WIN0012',
 # 'WIN0013',
 # 'WIN0014',
 # 'WIN0015',
 # 'WIN0016',
 # 'WIN0017',
 # 'WIN0018',
 # 'WIN0019',
 # 'WIN0020',
 # 'WIN0021',
 # 'WIN0022',
 # 'WIN0023',
 # 'WIN0024',
 # 'WIN0025',
 # 'WIN0026',
 # 'WIN0027',
 # 'WIN0028',
 # 'WIN0029',
 # 'WIN0030',
 # 'WIN0031',
 # 'WIN0032',
 # 'WIN0033',
 # 'WIN0034',
 # 'WIN0035',
 # 'WIN0036',
 # 'WIN0037',
 # 'WIN0038',
 # 'WIN0039',
 # 'WIN0040',
 # 'WIN0041',
 # 'WIN0042',
 # 'WIN0043',
 # 'WIN0044',
 # 'WIN0045',
 # 'WIN0046',
 # 'WIN0047',
 # 'WIN0048',
 # 'WIN0049',
 # 'WIN0050',
 # 'WIN0051',
 # 'WIN0052',
 # 'WIN0053',
 # 'WIN0054',
 # 'WIN0055',
 # 'WIN0056',
 # 'WIN0057',
 # 'WIN0058',
 # 'WIN0059',
 # 'WIN0060',
 # 'WIN0061',
 # 'WIN0062',
 # 'WIN0063',
 # 'WIN0064',
 # 'WIN0065',
 # 'WIN0066',
 # 'WIN0067',
 # 'WIN0068',
 # 'WIN0069',
 # 'WIN0070',
 # 'WIN0071',
 # 'WIN0072',
 # 'WIN0073',
 # 'WIN0074',
 # 'WIN0075',
 # 'WIN0076',
 # 'WIN0077',
 # 'WIN0078',
 # 'WIN0079',
 # 'WIN0080',
 # 'WIN0081',
 # 'WIN0082',
 # 'WIN0083',
 # 'WIN0084',
 # 'WIN0085',
 # 'WIN0086',
 # 'WIN0087',
 # 'WIN0088',
 # 'WIN0089',
 # 'WIN0090',
 # 'WIN0091',
 # 'WIN0092',
 # 'WIN0093',
 # 'WIN0094',
 # 'WIN0095',
 # 'WIN0096',
 # 'WIN0097',
 # 'WIN0098',
 # 'WIN0099',
 # 'WIN0100',
 # 'WIN0101',
 # 'WIN0102',
 # 'WIN0103',
 # 'WIN0104',
 # 'WIN0105',
 # 'WIN0106',
 # 'WIN0107',
 # 'WIN0108',
 # 'WIN0109',
 # 'WIN0110',
 # 'WIN0111',
 # 'WIN0112',
 # 'WIN0113',
 # 'WIN0114',
 # 'WIN0115',
 # 'WIN0116',
 # 'WIN0117',
 # 'WIN0118',
 # 'WIN0119',
 # 'WIN0120',
 # 'WIN0121',
 # 'WIN0122',
 # 'WIN0123',
 # 'WIN0124',
 # 'WIN0125',
 # 'WIN0126',
 # 'WIN0127',
 # 'WIN0128',
 # 'WIN0129',
 # 'WIN0130',
 # 'WIN0131',
 # 'WIN0132',
 # 'WIN0133',
 # 'WIN0134',
 # 'WIN0135',
 # 'WIN0136',
 # 'WIN0137',
 # 'WIN0138',
 # 'WIN0139',
 # 'WIN0140',
 # 'WIN0141',
 # 'WIN0142',
 # 'WIN0143',
 # 'WIN0144',
 # 'WIN0145',
 # 'WIN0146',
 # 'WIN0147',
 # 'WIN0148',
 # 'WIN0149',
 # 'WIN0150',
 # 'WIN0151',
 # 'WIN0152',
 # 'WIN0153',
 # 'WIN0154',
 # 'WIN0155',
 # 'WIN0156',
 # 'WIN0157',
 # 'WIN0158',
 # 'WIN0159',
 # 'WIN0160',
 # 'WIN0161',
 # 'WIN0162',
 # 'WIN0163',
 # 'WIN0164',
 # 'WIN0165',
 # 'WIN0166',
 # 'WIN0167',
 # 'WIN0168',
 # 'WIN0169',
 # 'WIN0170',
 # 'WIN0171',
 # 'WIN0172',
 # 'WIN0173',
 # 'WIN0174',
 # 'WIN0175',
 # 'WIN0176',
 # 'WIN0177',
 # 'WIN0178',
 # 'WIN0179',
 # 'WIN0180',
 # 'WIN0181',
 # 'WIN0182',
 # 'WIN0183',
 # 'WIN0184',
 # 'WIN0185',
 # 'WIN0186',
 # 'WIN0187',
 # 'WIN0188',
 # 'WIN0189',
 # 'WIN0190',
 # 'WIN0191',
 # 'WIN0192',
 # 'WIN0193',
 # 'WIN0194',
 # 'WIN0195',
 # 'WIN0196',
 # 'WIN0197',
 # 'WIN0198',
 # 'WIN0199',
 # 'WIN0200',
 # 'WIN0201',
 # 'WIN0202',
 # 'WIN0203',
 # 'WIN0204',
 # 'WIN0205',
 # 'WIN0206',
 # 'WIN0207',
 # 'WIN0208',
 # 'WIN0209',
 # 'WIN0210',
 # 'WIN0211',
 # 'WIN0212',
 # 'WIN0213',
 # 'WIN0214',
 # 'WIN0215',
 # 'WIN0216',
 # 'WIN0217',
 # 'WIN0218',
 # 'WIN0219',
 # 'WIN0220',
 # 'WIN0221',
 # 'WIN0222',
 # 'WIN0223',
 # 'WIN0224',
 # 'WIN0225',
 # 'WIN0226',
 # 'WIN0227',
 # 'WIN0228',
 # 'WIN0229',
 # 'WIN0230',
 # 'WIN0231',
 # 'WIN0232',
 # 'WIN0233',
 # 'WIN0234',
 # 'WIN0235',
 # 'WIN0236',
 # 'WIN0237',
 # 'WIN0238',
 # 'WIN0239',
 # 'WIN0240',
 # 'WSR0001',
 # 'WSR0002',
 # 'WSR0003',
 # 'WSR0004',
 # 'WSR0005',
 # 'WSR0006',
 # 'WSR0007',
 # 'WSR0008']
    sensors = [_ for _ in sensor_id_group_mapping
               if sensor_id_group_mapping[_] == "无分组"]

    report_page_class_mapping = {
        "log_search": ReportSenHost,
        "violation_define": ReportSenSafe,
        "network_violation": ReportSenNetwork,
        "file_operate": ReportFileOperation,
        "trust": ReportSenTrust,
        "critical_file": ReportSenFile,
    }

    # case = {
    #     "begin_t": "2019-07-20T00:00:00.000",
    #     "end_t": "2019-07-23T00:00:00.000",
    #     "report_pages": [
    #             {
    #                 "page_name": "log_search",
    #                 "kwargs":{
    #                     "fmts": [
    #                         "SENSOR_SAFEMODE_BOOT",
    #                         "SENSOR_MULTIPLE_OS_BOOT",
    #                         "SENSOR_VM_INSTALLED",
    #                         "SENSOR_SERVICECHANGE",
    #                         "SENSOR_HARDWARE_CHANGE"
    #                     ]
    #                 }
    #             },
            #     {
            #         "page_name": "violation_define",
            #         "kwargs": {
            #             "violation_detail_fmts": [
            #                 "SENSOR_IO",
            #                 "SENSOR_RESOURCE_OVERLOAD",
            #                 "SENSOR_SERVICE_FULL_LOAD",
            #                 "SENSOR_TIME_ABNORMAL"
            #             ],
            #             "violation_other_fmts": [
            #                 "SENSOR_AUTORUN",
            #                 "SENSOR_NET_SHARE"
            #             ]
            #         }
            #     },
            # {
            #     "page_name": "network_violation",
            #     "kwargs": {
            #         "network_violation_fmts": [
            #             "SENSOR_NETWORK_ABNORMAL"
            #         ],
            #         "netflow_violation_fmts": [
            #             "SENSOR_NETWORK_FLOW"
            #         ],
            #     }
            # },
            # {
            #     "page_name": "trust",
            #     "kwargs": {
            #         "port_fmts": ["SENSOR_OPEN_PORT"],
            #         "trust_fmts": [
            #             "SENSOR_CREDIBLE_APP",
            #             "SENSOR_CREDIBLE_NETWORK",
            #             "SENSOR_CREDIBLE_PORT",
            #             "SENSOR_CREDIBLE_DATA",
            #             "SENSOR_PSYSTEM_FILE"
            #         ]
            #     }
            # },
    #         {
    #             "page_name": "critical_file",
    #             "kwargs": {
    #                 "fmts": [
    #                     "SENSOR_FILESYSTEM"
    #                 ],
    #                 "rule_file_uuid": "8b79218ea23111e996490cc47ab4d1a4",
    #                 "sensor_parse_file": ["SENSOR_FILEPARSE_LOG"]
    #             }
    #         }
    #     ]
    # }

    case = {
        "begin_t": "2019-07-22T00:00:00.000",
        "end_t": "2019-07-29T00:00:00.000",
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

                },
            },
            "trust": {
                    "kwargs": {
                        "port_fmts": ["SENSOR_OPEN_PORT"],
                        "trust_fmts": [
                            "SENSOR_CREDIBLE_APP",
                            "SENSOR_CREDIBLE_NETWORK",
                            "SENSOR_CREDIBLE_PORT",
                            "SENSOR_CREDIBLE_DATA",
                            "SENSOR_PSYSTEM_FILE"
                        ]
                    }
            },
            "critical_file": {
                "kwargs": {
                    "fmts": [
                        "SENSOR_FILESYSTEM"
                    ],
                    "rule_file_uuid": "8b79218ea23111e996490cc47ab4d1a4",
                    "sensor_parse_file": ["SENSOR_FILEPARSE_LOG"]
                }
            },
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
            print(f"page_name: {pgname}")
            traceback.print_exc()

    PDFReport().draw()


if __name__ == "__main__":

    import time

    pf1 = time.perf_counter()
    test_case()
    print(time.perf_counter() - pf1)

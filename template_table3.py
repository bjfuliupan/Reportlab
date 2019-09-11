import collections
import copy
import json
import logging
from datetime import timedelta
from datetime import datetime

import requests

from pdflib.PDFTemplateR import PDFTemplateR
from utils import constant
from utils import util


class DummyOb(object):
    """
    process original data class
    """

    # ruleng_url = "http://192.168.11.200:8002"
    ruleng_url = "http://192.168.10.222:8002"
    # ruleng_url = "http://192.168.8.60:8002"
    post_time_out = 10000  # 秒

    def __init__(self):
        self.sensor_group_map = {}
        self.begin_t = None
        self.end_t = None
        self.sensors = []

    def indicate_date_scope(self, begin_t: str, end_t: str):
        self.begin_t = begin_t
        self.end_t = end_t

    def indicate_sensors(self, sensors: list):
        self.sensors = sensors

    def indicate_groups(self, group: dict):
        self.sensor_group_map = group

    def indicate_page_name(self, page_name: str):
        pass

    def indicate_sort_number(self, sort_number: int):
        pass

    def init_group_data(self) -> dict:
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
        ret = {}
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
        elif payload["page_name"] == "sensor_client":
            payload_log_format = ["在线", "离线"]
        else:
            payload_log_format = payload["data_scope"].get("FORMAT.raw")

        if payload_log_format is None:
            payload_log_format = [""]

        # 通过payload及时间参数，获取ES日志，并清洗
        # 返回折线图横坐标、纵坐标、折线标签数据
        print(payload)
        data = json.dumps(payload)
        es_log_data = self.ruleng_url_post(data)
        if not es_log_data:
            return ret

        chart_datas = util.init_data_for_pdf_with_interval(interval)
        for key_list, value, *_ in es_log_data["result"]:
            log_format, log_time, sensor_id, log_status = None, None, None, None
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

                elif key_dict.get("SENSOR_STATUS.raw"):
                    log_status = constant.LogConstant.FORMAT_DETAIL_MAPPING[
                        key_dict["SENSOR_STATUS.raw"]
                    ]

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
            elif log_status:
                chart_datas[log_status][value_index] += int(value)
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
            if payload_log_format in [["SENSOR_ALARM_MSG"], ["在线", "离线"]]:
                legend_names = payload_log_format
            # elif payload_log_format == ["SENSOR_POLICY_UPDATE_DAILY"]:
            #     legend_names = ["在线", "离线"]
            else:
                legend_names = [
                    constant.LogConstant.FORMAT_DETAIL_MAPPING[_]
                    for _ in payload_log_format
                ]
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

        # # 获取饼图日志类型
        # log_formats = list(pie_data.keys())

        # 违规定义日志的类型为'规则名称'
        if payload["page_name"] == "violation_define":
            category_names = list(pie_data.keys())
        else:
            category_names = [constant.LogConstant.FORMAT_DETAIL_MAPPING[_] for _ in payload_log_format]

        # 获取饼图日志数量
        if payload_log_format == ["SENSOR_ALARM_MSG"]:
            payload_log_format = category_names
        datas = [
            pie_data[_]
            for _ in payload_log_format
        ]

        ret = {
            "datas": datas,
            "category_names": category_names,
        }

        return ret

    def cook_bar_data(self, payload: dict, sort=True, limit=10, grouping=False, without_format=False):
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

            if without_format:
                del payload["data_scope"]["FORMAT.raw"]

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
                elif key_dict[0].get("KEYWORD.raw"):
                    key = key_dict[0]["KEYWORD.raw"]
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


class PDFReport(DummyOb):
    """
    generate report class.
    making pdf and translate data
    """

    def __init__(self, report_template: PDFTemplateR):
        """
        init
        """
        super(PDFReport, self).__init__()
        self.report_tpl = report_template
        self.report_tpl_pg_num = None

    def get_page_idx(self):
        return self.report_tpl_pg_num

    def set_page_idx(self, pg_num):
        self.report_tpl_pg_num = pg_num

    def set_report_name(self, report_name: str):
        self.report_tpl.set_pdf_file(report_name)

    def set_title(self, content, page_idx=0, element_name="title"):
        """
        设置标题, must
        :return:
        """
        self.report_tpl.set_item_data(page_idx, element_name, content=content)

    def set_intro(self, content, page_idx=0, element_name="Introduction"):
        """
        设置文章内容描述
        :return:
        """
        self.report_tpl.set_item_data(page_idx, element_name, content=content)

    def making_data(self, chart_typ: str, fmts=None, resolved=None, access_fmts=None,
                    page_name="log_classify", item_id=0, rule_id="00", search_index="log*",
                    grouping=False, opt1=None, need_second=False, level=None, limit=10,
                    rule_uuid=None, top=None, without_format=False, **kwargs):
        """
        生成数据并进行翻译
        :param fmts: array 查询功能列表
        :param access_fmts: array
        :param chart_typ: 需要生成图例类型 pie 饼图 line 线图 bar 柱图，看是否根据图例进行内容清洗
        :param page_name: rule engine param *
        :param resolved: 日志报警是否已解决，用于'违规定义日志'
        :param item_id: rule engine param *
        :param rule_id: rule engine param *
        :param search_index: rule engine param *
        :param grouping: 是否按探针组对数据进行分组
        :param opt1: 主机网络管控payload关键字
        :param need_second:
        :param level:
        :param limit:
        :param rule_uuid:
        :param top:
        :return: cooked data
        """
        logging.warning("kwargs is not used, %s", kwargs)

        content = {
            "start_time": self.begin_t,
            "end_time": self.end_t,
            "page_name": page_name,
            "item_id": item_id,
            "rule_id": rule_id,
            "search_index": search_index,
            "data_scope": {
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
            ret = self.cook_bar_data(content, grouping=grouping, limit=limit, without_format=without_format)
        elif chart_typ == "pie":
            ret = self.cook_pie_data(content)
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
            self.report_tpl.set_item_data(page_idx, description_elname, content=description_intro)

        self.report_tpl.set_item_data(page_idx, elname,
                                      data=datas, category_names=category_names, legend_names=legend_names)

    def report_draw_pie(self, page_idx, elname, datas, category_names, has_description=False,
                        description_elname="", description_intro=""):
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
            self.report_tpl.set_item_data(page_idx, description_elname, content=description_intro)

        self.report_tpl.set_item_data(page_idx, elname, data=datas, category_names=category_names)

    def report_draw_bar(self, page_idx, elname_prefix: str, bar_infos: dict, elname=None,
                        has_description=False, description_elname="",
                        description_intro="", limit=10, grouping=False, is_flow=False):
        """
        :param page_idx: page number
        :param elname_prefix: 生成柱图会通过组批量产生，提供前缀
        :param bar_infos:
        :param elname:
        :param has_description:
        :param description_elname:
        :param description_intro: 图描述
        :param limit: 柱数量
        :return:
        """
        logging.warning("elname is not used, %s", elname)

        if has_description:
            self.report_tpl.set_item_data(page_idx, description_elname, content=description_intro)

        for log_format, bar_chart_data in bar_infos.items():
            category_names = bar_chart_data["category_names"]
            legend_names = bar_chart_data["legend_names"]
            data = bar_chart_data["datas"]

            # if len(category_names) < limit:
            #     if grouping:
            #         for group_name in self.sensor_group_map.values():
            #             if group_name not in category_names and len(category_names) < limit:
            #                 category_names.append(group_name)
            #                 data[0].append(0)
            #     else:
            #         for sensor_id in self.sensors:
            #             if sensor_id not in category_names and len(category_names) < limit:
            #                 category_names.append(sensor_id)
            #                 data[0].append(0)

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
                                  "SENSOR_POLICY_UPDATE_DAILY",
                                  ] \
                else f"{elname_prefix}{log_format}"

            if is_flow:
                data = [[util.trans_bit_to_mb(value) for value in lst] for lst in data]

            self.report_tpl.set_item_data(page_idx, item_name, data=data,
                                          category_names=category_names,
                                          # legend_names=legend_names
                                          )

    def report_draw_bar1(self, page_idx, elname_prefix=None, bar_infos=None, elname=None,
                         has_description=False, description_elname="", description_intro="",
                         group_bar=False, limit=10, is_flow=False):
        """
        draw group bar

        :param page_idx: page number
        :param elname_prefix: 生成柱图会通过组批量产生，提供前缀
        :param bar_infos:
        :param elname:
        :param has_description:
        :param description_elname:
        :param description_intro: 图描述
        :param group_bar:
        :param limit:
        :return:
        """

        if has_description:
            self.report_tpl.set_item_data(page_idx, description_elname, content=description_intro)

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
                if _ik not in value["category_names"] and len(value["category_names"]) < limit:
                    value["category_names"].append(_ik)
                    value["datas"][0].append(0)

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

                datas = bar_chart_data["datas"]
                if is_flow:
                    datas = [[util.trans_bit_to_mb(value) for value in lst] for lst in datas]

                self.report_tpl.set_item_data(page_idx, item_name, data=datas,
                                              category_names=category_names,
                                              # legend_names=legend_names
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
                cns = bar_chart_data["category_names"]
                lns = bar_chart_data["legend_names"]

                _catelog = dict(zip(cns, bar_chart_data["datas"][0]))
                _category = sorted(_catelog)
                _temp_arr = []

                for i in _category:
                    _temp_arr.append(_catelog[i])

                # fill data
                # tp = tuple(bar_chart_data["datas"][0])
                datas.append(tuple(_temp_arr))

                # legend names
                legend_names.extend(lns)

                # category
                category_names = _category

            if is_flow:
                datas = [[util.trans_bit_to_mb(value) for value in lst] for lst in datas]

            self.report_tpl.set_item_data(page_idx, elname, data=datas,
                                          category_names=category_names,
                                          # legend_names=legend_names
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
            self.report_tpl.set_item_data(page_idx, description_elname, content=description_intro)

        data = [(category_names[i], datas[i]) for i in range(len(category_names))]
        self.report_tpl.set_item_data(page_idx, elname, content=data)

    def report_draw_paragraph(self, page_idx, description_elname, description_intro):
        """
        自定义报告段落
        :param page_idx: 当前操作页面的 page index
        :param elname:  段落template对应的element name
        :param description_intro: 段落内容
        :return:
        """
        self.report_tpl.set_item_data(page_idx, description_elname, content=description_intro)


class ReportSetTimeOfCover(PDFReport):
    # 设置封面时间 Title
    PG_NUM = 0
    ELNAME = "Introduction"
    def __init__(self, report_template: PDFTemplateR):
        super(ReportSetTimeOfCover, self).__init__(report_template)
        self.set_page_idx(self.PG_NUM)
        self.set_time_of_cover()

    def set_time_of_cover(self):
        """封面时间为当前时间，格式为 年-月-日"""
        now_date = datetime.now().strftime("%Y-%m-%d")
        self.report_draw_paragraph(self.report_tpl_pg_num, self.ELNAME, now_date)


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

    TAB_CONFIG_MAP = {
        "1": {
            "page_name": "log_classify",
            "rule_id": "00",
            "search_index": "log*",
            "fmts": [],
            "all_fmts": ALL_FMTS,
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
    }

    def __init__(self, report_template: PDFTemplateR):
        super(ReportSenHost, self).__init__(report_template)
        self.set_page_idx(self.PG_NUM)
        self.items = {
            "pages": []
        }

    def add_items(self, items: dict):
        for tab in items["tab"]:
            tab_config = self.TAB_CONFIG_MAP[tab]
            tab_config["fmts"] = items["type"]
            self.items["pages"].append(tab_config)


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
                    f"""
                    探针主机网络管控报告报告
                    分析图：运行趋势、运行日志分布展示、探针组Top10、探针Top10
                    日志类型: {line_ret['legend_names']}
                    时间范围: {line_ret['category_names'][0]} 至 {line_ret['category_names'][-1]}
                    """
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
                    sensor_group_bar_ret,
                    grouping=True
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
        "SENSOR_IO",
        "SENSOR_RESOURCE_OVERLOAD",
        "SENSOR_SERVICE_FULL_LOAD",
        "SENSOR_TIME_ABNORMAL"
    ]
    ALL_VIOLATION_OTHER_FMTS = [
        "SENSOR_AUTORUN",
        "SENSOR_NET_SHART",
    ]

    TAB_CONFIG_MAP = {
        "1": {
            "page_name": "violation_define",
            "rule_id": "00",
            "search_index": "log*",
            "all_fmts": ALL_VIOLATION_TRIGGERED_FMTS,
            "fmts": ALL_VIOLATION_TRIGGERED_FMTS,
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
        "2": {
            "page_name": "log_classify",
            "rule_id": "00",
            "search_index": "log*",
            "all_fmts": ALL_VIOLATION_DETAIL_FMTS,
            "fmts": [],
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
        "3": {
            "page_name": "log_classify",
            "rule_id": "00",
            "search_index": "log*",
            "all_fmts": ALL_VIOLATION_OTHER_FMTS,
            "fmts": [],
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
        },
    }

    def __init__(self, report_template: PDFTemplateR):
        super(ReportSenSafe, self).__init__(report_template)
        # 设置 page num
        self.set_page_idx(2)
        self.items = {
            "pages": []
        }

    def add_items(self, items):

        for tab in items["tab"]:
            tab_config = self.TAB_CONFIG_MAP[tab]
            # 违规详情日志、其他安全日志需要传入 log FORMAT
            if tab == "2":
                tab_config["fmts"] = self.ALL_VIOLATION_DETAIL_FMTS
            elif tab == "3":
                tab_config["fmts"] = self.ALL_VIOLATION_OTHER_FMTS

            self.items["pages"].append(tab_config)

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
    TAB_CONFIG_MAP = {
        "1": {
            "page_name": "network_violation",
            "rule_id": "00",
            "search_index": "datamap_precompute*",
            "fmts": ["SENSOR_NETWORK_ABNORMAL"],
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
        "2": {
            "page_name": "netflow_violation",
            "rule_id": "00",
            "search_index": "log*",
            "fmts": ["SENSOR_NETWORK_FLOW"],
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
        "3": {
            "page_name": "sensor_netio",
            "rule_id": "00",
            "search_index": "log*",
            # "fmts": "SENSOR_NETIO",
            # "item_id": {
            #     "download": 0,
            #     "upload": 1,
            # },
            # "elname": {
            #     "upload": "sensor_netio_aver_upload_flow_line_chart",
            #     "download": "sensor_netio_aver_download_flow_line_chart"
            # }
        },
    }

    def __init__(self, report_template: PDFTemplateR):
        super(ReportSenNetwork, self).__init__(report_template)
        self.set_page_idx(self.PG_NUM)
        self.items = {
            "pages": []
        }

    def add_items(self, items):
        for tab in items["tab"]:
            tab_config = self.TAB_CONFIG_MAP[tab]

            # 上下行流量
            if tab == "3":
                # 上行流量
                if items["type"][0] == "1":
                    tab_config["item_id"] = 1
                    tab_config["elname"] = "sensor_netio_aver_upload_flow_line_chart"
                # 下行流量
                else:
                    tab_config["item_id"] = 0
                    tab_config["elname"] = "sensor_netio_aver_download_flow_line_chart"

            self.items["pages"].append(tab_config)

    def draw_page(self):
        """
        """
        for page in self.items["pages"]:

            if page["page_name"] == "sensor_netio":
                self.draw_netio_chart(page)
            else:
                self.draw_network_control_flow_chart(page)

    def draw_netio_chart(self, page):
        # for direction in ["upload", "download"]:
        upload_line_ret = self.making_data(chart_typ="line",
                                           page_name=page["page_name"],
                                           item_id=page["item_id"],
                                           search_index=page["search_index"],
                                           need_second=True)
        if upload_line_ret:
            datas = [[util.trans_bit_to_mb(_) for _ in upload_line_ret["datas"][0]],
                     [util.trans_bit_to_mb(_) for _ in upload_line_ret["second_datas"]]]
            # datas.append([util.trans_bit_to_mb(_) for _ in upload_line_ret["second_datas"]])
            legend_names = ["文件访问总量", "网络平均访问量"]
            self.report_draw_line(
                self.report_tpl_pg_num,
                elname=page["elname"],
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
    TYPE_CONFIG_MAP = {
        "SENSOR_OPEN_PORT": {
            "page": "open_port",
            "page_name": "trust",
            "rule_id": "00",
            "search_index": "log*",
            "fmts": ["SENSOR_OPEN_PORT"],
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
        "SENSOR_CREDIBLE": {
            "page": "safe_base",
            "page_name": "trust",
            "rule_id": "00",
            "search_index": "log*",
            "fmts": [],
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
    }

    def __init__(self, report_template: PDFTemplateR):
        super(ReportSenTrust, self).__init__(report_template)
        self.items = {
            "pages": []
        }

    def add_items(self, items: dict):
        if not items.get("type"):
            self.items["pages"].append(self.TYPE_CONFIG_MAP["SENSOR_OPEN_PORT"])
        else:
            type_config = self.TYPE_CONFIG_MAP["SENSOR_CREDIBLE"]
            type_config["fmts"] = items["type"]
            self.items["pages"].append(type_config)

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
    CONFIG = {
        "page_name": "critical_file",
        "rule_id": "00",
        "search_index": {
            "normal": "logstash*",
            "spe": "datamap*",
        },
        "fmts": ["SENSOR_FILESYSTEM"],
        "fmts_sensor_parse_file": ["SENSOR_FILEPARSE_LOG"],
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
            "file_content_key_heat_top10": "file_content_key_heat_top10",
        },
        "description_elname": {
        },
        "rule_uuid": {
            "line_rule_file": []
        },
        "top": {
            "file_name_top5": "5",
        }
    }

    def __init__(self, report_template: PDFTemplateR):
        super(ReportSenFile, self).__init__(report_template)
        self.set_page_idx(self.PG_NUM)
        self.items = {
            "pages": []
        }

    def add_items(self, items):
        self.CONFIG["rule_uuid"]["line_rule_file"] = items["rule_uuid"]
        self.items["pages"].append(self.CONFIG)

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
                                              rule_uuid=page["rule_uuid"]["line_rule_file"])

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
                                               rule_uuid=page["rule_uuid"]["line_rule_file"],
                                               top=page["top"]["file_name_top5"])

            if table_file_top5:
                self.report_draw_table(
                    self.report_tpl_pg_num,
                    elname=page["elname"]["bar_all_file"],
                    datas=table_file_top5["SENSOR_FILEPARSE_LOG"]["datas"][0],
                    category_names=table_file_top5["SENSOR_FILEPARSE_LOG"]["category_names"],
                )

            table_key_heat_top10 = self.making_data(chart_typ="bar",
                                                    fmts=page["fmts_sensor_parse_file"],
                                                    page_name=page["page_name"],
                                                    item_id=page["item_id"]["table_key_heat_top10"],
                                                    search_index=page["search_index"]["spe"],
                                                    rule_uuid=page["rule_uuid"]["line_rule_file"],
                                                    without_format=True
                                                    )

            util.pretty_print(table_key_heat_top10)

            if table_key_heat_top10:
                self.report_draw_table(
                    self.report_tpl_pg_num,
                    elname=page["elname"]["file_content_key_heat_top10"],
                    datas=table_key_heat_top10["SENSOR_FILEPARSE_LOG"]["datas"][0],
                    category_names=table_key_heat_top10["SENSOR_FILEPARSE_LOG"]["category_names"]
                )

            bar_group_ret = self.making_data(chart_typ="bar", fmts=page["fmts_sensor_parse_file"],
                                             page_name=page["page_name"],
                                             item_id=page["item_id"]["bar_sensor_group"],
                                             search_index=page["search_index"]["normal"],
                                             rule_uuid=page["rule_uuid"]["line_rule_file"],
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
                                             rule_uuid=page["rule_uuid"]["line_rule_file"],
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

    TYPE_CONFIG_MAP = {
        "USB": {
            "page_name": "file_operate",
            "rule_id": "00",
            "search_index": "datamap_precompute*",
            "fmts": [],
            "item_id": {
                "line": 0,  # 文件出入日志 - 统计数量
                "bar_sensors": 2,  # 文件出入日志 - 出入数量top10
                "bar_groups": 3,  # 文件出入日志 - 出入流量top10
            },
            "elname": {
                "file_operate_num_line_chart_USB": {
                    "chart_type": "line",
                    "item_id": 0,
                    "access_format": ["USB_OUT", "USB_IN",
                                      "SEC_USB_IN", "SEC_USB_OUT"],
                },
                "file_operate_flow_line_chart_USB": {
                    "chart_type": "line",
                    "item_id": 1,
                    "access_format": ["USB_OUT", "USB_IN",
                                      "SEC_USB_IN", "SEC_USB_OUT"],
                    "is_flow": True
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
                    "is_flow": True
                },
                "file_operate_sensor_num_top_USB": {
                    "chart_type": "bar",
                    "item_id": 2,
                    "access_format": [["SEC_USB_IN", "USB_IN"],
                                      ["SEC_USB_OUT", "USB_OUT"]],
                    "split_request": True,
                },
                "file_operate_sensor_flow_top_USB": {
                    "chart_type": "bar",
                    "item_id": 3,
                    "access_format": [["SEC_USB_IN", "USB_IN"],
                                      ["SEC_USB_OUT", "USB_OUT"]],
                    "split_request": True,
                    "is_flow": True
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
        "CD": {
            "page_name": "file_operate",
            "rule_id": "00",
            "search_index": "datamap_precompute*",
            "fmts": [],
            "item_id": {
                "line": 0,  # 文件出入日志 - 统计数量
                "bar_sensors": 2,  # 文件出入日志 - 出入数量top10
                "bar_groups": 3,  # 文件出入日志 - 出入流量top10
            },
            "elname": {
                "file_operate_num_line_chart_CD": {
                    "chart_type": "line",
                    "item_id": 0,
                    "access_format": ["CD_OUT", "CD_IN"],
                },
                "file_operate_flow_line_chart_CD": {
                    "chart_type": "line",
                    "item_id": 1,
                    "access_format": ["CD_OUT", "CD_IN"],
                    "is_flow": True
                },
                "file_operate_sensor_group_num_top_CD": {
                    "chart_type": "bar",
                    "item_id": 2,
                    "access_format": [["CD_IN"],
                                      ["CD_OUT"]],
                    "group": True,
                    "split_request": True,
                },
                "file_operate_sensor_group_flow_top_CD": {
                    "chart_type": "bar",
                    "item_id": 3,
                    "access_format": [["CD_IN"],
                                      ["CD_OUT"]],
                    "group": True,
                    "split_request": True,
                    "is_flow": True
                },
                "file_operate_sensor_num_top_CD": {
                    "chart_type": "bar",
                    "item_id": 2,
                    "access_format": [["CD_IN"],
                                      ["CD_OUT"]],
                    "split_request": True,
                },
                "file_operate_sensor_flow_top_CD": {
                    "chart_type": "bar",
                    "item_id": 3,
                    "access_format": [["CD_IN"],
                                      ["CD_OUT"]],
                    "split_request": True,
                    "is_flow": True
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
        "SHARE": {
            "page_name": "file_operate",
            "rule_id": "00",
            "search_index": "datamap_precompute*",
            "fmts": [],
            "item_id": {
                "line": 0,  # 文件出入日志 - 统计数量
                "bar_sensors": 2,  # 文件出入日志 - 出入数量top10
                "bar_groups": 3,  # 文件出入日志 - 出入流量top10
            },
            "elname": {
                "file_operate_num_line_chart_SHARE": {
                    "chart_type": "line",
                    "item_id": 0,
                    "access_format": ["SHARE_OUT", "SHARE_IN"],
                },
                "file_operate_flow_line_chart_SHARE": {
                    "chart_type": "line",
                    "item_id": 1,
                    "access_format": ["SHARE_OUT", "SHARE_IN"],
                    "is_flow": True
                },
                "file_operate_sensor_group_num_top_SHARE": {
                    "chart_type": "bar",
                    "item_id": 2,
                    "access_format": [["SHARE_IN"],
                                      ["SHARE_OUT"]],
                    "group": True,
                    "split_request": True,
                },
                "file_operate_sensor_group_flow_top_SHARE": {
                    "chart_type": "bar",
                    "item_id": 3,
                    "access_format": [["SHARE_IN"],
                                      ["SHARE_OUT"]],
                    "group": True,
                    "split_request": True,
                    "is_flow": True
                },
                "file_operate_sensor_num_top_SHARE": {
                    "chart_type": "bar",
                    "item_id": 2,
                    "access_format": [["SHARE_IN"],
                                      ["SHARE_OUT"]],
                    "split_request": True,
                },
                "file_operate_sensor_flow_top_SHARE": {
                    "chart_type": "bar",
                    "item_id": 3,
                    "access_format": [["SHARE_IN"],
                                      ["SHARE_OUT"]],
                    "split_request": True,
                    "is_flow": True
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
        "PRINT": {
            "page_name": "file_operate",
            "rule_id": "00",
            "search_index": "datamap_precompute*",
            "fmts": [],
            "item_id": {
                "line": 0,  # 文件出入日志 - 统计数量
                "bar_sensors": 2,  # 文件出入日志 - 出入数量top10
                "bar_groups": 3,  # 文件出入日志 - 出入流量top10
            },
            "elname": {
                "file_operate_num_line_chart_PRINT": {
                    "chart_type": "line",
                    "item_id": 0,
                    "access_format": ["PRINT"],
                },
                "file_operate_sensor_group_num_top_PRINT": {
                    "chart_type": "bar",
                    "item_id": 2,
                    "access_format": ["PRINT"],
                    "group": True,
                    "split_request": False,
                },
                "file_operate_sensor_num_top_PRINT": {
                    "chart_type": "bar",
                    "item_id": 2,
                    "access_format": ["PRINT"],
                    "split_request": False,
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
        "EXTERNAL": {
            "page_name": "file_operate",
            "rule_id": "00",
            "search_index": "datamap_precompute*",
            "fmts": [],
            "item_id": {
                "line": 0,  # 文件出入日志 - 统计数量
                "bar_sensors": 2,  # 文件出入日志 - 出入数量top10
                "bar_groups": 3,  # 文件出入日志 - 出入流量top10
            },
            "elname": {
                "file_operate_num_line_chart_EXTERNAL": {
                    "chart_type": "line",
                    "item_id": 0,
                    "access_format": ["EXTERNAL"],
                },
                "file_operate_flow_line_chart_EXTERNAL": {
                    "chart_type": "line",
                    "item_id": 1,
                    "access_format": ["EXTERNAL"]
                },
                "file_operate_sensor_group_num_top_EXTERNAL": {
                    "chart_type": "bar",
                    "item_id": 2,
                    "access_format": ["EXTERNAL"],
                    "group": True,
                    "split_request": False,
                },
                "file_operate_sensor_group_flow_top_EXTERNAL": {
                    "chart_type": "bar",
                    "item_id": 3,
                    "access_format": ["EXTERNAL"],
                    "group": True,
                    "split_request": False,
                    "is_flow": True,
                },
                "file_operate_sensor_num_top_EXTERNAL": {
                    "chart_type": "bar",
                    "item_id": 2,
                    "access_format": ["EXTERNAL"],
                    "split_request": False,
                },
                "file_operate_sensor_flow_top_EXTERNAL": {
                    "chart_type": "bar",
                    "item_id": 3,
                    "access_format": ["EXTERNAM"],
                    "split_request": "False",
                    "is_flow": True,
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
    }

    def __init__(self, report_template: PDFTemplateR):
        super(ReportFileOperation, self).__init__(report_template)
        self.set_page_idx(self.PG_NUM)
        self.items = {
            "pages": []
        }

    def add_items(self, items):
        self.items["pages"].append(
            self.TYPE_CONFIG_MAP[items["type"][0]]
        )

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

                print(json.dumps(merged_data, indent=4, ensure_ascii=False))

                if v["chart_type"] == "line":
                    # drawline
                    datas, legend_names, category_names = r['datas'], r['legend_names'], r['category_names']

                    if v.get("is_flow"):
                        datas = [[util.trans_bit_to_mb(value) for value in lst] for lst in datas]

                    self.report_draw_line(self.report_tpl_pg_num, element_name, datas,
                                          legend_names=legend_names,
                                          category_names=category_names)
                elif v["chart_type"] == "bar":
                    # drawbar

                    _group = True if len(merged_data.keys()) > 1 else False
                    self.report_draw_bar1(self.report_tpl_pg_num,
                                          elname=element_name,
                                          bar_infos=merged_data,
                                          group_bar=_group,
                                          is_flow=v.get("is_flow"))

                elif v["chart_type"] == "pie":
                    # drawpie
                    raise NotImplemented
                else:
                    raise ValueError("chart type not in [line, bar, pie].")


class ReportRunLog(PDFReport):
    """运行日志"""
    PG_NUM = 8
    TAB_CONFIG_MAP = {
        "1": {
            "page_name": "sensor_client",
            "rule_id": "00",
            "search_index": "log*",
            "fmts": ["SENSOR_POLICY_UPDATE_DAILY"],
            "elname": {
                "sensor_client_running_state_line_chart": {
                    "item_id": 0,
                    "chart_typ": "line"
                },
                "aver_online_sensor_group_top10": {
                    "item_id": 1,
                    "chart_typ": "bar",
                    "grouping": True,
                },
                "aver_offline_sensor_group_top10": {
                    "item_id": 2,
                    "chart_typ": "bar",
                    "grouping": True,
                }
            }
        },
        "2": {
            "page_name": "sensor_client",
            "rule_id": "00",
            "search_index": "log*",
            "fmts": ["SENSOR_POLICY_UPDATE_DAILY"],
            "elname": {
                "policy_change_log": {
                    "item_id": 3,
                    "chart_typ": "line"
                }
            }
        }
    }

    def __init__(self, report_template: PDFTemplateR):
        super(ReportRunLog, self).__init__(report_template)
        self.set_page_idx(self.PG_NUM)
        self.items = {
            "pages": []
        }

    def add_items(self, items: dict):
        tab_config = self.TAB_CONFIG_MAP[items["tab"][0]]
        self.items["pages"].append(tab_config)

    def draw_page(self):
        for page in self.items["pages"]:
            for elname in page["elname"]:

                _grouping = True if page["elname"][elname].get("grouping") else False

                chart_ret = self.making_data(
                    chart_typ=page["elname"][elname]["chart_typ"], fmts=page["fmts"],
                    page_name=page["page_name"], item_id=page["elname"][elname]["item_id"],
                    search_index=page["search_index"], grouping=_grouping
                )

                util.pretty_print(chart_ret)
                if elname == "sensor_client_running_state_line_chart":
                    # 该图数据为折线图格式，但展示时使用柱状图
                    page["elname"][elname]["chart_typ"] = "bar"
                    chart_ret = {
                        "SENSOR_POLICY_UPDATE_DAILY": chart_ret
                    }
                elif elname == "policy_change_log":
                    # 策略未更新探针数量只取列表的第一个元素
                    chart_ret["datas"] = [chart_ret["datas"][0]]
                    chart_ret["legend_names"] = ["策略未更新探针数量"]

                if page["elname"][elname]["chart_typ"] == "line":
                    self.report_draw_line(
                        self.report_tpl_pg_num,
                        elname=elname,
                        datas=chart_ret["datas"],
                        category_names=chart_ret["category_names"],
                        legend_names=chart_ret["legend_names"]
                    )

                elif page["elname"][elname]["chart_typ"] == "bar":
                    self.report_draw_bar(
                        self.report_tpl_pg_num,
                        elname_prefix=elname,
                        bar_infos=chart_ret
                    )

                else:
                    raise KeyError("chart type is not in ('line', 'bar')")

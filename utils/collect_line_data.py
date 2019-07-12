from utils import constant
from utils import util
from datetime import datetime
from datetime import timedelta


def collect_data_from_es(payload: dict, days_interval: int, start_time_datetime: datetime) -> tuple:
    # 通过payload及时间参数，获取ES日志，并清洗
    # 返回折线图横坐标、纵坐标、折线标签数据
    es_log_data = util.post_mrule(payload)
    # util.pretty_print(es_log_data)

    # 统计数据
    chart_data = util.init_data_for_PDF(days_interval)
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

        value_index = (log_time_datetime - start_time_datetime).days

        # 折线图 多条线， 每条线单独请求
        if log_format is None:
            log_format = "UNKNOW_FORMAT"

        chart_data[log_format][value_index] += value

    # 获取折线图横坐标数据
    category_names = [
        util.datetime_to_category_time(start_time_datetime + timedelta(int(_)))
        for _ in range(days_interval + 1)
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


def collect_line_data_for_draw(payload: dict) -> tuple:
    """通过payload获取日志，进行清洗并返回
    :param payload: ES 日志post 参数
    :return:
    """
    start_time_datetime = util.payload_time_to_datetime(payload["start_time"])
    end_time_datetime = util.payload_time_to_datetime(payload["end_time"])
    days_interval = (end_time_datetime - start_time_datetime).days

    # datas, legend_names, category_names
    return collect_data_from_es(payload, days_interval, start_time_datetime)

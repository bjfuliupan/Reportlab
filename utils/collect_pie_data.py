from utils import constant
from utils import util
from datetime import datetime
from datetime import timedelta


def collect_data_from_es(payload: dict) -> tuple:
    # 通过payload及时间参数，获取ES日志，并清洗
    # 返回饼图日志类别、日志数量
    es_log_data = util.post_mrule(payload)
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


def collect_pie_data_for_draw(payload: dict) -> tuple:
    """通过payload获取日志，进行清洗并返回
    :param payload: ES 日志 POST 参数
    :return:
    """
    # start_time_datetime = util.payload_time_to_datetime(payload["start_time"])
    # end_time_datetime = util.payload_time_to_datetime(payload["end_time"])
    # days_interval = (end_time_datetime - start_time_datetime).days

    return collect_data_from_es(payload)


def test_case():
    payload = {
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
        }
    datas, category_names = collect_pie_data_for_draw(payload)
    print(datas, "\n", category_names)


if __name__ == "__main__":
    test_case()

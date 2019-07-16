from utils import util
from utils import constant
import copy
import collections


def collect_bar_data_for_draw(base_payload: dict, log_formats: list, sort_flag=True, limit_num=10):
    """ 通过payload获取日志，进行清洗并返回
    :param base_payload: payload的FORMAT缺省，使用log_formats字段顺序填充
    :param log_formats: 探针日志列表，每种日志类型一个柱状图
    :param sensor_id_group_mapping: 探针-探针组映射关系
    :param sort_flag: 是否排序，支持倒序
    :param limit_num: 最大展示数量
    :return:
    """
    data_for_draw = {}

    for log_format in log_formats:
        # 生成payload
        payload = copy.deepcopy(base_payload)
        payload["data_scope"]["FORMAT.raw"] = [log_format]

        # 获取数据
        es_log_data = util.post_mrule(payload)
        # 请求结果为空
        if not es_log_data["result"]:
            continue

        # 数据统计
        data_for_draw_with_sensor = util.init_data_for_pdf_with_default_int()
        for sensor_id_dict, value, *_ in es_log_data["result"]:
            sensor_id = sensor_id_dict[0]["SENSOR_ID.raw"]
            data_for_draw_with_sensor[sensor_id] += value

        if sort_flag:
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

        data_for_draw[log_format] = {
            "data": data,
            "category_names": category_names,
            "legend_names": legend_names,
        }

    return data_for_draw


def test_case():
    payload = {
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
        }
    log_formats = [
            "SENSOR_SERVICECHANGE",
            "SENSOR_HARDWARE_CHANGE",
            "SENSOR_MULTIPLE_OS_BOOT",
            "SENSOR_SAFEMODE_BOOT",
            "SENSOR_VM_INSTALLED",
            "SENSOR_SOFTWARE_CHANGE",
            "SENSOR_INFO_WORK_TIME"
        ]


if __name__ == "__main__":
    test_case()
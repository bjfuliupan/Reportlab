import datetime
import collections
import json
import requests


url = "http://192.168.8.60:8002"


GROUP_SENSORS_MAPPING = {
    "无分组": [
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
        "WSR0001",
    ],
    "cnwang_laptop": ["WIN0010"],
    "FAE": ["WIN0003"],
    "demo": ["WIN0009"],
    "hjn-demo": ["WIN0007"],
}


SENSOR_GROUP_MAPPING = {
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
                        "WIN0010": "cnwang_laptop",
                        "WIN0003": "FAE",
                        "WIN0009": "demo",
                        "WIN0007": "hjn-demo"
                    }


def datetime_to_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def payload_time_to_str(payload_time):
    return post_time_to_datetime(payload_time).strftime("%Y-%m-%d")


def post_time_to_datetime(post_time: str) -> datetime:
    """将POST数据中的时间转换为datetime格式"""
    return datetime.datetime.strptime(post_time, "%Y-%m-%dT%H:%M:%S.000")


def time_with_Z_to_datetime(z_time: str) -> datetime:
    return datetime.datetime.strptime(z_time, "%Y-%m-%dT%H:%M:%S.000Z") + \
           datetime.timedelta(hours=8)


def init_data_for_PDF(days_interval: int) -> collections.defaultdict:
    # 初始化图数据，初始list中元素数量为 end_time - start_time + 1
    return collections.defaultdict(lambda: [0] * (days_interval + 1))


def post_log_rule(payload: json) -> tuple:
    response = requests.post(url, data=json.dumps(payload))
    return response.status_code, json.loads(response.content)


if __name__ == "__main__":
    print(init_data_for_PDF(10))
    print(init_data_for_PDF(10)[1])


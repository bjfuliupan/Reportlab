from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import select

from utils.config import SessionFactory
from utils.config import engine
from utils.model_465_rel import TabSensorGroup
from utils.model_465_rel import TabSensorReport
from utils.model_465_rel import TabSensorReportDetail
from utils.model_465_rel import t_tab_sensor_group_relation


def get_report_info(report_uuid: str) -> tuple:
    result = {}
    ok = False

    session = SessionFactory()

    try:
        _query = session.query(
            TabSensorReport.report_name,
            TabSensorReport.report_format,
            TabSensorReport.data_scope,
            TabSensorReport.sensor_group_ids,
            TabSensorReport.send_email,
            TabSensorReport.send_date,
            TabSensorReport.timed,
        ).filter(
            TabSensorReport.uuid == report_uuid,
        ).all()

        for row in _query:
            result = {
                "report_name": row.report_name,
                "report_format": row.report_format,
                "data_scope": row.data_scope,
                "sensor_group_ids": row.sensor_group_ids,
                "send_email": row.send_email,
                "send_date": row.send_date,
                "timed": row.timed,
            }

        ok = True
    except Exception as e:
        print(e)
    finally:
        if session:
            session.close()
    return ok, result


def get_all_report_info() -> tuple:
    result = []
    ok = False

    session = SessionFactory()

    try:
        _query = session.query(
            TabSensorReport
        ).all()

        if _query:
            result = [_.to_dict() for _ in _query]

        ok = True
    except Exception as e:
        result = repr(e)
    finally:
        if session:
            session.close()
    return ok, result


def get_report_detail_info_by_id(report_id: str) -> tuple:
    result = []
    ok = False

    session = SessionFactory()

    try:
        _query = session.query(
            TabSensorReportDetail.custom_name,
            TabSensorReportDetail.page_source_name,
            TabSensorReportDetail.page_source_url,
            TabSensorReportDetail.sort_number,
        ).filter(
            TabSensorReportDetail.uuid == report_id,
        ).all()

        if _query:
            for row in _query:
                result.append(
                    {
                        "custom_name": row.custom_name,
                        "page_source_name": row.page_source_name,
                        "page_source_url": row.page_source_url,
                        "sort_number": row.sort_number,
                    }
                )

        ok = True
    except Exception as e:
        print(e)
    finally:
        if session:
            session.close()
    return ok, result


def get_group_sensor_map(group_ids: str):
    ok = False
    sensor_id_group_mapping = {}

    conn = None

    try:
        conn = engine.connect()
        _query = conn.execute(
            select(
                [
                    TabSensorGroup.name,
                    t_tab_sensor_group_relation.c.sensor_id
                ]
            ).where(
                and_(
                    func.find_in_set(
                        t_tab_sensor_group_relation.c.group_id,
                        group_ids
                    ),
                    TabSensorGroup.id == t_tab_sensor_group_relation.c.group_id
                )
            )
        ).fetchall()

        for row in _query:
            sensor_id_group_mapping[row[1]] = row[0]

        ok = True
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()

    return ok, sensor_id_group_mapping


def get_all_report_uuid() -> tuple:
    result = []
    ok = False

    session = SessionFactory()

    try:
        _query = session.query(
            TabSensorReport.uuid
        ).all()

        if _query:
            result = [_.uuid for _ in _query]

        ok = True
    except Exception as e:
        print(e)
        result = repr(e)
    finally:
        if session:
            session.close()
    return ok, result

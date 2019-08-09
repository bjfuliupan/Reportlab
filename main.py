import json

import tornado
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from tornado.options import define
from tornado.options import options

from report import gen_report
from utils import storage

define("port", default=21001, help="run on the given port", type=int)


class DefaultErrorHandler(tornado.web.ErrorHandler):
    def data_received(self, chunk):
        pass

    def write_error(self, status_code, **kwargs):
        self.set_status(status_code)
        self.write("<h1>404 Error!</h1>")
        self.finish()


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.scheduler = self.settings.get("scheduler")

    def data_received(self, chunk):
        pass


class ReportHandler(BaseHandler):
    def __init__(self, *args, **kwargs):
        super(ReportHandler, self).__init__(*args, **kwargs)

    def cook_report_uuid(self, scheduler: BackgroundScheduler, report_uuid: str,
                         action="add") -> None:
        """
        :param scheduler:
        :param report_uuid:
        :param action: add/mod/del
        :return:
        """

    def cook_body(self, action="add"):
        result = {
            "success": False,
            "msg": ""
        }
        try:
            body = json.loads(self.request.body)
            report_uuid = body["report_uuid"]

            if action == "del":
                self.scheduler.remove_job(job_id=report_uuid)

            else:
                send_date = body["send_date"]
                cron_trigger = CronTrigger.from_crontab(send_date)

                if action == "add":
                    self.scheduler.add_job(func=gen_report, trigger=cron_trigger,
                                           kwargs=body, id=report_uuid)

                elif action == "mod":
                    self.scheduler.modify_job(job_id=report_uuid, trigger=cron_trigger,
                                              kwargs=body)

                else:
                    raise ValueError(f"request scheduler action type must in ('add', 'mod', 'del')")

            result["success"] = True
        except Exception as e:
            result["msg"] = repr(e)
            self.set_status(500)
        finally:
            self.write(json.dumps(result))

    async def post(self, *args, **kwargs):
        self.cook_body(action="add")

    async def put(self, *args, **kwargs):
        self.cook_body(action="mod")

    async def delete(self, *args, **kwargs):
        self.cook_body(action="del")


routes = [
    ("/reportpdf", ReportHandler),
]


class ReportApp(tornado.web.Application):
    def __init__(self, scheduler):
        settings = dict(
            default_handler_class=DefaultErrorHandler,
            default_handler_args={"status_code": 404},
            gzip=True,
            debug=False,
            cookie_secret='3hJxpjy/T/0JHy0P7eCgt/zhDUbLEUwImtdmKT9i8RU=',
            scheduler=scheduler
        )

        tornado.web.Application.__init__(self, routes, **settings)


def cook_report_uuid(scheduler: BackgroundScheduler, report_uuid: str,
                     action="add") -> None:
    """
    :param scheduler:
    :param report_uuid:
    :param action: add/mod/del
    :return:
    """
    print(f"cook report uuid, scheduler: {scheduler}, report_uuid: {report_uuid}"
          f"action: {action}")
    if action == "del":
        scheduler.remove_job(job_id=report_uuid)

    ok, report_info = storage.get_report_info(report_uuid)
    print(f"report_info: {report_info}")
    if not ok:
        print(f"Fail to get report info for uuid: {report_uuid}"
              f"errmsg: {report_info}")
        return

    ok, page_info = storage.get_report_detail_info_by_id(report_uuid)
    if not ok:
        print(f"Fail to get report detail info for uuid: {report_uuid}, "
              f"errmsg: {page_info}")
        return

    # week/month
    sensor_group_ids = report_info["sensor_group_ids"]

    # 获取探针、探针组信息
    ok, sensor_id_group_mapping = storage.get_group_sensor_map(sensor_group_ids)
    if not ok:
        print(f"fail to get sensor_groups by id: {sensor_group_ids}")
        return

    sensors = list(sensor_id_group_mapping.keys())

    cron = CronTrigger.from_crontab(report_info["send_date"])
    _report_params = {
        "report_name": report_info["report_name"],
        "report_format": report_info["report_format"],
        "timed": report_info["timed"],
        "data_scope": report_info["data_scope"],
        "sensor_ids": sensors,
        "sensor_id_group_mapping": sensor_id_group_mapping,
        "page_info": page_info,
        "send_mail": report_info["send_email"],
    }

    if action == "mod":
        scheduler.modify_job(job_id=report_uuid, trigger=cron,
                             kwargs=_report_params)

    elif action == "add":
        gen_report(**_report_params)
        scheduler.add_job(func=gen_report, trigger=cron,
                          kwargs=_report_params, id=report_uuid)

    else:
        raise ValueError("action must in ('add', 'del', 'mod')")


def init_scheduler_infomation(scheduler):
    """
    :param scheduler:
    :return:
    """
    ok, all_report_uuids = storage.get_all_report_uuid()
    if not ok:
        raise RuntimeError(f"Fail to get reports info: {all_report_uuids}")
    if not all_report_uuids:
        print("No reports info in db")
        return

    for report_uuid in all_report_uuids:
        cook_report_uuid(scheduler=scheduler, report_uuid=report_uuid, action="add")


if __name__ == "__main__":
    back_scheduler = BackgroundScheduler()
    back_scheduler.start()

    init_scheduler_infomation(back_scheduler)

    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(
        ReportApp(back_scheduler),
        xheaders=True
    )

    http_server.listen(options.port, address="127.0.0.1")
    tornado.ioloop.IOLoop.instance().start()

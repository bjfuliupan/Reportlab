class LogConstant:
    FORMAT_DETAIL_MAPPING = {
        "SENSOR_INFO_WORK_TIME": "开关机记录日志",
        "SENSOR_INFO_SYS_LOG": "探针系统日志",
        "SENSOR_USER": "用户信息日志",
        "SENSOR_FILESYSTEM": "文件访问日志",
        "SENSOR_REGISTRY": "注册表访问日志",
        "SENSOR_NETIO": "网络访问日志",
        "SENSOR_IO": "外设操作日志",
        "SENSOR_INPUT_ACTIVITY": "探针绩效日志",
        # "SENSOR_ACTIVITY": "探针绩效日志",  # SENSOR_INPUT_ACTIVITY在后台清洗后，重写为SENSOR_ACTIVITY
        "SENSOR_OUTLOOK": "邮件审计日志",
        "SENSOR_PRINT": "打印审计日志",
        "SENSOR_CDBURN": "光盘刻录审计日志",
        "SENSOR_SERVICERUN": "服务项运行日志",
        "SENSOR_USER_INFO": "用户信息采集日志",
        "SENSOR_ACCOUNT_AUDIT": "系统账户监控与审计日志",
        "SENSOR_NET_SHARE": "网络共享日志",
        "SENSOR_RESOURCE_MONITOR": "系统资源监控日志",
        "SENSOR_SAFEMODE_BOOT": "安全模式登陆日志",
        "SENSOR_MULTIPLE_OS_BOOT": "多操作系统安装日志",
        "SENSOR_VM_INSTALLED": "虚拟机安装日志",
        "SENSOR_PORT_MONITOR": "开放端口监控日志",
        "SENSOR_AUTORUN": "自启动项变更日志",
        "SENSOR_CURRENT_AUTORUN": "当前自启动项日志",
        "SENSOR_CURRENT_SERVICE": "当前系统服务项日志",
        "SENSOR_ARP_SCAN": "ARP扫描日志",
        "SENSOR_PC_FRACTION": "PC得分日志",
        "SENSOR_RECEPTION_PROCESS": "前台进程活动日志",
        "SENSOR_SERVICECHANGE": "服务变更日志",
        "SENSOR_WORK_TIME": "工作时间日志",
        "SENSOR_HARDWARE_CHANGE": "硬件变更日志",
        "SENSOR_SOFTWARE_CHANGE": "软件变更日志",
        "SENSOR_PORT_CONNECT": "常用端口连接日志",
        "SENSOR_SERVICE_FULL_LOAD": "服务程序满负荷运行日志",
        "SENSOR_NET_CONNECTION": "网络访问违规日志",
        "SENSOR_RESOURCE_OVERLOAD": "资源使用超负荷日志",
        "SENSOR_ANTIVIRUS_OUTDATE": "杀毒软件未安装未更新日志",
        "SENSOR_ANTIVIRUS_STATUS": "杀毒软件状态日志",
        "SENSOR_SERVICE_STOP": "关键服务未启动日志",
        "SENSOR_REG_MODIFY": "注册表关键位置被修改日志",
        "SENSOR_TIME_ABNORMAL": "客户端时间异常日志",
        "SENSOR_FLOW_ABNORMAL": "进程流量异常日志",
        "SENSOR_HOTFIX_STATUS": "补丁更新状态日志",
        "SENSOR_NETWORK_ABNORMAL": "服务器/程序网络使用异常日志",
        "SENSOR_NETWORK_FLOW": "服务器/程序流量使用异常日志",
        # "SENSOR_ALARM_MSG": "违规定义日志",
        "SENSOR_CURRENT_AUTORUN_DAILY": "主机服务运行日志",
        # "SENSOR_FILEPARSE_LOG": "关键文件分析日志",
        # "SENSOR_FILESYSYTEM_MERGE": "文件合并日志",
        # "SENSOR_POLICY_UPDATE_DAILY": "探针策略更新日志",
        "SENSOR_OPEN_PORT": "端口开放管理日志",
        "SENSOR_CREDIBLE_APP": "可信应用日志",
        "SENSOR_CREDIBLE_NETWORK": "可信网络日志",
        "SENSOR_CREDIBLE_PORT": "可信端口日志",
        "SENSOR_CREDIBLE_DATA": "可信数据日志",
        "SENSOR_PSYSTEM_FILE": "Linux系统应用保护日志",
        "SENSOR_ALARM_MSG": "探针离线报警",
        "SENSOR_NET_SHART": "网络共享日志",
        "SENSOR_POLICY_UPDATE_DAILY": "策略更新日志",
        "USB_IN": "U盘拷入",
        "USB_OUT": "U盘拷出",
        "SEC_USB_IN": "安全U盘拷入",
        "SEC_USB_OUT": "安全U盘拷出",
        "CD_IN": "CD拷入",
        "CD_OUT": "CD拷出",
        "SHARE_IN": "共享服务器拷入",
        "SHARE_OUT": "共享服务器拷出",
        "PRINT": "打印",
        "EXTERNAL": "外部互传",
        "online": "在线",
        "offline": "离线",
    }

    CATAEGORY_TIME_FORMAT = "%Y-%m-%d"

    ES_LOG_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"

    PAYLOAD_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000"


class Case:
    report = {
        "eb318a1caeb411e9b4740242edef7f35": {
            "report_name": "test",
            "report_format": "pdf",
            "timed": 1,
            "send_date": "0 * * * 1",
            "data_scope": "week",
            "sensor_group_ids": "",
            "send_mail": "",
            "update_time": "2019-07-26 11:05:33",
            "create_time": "2019-07-26 11:05:33"
        }
    }

    report_detail = {
        "eb318a1caeb411e9b4740242edef7f35": [
            {
                "custom_name": "host",
                "page_source_name": "主机运行日志",
                "page_source_url": "/host_log?"
                                   "tab=1&"
                                   "type=SENSOR_MULTIPLE_OS_BOOT,SENSOR_VM_INSTALLED,SENSOR_INFO_WORK_TIME,"
                                   "SENSOR_SOFTWARE_CHANGE,SENSOR_HARDWARE_CHANGE,SENSOR_SERVICECHANGE,"
                                   "SENSOR_SAFEMODE_BOOT",
                "sort_number": 0,
            },
            {
                "custom_name": "123",
                "page_source_name": "违规定义日志",
                "page_source_url": "/host_security_log?tab=1",
                "sort_number": 1,
            },
            {
                "custom_name": "111",
                "page_source_name": "违规详情日志",
                "page_source_url": "/host_security_log?tab=2",
                "sort_number": 2,
            },
            {
                "custom_name": "222",
                "page_source_name": "其他安全日志",
                "page_source_url": "/host_security_log?tab=3",
                "sort_number": 3,
            },
            {
                "custom_name": "访问管控策略日志",
                "page_source_name": "访问管控策略日志",
                "page_source_url": "/network_isolation_log?tab=1",
                "sort_number": 4,
            },
            {
                "custom_name": "流量管控策略日志",
                "page_source_name": "流量管控策略日志",
                "page_source_url": "/network_isolation_log?tab=2",
                "sort_number": 5,
            },
            {
                "custom_name": "平均流量统计",
                "page_source_name": "平均流量统计",
                "page_source_url": "/network_isolation_log?tab=3&type=1",
                "sort_number": 5,
            },
            {
                "custom_name": "平均流量统计",
                "page_source_name": "平均流量统计",
                "page_source_url": "/network_isolation_log?tab=3&type=2",
                "sort_number": 6,
            },
            {
                "custom_name": "端口开放管理日志",
                "page_source_name": "端口开放管理日志",
                "page_source_url": "/port_log?",
                "sort_number": 7,
            },
            {
                "custom_name": "应用安全基线日志",
                "page_source_name": "应用安全基线日志",
                "page_source_url": "/baseline_log?&type=SENSOR_CREDIBLE_APP",
                "sort_number": 8,
            },
            # {
            #     "custom_name": "应用安全基线日志",
            #     "page_source_name": "应用安全基线日志",
            #     "page_source_url": "/baseline_log?&type=SENSOR_CREDIBLE_NETWORK",
            #     "sort_number": 9,
            # },
            # {
            #     "custom_name": "应用安全基线日志",
            #     "page_source_name": "应用安全基线日志",
            #     "page_source_url": "/baseline_log?&type=SENSOR_CREDIBLE_PORT",
            #     "sort_number": 10,
            # },
            # {
            #     "custom_name": "应用安全基线日志",
            #     "page_source_name": "应用安全基线日志",
            #     "page_source_url": "/baseline_log?&type=SENSOR_CREDIBLE_DATA",
            #     "sort_number": 11,
            # },
            # {
            #     "custom_name": "应用安全基线日志",
            #     "page_source_name": "应用安全基线日志",
            #     "page_source_url": "/baseline_log?&type=SENSOR_CREDIBLE_FILE",
            #     "sort_number": 12,
            # },
            # {
            #     "custom_name": "关键文件分析日志",
            #     "page_source_name": "关键文件分析日志",
            #     "page_source_url": "/key_file_log?",
            #     # TODO: 从tab_file_analysis获取全部uuid
            #     "uuid": ["8b79218ea23111e996490cc47ab4d1a4"],
            #     "sort_number": 13,
            # },
            {
                "custom_name": "文件出入日志",
                "page_source_name": "文件"
                                    "出入日志",
                "page_source_url": "/file_log?&type=USB",
                "sort_number": 14,
            },
            {
                "custom_name": "文件出入日志",
                "page_source_name": "文件出入日志",
                "page_source_url": "/file_log?&type=CD",
                "sort_number": 15,
            },
            {
                "custom_name": "文件出入日志",
                "page_source_name": "文件出入日志",
                "page_source_url": "/file_log?&type=SHARE",
                "sort_number": 16,
            },
            {
                "custom_name": "文件出入日志",
                "page_source_name": "文件出入日志",
                "page_source_url": "/file_log?&type=PRINT",
                "sort_number": 17,
            },
            {
                "custom_name": "文件出入日志",
                "page_source_name": "文件出入日志",
                "page_source_url": "/file_log?&type=EXTERNAL",
                "sort_number": 18,
            },
            {
                "custom_name": "运行日志",
                "page_source_name": "运行日志",
                "page_source_url": "/zmw_log?tab=1",
                "sort_number": 19,
            },
        ]
    }
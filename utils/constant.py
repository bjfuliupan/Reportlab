

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
        "SENSOR_ALARM_MSG": "违规定义日志",
        "SENSOR_CURRENT_AUTORUN_DAILY": "主机服务运行日志",
    }

    CATAEGORY_TIME_FORMAT = "%Y-%m-%d"

    ES_LOG_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"

    PAYLOAD_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000"
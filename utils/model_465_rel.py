# coding: utf-8
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import text
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import SmallInteger
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy import Text
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql.types import BIT
from sqlalchemy.dialects.mysql.enumerated import ENUM
from sqlalchemy.orm import mapper
from datetime import datetime

from utils.config import DB_BASE

metadata = DB_BASE.metadata


class BaseAttach(object):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    

class SsBasicMenu(BaseAttach, DB_BASE):
    __tablename__ = 'ss_basic_menus'

    menu_id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, nullable=False, server_default=FetchedValue())
    name = Column(String(50, 'utf8_bin'), nullable=False)
    path = Column(String(255, 'utf8_bin'), nullable=False)
    order = Column(Integer, server_default=FetchedValue())
    enable = Column(Integer, server_default=FetchedValue())
    description = Column(String(255, 'utf8_bin'))

    roles = relationship('SsBasicRole', secondary='ss_role_menu_relation', backref='ss_basic_menus')


class SsBasicRole(BaseAttach, DB_BASE):
    __tablename__ = 'ss_basic_roles'

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(40, 'utf8_bin'))
    description = Column(String(200, 'utf8_bin'))
    enable = Column(Integer, server_default=FetchedValue())
    is_default = Column(Integer, server_default=FetchedValue())
    parent_id = Column(Integer, server_default=FetchedValue())
    parent_ids = Column(String(1000, 'utf8_bin'))

    users = relationship('SsBasicUser', secondary='ss_user_role_relation', backref='ss_basic_roles')


class SsBasicUser(BaseAttach, DB_BASE):
    __tablename__ = 'ss_basic_users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(80, 'utf8_bin'))
    real_name = Column(String(40, 'utf8_bin'))
    department = Column(String(256, 'utf8_bin'))
    phone = Column(String(20, 'utf8_bin'))
    email = Column(String(200, 'utf8_bin'))
    password = Column(String(256, 'utf8_bin'))
    enable = Column(Integer, server_default=FetchedValue())
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    update_time = Column(DateTime)
    last_change_password_time = Column(DateTime)
    password_error_times = Column(Integer, server_default=FetchedValue())
    last_lock_time = Column(DateTime)
    wechat_no = Column(String(30, 'utf8_bin'))


t_ss_role_menu_relation = Table(
    'ss_role_menu_relation', metadata,
    Column('role_id', ForeignKey('ss_basic_roles.role_id', ondelete='CASCADE'), nullable=False, index=True),
    Column('menu_id', ForeignKey('ss_basic_menus.menu_id', ondelete='CASCADE'), nullable=False, index=True)
)


t_ss_sensor_user_group_relation = Table(
    'ss_sensor_user_group_relation', metadata,
    Column('sensor_user_id', ForeignKey('ss_sensor_users.id', ondelete='CASCADE'), primary_key=True, nullable=False, unique=True),
    Column('group_id', ForeignKey('ss_sensor_user_groups.group_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class SsSensorUserGroup(BaseAttach, DB_BASE):
    __tablename__ = 'ss_sensor_user_groups'

    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(384, 'utf8_bin'))
    description = Column(String(3000, 'utf8_bin'))
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    parent_id = Column(Integer)

    sensor_users = relationship('SsSensorUser', secondary='ss_sensor_user_group_relation', backref='ss_sensor_user_groups')


class SsSensorUser(BaseAttach, DB_BASE):
    __tablename__ = 'ss_sensor_users'

    id = Column(Integer, primary_key=True)
    loginname = Column(String(80, 'utf8_bin'))
    user_name = Column(String(80, 'utf8_bin'))
    realm_name = Column(String(80, 'utf8_bin'))
    real_name = Column(String(80, 'utf8_bin'))
    email = Column(String(200, 'utf8_bin'))
    current_logon_host = Column(String(810, 'utf8_bin'))
    enable = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime)


t_ss_user_role_relation = Table(
    'ss_user_role_relation', metadata,
    Column('user_id', ForeignKey('ss_basic_users.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('role_id', ForeignKey('ss_basic_roles.role_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class SsUserStrategy(BaseAttach, DB_BASE):
    __tablename__ = 'ss_user_strategy'

    id = Column(Integer, primary_key=True)
    content = Column(String(500, 'utf8_bin'))


class SsUserStrategyBackupFile(BaseAttach, DB_BASE):
    __tablename__ = 'ss_user_strategy_backup_file'

    id = Column(Integer, primary_key=True)
    md5_sum = Column(String(100, 'utf8_bin'), nullable=False)
    info = Column(String(500, 'utf8_bin'), nullable=False)


t_tab_CC = Table(
    'tab_CC', metadata,
    Column('cc_flag', Integer, server_default=FetchedValue()),
    Column('complex_password', Integer, server_default=FetchedValue()),
    Column('password_expiration', Integer, server_default=FetchedValue()),
    Column('password_expiration_length', Integer),
    Column('password_change_flag', Integer, server_default=FetchedValue()),
    Column('regular_alarm', Integer, server_default=FetchedValue()),
    Column('last_alarm_date', DateTime, nullable=False, server_default=FetchedValue()),
    Column('admin_password_expiration', Integer, server_default=FetchedValue()),
    Column('admin_password_expiration_length', Integer, server_default=FetchedValue())
)


class TabAlarmCondition(BaseAttach, DB_BASE):
    __tablename__ = 'tab_alarm_condition'

    id = Column(Integer, primary_key=True)
    name = Column(String(256, 'utf8_bin'))
    query_condition = Column(String(1024, 'utf8_bin'))


class TabAlarmModule(BaseAttach, DB_BASE):
    __tablename__ = 'tab_alarm_module'

    module_id = Column(Integer, primary_key=True)
    type = Column(String(50, 'utf8_bin'))
    io = Column(Integer)

    policys = relationship('TabAlarmPolicy', secondary='tab_alarm_module_policy_relation', backref='tab_alarm_modules')


t_tab_alarm_module_policy_relation = Table(
    'tab_alarm_module_policy_relation', metadata,
    Column('policy_id', ForeignKey('tab_alarm_policy.policy_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('module_id', ForeignKey('tab_alarm_module.module_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabAlarmMsgClassification(BaseAttach, DB_BASE):
    __tablename__ = 'tab_alarm_msg_classification'

    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer)
    policy_desc = Column(String(1000, 'utf8_bin'))
    src_id = Column(Integer)
    msg_type = Column(String(64, 'utf8_bin'))
    src_alarm_name_id = Column(Integer)
    src_alarm_name = Column(String(1000, 'utf8_bin'))
    level_id = Column(Integer)
    intelligent_adjust = Column(String(1000, 'utf8_bin'))


class TabAlarmMsgType(BaseAttach, DB_BASE):
    __tablename__ = 'tab_alarm_msg_type'

    alarm_msg_type_id = Column(Integer, primary_key=True)
    msg_type = Column(String(40, 'utf8_bin'))

    roles = relationship('TabBasicRole', secondary='tab_role_alarm_msg_type_relation', backref='tab_alarm_msg_types')


class TabAlarmPolicy(BaseAttach, DB_BASE):
    __tablename__ = 'tab_alarm_policy'

    policy_id = Column(Integer, primary_key=True)
    msg_type_list = Column(String(500, 'utf8_bin'))
    level_list = Column(String(500, 'utf8_bin'))
    output_list = Column(String(500, 'utf8_bin'))
    all_users_flag = Column(Integer, server_default=FetchedValue())

    users = relationship('SsBasicUser', secondary='tab_alarm_policy_user_relation', backref='tab_alarm_policies')


class TabAlarmPolicyTemplet(BaseAttach, DB_BASE):
    __tablename__ = 'tab_alarm_policy_templet'

    id = Column(Integer, primary_key=True)
    templet_type = Column(String(50, 'utf8_bin'))
    copy_to = Column(String(1000, 'utf8_bin'))
    email_title = Column(String(200, 'utf8_bin'))
    text = Column(String(1000, 'utf8_bin'))
    language = Column(String(10, 'utf8_bin'))
    bak_flag = Column(Integer)
    placeholder_list = Column(String(1000, 'utf8_bin'))
    description = Column(String(2000, 'utf8_bin'))


t_tab_alarm_policy_user_relation = Table(
    'tab_alarm_policy_user_relation', metadata,
    Column('user_id', ForeignKey('ss_basic_users.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('policy_id', ForeignKey('tab_alarm_policy.policy_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabAlarmPolicyUsergroupRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_alarm_policy_usergroup_relation'

    group_id = Column(Integer, primary_key=True, nullable=False)
    policy_id = Column(Integer, primary_key=True, nullable=False)


class TabAlarmType(BaseAttach, DB_BASE):
    __tablename__ = 'tab_alarm_type'

    id = Column(Integer, primary_key=True)
    type = Column(String(30, 'utf8_bin'))


class TabAlarm(BaseAttach, DB_BASE):
    __tablename__ = 'tab_alarms'

    alarm_id = Column(Integer, primary_key=True)
    name = Column(String(50, 'utf8_bin'))
    type = Column(String(50, 'utf8_bin'))
    level = Column(String(10, 'utf8_bin'))
    content = Column(String(1000, 'utf8_bin'))
    state = Column(Integer)
    create_time = Column(DateTime)
    generator_name = Column(String(50, 'utf8_bin'))
    zone_name = Column(String(50, 'utf8_bin'))
    target_type = Column(String(50, 'utf8_bin'))
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    handle_description = Column(String(1000, 'utf8_bin'))
    alarm_elk_id = Column(String(36, 'utf8_bin'))
    relevance_id = Column(String(100, 'utf8_bin'))
    manage_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    sensor_id = Column(String(36, 'utf8_bin'))

    users = relationship('SsBasicUser', secondary='tab_alarms_user_relation', backref='tab_alarms')


t_tab_alarms_user_relation = Table(
    'tab_alarms_user_relation', metadata,
    Column('alarm_id', ForeignKey('tab_alarms.alarm_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('user_id', ForeignKey('ss_basic_users.id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabAllSensor(BaseAttach, DB_BASE):
    __tablename__ = 'tab_all_sensors'

    sensor_id = Column(String(36, 'utf8_bin'), primary_key=True)
    node_id = Column(String(36, 'utf8_bin'))
    dev_id = Column(String(36, 'utf8_bin'))
    name = Column(String(30, 'utf8_bin'))
    ip = Column(String(20, 'utf8_bin'))
    create_time = Column(DateTime)
    mac = Column(String(30, 'utf8_bin'))
    type = Column(Integer)
    state = Column(Integer)
    special_audit = Column(Integer)
    description = Column(String(200, 'utf8_bin'))
    machine = Column(String(30, 'utf8_bin'))


t_tab_all_users = Table(
    'tab_all_users', metadata,
    Column('node_id', String(36, 'utf8_bin')),
    Column('loginname', String(80, 'utf8_bin')),
    Column('node_name', String(40, 'utf8_bin')),
    Column('field_ids', String(1024, 'utf8_bin')),
    Column('field_names', String(1024, 'utf8_bin')),
    Column('role_ids', String(256, 'utf8_bin')),
    Column('role_names', String(1024, 'utf8_bin')),
    Column('real_name', String(40, 'utf8_bin')),
    Column('description', String(1000, 'utf8_bin')),
    Column('create_time', DateTime),
    Column('user_id', Integer),
    Column('realm_name', String(40, 'utf8_bin')),
    Column('manage_filed_ids', String(1024, 'utf8_bin')),
    Column('is_field_admin', Integer, server_default=FetchedValue()),
    Column('email', String(200, 'utf8_bin')),
    Column('enable', Integer),
    Column('guid', String(36, 'utf8_bin'))
)


t_tab_analytics_port_scan = Table(
    'tab_analytics_port_scan', metadata,
    Column('port', Integer),
    Column('exe_name', String(512, 'utf8_bin'))
)


class TabApplication(BaseAttach, DB_BASE):
    __tablename__ = 'tab_applications'

    application_id = Column(Integer, primary_key=True)
    application_name = Column(String(200, 'utf8_bin'))
    description = Column(String(1000, 'utf8_bin'))


t_tab_approval_chain_template = Table(
    'tab_approval_chain_template', metadata,
    Column('id', Integer),
    Column('name', String(50, 'utf8_bin')),
    Column('chain', String(1000, 'utf8_bin')),
    Column('pic_url', String(200, 'utf8_bin'))
)


class TabApprovalEmailTemplet(BaseAttach, DB_BASE):
    __tablename__ = 'tab_approval_email_templet'

    id = Column(Integer, primary_key=True)
    tem_type = Column(String(50, 'utf8_bin'))
    copy_to = Column(String(1000, 'utf8_bin'))
    email_title = Column(String(200, 'utf8_bin'))
    email_text = Column(String(1000, 'utf8_bin'))
    bak_flag = Column(Integer)
    email_language = Column(String(50, 'utf8_bin'))
    placeholder_list = Column(String(1000, 'utf8_bin'))
    email_explain = Column(String(2000, 'utf8_bin'))


class TabApprovalModuleChain(BaseAttach, DB_BASE):
    __tablename__ = 'tab_approval_module_chain'

    chain_id = Column(Integer, primary_key=True)
    name = Column(String(50, 'utf8_bin'), unique=True)
    type = Column(Integer)
    source_id = Column(Integer)
    destination_id = Column(Integer)
    chain = Column(String(1000, 'utf8_bin'))
    enable = Column(Integer)
    priority = Column(Integer, server_default=FetchedValue())
    all_users_flag = Column(Integer)
    is_default = Column(Integer)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    process_path_for_show = Column(String(64, 'utf8_bin'))
    process_path_for_back = Column(String(64, 'utf8_bin'))
    status = Column(Integer, server_default=FetchedValue())

    groups = relationship('TabUserGroup', secondary='tab_chain_groups_relation', backref='tab_approval_module_chains')
    users = relationship('TabBasicUser', secondary='tab_chain_users_relation', backref='tab_approval_module_chains')


class TabApprovalModule(BaseAttach, DB_BASE):
    __tablename__ = 'tab_approval_modules'

    module_id = Column(Integer, primary_key=True)
    name = Column(String(50, 'utf8_bin'))
    type = Column(Integer)
    param_1 = Column(String(1000, 'utf8_bin'))
    param_2 = Column(String(1000, 'utf8_bin'))


t_tab_approving_nodes = Table(
    'tab_approving_nodes', metadata,
    Column('node_id', String(36, 'utf8_bin'), nullable=False),
    Column('name', String(40, 'utf8_bin')),
    Column('type', Integer),
    Column('ip1', String(20, 'utf8_bin')),
    Column('ip2', String(20, 'utf8_bin')),
    Column('state', Integer, server_default=FetchedValue()),
    Column('create_time', DateTime),
    Column('user_number', Integer, server_default=FetchedValue()),
    Column('sensor_number', Integer, server_default=FetchedValue()),
    Column('alarm_number', Integer, server_default=FetchedValue()),
    Column('description', String(200, 'utf8_bin')),
    Column('location_level1', String(100, 'utf8_bin')),
    Column('location_level2', String(100, 'utf8_bin')),
    Column('location_level3', String(100, 'utf8_bin')),
    Column('approving_state', Integer, server_default=FetchedValue()),
    Column('parent_node_id', String(36, 'utf8_bin'))
)


class TabAuditItem(BaseAttach, DB_BASE):
    __tablename__ = 'tab_audit_items'

    audit_item_id = Column(Integer, primary_key=True)
    audit_item_name = Column(String(40, 'utf8_bin'))
    description = Column(String(1000, 'utf8_bin'))

    zones = relationship('TabZone', secondary='tab_zone_audititem_relation', backref='tab_audit_items')


class TabAuditItemsWsa(BaseAttach, DB_BASE):
    __tablename__ = 'tab_audit_items_wsa'

    audit_item_id = Column(Integer, primary_key=True)
    audit_item_name = Column(String(40, 'utf8_bin'))
    description = Column(String(1000, 'utf8_bin'))


class TabAudititemWsaUserDefault(TabAuditItemsWsa):
    __tablename__ = 'tab_audititem_wsa_user_default'

    audit_item_id = Column(ForeignKey('tab_audit_items_wsa.audit_item_id', ondelete='CASCADE'), primary_key=True)
    enable = Column(Integer)
    time_scope_value = Column(String(10, 'utf8_bin'))
    num_scope_value = Column(BigInteger)


class TabAudititemWsaUserRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_audititem_wsa_user_relation'

    user_id = Column(Integer, primary_key=True, nullable=False)
    audit_item_id = Column(ForeignKey('tab_audit_items_wsa.audit_item_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    enable = Column(Integer)
    time_scope_value = Column(String(10, 'utf8_bin'))
    num_scope_value = Column(BigInteger)
    is_default = Column(Integer)

    audit_item = relationship('TabAuditItemsWsa', primaryjoin='TabAudititemWsaUserRelation.audit_item_id == TabAuditItemsWsa.audit_item_id', backref='tab_audititem_wsa_user_relations')


class TabAutoLoginDefaultuser(BaseAttach, DB_BASE):
    __tablename__ = 'tab_auto_login_defaultuser'

    zone_id = Column(ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    server_type = Column(Integer, primary_key=True, nullable=False, server_default=FetchedValue())
    value = Column(Integer, server_default=FetchedValue())

    zone = relationship('TabZone', primaryjoin='TabAutoLoginDefaultuser.zone_id == TabZone.zone_id', backref='tab_auto_login_defaultusers')


class TabAutoLoginServer(BaseAttach, DB_BASE):
    __tablename__ = 'tab_auto_login_server'
    __table_args__ = (
        Index('AK_Key_2', 'zone_id', 'server_type', 'ip'),
    )

    server_id = Column(Integer, primary_key=True)
    zone_id = Column(ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), nullable=False)
    server_type = Column(Integer)
    ip = Column(String(20, 'utf8_bin'), nullable=False)
    user_number = Column(Integer, server_default=FetchedValue())
    protocol = Column(String(20, 'utf8_bin'))
    description = Column(String(200, 'utf8_bin'))
    pool_id = Column(String(36, 'utf8_bin'))
    display_ip = Column(String(1000, 'utf8_bin'))
    available_number = Column(Integer)

    zone = relationship('TabZone', primaryjoin='TabAutoLoginServer.zone_id == TabZone.zone_id', backref='tab_auto_login_servers')


class TabAutoLoginUser(BaseAttach, DB_BASE):
    __tablename__ = 'tab_auto_login_user'

    id = Column(Integer, nullable=False, index=True)
    pool_id = Column(String(36, 'utf8_bin'))
    loginname = Column(String(80, 'utf8_bin'), primary_key=True, nullable=False)
    zone_name = Column(String(50, 'utf8_bin'), primary_key=True, nullable=False)
    assign_ip = Column(String(20, 'utf8_bin'), primary_key=True, nullable=False)
    protocol = Column(String(20, 'utf8_bin'), primary_key=True, nullable=False)
    description = Column(String(200, 'utf8_bin'))


class TabBasicMenu(BaseAttach, DB_BASE):
    __tablename__ = 'tab_basic_menu'

    menuId = Column(Integer, primary_key=True)
    parentId = Column(Integer, nullable=False)
    name = Column(String(50, 'utf8_bin'), nullable=False)
    path = Column(String(255, 'utf8_bin'))
    orderId = Column(Integer, nullable=False)
    enable = Column(Integer, nullable=False)
    description = Column(String(255, 'utf8_bin'))


class TabBasicPathPrivilege(BaseAttach, DB_BASE):
    __tablename__ = 'tab_basic_path_privileges'

    privilegeId = Column(Integer, primary_key=True)
    path = Column(String(255, 'utf8_bin'))
    description = Column(String(255, 'utf8_bin'))
    tag = Column(String(50, 'utf8_bin'))
    operation = Column(String(100, 'utf8_bin'))


class TabBasicPrivilege(BaseAttach, DB_BASE):
    __tablename__ = 'tab_basic_privileges'

    privilege_id = Column(Integer, primary_key=True)
    privilege_name = Column(String(40, 'utf8_bin'), unique=True)
    type = Column(Integer)
    action_type_list = Column(Integer)
    is_high_security = Column(Integer)
    description = Column(String(1000, 'utf8_bin'))
    display_flag = Column(Integer, server_default=FetchedValue())


class TabBasicRoleMenuRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_basic_role_menu_relation'

    id = Column(Integer, primary_key=True)
    role_id = Column(ForeignKey('tab_basic_roles.role_id', ondelete='CASCADE'), nullable=False, index=True)
    menu_id = Column(ForeignKey('tab_basic_menu.menuId', ondelete='CASCADE'), nullable=False, index=True)

    menu = relationship('TabBasicMenu', primaryjoin='TabBasicRoleMenuRelation.menu_id == TabBasicMenu.menuId', backref='tab_basic_role_menu_relations')
    role = relationship('TabBasicRole', primaryjoin='TabBasicRoleMenuRelation.role_id == TabBasicRole.role_id', backref='tab_basic_role_menu_relations')


class TabBasicRolePathRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_basic_role_path_relation'

    relationId = Column(Integer, primary_key=True)
    privilegeId = Column(ForeignKey('tab_basic_path_privileges.privilegeId', ondelete='CASCADE'), index=True)
    roleId = Column(ForeignKey('tab_basic_roles.role_id', ondelete='CASCADE'), index=True)

    tab_basic_path_privilege = relationship('TabBasicPathPrivilege', primaryjoin='TabBasicRolePathRelation.privilegeId == TabBasicPathPrivilege.privilegeId', backref='tab_basic_role_path_relations')
    tab_basic_role = relationship('TabBasicRole', primaryjoin='TabBasicRolePathRelation.roleId == TabBasicRole.role_id', backref='tab_basic_role_path_relations')


class TabBasicRolePrivilegeRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_basic_role_privilege_relation'

    role_id = Column(ForeignKey('tab_basic_roles.role_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    privilege_id = Column(ForeignKey('tab_basic_privileges.privilege_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    action_type = Column(Integer)
    target_role_id = Column(String(1000, 'utf8_bin'), server_default=FetchedValue())
    pre_condition = Column(String(1000, 'utf8_bin'), server_default=FetchedValue())
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    privilege = relationship('TabBasicPrivilege', primaryjoin='TabBasicRolePrivilegeRelation.privilege_id == TabBasicPrivilege.privilege_id', backref='tab_basic_role_privilege_relations')
    role = relationship('TabBasicRole', primaryjoin='TabBasicRolePrivilegeRelation.role_id == TabBasicRole.role_id', backref='tab_basic_role_privilege_relations')


class TabBasicRole(BaseAttach, DB_BASE):
    __tablename__ = 'tab_basic_roles'

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(40, 'utf8_bin'))
    type = Column(Integer)
    description = Column(String(200, 'utf8_bin'))
    display_flag = Column(Integer, server_default=FetchedValue())

    users = relationship('TabBasicUser', secondary='tab_basic_user_role_relation', backref='tab_basic_roles')


t_tab_basic_user_role_relation = Table(
    'tab_basic_user_role_relation', metadata,
    Column('user_id', ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('role_id', ForeignKey('tab_basic_roles.role_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabBasicUser(BaseAttach, DB_BASE):
    __tablename__ = 'tab_basic_users'

    user_id = Column(Integer, primary_key=True)
    loginname = Column(String(80, 'utf8_bin'), unique=True)
    password = Column(String(256, 'utf8_bin'))
    description = Column(String(1000, 'utf8_bin'))
    real_name = Column(String(40, 'utf8_bin'))
    email = Column(String(200, 'utf8_bin'))
    enable = Column(Integer, server_default=FetchedValue())
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    realm_name = Column(String(40, 'utf8_bin'), server_default=FetchedValue())
    user_name = Column(String(40, 'utf8_bin'))
    change_password = Column(Integer, server_default=FetchedValue())
    last_change_password_date = Column(DateTime)
    last_lock_time = Column(DateTime)
    password_error_times = Column(Integer, nullable=False, server_default=FetchedValue())
    desktop_st_user_zone11 = Column(String(80, 'utf8_bin'))
    desktop_st_user_zone12 = Column(String(80, 'utf8_bin'))
    desktop_st_user_zone13 = Column(String(80, 'utf8_bin'))
    desktop_st_user_zone14 = Column(String(80, 'utf8_bin'))
    desktop_st_user_zone15 = Column(String(80, 'utf8_bin'))
    desktop_st_user_zone16 = Column(String(80, 'utf8_bin'))
    desktop_st_user_zone17 = Column(String(80, 'utf8_bin'))
    user_expiration_time = Column(DateTime)
    desktop_expiration_days = Column(Integer, server_default=FetchedValue())
    user_expiration_alarm_days = Column(Integer, server_default=FetchedValue())
    use_zone_desktop_expiration = Column(Integer, server_default=FetchedValue())
    user_language = Column(String(50, 'utf8_bin'), server_default=FetchedValue())
    wechat_no = Column(String(64, 'utf8_bin'))
    phone_no = Column(String(64, 'utf8_bin'))
    area_code = Column(String(20, 'utf8_bin'), server_default=FetchedValue())


t_tab_chain_groups_relation = Table(
    'tab_chain_groups_relation', metadata,
    Column('chain_id', ForeignKey('tab_approval_module_chain.chain_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('group_id', ForeignKey('tab_user_groups.group_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_chain_users_relation = Table(
    'tab_chain_users_relation', metadata,
    Column('chain_id', ForeignKey('tab_approval_module_chain.chain_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('user_id', ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_client_login = Table(
    'tab_client_login', metadata,
    Column('dev_id', String(40, 'utf8_bin'), nullable=False),
    Column('hostname', String(40, 'utf8_bin'), nullable=False),
    Column('user', String(80, 'utf8_bin'), nullable=False),
    Column('zone_name', String(40, 'utf8_bin'), nullable=False),
    Column('client_ip', String(20, 'utf8_bin')),
    Column('client_mac', String(40, 'utf8_bin')),
    Column('login_time', DateTime)
)


t_tab_client_runtime = Table(
    'tab_client_runtime', metadata,
    Column('dev_id', String(40, 'utf8_bin')),
    Column('hostname', String(40, 'utf8_bin')),
    Column('screennum', Integer),
    Column('user', String(80, 'utf8_bin')),
    Column('zonename', String(40, 'utf8_bin')),
    Column('client_ip', String(20, 'utf8_bin')),
    Column('client_mac', String(40, 'utf8_bin')),
    Column('client_port', Integer),
    Column('login_time', DateTime),
    Column('online', Integer, server_default=FetchedValue()),
    Column('client_version', String(40, 'utf8_bin'))
)


class TabCluster(BaseAttach, DB_BASE):
    __tablename__ = 'tab_cluster'

    dev_id = Column(String(40, 'utf8_bin'), primary_key=True)
    ip = Column(String(40, 'utf8_bin'))
    weight = Column(Integer)
    type = Column(String(100, 'utf8_bin'))
    online = Column(Integer)
    id = Column(Integer, nullable=False)
    ha_ip = Column(String(40, 'utf8_bin'))


class TabConfReceiveByParentNode(BaseAttach, DB_BASE):
    __tablename__ = 'tab_conf_receive_by_parent_node'

    id = Column(Integer, primary_key=True)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    parent_ip = Column(String(20, 'utf8_bin'))
    parent_node_id = Column(String(36, 'utf8_bin'))
    is_force = Column(Integer, server_default=FetchedValue())
    module_name = Column(String(256, 'utf8_bin'))
    table_names = Column(String(256, 'utf8_bin'))
    table_data = Column(Text(collation='utf8_bin'))
    uuid = Column(String(36, 'utf8_bin'))


class TabContainerRuntime(BaseAttach, DB_BASE):
    __tablename__ = 'tab_container_runtime'

    dev_id = Column(String(40, 'utf8_bin'), primary_key=True, nullable=False)
    hostname = Column(String(40, 'utf8_bin'), primary_key=True, nullable=False)
    user = Column(String(80, 'utf8_bin'), primary_key=True, nullable=False)
    zonename = Column(String(40, 'utf8_bin'), primary_key=True, nullable=False)
    netname = Column(String(40, 'utf8_bin'))
    start_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    geometry = Column(String(20, 'utf8_bin'))
    screennum = Column(Integer, primary_key=True, nullable=False)
    filein = Column(Integer)
    fileout = Column(Integer)
    internet = Column(Integer)
    transfer = Column(Integer)
    clipboard = Column(Integer)
    mflag = Column(Integer)
    force_offline = Column(Integer, server_default=FetchedValue())
    last_offline_time = Column(DateTime)
    client_version = Column(String(40, 'utf8_bin'))
    rdp_hostname = Column(String(40, 'utf8_bin'), primary_key=True, nullable=False, server_default=FetchedValue())


class TabCustomSetting(BaseAttach, DB_BASE):
    __tablename__ = 'tab_custom_setting'

    user_id = Column(Integer, primary_key=True, nullable=False)
    page_name = Column(String(50, 'utf8_bin'), primary_key=True, nullable=False)
    column_names = Column(String(512, 'utf8_bin'))


t_tab_data_down_report_config = Table(
    'tab_data_down_report_config', metadata,
    Column('source_node_id', String(36, 'utf8_bin'), primary_key=True, nullable=False),
    Column('destination_node_id', String(36, 'utf8_bin'), primary_key=True, nullable=False),
    Column('service_id', ForeignKey('tab_data_report_service.service_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True),
    ForeignKeyConstraint(['source_node_id', 'destination_node_id'], ['tab_data_report_relation.source_node_id', 'tab_data_report_relation.destination_node_id'], ondelete='CASCADE')
)


class TabDataReportFunctionType(BaseAttach, DB_BASE):
    __tablename__ = 'tab_data_report_function_type'

    type_id = Column(Integer, primary_key=True)
    name = Column(String(50, 'utf8_bin'))


t_tab_data_report_relation = Table(
    'tab_data_report_relation', metadata,
    Column('source_node_id', ForeignKey('tab_nodes.node_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('destination_node_id', ForeignKey('tab_nodes.node_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabDataReportRelation(object):
    def __init__(self, source_node_id, destination_node_id):
        self.source_node_id = source_node_id
        self.destination_node_id = destination_node_id


mapper(TabDataReportRelation, t_tab_data_report_relation)


class TabDataReportService(BaseAttach, DB_BASE):
    __tablename__ = 'tab_data_report_service'

    service_id = Column(String(36, 'utf8_bin'), primary_key=True)
    name = Column(String(50, 'utf8_bin'))
    description = Column(String(200, 'utf8_bin'))

    source_nodes = relationship(TabDataReportRelation, secondary='tab_data_down_report_config', backref='tab_data_report_services')
    source_nodes1 = relationship(TabDataReportRelation, secondary='tab_data_up_report_config', backref='tab_data_report_services_0')


class TabDataReportServiceDefine(BaseAttach, DB_BASE):
    __tablename__ = 'tab_data_report_service_define'

    define_id = Column(String(36, 'utf8_bin'), primary_key=True)
    type_id = Column(ForeignKey('tab_data_report_service_type.type_id', ondelete='CASCADE'), index=True)
    service_id = Column(ForeignKey('tab_data_report_service.service_id', ondelete='CASCADE'), index=True)
    param_1 = Column(String(200, 'utf8_bin'))
    param_2 = Column(String(200, 'utf8_bin'))
    param_3 = Column(String(200, 'utf8_bin'))
    param_4 = Column(String(200, 'utf8_bin'))
    param_5 = Column(String(200, 'utf8_bin'))

    service = relationship('TabDataReportService', primaryjoin='TabDataReportServiceDefine.service_id == TabDataReportService.service_id', backref='tab_data_report_service_defines')
    type = relationship('TabDataReportServiceType', primaryjoin='TabDataReportServiceDefine.type_id == TabDataReportServiceType.type_id', backref='tab_data_report_service_defines')


class TabDataReportServiceType(BaseAttach, DB_BASE):
    __tablename__ = 'tab_data_report_service_type'

    type_id = Column(Integer, primary_key=True)
    name = Column(String(200, 'utf8_bin'))


t_tab_data_up_report_config = Table(
    'tab_data_up_report_config', metadata,
    Column('source_node_id', String(36, 'utf8_bin'), primary_key=True, nullable=False),
    Column('destination_node_id', String(36, 'utf8_bin'), primary_key=True, nullable=False),
    Column('service_id', ForeignKey('tab_data_report_service.service_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True),
    ForeignKeyConstraint(['source_node_id', 'destination_node_id'], ['tab_data_report_relation.source_node_id', 'tab_data_report_relation.destination_node_id'], ondelete='CASCADE')
)


class TabDaySensorActivityRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_day_sensor_activity_record'
    __table_args__ = (
        Index('Index_3', 'user_name', 'zone_name'),
    )

    id = Column(Integer, primary_key=True)
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    user_name = Column(String(80, 'utf8_bin'), index=True)
    zone_name = Column(String(40, 'utf8_bin'), index=True)
    time = Column(DateTime, nullable=False, server_default=FetchedValue())
    time_span = Column(Integer)
    process_index = Column(Integer, server_default=FetchedValue())
    data_index = Column(Integer, server_default=FetchedValue())
    io_index = Column(Integer, server_default=FetchedValue())
    source_node_id = Column(String(36, 'utf8_bin'))


class TabDayUserActivityRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_day_user_activity_record'
    __table_args__ = (
        Index('Index_3', 'user_name', 'zone_name'),
    )

    id = Column(Integer, primary_key=True)
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    user_name = Column(String(80, 'utf8_bin'), index=True)
    zone_name = Column(String(40, 'utf8_bin'), index=True)
    time = Column(DateTime, nullable=False, server_default=FetchedValue())
    time_span = Column(Integer)
    keyboard_index = Column(Integer, server_default=FetchedValue())
    mouse_index = Column(Integer, server_default=FetchedValue())
    screen_index = Column(Integer, server_default=FetchedValue())
    source_node_id = Column(String(36, 'utf8_bin'))


class TabDeviceConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_device_config'

    name = Column(String(100, 'utf8_bin'), primary_key=True)
    value = Column(String(200, 'utf8_bin'))


class TabDeviceStorage(BaseAttach, DB_BASE):
    __tablename__ = 'tab_device_storage'

    ip = Column(String(32, 'utf8_bin'), primary_key=True)
    sys_total_storage = Column(Integer)
    sys_used_storage = Column(Integer)
    sys_available_storage = Column(Integer)
    es_total_storage = Column(Integer)
    es_used_storage = Column(Integer)
    es_available_storage = Column(Integer)


class TabDevice(BaseAttach, DB_BASE):
    __tablename__ = 'tab_devices'

    device_id = Column(String(36, 'utf8_bin'), primary_key=True)
    node_id = Column(ForeignKey('tab_nodes.node_id', ondelete='CASCADE'), index=True)
    name = Column(String(30, 'utf8_bin'))
    ip = Column(String(20, 'utf8_bin'))
    is_management = Column(Integer)
    is_management_active = Column(Integer)
    is_security = Column(Integer)
    hardware = Column(String(20, 'utf8_bin'))
    software = Column(String(20, 'utf8_bin'))
    user_number_limit = Column(Integer)
    total_storage = Column(Integer)
    zone_number = Column(Integer)
    create_time = Column(DateTime)

    node = relationship('TabNode', primaryjoin='TabDevice.node_id == TabNode.node_id', backref='tab_devices')


class TabDomain(BaseAttach, DB_BASE):
    __tablename__ = 'tab_domains'

    domain_id = Column(Integer, primary_key=True)
    type = Column(String(20, 'utf8_bin'))
    realm_name = Column(String(40, 'utf8_bin'), unique=True)
    domain_name = Column(String(200, 'utf8_bin'))
    domain_user = Column(String(100, 'utf8_bin'))
    domain_password = Column(String(256, 'utf8_bin'))
    domain_host_ip = Column(String(256, 'utf8_bin'))
    domain_ou = Column(String(1000, 'utf8_bin'))
    port = Column(Integer)
    sync_status = Column(String(40, 'utf8_bin'))
    sync_begin_time = Column(DateTime)
    sync_end_time = Column(DateTime)
    user_paramer = Column(String(1000, 'utf8_bin'))


class TabDomainsSensor(BaseAttach, DB_BASE):
    __tablename__ = 'tab_domains_sensor'

    domain_id = Column(Integer, primary_key=True)
    type = Column(String(20, 'utf8_bin'))
    realm_name = Column(String(40, 'utf8_bin'), unique=True)
    domain_name = Column(String(200, 'utf8_bin'))
    domain_user = Column(String(100, 'utf8_bin'))
    domain_password = Column(String(256, 'utf8_bin'))
    domain_host_ip = Column(String(256, 'utf8_bin'))
    domain_ou = Column(String(1000, 'utf8_bin'))
    port = Column(Integer)
    sync_status = Column(String(40, 'utf8_bin'))
    sync_begin_time = Column(DateTime)
    sync_end_time = Column(DateTime)
    user_paramer = Column(String(1000, 'utf8_bin'))
    domain_group_flag = Column(Integer)


class TabField(BaseAttach, DB_BASE):
    __tablename__ = 'tab_fields'

    field_id = Column(String(36, 'utf8_bin'), primary_key=True)
    name = Column(String(30, 'utf8_bin'), unique=True)
    create_time = Column(DateTime)
    description = Column(String(200, 'utf8_bin'))

    systemusers = relationship('TabBasicUser', secondary='tab_systemuser_field_relation', backref='tab_fields')


class TabFileAccessControlRule(BaseAttach, DB_BASE):
    __tablename__ = 'tab_file_access_control_rules'

    id = Column(Integer, primary_key=True)
    name = Column(String(50, 'utf8_bin'))
    enable = Column(Integer)
    server_name = Column(String(256, 'utf8_bin'))
    user_id = Column(Integer)
    group_id = Column(Integer)
    http_request_method = Column(String(50, 'utf8_bin'))
    url = Column(Text(collation='utf8_bin'))
    http_request_param = Column(String(256, 'utf8_bin'))
    file_type = Column(String(1000, 'utf8_bin'))
    description = Column(String(100, 'utf8_bin'))
    operation_control = Column(String(20, 'utf8_bin'))
    priority = Column(Integer)
    intercept_format = Column(Integer, server_default=FetchedValue())

    servers = relationship('TabWsaServerManage', secondary='tab_file_rule_server_relation', backref='tab_file_access_control_rules')
    users = relationship('TabBasicUser', secondary='tab_file_rule_user_relation', backref='tab_file_access_control_rules')
    usergroups = relationship('TabUserGroup', secondary='tab_file_rule_usergroup_relation', backref='tab_file_access_control_rules')


t_tab_file_rule_server_relation = Table(
    'tab_file_rule_server_relation', metadata,
    Column('rule_id', ForeignKey('tab_file_access_control_rules.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('server_id', ForeignKey('tab_wsa_server_manage.server_manage_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_file_rule_user_relation = Table(
    'tab_file_rule_user_relation', metadata,
    Column('rule_id', ForeignKey('tab_file_access_control_rules.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('user_id', ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_file_rule_usergroup_relation = Table(
    'tab_file_rule_usergroup_relation', metadata,
    Column('rule_id', ForeignKey('tab_file_access_control_rules.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('usergroup_id', ForeignKey('tab_user_groups.group_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_file_transfer_config = Table(
    'tab_file_transfer_config', metadata,
    Column('ticket_id', Integer, nullable=False),
    Column('dev_ip', String(30, 'utf8_bin')),
    Column('dev_port', Integer, server_default=FetchedValue()),
    Column('dev_user', String(80, 'utf8_bin')),
    Column('dev_password', String(256, 'utf8_bin')),
    Column('dev_path', String(256, 'utf8_bin')),
    Column('ftp_ip', String(30, 'utf8_bin')),
    Column('ftp_port', Integer, server_default=FetchedValue()),
    Column('ftp_user', String(80, 'utf8_bin')),
    Column('ftp_password', String(256, 'utf8_bin')),
    Column('ftp_path', String(256, 'utf8_bin')),
    Column('flag', String(16, 'utf8_bin'))
)


class TabFilterAlarm(BaseAttach, DB_BASE):
    __tablename__ = 'tab_filter_alarms'

    alarm_id = Column(Integer, primary_key=True)
    name = Column(String(50, 'utf8_bin'))
    type = Column(String(50, 'utf8_bin'))
    level = Column(String(10, 'utf8_bin'))
    content = Column(String(1000, 'utf8_bin'))
    state = Column(Integer)
    create_time = Column(DateTime)
    generator_name = Column(String(50, 'utf8_bin'))
    zone_name = Column(String(50, 'utf8_bin'))
    target_type = Column(String(50, 'utf8_bin'))
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    handle_description = Column(String(1000, 'utf8_bin'))
    alarm_elk_id = Column(String(36, 'utf8_bin'))


class TabFont(BaseAttach, DB_BASE):
    __tablename__ = 'tab_fonts'

    id = Column(Integer, primary_key=True)
    name = Column(String(50, 'utf8_bin'))
    type = Column(String(50, 'utf8_bin'))
    description = Column(String(50, 'utf8_bin'))
    path = Column(String(200, 'utf8_bin'))


class TabFtpConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_ftp_configs'

    id = Column(Integer, primary_key=True)
    remote_ip = Column(String(30, 'utf8_bin'))
    remote_port = Column(Integer)
    remote_username = Column(String(80, 'utf8_bin'))
    remote_password = Column(String(256, 'utf8_bin'))
    type = Column(Integer)
    remote_dir = Column(String(256, 'utf8_bin'))
    auto_upload = Column(BIT(1))


class TabFtpZoneConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_ftp_zone_configs'

    id = Column(Integer, primary_key=True)
    zone_id = Column(ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), index=True)
    remote_ip = Column(String(30, 'utf8_bin'))
    remote_port = Column(Integer)
    remote_username = Column(String(80, 'utf8_bin'))
    remote_password = Column(String(256, 'utf8_bin'))
    remote_dir = Column(String(256, 'utf8_bin'))
    auto_upload = Column(Integer)

    zone = relationship('TabZone', primaryjoin='TabFtpZoneConfig.zone_id == TabZone.zone_id', backref='tab_ftp_zone_configs')


class TabGlobalConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_global_config'

    name = Column(String(100, 'utf8_bin'), primary_key=True)
    value = Column(String(200, 'utf8_bin'))


class TabGlobalNodeConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_global_node_config'

    name = Column(String(100, 'utf8_bin'), primary_key=True)
    value = Column(String(2000, 'utf8_bin'))
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


t_tab_history_alarms = Table(
    'tab_history_alarms', metadata,
    Column('alarm_id', Integer, index=True),
    Column('name', String(50, 'utf8_bin')),
    Column('type', String(50, 'utf8_bin'), index=True),
    Column('level', String(10, 'utf8_bin'), index=True),
    Column('content', String(1000, 'utf8_bin')),
    Column('state', Integer),
    Column('create_time', DateTime),
    Column('generator_name', String(50, 'utf8_bin'), index=True),
    Column('zone_name', String(50, 'utf8_bin'), index=True),
    Column('target_type', String(50, 'utf8_bin')),
    Column('handler_type', Text(collation='utf8_bin')),
    Column('handler_name', String(50, 'utf8_bin'), index=True),
    Column('handle_time', DateTime),
    Column('handle_description', String(1000, 'utf8_bin')),
    Column('source_guid', String(36, 'utf8_bin')),
    Column('source_type', Integer)
)


class TabHistoryZoneUser(BaseAttach, DB_BASE):
    __tablename__ = 'tab_history_zone_user'

    zone_name = Column(String(40, 'utf8_bin'), primary_key=True, nullable=False)
    user_name = Column(String(80, 'utf8_bin'), primary_key=True, nullable=False)
    type = Column(String(10, 'utf8_bin'))


class TabInnerSystem(BaseAttach, DB_BASE):
    __tablename__ = 'tab_inner_systems'

    id = Column(Integer, primary_key=True)
    dev_id = Column(String(40, 'utf8_bin'))
    display_name = Column(String(30, 'utf8_bin'))
    system_name = Column(String(30, 'utf8_bin'))
    type = Column(String(20, 'utf8_bin'))
    service_status = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime)
    services = Column(String(2048, 'utf8_bin'))
    last_check_time = Column(DateTime)


class TabLicense(BaseAttach, DB_BASE):
    __tablename__ = 'tab_license'

    dev_id = Column(String(36, 'utf8_bin'), primary_key=True)
    node_id = Column(String(36, 'utf8_bin'))
    status = Column(Integer, server_default=FetchedValue())
    limit_vds = Column(Integer, server_default=FetchedValue())
    current_vds = Column(Integer, server_default=FetchedValue())
    limit_sensor = Column(Integer, server_default=FetchedValue())
    current_sensor = Column(Integer, server_default=FetchedValue())
    limit_sensor_user = Column(Integer, server_default=FetchedValue())
    update_datetime = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabLoadAlarmConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_load_alarm_config'

    id = Column(Integer, primary_key=True)
    type = Column(ENUM('cpu', 'memory'), nullable=False)
    status = Column(Integer)
    serial_minute = Column(Integer)
    alarm_value = Column(Integer)


class TabLoadInfo(BaseAttach, DB_BASE):
    __tablename__ = 'tab_load_info'

    id = Column(Integer, primary_key=True)
    server_ip = Column(String(20, 'utf8_bin'))
    cpu_number = Column(Integer)
    cpu_frequency = Column(Float)
    load_average = Column(Float)
    login_users = Column(Integer)
    query_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    mem_total = Column(Integer)
    mem_used = Column(Integer)
    user_list = Column(String(1000, 'utf8_bin'))
    os_version = Column(String(100, 'utf8_bin'))
    disk_size = Column(String(10, 'utf8_bin'))
    disk_usage = Column(String(10, 'utf8_bin'))


class TabLoadServer(BaseAttach, DB_BASE):
    __tablename__ = 'tab_load_server'

    id = Column(Integer, primary_key=True)
    zone_id = Column(ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), index=True)
    ip = Column(String(20, 'utf8_bin'))
    type = Column(Integer)
    user = Column(String(80, 'utf8_bin'))
    password = Column(String(1024, 'utf8_bin'))
    description = Column(String(256, 'utf8_bin'))
    name = Column(String(256, 'utf8_bin'))
    status = Column(Integer, server_default=FetchedValue())
    online = Column(Integer, server_default=FetchedValue())
    port = Column(Integer, server_default=FetchedValue())
    os_type = Column(String(10, 'utf8_bin'))

    zone = relationship('TabZone', primaryjoin='TabLoadServer.zone_id == TabZone.zone_id', backref='tab_load_servers')


t_tab_log_backup = Table(
    'tab_log_backup', metadata,
    Column('id', Integer, nullable=False, index=True),
    Column('path', String(200, 'utf8_bin'), nullable=False),
    Column('last_modify_time', DateTime, nullable=False, server_default=FetchedValue()),
    Column('size', Integer, nullable=False),
    Column('hash', String(500, 'utf8_bin'), nullable=False)
)


class TabLogFile(BaseAttach, DB_BASE):
    __tablename__ = 'tab_log_files'

    log_file_id = Column(Integer, primary_key=True)
    application_id = Column(ForeignKey('tab_applications.application_id', ondelete='CASCADE'), index=True)
    start_datetime = Column(DateTime, nullable=False, server_default=FetchedValue())
    end_datetime = Column(DateTime, nullable=False, server_default=FetchedValue())
    user_name = Column(String(80, 'utf8_bin'))
    zone_name = Column(String(40, 'utf8_bin'))
    network_name = Column(String(40, 'utf8_bin'))
    file_name = Column(String(200, 'utf8_bin'))
    file_size = Column(Integer)
    description = Column(String(1000, 'utf8_bin'))
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    source_node_id = Column(String(36, 'utf8_bin'))
    source_ip = Column(String(20, 'utf8_bin'))
    source_mac = Column(String(30, 'utf8_bin'))
    source_dev_id = Column(String(40, 'utf8_bin'))
    flag = Column(Integer, server_default=FetchedValue())
    origin = Column(String(10, 'utf8_bin'))

    application = relationship('TabApplication', primaryjoin='TabLogFile.application_id == TabApplication.application_id', backref='tab_log_files')


class TabLogManagerAlarm(BaseAttach, DB_BASE):
    __tablename__ = 'tab_log_manager_alarm'

    id = Column(Integer, primary_key=True)
    zone_name = Column(String(40, 'utf8_bin'))
    network_name = Column(String(40, 'utf8_bin'))
    audit_type = Column(String(20, 'utf8_bin'))
    log_type = Column(String(20, 'utf8_bin'))
    alarm_time = Column(DateTime)
    alarm_type = Column(String(20, 'utf8_bin'))


class TabLogManagerTask(BaseAttach, DB_BASE):
    __tablename__ = 'tab_log_manager_task'

    task_id = Column(Integer, primary_key=True)
    ps_id = Column(Integer)
    task_name = Column(String(40, 'utf8_bin'))
    start_datetime = Column(DateTime, nullable=False, server_default=FetchedValue())
    end_datetime = Column(DateTime, nullable=False, server_default=FetchedValue())
    task_status = Column(Integer)


class TabManApprovalNode(BaseAttach, DB_BASE):
    __tablename__ = 'tab_man_approval_nodes'

    man_node_id = Column(Integer, primary_key=True)
    chain_id = Column(ForeignKey('tab_approval_module_chain.chain_id', ondelete='CASCADE'), nullable=False, index=True)
    type = Column(Integer, nullable=False)
    all_approvals_flag = Column(Integer)
    priority = Column(Integer, nullable=False)
    is_default = Column(Integer)
    default_user_id = Column(Integer)
    result_symbol = Column(String(20, 'utf8_bin'))

    chain = relationship('TabApprovalModuleChain', primaryjoin='TabManApprovalNode.chain_id == TabApprovalModuleChain.chain_id', backref='tab_man_approval_nodes')
    users = relationship('TabBasicUser', secondary='tab_man_nodes_users_relation', backref='tab_man_approval_nodes')


class TabManApprovalProces(BaseAttach, DB_BASE):
    __tablename__ = 'tab_man_approval_process'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    role_id = Column(Integer, index=True)
    ticket_id = Column(Integer, index=True)
    message = Column(String(1000, 'utf8_bin'))
    module_name = Column(String(50, 'utf8_bin'))


t_tab_man_nodes_groups_relation = Table(
    'tab_man_nodes_groups_relation', metadata,
    Column('man_node_id', ForeignKey('tab_man_approval_nodes.man_node_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('group_id', ForeignKey('tab_user_groups.group_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_man_nodes_users_relation = Table(
    'tab_man_nodes_users_relation', metadata,
    Column('man_node_id', ForeignKey('tab_man_approval_nodes.man_node_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('user_id', ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabMonthSensorActivityRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_month_sensor_activity_record'
    __table_args__ = (
        Index('Index_3', 'user_name', 'zone_name'),
    )

    id = Column(Integer, primary_key=True)
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    user_name = Column(String(80, 'utf8_bin'), index=True)
    zone_name = Column(String(40, 'utf8_bin'), index=True)
    time = Column(DateTime, nullable=False, server_default=FetchedValue())
    time_span = Column(Integer)
    process_index = Column(Integer, server_default=FetchedValue())
    data_index = Column(Integer, server_default=FetchedValue())
    io_index = Column(Integer, server_default=FetchedValue())
    source_node_id = Column(String(36, 'utf8_bin'))


class TabMonthUserActivityRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_month_user_activity_record'
    __table_args__ = (
        Index('Index_3', 'user_name', 'zone_name'),
    )

    id = Column(Integer, primary_key=True)
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    user_name = Column(String(80, 'utf8_bin'), index=True)
    zone_name = Column(String(40, 'utf8_bin'), index=True)
    time = Column(DateTime, nullable=False, server_default=FetchedValue())
    time_span = Column(Integer)
    keyboard_index = Column(Integer, server_default=FetchedValue())
    mouse_index = Column(Integer, server_default=FetchedValue())
    screen_index = Column(Integer, server_default=FetchedValue())
    source_node_id = Column(String(36, 'utf8_bin'))


class TabNeighborIp(BaseAttach, DB_BASE):
    __tablename__ = 'tab_neighbor_ips'

    ip = Column(String(20, 'utf8_bin'), primary_key=True)


class TabNetSource(BaseAttach, DB_BASE):
    __tablename__ = 'tab_net_source'

    id = Column(Integer, primary_key=True)
    type = Column(Integer, nullable=False)
    ip = Column(String(20, 'utf8_bin'), nullable=False)
    access = Column(String(256, 'utf8_bin'), nullable=False)
    description = Column(String(1024, 'utf8_bin'), server_default=FetchedValue())


class TabNetworkAccessControlRule(BaseAttach, DB_BASE):
    __tablename__ = 'tab_network_access_control_rules'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    group_id = Column(Integer)
    ip = Column(String(20, 'utf8_bin'))
    mask = Column(String(20, 'utf8_bin'))
    server = Column(String(256, 'utf8_bin'))
    time_type = Column(String(30, 'utf8_bin'))
    begin_time = Column(String(10, 'utf8_bin'))
    end_time = Column(String(10, 'utf8_bin'))
    begin_day = Column(String(15, 'utf8_bin'))
    end_day = Column(String(15, 'utf8_bin'))
    control_type = Column(String(20, 'utf8_bin'))
    enable = Column(Integer)
    is_default = Column(Integer)
    priority = Column(Integer)
    description = Column(String(100, 'utf8_bin'))

    servers = relationship('TabWsaServerManage', secondary='tab_network_rule_server_relation', backref='tab_network_access_control_rules')
    users = relationship('TabBasicUser', secondary='tab_network_rule_user_relation', backref='tab_network_access_control_rules')
    usergroups = relationship('TabUserGroup', secondary='tab_network_rule_usergroup_relation', backref='tab_network_access_control_rules')


t_tab_network_rule_server_relation = Table(
    'tab_network_rule_server_relation', metadata,
    Column('rule_id', ForeignKey('tab_network_access_control_rules.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('server_id', ForeignKey('tab_wsa_server_manage.server_manage_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_network_rule_user_relation = Table(
    'tab_network_rule_user_relation', metadata,
    Column('rule_id', ForeignKey('tab_network_access_control_rules.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('user_id', ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_network_rule_usergroup_relation = Table(
    'tab_network_rule_usergroup_relation', metadata,
    Column('rule_id', ForeignKey('tab_network_access_control_rules.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('usergroup_id', ForeignKey('tab_user_groups.group_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabNetwork(BaseAttach, DB_BASE):
    __tablename__ = 'tab_networks'

    network_id = Column(Integer, primary_key=True)
    network_name = Column(String(40, 'utf8_bin'), nullable=False)
    protocol_type = Column(String(6, 'utf8_bin'))
    ip = Column(String(20, 'utf8_bin'))
    netmask = Column(String(20, 'utf8_bin'))
    gateway = Column(String(20, 'utf8_bin'))
    status = Column(Integer, server_default=FetchedValue())
    speed = Column(String(20, 'utf8_bin'))
    mac = Column(String(20, 'utf8_bin'))
    dns_type = Column(Integer)
    dns1 = Column(String(20, 'utf8_bin'))
    dns2 = Column(String(20, 'utf8_bin'))
    domain_search = Column(String(1000, 'utf8_bin'), server_default=FetchedValue())
    configed = Column(Integer, server_default=FetchedValue())

    zones = relationship('TabZone', secondary='tab_zone_network_relation', backref='tab_networks')


t_tab_node_default_down_report_config = Table(
    'tab_node_default_down_report_config', metadata,
    Column('node_id', ForeignKey('tab_nodes.node_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('service_id', ForeignKey('tab_data_report_service.service_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_node_default_up_report_config = Table(
    'tab_node_default_up_report_config', metadata,
    Column('node_id', ForeignKey('tab_nodes.node_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('service_id', ForeignKey('tab_data_report_service.service_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_node_field_relation = Table(
    'tab_node_field_relation', metadata,
    Column('field_id', ForeignKey('tab_fields.field_id', ondelete='CASCADE'), index=True),
    Column('node_id', ForeignKey('tab_nodes.node_id', ondelete='CASCADE'), index=True),
    Column('is_admin', Integer, server_default=FetchedValue())
)


class TabNode(BaseAttach, DB_BASE):
    __tablename__ = 'tab_nodes'

    node_id = Column(String(36, 'utf8_bin'), primary_key=True)
    name = Column(String(40, 'utf8_bin'), unique=True)
    type = Column(Integer)
    ip1 = Column(String(20, 'utf8_bin'))
    ip2 = Column(String(20, 'utf8_bin'))
    state = Column(Integer, server_default=FetchedValue())
    create_time = Column(DateTime)
    user_number = Column(Integer, server_default=FetchedValue())
    sensor_number = Column(Integer, server_default=FetchedValue())
    alarm_number = Column(Integer, server_default=FetchedValue())
    description = Column(String(200, 'utf8_bin'))
    location_level1 = Column(String(100, 'utf8_bin'))
    location_level2 = Column(String(100, 'utf8_bin'))
    location_level3 = Column(String(100, 'utf8_bin'))
    parent_node_id = Column(String(36, 'utf8_bin'))

    source_nodes = relationship(
        'TabNode',
        secondary='tab_data_report_relation',
        primaryjoin='TabNode.node_id == tab_data_report_relation.c.destination_node_id',
        secondaryjoin='TabNode.node_id == tab_data_report_relation.c.source_node_id',
        backref='tab_nodes'
    )
    services = relationship('TabDataReportService', secondary='tab_node_default_down_report_config', backref='tabdatareportservice_tab_nodes')
    services1 = relationship('TabDataReportService', secondary='tab_node_default_up_report_config', backref='tabdatareportservice_tab_nodes_0')


class TabSensorReport(BaseAttach, DB_BASE):
    __tablename__ = "tab_sensor_report"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    uuid = Column(String(64), nullable=False)
    report_name = Column(String(128), nullable=False, unique=True)
    report_format = Column(String(64), nullable=False, default="pdf")
    timed = Column(Integer, nullable=False, default=0)
    send_date = Column(String(64))
    data_scope = Column(String(64))
    sensor_group_ids = Column(String(128))
    user_group_ids = Column(String(128))
    send_email = Column(Text)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    create_time = Column(DateTime)


class TabSensorReportDetail(BaseAttach, DB_BASE):
    __tablename__ = "tab_sensor_report_detail"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    uuid = Column(String(64), nullable=False)
    custom_name = Column(String(256), nullable=False)
    page_source_name = Column(String(256), nullable=False)
    page_source_url = Column(Text, nullable=False)
    sort_number = Column(Integer, nullable=False)


class TabSensorSimpleConfiguration(TabNode):
    __tablename__ = 'tab_sensor_simple_configurations'

    node_id = Column(ForeignKey('tab_nodes.node_id', ondelete='CASCADE'), primary_key=True)
    screen_flag = Column(Integer)
    keyboard_flag = Column(Integer)
    frame_rate = Column(Integer)
    resolution = Column(String(30, 'utf8_bin'))


class TabNodesIssueConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_nodes_issue_config'

    id = Column(Integer, primary_key=True)
    module_name = Column(String(100, 'utf8_bin'), nullable=False)
    conf_marking = Column(String(100, 'utf8_bin'), nullable=False)
    tables = Column(String(2000, 'utf8_bin'), nullable=False)
    is_issued = Column(Integer, server_default=FetchedValue())
    is_forced = Column(Integer, server_default=FetchedValue())
    is_local_mod = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabNodesReportRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_nodes_report_record'

    path = Column(String(200, 'utf8_bin'), primary_key=True, nullable=False, server_default=FetchedValue())
    dev_id = Column(String(36, 'utf8_bin'), primary_key=True, nullable=False, server_default=FetchedValue())
    inode = Column(String(20, 'utf8_bin'))
    type = Column(String(20, 'utf8_bin'), server_default=FetchedValue())
    line_num = Column(Integer, server_default=FetchedValue())
    jump_flag = Column(Integer, server_default=FetchedValue())
    parent_node_id = Column(String(36, 'utf8_bin'))
    parent_node_ip = Column(String(20, 'utf8_bin'))
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabNodesSyncStatu(BaseAttach, DB_BASE):
    __tablename__ = 'tab_nodes_sync_status'

    id = Column(Integer, primary_key=True)
    flag = Column(Integer, server_default=FetchedValue())
    type = Column(Integer, server_default=FetchedValue())
    direction = Column(String(36, 'utf8_bin'))
    parent_node_id = Column(String(36, 'utf8_bin'))
    child_node_id = Column(String(36, 'utf8_bin'))
    msg = Column(Text(collation='utf8_bin'))
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabNodesTimingJuniorStatu(BaseAttach, DB_BASE):
    __tablename__ = 'tab_nodes_timing_junior_status'

    node_id = Column(String(36, 'utf8_bin'), primary_key=True, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabNsAcces(BaseAttach, DB_BASE):
    __tablename__ = 'tab_ns_access'

    src_id = Column(Integer, primary_key=True, nullable=False)
    policy_id = Column(Integer, primary_key=True, nullable=False)


class TabNsPolicy(BaseAttach, DB_BASE):
    __tablename__ = 'tab_ns_policy'

    id = Column(Integer, primary_key=True)
    user_name = Column(Text(collation='utf8_bin'))
    ip = Column(String(16, 'utf8_bin'))
    mask = Column(String(16, 'utf8_bin'))
    begin_time = Column(String(16, 'utf8_bin'))
    end_time = Column(String(16, 'utf8_bin'))
    begin_day = Column(String(16, 'utf8_bin'))
    end_day = Column(String(16, 'utf8_bin'))
    type = Column(String(64, 'utf8_bin'))
    access = Column(String(256, 'utf8_bin'))
    enable = Column(Integer, server_default=FetchedValue())
    description = Column(String(1024, 'utf8_bin'), server_default=FetchedValue())
    is_default = Column(Integer, server_default=FetchedValue())
    operate_time = Column(String(100, 'utf8_bin'), server_default=FetchedValue())


t_tab_other_device = Table(
    'tab_other_device', metadata,
    Column('ip', String(20, 'utf8_bin')),
    Column('name', String(50, 'utf8_bin'))
)


class TabPortProces(BaseAttach, DB_BASE):
    __tablename__ = 'tab_port_process'

    flow_type = Column(String(64, 'utf8_bin'), primary_key=True)
    port_list = Column(String(4096, 'utf8_bin'))


class TabPublicZone(BaseAttach, DB_BASE):
    __tablename__ = 'tab_public_zones'

    zone_id = Column(Integer, primary_key=True)
    zone_name = Column(String(40, 'utf8_bin'))
    description = Column(String(1000, 'utf8_bin'))
    enable = Column(Integer)
    audit_enable = Column(Integer)
    screen_audit_quota = Column(Integer)
    log_audit_quota = Column(Integer)
    quota_policy = Column(String(20, 'utf8_bin'))
    sftpport = Column(Integer)
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabRdpRuntime(BaseAttach, DB_BASE):
    __tablename__ = 'tab_rdp_runtime'

    dev_id = Column(String(40, 'utf8_bin'), primary_key=True, nullable=False)
    hostname = Column(String(40, 'utf8_bin'), primary_key=True, nullable=False)
    user = Column(String(80, 'utf8_bin'), primary_key=True, nullable=False)
    zonename = Column(String(40, 'utf8_bin'), primary_key=True, nullable=False)
    start_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    host_ip = Column(String(40, 'utf8_bin'), nullable=False)
    rdp_proxyport = Column(Integer, primary_key=True, nullable=False)
    failuretime = Column(Integer, server_default=FetchedValue())
    rdp_hostname = Column(String(40, 'utf8_bin'), primary_key=True, nullable=False)
    rdp_port = Column(Integer)
    online = Column(Integer, server_default=FetchedValue())
    client_ip = Column(String(40, 'utf8_bin'), nullable=False)
    client_port = Column(Integer)
    login_time = Column(DateTime)
    logout_time = Column(DateTime)


class TabRemoteCommunication(BaseAttach, DB_BASE):
    __tablename__ = 'tab_remote_communications'

    record_id = Column(String(36, 'utf8_bin'), primary_key=True)
    destination_type = Column(Integer)
    destination = Column(Text(collation='utf8_bin'))
    type = Column(Integer)
    content = Column(Text(collation='utf8_bin'))
    create_user = Column(String(80, 'utf8_bin'))
    create_node = Column(String(36, 'utf8_bin'))
    create_time = Column(DateTime)
    status = Column(Integer)
    status_description = Column(Text(collation='utf8_bin'))


t_tab_role_alarm_msg_type_relation = Table(
    'tab_role_alarm_msg_type_relation', metadata,
    Column('role_id', ForeignKey('tab_basic_roles.role_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('alarm_msg_type_id', ForeignKey('tab_alarm_msg_type.alarm_msg_type_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabRulesRunning(BaseAttach, DB_BASE):
    __tablename__ = 'tab_rules_running'

    rule_id = Column(String(36, 'utf8_bin'), primary_key=True)
    name = Column(String(50, 'utf8_bin'))
    create_time = Column(DateTime)
    last_modify_time = Column(DateTime)
    enable = Column(Integer, server_default=FetchedValue())
    status = Column(Integer, server_default=FetchedValue())
    status_description = Column(String(1000, 'utf8_bin'))
    status_time = Column(DateTime)
    expired = Column(Integer, server_default=FetchedValue())
    history_flag = Column(Integer, server_default=FetchedValue())
    last_success_timestamp = Column(DateTime)
    incremental_flag = Column(Integer, server_default=FetchedValue())
    use_timestamp = Column(Integer, server_default=FetchedValue())
    time_spec_start = Column(DateTime)
    time_spec_end = Column(DateTime)
    conditions = Column(Text(collation='utf8_bin'))
    is_delete = Column(Integer, server_default=FetchedValue())


class TabScreenFile(BaseAttach, DB_BASE):
    __tablename__ = 'tab_screen_files'

    screen_file_id = Column(Integer, primary_key=True)
    application_id = Column(ForeignKey('tab_applications.application_id', ondelete='CASCADE'), index=True)
    start_datetime = Column(DateTime, nullable=False, server_default=FetchedValue())
    length = Column(Integer)
    user_name = Column(String(80, 'utf8_bin'))
    zone_name = Column(String(40, 'utf8_bin'))
    network_name = Column(String(40, 'utf8_bin'))
    file_name = Column(String(200, 'utf8_bin'))
    file_size = Column(Integer)
    description = Column(String(1000, 'utf8_bin'))
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    source_node_id = Column(String(36, 'utf8_bin'))
    source_ip = Column(String(20, 'utf8_bin'))
    source_mac = Column(String(30, 'utf8_bin'))
    source_dev_id = Column(String(40, 'utf8_bin'))
    flag = Column(Integer, server_default=FetchedValue())
    origin = Column(String(10, 'utf8_bin'))

    application = relationship('TabApplication', primaryjoin='TabScreenFile.application_id == TabApplication.application_id', backref='tab_screen_files')


class TabSecurityItem(BaseAttach, DB_BASE):
    __tablename__ = 'tab_security_items'

    security_item_id = Column(Integer, primary_key=True)
    security_item_name = Column(String(40, 'utf8_bin'))
    description = Column(String(1000, 'utf8_bin'))

    zones = relationship('TabZone', secondary='tab_zone_securityitem_relation', backref='tab_security_items')


class TabSeniorItem(BaseAttach, DB_BASE):
    __tablename__ = 'tab_senior_items'

    senior_item_id = Column(Integer, primary_key=True)
    senior_item_name = Column(String(40, 'utf8_bin'))
    description = Column(String(1000, 'utf8_bin'))


class TabSensorActivityRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_activity_record'
    __table_args__ = (
        Index('Index_3', 'user_name', 'zone_name'),
    )

    id = Column(Integer, primary_key=True)
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    user_name = Column(String(80, 'utf8_bin'), index=True)
    zone_name = Column(String(40, 'utf8_bin'), index=True)
    time = Column(DateTime, nullable=False, server_default=FetchedValue())
    time_span = Column(Integer)
    process_index = Column(SmallInteger, server_default=FetchedValue())
    data_index = Column(SmallInteger, server_default=FetchedValue())
    io_index = Column(SmallInteger, server_default=FetchedValue())
    source_node_id = Column(String(36, 'utf8_bin'))


class TabSensorApp(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_app'

    app_id = Column(Integer, primary_key=True)
    type_id = Column(ForeignKey('tab_sensor_app_type.type_id', ondelete='CASCADE'), nullable=False, index=True)
    app_name = Column(String(200, 'utf8_bin'), nullable=False)
    enable = Column(Integer, nullable=False, server_default=FetchedValue())
    description = Column(Text(collation='utf8_bin'))
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    os = Column(String(50, 'utf8_bin'))

    type = relationship('TabSensorAppType', primaryjoin='TabSensorApp.type_id == TabSensorAppType.type_id', backref='tab_sensor_apps')

class TabSensorVmStrategy(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_vm_strategy'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    uuid = Column(String(64), nullable=False)
    template_uuid = Column(String(64))
    machine_type = Column(String(32), nullable=False, default="container")
    strategy = Column(String(32), nullable=False)
    sensor_group_ids = Column(String(128))
    is_default = Column(Integer, default=0, nullable=False)

    vm_name = Column(String(128))
    vm_image_id = Column(String(128))
    vm_image_name = Column(String(128))
    vm_image_md5 = Column(String(64))
    vm_image_path = Column(String(256))
    vm_strategy_type = Column(String(64))

    container_name = Column(String(128))
    container_image_id = Column(String(256))
    container_image_name = Column(String(128))
    container_host_name = Column(String(128))
    container_command = Column(Text)
    container_net_type = Column(String(128))
    container_net_info = Column(Text)

    strategy_comment = Column(Text)
    update_time = Column(DateTime, nullable=False)
    create_time = Column(DateTime, nullable=False)



class TabSensorAppType(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_app_type'

    type_id = Column(Integer, primary_key=True)
    type_name = Column(String(100, 'utf8_bin'), nullable=False, unique=True)
    is_default = Column(Integer, nullable=False, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    type_type = Column(String(64, 'utf8_bin'), nullable=False)


class TabSensorArpGroup(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_arp_group'

    group_id = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False)
    members = Column(String(128, 'utf8_bin'), primary_key=True, nullable=False)
    sensor_id = Column(String(64, 'utf8_bin'))


class TabSensorArpInfo(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_arp_info'

    mac = Column(String(128, 'utf8_bin'), primary_key=True)
    ip = Column(String(128, 'utf8_bin'), nullable=False)
    hostname = Column(String(256, 'utf8_bin'))
    type = Column(String(64, 'utf8_bin'), nullable=False)
    parent_node_mac = Column(String(64, 'utf8_bin'), nullable=False)
    create_time = Column(DateTime)
    sensor_id = Column(String(64, 'utf8_bin'))


class TabSensorBasicUserInfo(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_basic_user_info'

    sensor_id = Column(String(36, 'utf8_bin'), primary_key=True, server_default=FetchedValue())
    unit = Column(String(128, 'utf8_bin'))
    dept = Column(String(128, 'utf8_bin'))
    resp = Column(String(128, 'utf8_bin'))
    phone = Column(String(32, 'utf8_bin'))
    avatar = Column(Text(collation='utf8_bin'))
    create_time = Column(DateTime)
    is_lock = Column(Integer, server_default=FetchedValue())


class TabSensorConfigAlarm(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_alarm'

    name = Column(String(100, 'utf8_bin'), primary_key=True)
    value = Column(String(200, 'utf8_bin'))
    num = Column(Integer)
    update_time = Column(DateTime)


class TabSensorConfigBasic(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_basic'

    cfg_id = Column(String(36, 'utf8_bin'), primary_key=True, nullable=False)
    key_name = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False)
    key_value = Column(String(128, 'utf8_bin'))
    key_value2 = Column(String(128, 'utf8_bin'))
    update_time = Column(DateTime)


class TabSensorConfigDatum(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_data'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(String(36, 'utf8_bin'))
    rule_name = Column(String(36, 'utf8_bin'))
    data_path = Column(Text(collation='utf8_bin'))
    data_behavior_flag = Column(Integer)
    data_copy_flag = Column(Integer)
    data_alarm_flag = Column(Integer)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    create_time = Column(DateTime)


class TabSensorConfigFlag(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_flag'

    gid = Column(Integer, primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    io_flag = Column(Integer, server_default=FetchedValue())
    usb_flag = Column(Integer, server_default=FetchedValue())
    network_flag = Column(Integer, server_default=FetchedValue())
    user_behavior_flag = Column(Integer, server_default=FetchedValue())
    process_flag = Column(Integer, server_default=FetchedValue())
    net_port_flag = Column(Integer, server_default=FetchedValue())
    peripheral_port_flag = Column(Integer, server_default=FetchedValue())
    regedit_flag = Column(Integer, server_default=FetchedValue())
    keydata_flag = Column(Integer, server_default=FetchedValue())
    print_flag = Column(Integer, server_default=FetchedValue())
    system_flag = Column(Integer, server_default=FetchedValue())
    basic_flag = Column(Integer, server_default=FetchedValue())
    protocol_port_flag = Column(Integer, server_default=FetchedValue())
    other_flag = Column(Integer, server_default=FetchedValue())
    flow_flag = Column(Integer, server_default=FetchedValue())
    is_template = Column(Integer, server_default=FetchedValue())

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigFlag.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_flags')


class TabSensorConfigFlow(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_flow'

    gid = Column(Integer, primary_key=True)
    config_id = Column(String(40, 'utf8_bin'))
    name = Column(String(200, 'utf8_bin'))
    up_limit = Column(Integer)
    down_limit = Column(Integer)
    write_log = Column(Integer, server_default=FetchedValue())
    prevent = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime)


class TabSensorConfigFlowControl(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_flow_control'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    name = Column(String(128, 'utf8_bin'), nullable=False)
    protocol = Column(String(64, 'utf8_bin'))
    src_ip = Column(String(512, 'utf8_bin'))
    src_sensor_group = Column(String(512, 'utf8_bin'))
    src_user_group = Column(String(512, 'utf8_bin'))
    dest_ip = Column(String(512, 'utf8_bin'))
    dest_sensor_group = Column(String(512, 'utf8_bin'))
    dest_server_group = Column(String(512, 'utf8_bin'))
    dest_app_group = Column(String(512, 'utf8_bin'))
    dest_user_group = Column(String(512, 'utf8_bin'))
    level_id = Column(Integer)
    direction = Column(String(64, 'utf8_bin'))
    threshold_value = Column(String(64, 'utf8_bin'))
    flow_rule = Column(String(64, 'utf8_bin'))
    nic_type = Column(String(64, 'utf8_bin'))
    days = Column(Integer)
    valid = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabSensorConfigIo(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_io'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    rule_name = Column(String(36, 'utf8_bin'))
    io_devicetype = Column(String(200, 'utf8_bin'))
    io_behavior_flag = Column(Integer)
    io_readonly_flag = Column(Integer)
    io_prevent_flag = Column(Integer)
    io_alarm_flag = Column(Integer)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    device_access_flag = Column(Integer)
    create_time = Column(DateTime)

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigIo.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_ios')


class TabSensorConfigKeydatum(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_keydata'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    description = Column(String(36, 'utf8_bin'))
    data_path = Column(Text(collation='utf8_bin'))
    data_prevent_flag = Column(Integer)
    data_alarm_flag = Column(Integer)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    os = Column(String(50, 'utf8_bin'))

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigKeydatum.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_keydata')


class TabSensorConfigLastVersion(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_last_version'

    sensor_id = Column(String(48, 'utf8_bin'), primary_key=True)
    config_version = Column(String(48, 'utf8_bin'))


class TabSensorConfigNetPort(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_net_port'

    gid = Column(Integer, primary_key=True)
    name = Column(String(128, 'utf8_bin'), nullable=False)
    protocol = Column(String(64, 'utf8_bin'))
    src_ip = Column(String(512, 'utf8_bin'))
    src_sensor_group = Column(String(512, 'utf8_bin'))
    src_user_group = Column(String(512, 'utf8_bin'))
    dest_ip = Column(String(512, 'utf8_bin'))
    dest_sensor_group = Column(String(512, 'utf8_bin'))
    dest_server_group = Column(String(512, 'utf8_bin'))
    dest_app_group = Column(String(512, 'utf8_bin'))
    dest_user_group = Column(String(512, 'utf8_bin'))
    port_range = Column(String(512, 'utf8_bin'))
    control = Column(String(64, 'utf8_bin'))
    level_id = Column(Integer)
    direction = Column(String(64, 'utf8_bin'))
    nic_type = Column(String(64, 'utf8_bin'))
    days = Column(Integer)
    valid = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    is_default = Column(Integer, server_default=FetchedValue())


class TabSensorConfigNetworkAddres(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_network_address'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    network_address = Column(String(30, 'utf8_bin'))
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigNetworkAddres.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_network_address')


class TabSensorConfigNetworkFlag(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_network_flag'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    network_flag = Column(Integer)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigNetworkFlag.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_network_flags')


class TabSensorConfigOther(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_other'

    config_id = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False)
    name = Column(String(128, 'utf8_bin'), primary_key=True, nullable=False)
    v1 = Column(String(64, 'utf8_bin'))
    v2 = Column(String(64, 'utf8_bin'))
    v3 = Column(String(64, 'utf8_bin'))
    v4 = Column(String(64, 'utf8_bin'))
    v5 = Column(String(1024, 'utf8_bin'))
    v6 = Column(String(1024, 'utf8_bin'))
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabSensorConfigPeripheralPort(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_peripheral_port'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    name = Column(String(50, 'utf8_bin'))
    data_prevent_flag = Column(Integer)
    io_readonly_flag = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigPeripheralPort.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_peripheral_ports')


class TabSensorConfigProces(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_process'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    name = Column(String(50, 'utf8_bin'))
    data_prevent_flag = Column(Integer)
    data_alarm_flag = Column(Integer)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigProces.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_process')


class TabSensorConfigProtocolPort(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_protocol_port'

    config_id = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False, server_default=FetchedValue())
    protocol = Column(String(32, 'utf8_bin'), primary_key=True, nullable=False, server_default=FetchedValue())
    switch = Column(Integer, server_default=FetchedValue())
    ports = Column(String(1024, 'utf8_bin'))
    period = Column(String(64, 'utf8_bin'))
    count = Column(Integer)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabSensorConfigRegedit(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_regedit'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    description = Column(String(256, 'utf8_bin'))
    data_path = Column(Text(collation='utf8_bin'))
    data_prevent_flag = Column(Integer)
    data_alarm_flag = Column(Integer)
    is_default = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigRegedit.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_regedits')


class TabSensorConfigSoftwareDistribute(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_software_distribute'

    guid = Column(Integer, primary_key=True)
    file_id = Column(ForeignKey('tab_sensor_softwares.guid', ondelete='CASCADE'), nullable=False, index=True)
    filepath = Column(String(128, 'utf8_bin'))
    sensor_id = Column(String(32, 'utf8_bin'))
    sensor_group_id = Column(Integer)
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())

    file = relationship('TabSensorSoftware', primaryjoin='TabSensorConfigSoftwareDistribute.file_id == TabSensorSoftware.guid', backref='tab_sensor_config_software_distributes')


class TabSensorConfigSoftwareInstall(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_software_install'

    guid = Column(Integer, primary_key=True)
    file_id = Column(ForeignKey('tab_sensor_softwares.guid', ondelete='CASCADE'), nullable=False, index=True)
    install_type = Column(String(32, 'utf8_bin'), server_default=FetchedValue())
    sensor_id = Column(String(32, 'utf8_bin'))
    sensor_group_id = Column(Integer)
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())

    file = relationship('TabSensorSoftware', primaryjoin='TabSensorConfigSoftwareInstall.file_id == TabSensorSoftware.guid', backref='tab_sensor_config_software_installs')


class TabSensorConfigSurveillance(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_surveillance'

    surveillance_id = Column(String(36, 'utf8_bin'), primary_key=True)
    name = Column(String(100, 'utf8_bin'))
    user_name = Column(String(50, 'utf8_bin'))
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    is_default = Column(Integer, server_default=FetchedValue())
    description = Column(String(200, 'utf8_bin'))
    is_template = Column(Integer, server_default=FetchedValue())


class TabSensorConfigSurveillanceSensorRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_surveillance_sensor_relation'

    id = Column(Integer, primary_key=True)
    surveillance_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    sensor_id = Column(String(36, 'utf8_bin'))

    surveillance = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigSurveillanceSensorRelation.surveillance_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_surveillance_sensor_relations')


class TabSensorConfigSurveillanceSensorgroupRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_surveillance_sensorgroup_relation'

    id = Column(Integer, primary_key=True)
    surveillance_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    group_id = Column(Integer)

    surveillance = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigSurveillanceSensorgroupRelation.surveillance_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_surveillance_sensorgroup_relations')


class TabSensorConfigSystemDetail(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_system_detail'

    cfg_id = Column(String(36, 'utf8_bin'), primary_key=True, nullable=False)
    switch_name = Column(String(128, 'utf8_bin'), primary_key=True, nullable=False)
    switch = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime)


class TabSensorConfigUsbAdvance(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_usb_advance'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), index=True)
    vendor_id = Column(String(50, 'utf8_bin'))
    product_id = Column(String(50, 'utf8_bin'))
    prevent_flag = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigUsbAdvance.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_usb_advances')


class TabSensorConfigUserBehavior(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_user_behavior'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(ForeignKey('tab_sensor_config_surveillance.surveillance_id', ondelete='CASCADE'), nullable=False, index=True)
    screen_flag = Column(Integer, server_default=FetchedValue())
    keyboard_flag = Column(Integer, server_default=FetchedValue())
    frame_rate = Column(Integer, server_default=FetchedValue())
    resolution = Column(String(10, 'utf8_bin'), server_default=FetchedValue())
    video_gray = Column(Integer, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())

    config = relationship('TabSensorConfigSurveillance', primaryjoin='TabSensorConfigUserBehavior.config_id == TabSensorConfigSurveillance.surveillance_id', backref='tab_sensor_config_user_behaviors')


class TabSensorConfigVersion(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_version'

    name = Column(String(32, 'utf8_bin'), primary_key=True, server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabSensorConfigWhitelist(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_config_whitelist'

    gid = Column(String(36, 'utf8_bin'), primary_key=True)
    config_id = Column(String(36, 'utf8_bin'))
    white_list = Column(Text(collation='utf8_bin'))
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class TabSensorCredibleAppLib(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_credible_app_lib'

    id = Column(Integer, primary_key=True)
    app_name = Column(String(128, 'utf8_bin'), nullable=False)
    baseline_type = Column(String(32, 'utf8_bin'))
    baseline_type_value = Column(String(512, 'utf8_bin'))
    baseline_para = Column(String(128, 'utf8_bin'))
    key_word = Column(String(32, 'utf8_bin'))


class TabSensorCredibleAppStrategy(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_credible_app_strategy'

    id = Column(Integer, primary_key=True)
    strategy_name = Column(String(32, 'utf8_bin'), nullable=False)
    app_ids = Column(String(128, 'utf8_bin'))
    sensor_group_ids = Column(String(128, 'utf8_bin'))
    control = Column(String(32, 'utf8_bin'))
    is_default = Column(Integer, server_default=FetchedValue())
    enable = Column(Integer)


class TabSensorCredibleDatum(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_credible_data'

    id = Column(Integer, primary_key=True)
    baseline_name = Column(String(32, 'utf8_bin'), nullable=False)
    key_data_path = Column(String(512, 'utf8_bin'))
    app_ids = Column(String(128, 'utf8_bin'))
    sensor_group_ids = Column(String(128, 'utf8_bin'))
    operate_permission = Column(String(32, 'utf8_bin'))
    control = Column(String(32, 'utf8_bin'))
    is_default = Column(Integer, server_default=FetchedValue())
    enable = Column(Integer)


class TabSensorCredibleNetworkControl(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_credible_network_control'

    id = Column(Integer, primary_key=True)
    strategy_name = Column(String(32, 'utf8_bin'), nullable=False)
    app_ids = Column(String(128, 'utf8_bin'))
    sensor_group_ids = Column(String(128, 'utf8_bin'))
    direction = Column(String(32, 'utf8_bin'))
    ips = Column(String(512, 'utf8_bin'))
    ports = Column(String(512, 'utf8_bin'))
    protocol = Column(String(32, 'utf8_bin'))
    control = Column(String(32, 'utf8_bin'))
    is_default = Column(Integer, server_default=FetchedValue())
    enable = Column(Integer)


class TabSensorCrediblePortControl(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_credible_port_control'

    id = Column(Integer, primary_key=True)
    strategy_name = Column(String(32, 'utf8_bin'), nullable=False)
    app_ids = Column(String(128, 'utf8_bin'), nullable=False)
    sensor_group_ids = Column(String(128, 'utf8_bin'), nullable=False)
    ports = Column(String(512, 'utf8_bin'), nullable=False)
    protocol = Column(String(32, 'utf8_bin'), nullable=False)
    control = Column(String(32, 'utf8_bin'))
    enable = Column(Integer)
    is_default = Column(Integer, server_default=FetchedValue())


class TabSensorCurrentUser(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_current_user'

    sensor_id = Column(String(36, 'utf8_bin'), primary_key=True, nullable=False, server_default=FetchedValue())
    user_name = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False, server_default=FetchedValue())
    remote_ip = Column(String(16, 'utf8_bin'))
    session_id = Column(Integer)
    remote_login = Column(Integer)
    remote_computer_name = Column(String(128, 'utf8_bin'))
    remote_active = Column(Integer)
    logon_time = Column(DateTime)
    logon_domain = Column(String(128, 'utf8_bin'), primary_key=True, nullable=False, server_default=FetchedValue())


class TabSensorDataScope(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_data_scope'

    data_scope_id = Column(Integer, primary_key=True)
    data_scope_name = Column(String(255, 'utf8_bin'))
    os_type = Column(Text(collation='utf8_bin'))
    sensor_group_id = Column(String(255, 'utf8_bin'))
    sensor_file_type = Column(String(255, 'utf8_bin'))


class TabSensorDebugConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_debug_config'

    uuid = Column(String(64, 'utf8_bin'))
    sensor_id = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False, server_default=FetchedValue())
    module_id = Column(Integer, primary_key=True, nullable=False, server_default=FetchedValue())
    level = Column(Integer)
    modified_time = Column(DateTime, nullable=False, server_default=FetchedValue())


t_tab_sensor_group_relation = Table(
    'tab_sensor_group_relation', metadata,
    Column('group_id', ForeignKey('tab_sensor_groups.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('sensor_id', ForeignKey('tab_sensors.sensor_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabSensorGroup(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(100, 'utf8_bin'))
    remark = Column(String(200, 'utf8_bin'))
    config_id = Column(String(36, 'utf8_bin'), server_default=FetchedValue())
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    expanded = Column(Integer, server_default=FetchedValue())
    parent_group_id = Column(Integer)
    surveillance_mode = Column(Integer)

    sensors = relationship('TabSensor', secondary='tab_sensor_group_relation', backref='tab_sensor_groups')


class TabSensorHistoryUser(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_history_user'

    sensor_id = Column(String(36, 'utf8_bin'), primary_key=True)
    user_name = Column(String(64, 'utf8_bin'), nullable=False)
    remote_ip = Column(String(20, 'utf8_bin'))
    session_id = Column(Integer)
    remote_login = Column(Integer)
    remote_computer_name = Column(String(128, 'utf8_bin'))
    remote_active = Column(Integer)
    logon_time = Column(DateTime)
    logon_domain = Column(String(128, 'utf8_bin'), nullable=False)


class TabSensorIcon(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_icon'

    id = Column(Integer, primary_key=True)
    name = Column(String(256, 'utf8_bin'))
    ip = Column(String(32, 'utf8_bin'))
    path = Column(String(512, 'utf8_bin'))
    type = Column(String(128, 'utf8_bin'))
    order_num = Column(Integer)
    group_name = Column(String(256, 'utf8_bin'))
    data_prevent_flag = Column(Integer, server_default=FetchedValue())


class TabSensorId(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_id'

    sensor_id = Column(String(64, 'utf8_bin'), primary_key=True)
    sys_id = Column(String(64, 'utf8_bin'), nullable=False)
    hw_id = Column(String(64, 'utf8_bin'), nullable=False)
    mac_list = Column(String(128, 'utf8_bin'), nullable=False)


class TabSensorImage(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_images'

    id = Column(Integer, primary_key=True)
    os_type = Column(String(30, 'utf8_bin'))
    version = Column(String(20, 'utf8_bin'))
    upload_time = Column(DateTime)
    name = Column(String(100, 'utf8_bin'))
    file_url = Column(String(100, 'utf8_bin'))


class TabSensorInfoPcFraction(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_info_pc_fraction'

    sensor_id = Column(String(36, 'utf8_bin'), primary_key=True, server_default=FetchedValue())
    cpu_fraction = Column(Integer)
    mem_fraction = Column(Integer)
    disk_fraction = Column(Integer)
    port_fraction = Column(Integer)
    antivirus_fraction = Column(Integer)
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabSensorKnowledgeBase(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_knowledge_base'

    id = Column(Integer, primary_key=True)
    knowledge_base_name = Column(String(20, 'utf8_bin'), nullable=False)
    now_version = Column(String(20, 'utf8_bin'), nullable=False)
    old_version = Column(String(20, 'utf8_bin'))
    exchange_time = Column(DateTime)
    enable = Column(Integer, server_default=FetchedValue())


class TabSensorLogAntivirusOutdate(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_log_antivirus_outdate'

    sensor_id = Column(String(64, 'utf8_bin'), primary_key=True)
    desc = Column(String(1024, 'utf8_bin'))
    time = Column(String(64, 'utf8_bin'))
    level = Column(String(64, 'utf8_bin'))
    format = Column(String(64, 'utf8_bin'))


class TabSensorLogAntivirusStatu(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_log_antivirus_status'

    sensor_id = Column(String(64, 'utf8_bin'), primary_key=True)
    antivirus_info = Column(Text(collation='utf8_bin'))
    time = Column(String(64, 'utf8_bin'))
    level = Column(String(64, 'utf8_bin'))
    format = Column(String(64, 'utf8_bin'))


class TabSensorLogCurrentAutorun(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_log_current_autorun'

    sensor_id = Column(String(64, 'utf8_bin'), primary_key=True)
    autoruns = Column(Text(collation='utf8_bin'))
    time = Column(String(64, 'utf8_bin'))
    level = Column(String(64, 'utf8_bin'))
    format = Column(String(64, 'utf8_bin'))


class TabSensorLogCurrentService(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_log_current_service'

    sensor_id = Column(String(64, 'utf8_bin'), primary_key=True)
    autoruns = Column(Text(collation='utf8_bin'))
    time = Column(String(64, 'utf8_bin'))
    level = Column(String(64, 'utf8_bin'))
    format = Column(String(64, 'utf8_bin'))


t_tab_sensor_log_current_service_detail = Table(
    'tab_sensor_log_current_service_detail', metadata,
    Column('sensor_id', String(64, 'utf8_bin')),
    Column('level', String(64, 'utf8_bin')),
    Column('time', String(64, 'utf8_bin')),
    Column('service_name', String(64, 'utf8_bin')),
    Column('service_description', Text(collation='utf8_bin')),
    Column('caption', String(512, 'utf8_bin')),
    Column('command_line', String(512, 'utf8_bin'))
)


class TabSensorLogInfo(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_log_info'

    sensor_id = Column(String(64, 'utf8_bin'), primary_key=True)
    sys_id = Column(String(64, 'utf8_bin'))
    hw_id = Column(String(64, 'utf8_bin'))
    hw_cfg = Column(Text(collation='utf8_bin'))
    sw_cfg = Column(Text(collation='utf8_bin'))
    time = Column(String(64, 'utf8_bin'))
    level = Column(String(64, 'utf8_bin'))
    format = Column(String(64, 'utf8_bin'))


class TabSensorLogPortMonitor(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_log_port_monitor'

    sensor_id = Column(String(64, 'utf8_bin'), primary_key=True)
    portlist = Column(Text(collation='utf8_bin'))
    time = Column(String(64, 'utf8_bin'))
    level = Column(String(64, 'utf8_bin'))
    format = Column(String(64, 'utf8_bin'))


t_tab_sensor_log_process = Table(
    'tab_sensor_log_process', metadata,
    Column('sensor_id', String(36, 'utf8_bin')),
    Column('exe_name', String(128, 'utf8_bin')),
    Column('session_id', Integer),
    Column('pid', Integer),
    Column('exe_path', String(256, 'utf8_bin')),
    Column('user_name', String(64, 'utf8_bin')),
    Column('user_name_ex', String(128, 'utf8_bin')),
    Column('pro_start_time', DateTime),
    Column('parent_name', String(128, 'utf8_bin')),
    Column('ppid', Integer),
    Column('exe_desc', String(512, 'utf8_bin')),
    Column('exe_publisher', String(128, 'utf8_bin')),
    Column('exe_ver', String(64, 'utf8_bin')),
    Column('exe_modify_time', DateTime),
    Column('exe_signature', String(16, 'utf8_bin')),
    Column('app_group_name', String(64, 'utf8_bin')),
    Column('mem_usage', String(16, 'utf8_bin'))
)


class TabSensorLogShowConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_log_show_config'

    id = Column(Integer, primary_key=True)
    page_size = Column(Integer, server_default=FetchedValue())
    export_size = Column(Integer, server_default=FetchedValue())


t_tab_sensor_log_status = Table(
    'tab_sensor_log_status', metadata,
    Column('sensor_id', String(64, 'utf8_bin')),
    Column('time', String(64, 'utf8_bin')),
    Column('format', String(64, 'utf8_bin')),
    Column('level', String(64, 'utf8_bin')),
    Column('node_id', String(64, 'utf8_bin')),
    Column('status', String(64, 'utf8_bin')),
    Column('operator', String(64, 'utf8_bin')),
    Column('exe_name', String(64, 'utf8_bin')),
    Column('ip', String(64, 'utf8_bin')),
    Column('operation', String(64, 'utf8_bin')),
    Column('operate_object', String(64, 'utf8_bin')),
    Column('operation_result', String(64, 'utf8_bin')),
    Column('operation_description', String(1024, 'utf8_bin'))
)


t_tab_sensor_log_switch = Table(
    'tab_sensor_log_switch', metadata,
    Column('name', String(20, 'utf8_bin')),
    Column('enable', Integer)
)


t_tab_sensor_log_vm_installed = Table(
    'tab_sensor_log_vm_installed', metadata,
    Column('sensor_id', String(48, 'utf8_bin')),
    Column('vm_name', String(48, 'utf8_bin')),
    Column('vm_install_date', String(48, 'utf8_bin')),
    Column('vm_version', String(48, 'utf8_bin')),
    Column('desc', String(1024, 'utf8_bin')),
    Column('log_id', String(48, 'utf8_bin')),
    Column('level_ex', String(48, 'utf8_bin')),
    Column('event_type', String(48, 'utf8_bin')),
    Column('product_type', String(48, 'utf8_bin')),
    Column('behaviour_type', String(48, 'utf8_bin')),
    Column('format', String(48, 'utf8_bin')),
    Column('time', String(48, 'utf8_bin'))
)


class TabSensorMonitorRule(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_monitor_rule'

    rule_id = Column(String(36, 'utf8_bin'), primary_key=True)
    rule_type = Column(String(50, 'utf8_bin'), nullable=False)
    description = Column(String(100, 'utf8_bin'), nullable=False)
    enable = Column(Integer, nullable=False)
    rule_condition = Column(String(2000, 'utf8_bin'), nullable=False)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    publish = Column(Integer, server_default=FetchedValue())
    sensor_ids = Column(Text(collation='utf8_bin'))
    reason = Column(String(1000, 'utf8_bin'))
    rule = Column(Text(collation='utf8_bin'))
    name_list_id = Column(Integer)


class TabSensorMonitorRuleGroupRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_monitor_rule_group_relation'

    id = Column(Integer, primary_key=True)
    rule_id = Column(ForeignKey('tab_sensor_monitor_rule.rule_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    group_id = Column(ForeignKey('tab_sensor_groups.id', ondelete='CASCADE'), index=True)

    group = relationship('TabSensorGroup', primaryjoin='TabSensorMonitorRuleGroupRelation.group_id == TabSensorGroup.id', backref='tab_sensor_monitor_rule_group_relations')
    rule = relationship('TabSensorMonitorRule', primaryjoin='TabSensorMonitorRuleGroupRelation.rule_id == TabSensorMonitorRule.rule_id', backref='tab_sensor_monitor_rule_group_relations')


class TabSensorMonitorRuleSensorRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_monitor_rule_sensor_relation'

    id = Column(Integer, primary_key=True)
    rule_id = Column(String(36, 'utf8_bin'))
    sensor_id = Column(String(36, 'utf8_bin'))


class TabSensorNetworkSource(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_network_source'

    id = Column(Integer, primary_key=True)
    name = Column(String(100, 'utf8_bin'), unique=True)
    type = Column(Integer, nullable=False)
    sensitive_level = Column(Integer)
    source = Column(String(2000, 'utf8_bin'))
    comment = Column(String(512, 'utf8_bin'))
    is_default = Column(Integer)
    update_time = Column(DateTime)


class TabSensorOpenPortManagement(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_open_port_management'

    id = Column(Integer, primary_key=True)
    sensor_group_ids = Column(String(128, 'utf8_bin'))
    port_name = Column(String(128, 'utf8_bin'), nullable=False)
    protocol = Column(String(32, 'utf8_bin'))
    ports = Column(String(512, 'utf8_bin'))
    control = Column(String(32, 'utf8_bin'))
    is_default = Column(Integer, server_default=FetchedValue())
    enable = Column(Integer)


class TabSensorPatch(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_patch'

    guid = Column(String(64, 'utf8_bin'), primary_key=True)
    id = Column(String(64, 'utf8_bin'), nullable=False)
    is_x86 = Column(Integer, server_default=FetchedValue())
    title = Column(String(512, 'utf8_bin'), nullable=False)
    description = Column(String(2048, 'utf8_bin'), nullable=False, server_default=FetchedValue())
    classify = Column(String(64, 'utf8_bin'), nullable=False, server_default=FetchedValue())
    produce = Column(String(256, 'utf8_bin'), nullable=False, server_default=FetchedValue())
    msrc_level = Column(String(128, 'utf8_bin'), nullable=False, server_default=FetchedValue())
    msrc_num = Column(String(64, 'utf8_bin'), nullable=False, server_default=FetchedValue())
    more = Column(String(256, 'utf8_bin'), nullable=False, server_default=FetchedValue())
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabSensorPatchGroupRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_patch_group_relation'

    group_id = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False)
    patch_guid = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False)
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabSensorPatchInfo(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_patch_infos'

    sid = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False)
    patch_guid = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False)
    installed = Column(Integer, server_default=FetchedValue())


class TabSensorSoftware(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_softwares'

    guid = Column(String(128, 'utf8_bin'), primary_key=True)
    filedes = Column(String(64, 'utf8_bin'))
    filepath = Column(String(128, 'utf8_bin'))
    normal_cmd = Column(String(256, 'utf8_bin'))
    quiet_cmd = Column(String(256, 'utf8_bin'))


t_tab_sensor_user_tag_relation = Table(
    'tab_sensor_user_tag_relation', metadata,
    Column('sensor_id', String(36, 'utf8_bin')),
    Column('tag_text', String(255, 'utf8_bin')),
    Column('tag_shape', String(20, 'utf8_bin')),
    Column('user_id', Integer)
)


class TabSensorViolationConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_violation_config'

    id = Column(Integer, primary_key=True)
    period = Column(String(10, 'utf8_bin'))
    flow_num = Column(Integer)
    unit = Column(String(10, 'utf8_bin'))
    history_alarm = Column(Integer)
    update_flag = Column(Integer)
    type = Column(ENUM('network', 'removeable', 'server'))
    flow_direction = Column(ENUM('up', 'down'))


class TabSensorViolationRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_violation_record'

    record_id = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False)
    create_time = Column(DateTime, nullable=False)
    type_id = Column(String(64, 'utf8_bin'), primary_key=True, nullable=False)
    sensor_id = Column(String(64, 'utf8_bin'), nullable=False)
    user_name = Column(String(256, 'utf8_bin'), server_default=FetchedValue())
    ip = Column(String(64, 'utf8_bin'), server_default=FetchedValue())
    alarm_rel_id = Column(String(128, 'utf8_bin'), nullable=False)
    alarm_reason = Column(String(1024, 'utf8_bin'), server_default=FetchedValue())
    relevance_sensors = Column(Text(collation='utf8_bin'))
    sensor_alarm_type = Column(Integer, server_default=FetchedValue())
    reset_flag = Column(Integer, server_default=FetchedValue())


class TabSensorWhitelistRelatedExe(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_whitelist_related_exe'

    id = Column(Integer, primary_key=True)
    app_name = Column(String(40, 'utf8_bin'))
    related_exe_list = Column(String(512, 'utf8_bin'))
    saveas_list = Column(String(1024, 'utf8_bin'), server_default=FetchedValue())


t_tab_sensor_zone_relation = Table(
    'tab_sensor_zone_relation', metadata,
    Column('zone_id', ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), index=True),
    Column('sensor_id', ForeignKey('tab_sensors.sensor_id', ondelete='CASCADE'), primary_key=True)
)


class TabSensor(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensors'

    sensor_id = Column(String(36, 'utf8_bin'), primary_key=True)
    node_id = Column(String(36, 'utf8_bin'))
    dev_id = Column(String(36, 'utf8_bin'))
    name = Column(String(30, 'utf8_bin'))
    ip = Column(String(20, 'utf8_bin'))
    mask = Column(String(20, 'utf8_bin'))
    ip6 = Column(String(64, 'utf8_bin'))
    create_time = Column(DateTime)
    mac = Column(String(30, 'utf8_bin'))
    state = Column(Integer, server_default=FetchedValue())
    special_audit = Column(Integer)
    description = Column(String(200, 'utf8_bin'))
    machine = Column(String(30, 'utf8_bin'))
    computer_info = Column(String(128, 'utf8_bin'))
    os_type = Column(String(30, 'utf8_bin'))
    version = Column(String(30, 'utf8_bin'))
    server_ip = Column(String(20, 'utf8_bin'))
    state_update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    challenge = Column(String(32, 'utf8_bin'))
    seed = Column(String(32, 'utf8_bin'))
    action = Column(String(128, 'utf8_bin'), server_default=FetchedValue())
    relative_sensors = Column(String(2000, 'utf8_bin'), server_default=FetchedValue())
    config_sensors = Column(String(2000, 'utf8_bin'), server_default=FetchedValue())

    zones = relationship('TabZone', secondary='tab_sensor_zone_relation', backref='tab_sensors')


class TabSensorBinding(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_binding'

    sensor_id = Column(ForeignKey('tab_sensors.sensor_id', ondelete='CASCADE'), primary_key=True)
    ip = Column(String(50, 'utf8_bin'))
    mac = Column(String(50, 'utf8_bin'))
    update_time = Column(DateTime, nullable=False, server_default=FetchedValue())


class TabService(BaseAttach, DB_BASE):
    __tablename__ = 'tab_services'

    id = Column(Integer, primary_key=True)
    dev_id = Column(String(40, 'utf8_bin'))
    display_name = Column(String(30, 'utf8_bin'))
    service_name = Column(String(30, 'utf8_bin'))
    type = Column(String(20, 'utf8_bin'))
    service_status = Column(Integer, server_default=FetchedValue())
    restart_times = Column(Integer, server_default=FetchedValue())
    last_restart_time = Column(DateTime)
    update_time = Column(DateTime)
    last_check_time = Column(DateTime)


class TabServicesConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_services_config'

    id = Column(Integer, primary_key=True)
    display_name = Column(String(30, 'utf8_bin'))
    service_name = Column(String(30, 'utf8_bin'))
    type = Column(String(20, 'utf8_bin'))


class TabSmsConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sms_config'

    id = Column(Integer, primary_key=True)
    nexmo_nkey = Column(String(256, 'utf8_bin'))
    nexmo_nsecret = Column(String(256, 'utf8_bin'))
    nexmo_fromtel = Column(String(256, 'utf8_bin'))
    aliyun_akey = Column(String(256, 'utf8_bin'))
    aliyun_asecret = Column(String(256, 'utf8_bin'))
    aliyun_sign_name = Column(String(256, 'utf8_bin'))
    aliyun_sms_template = Column(String(256, 'utf8_bin'))
    description = Column(String(256, 'utf8_bin'))


class TabSmtpConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_smtp_config'

    id = Column(Integer, primary_key=True)
    mail_account = Column(String(128, 'utf8_bin'))
    mail_password = Column(String(128, 'utf8_bin'))
    mail_smtpserver = Column(String(128, 'utf8_bin'))
    mail_user = Column(String(128, 'utf8_bin'))
    flag = Column(Integer)
    port = Column(Integer, server_default=FetchedValue())
    domain = Column(String(256, 'utf8_bin'), nullable=False, server_default=FetchedValue())


t_tab_svr_run_config = Table(
    'tab_svr_run_config', metadata,
    Column('name', String(50, 'utf8_bin')),
    Column('value', String(200, 'utf8_bin'))
)


class TabSystemHardwareStatu(BaseAttach, DB_BASE):
    __tablename__ = 'tab_system_hardware_status'

    id = Column(Integer, primary_key=True)
    ip = Column(String(32, 'utf8_bin'), nullable=False)
    network_card_status = Column(String(20, 'utf8_bin'))
    disk_status = Column(String(20, 'utf8_bin'))
    bios_status = Column(String(20, 'utf8_bin'))
    time = Column(DateTime)
    time_cost = Column(Integer)
    description = Column(Text(collation='utf8_bin'))


class TabSystemPort(BaseAttach, DB_BASE):
    __tablename__ = 'tab_system_port'

    id = Column(Integer, primary_key=True)
    start_port = Column(Integer, nullable=False)
    end_port = Column(Integer, nullable=False)
    module = Column(String(256, 'utf8_bin'))
    description = Column(String(256, 'utf8_bin'))


class TabSystemUpdate(BaseAttach, DB_BASE):
    __tablename__ = 'tab_system_update'

    id = Column(Integer, primary_key=True)
    type = Column(Integer)
    file_name = Column(String(500, 'utf8_bin'))
    version = Column(String(30, 'utf8_bin'))
    dev_version = Column(Integer)
    status = Column(Integer, server_default=FetchedValue())
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    description = Column(String(5000, 'utf8_bin'))


t_tab_systemuser_field_relation = Table(
    'tab_systemuser_field_relation', metadata,
    Column('field_id', ForeignKey('tab_fields.field_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('systemuser_id', ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabSystemuserZoneRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_systemuser_zone_relation'

    zone_id = Column(ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    role_id = Column(ForeignKey('tab_basic_roles.role_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    systemuser_id = Column(ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)

    role = relationship('TabBasicRole', primaryjoin='TabSystemuserZoneRelation.role_id == TabBasicRole.role_id', backref='tab_systemuser_zone_relations')
    systemuser = relationship('TabBasicUser', primaryjoin='TabSystemuserZoneRelation.systemuser_id == TabBasicUser.user_id', backref='tab_systemuser_zone_relations')
    zone = relationship('TabZone', primaryjoin='TabSystemuserZoneRelation.zone_id == TabZone.zone_id', backref='tab_systemuser_zone_relations')


class TabTaskStatu(BaseAttach, DB_BASE):
    __tablename__ = 'tab_task_status'

    task_id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False, unique=True, server_default=FetchedValue())
    task_status = Column(SmallInteger, server_default=FetchedValue())


class TabTaskStatusDetail(BaseAttach, DB_BASE):
    __tablename__ = 'tab_task_status_detail'
    __table_args__ = (
        Index('user_zone', 'user_name', 'zone_name', 'time'),
    )

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, nullable=False)
    user_name = Column(String(80, 'utf8_bin'))
    time = Column(DateTime, nullable=False, server_default=FetchedValue())
    task_status = Column(SmallInteger, server_default=FetchedValue())
    zone_name = Column(String(10, 'utf8_bin'))


t_tab_ticket_files = Table(
    'tab_ticket_files', metadata,
    Column('ticket_id', Integer, nullable=False),
    Column('path', String(256, 'utf8_bin'), nullable=False),
    Column('name', String(256, 'utf8_bin'), nullable=False),
    Column('size', BigInteger, nullable=False),
    Column('hash', String(64, 'utf8_bin'), nullable=False),
    Column('create_time', DateTime, nullable=False),
    Column('download_count', Integer, server_default=FetchedValue()),
    Column('user_ln_path', String(256, 'utf8_bin'))
)


t_tab_ticket_wsa_files = Table(
    'tab_ticket_wsa_files', metadata,
    Column('ticket_id', Integer, nullable=False),
    Column('path', String(256, 'utf8_bin'), nullable=False),
    Column('name', String(256, 'utf8_bin'), nullable=False),
    Column('size', BigInteger, nullable=False),
    Column('hash', String(64, 'utf8_bin'), nullable=False),
    Column('create_time', DateTime, nullable=False),
    Column('download_count', Integer, server_default=FetchedValue()),
    Column('user_ln_path', String(2560, 'utf8_bin')),
    Column('server', String(256, 'utf8_bin'), nullable=False),
    Column('download_time', DateTime, nullable=False),
    Column('download_url', String(2560, 'utf8_bin'), nullable=False),
    Column('referer_url', String(2560, 'utf8_bin'), nullable=False)
)


class TabTicket(BaseAttach, DB_BASE):
    __tablename__ = 'tab_tickets'

    ticket_id = Column(Integer, primary_key=True)
    applicant_id = Column(Integer)
    applicant_name = Column(String(50, 'utf8_bin'))
    application_time = Column(DateTime)
    application_method = Column(Integer)
    type = Column(Integer)
    content = Column(Text(collation='utf8_bin'))
    begin_time = Column(DateTime)
    end_time = Column(DateTime)
    state = Column(Integer, server_default=FetchedValue())
    inner_state = Column(String(100, 'utf8_bin'))
    approver_id = Column(String(1000, 'utf8_bin'))
    approver_name = Column(String(1000, 'utf8_bin'))
    approval_time = Column(DateTime)
    approval_description = Column(Text(collation='utf8_bin'))
    param_1 = Column(Integer)
    param_2 = Column(Integer)
    param_3 = Column(Text(collation='utf8_bin'))
    param_4 = Column(BigInteger)
    param_5 = Column(BigInteger)
    param_6 = Column(String(1000, 'utf8_bin'))
    last_operation_time = Column(DateTime)
    operation_record = Column(Text(collation='utf8_bin'))
    dev_id = Column(String(40, 'utf8_bin'))
    view_cache_path = Column(String(256, 'utf8_bin'))
    preview_flag = Column(Integer, server_default=FetchedValue())
    preview_detail = Column(Text(collation='utf8_bin'))
    uuid = Column(String(36, 'utf8_bin'))
    desktop_ln_dir = Column(String(256, 'utf8_bin'))
    is_file_delete = Column(Integer, server_default=FetchedValue())
    history_approvals = Column(String(1000, 'utf8_bin'))


class TabTicketsApprovalingManNode(TabTicket):
    __tablename__ = 'tab_tickets_approvaling_man_nodes'

    ticket_id = Column(ForeignKey('tab_tickets.ticket_id', ondelete='CASCADE'), primary_key=True)
    chain_id = Column(Integer, nullable=False)
    token_flag = Column(Integer, server_default=FetchedValue())
    token_result_symbol = Column(String(20, 'utf8_bin'))
    token_result_flag = Column(Integer)
    man_flag = Column(Integer, server_default=FetchedValue())
    man_result_symbol = Column(String(20, 'utf8_bin'))
    man_result_flag = Column(Integer)
    man_nodes_msg = Column(String(2000, 'utf8_bin'))
    chain_msg = Column(String(2000, 'utf8_bin'))


class TabTicketsSecretKey(BaseAttach, DB_BASE):
    __tablename__ = 'tab_tickets_secret_key'

    secret_key = Column(String(64, 'utf8_bin'), primary_key=True)
    ticket_id = Column(ForeignKey('tab_tickets.ticket_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, nullable=False)
    update_time = Column(DateTime)

    ticket = relationship('TabTicket', primaryjoin='TabTicketsSecretKey.ticket_id == TabTicket.ticket_id', backref='tab_tickets_secret_keys')


t_tab_token_groups_relation = Table(
    'tab_token_groups_relation', metadata,
    Column('token_id', ForeignKey('tab_tokens.token_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True),
    Column('group_id', ForeignKey('tab_user_groups.group_id', ondelete='CASCADE'), primary_key=True, nullable=False)
)


t_tab_token_users_relation = Table(
    'tab_token_users_relation', metadata,
    Column('token_id', ForeignKey('tab_tokens.token_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('user_id', ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabToken(BaseAttach, DB_BASE):
    __tablename__ = 'tab_tokens'

    token_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), index=True)
    chain_id = Column(ForeignKey('tab_approval_module_chain.chain_id', ondelete='CASCADE'), index=True)
    name = Column(String(50, 'utf8_bin'))
    type = Column(Integer)
    policy = Column(Integer)
    param_1 = Column(String(1000, 'utf8_bin'))
    param_2 = Column(String(1000, 'utf8_bin'))
    param_3 = Column(String(1000, 'utf8_bin'))
    param_4 = Column(String(1000, 'utf8_bin'))
    param_5 = Column(String(1000, 'utf8_bin'))
    param_6 = Column(String(1000, 'utf8_bin'))
    param_7 = Column(String(1000, 'utf8_bin'))
    param_8 = Column(String(1000, 'utf8_bin'))
    param_9 = Column(String(1000, 'utf8_bin'))
    param_10 = Column(String(1000, 'utf8_bin'))
    description = Column(String(1000, 'utf8_bin'))
    operator_id = Column(Integer)
    operator_name = Column(String(50, 'utf8_bin'))
    operate_time = Column(DateTime)
    status_1 = Column(BigInteger)
    status_2 = Column(BigInteger)
    enable = Column(Integer)
    priority = Column(Integer)
    is_default = Column(Integer)
    all_users_flag = Column(Integer)

    chain = relationship('TabApprovalModuleChain', primaryjoin='TabToken.chain_id == TabApprovalModuleChain.chain_id', backref='tab_tokens')
    user = relationship('TabBasicUser', primaryjoin='TabToken.user_id == TabBasicUser.user_id', backref='tabbasicuser_tab_tokens')
    users = relationship('TabBasicUser', secondary='tab_token_users_relation', backref='tabbasicuser_tab_tokens_0')


class TabUserActivityRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_activity_record'
    __table_args__ = (
        Index('Index_3', 'user_name', 'zone_name'),
    )

    id = Column(Integer, primary_key=True)
    user_name = Column(String(80, 'utf8_bin'), index=True)
    zone_name = Column(String(40, 'utf8_bin'), index=True)
    time = Column(DateTime, nullable=False, server_default=FetchedValue())
    time_span = Column(Integer)
    keyboard_index = Column(SmallInteger, server_default=FetchedValue())
    mouse_index = Column(SmallInteger, server_default=FetchedValue())
    screen_index = Column(SmallInteger, server_default=FetchedValue())
    source_node_id = Column(String(36, 'utf8_bin'))
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)


t_tab_user_activity_statistic = Table(
    'tab_user_activity_statistic', metadata,
    Column('user_name', String(80, 'utf8_bin')),
    Column('zone_name', String(40, 'utf8_bin')),
    Column('year', Integer),
    Column('day', Integer),
    Column('time', BigInteger),
    Column('c1', Integer, server_default=FetchedValue()),
    Column('c2', Integer, server_default=FetchedValue()),
    Column('c3', Integer, server_default=FetchedValue()),
    Column('c4', Integer, server_default=FetchedValue()),
    Column('c5', Integer, server_default=FetchedValue()),
    Column('c6', Integer, server_default=FetchedValue()),
    Column('c7', Integer, server_default=FetchedValue()),
    Column('c8', Integer, server_default=FetchedValue()),
    Column('c9', Integer, server_default=FetchedValue()),
    Column('c10', Integer, server_default=FetchedValue()),
    Column('c11', Integer, server_default=FetchedValue()),
    Column('c12', Integer, server_default=FetchedValue()),
    Column('c13', Integer, server_default=FetchedValue()),
    Column('c14', Integer, server_default=FetchedValue()),
    Column('c15', Integer, server_default=FetchedValue()),
    Column('c16', Integer, server_default=FetchedValue()),
    Column('c17', Integer, server_default=FetchedValue()),
    Column('c18', Integer, server_default=FetchedValue()),
    Column('c19', Integer, server_default=FetchedValue()),
    Column('c20', Integer, server_default=FetchedValue()),
    Column('c21', Integer, server_default=FetchedValue()),
    Column('c22', Integer, server_default=FetchedValue()),
    Column('c23', Integer, server_default=FetchedValue()),
    Column('c24', Integer, server_default=FetchedValue()),
    Column('c25', Integer, server_default=FetchedValue()),
    Column('c26', Integer, server_default=FetchedValue()),
    Column('c27', Integer, server_default=FetchedValue()),
    Column('c28', Integer, server_default=FetchedValue()),
    Column('c29', Integer, server_default=FetchedValue()),
    Column('c30', Integer, server_default=FetchedValue()),
    Column('c31', Integer, server_default=FetchedValue()),
    Column('c32', Integer, server_default=FetchedValue()),
    Column('c33', Integer, server_default=FetchedValue()),
    Column('c34', Integer, server_default=FetchedValue()),
    Column('c35', Integer, server_default=FetchedValue()),
    Column('c36', Integer, server_default=FetchedValue()),
    Column('c37', Integer, server_default=FetchedValue()),
    Column('c38', Integer, server_default=FetchedValue()),
    Column('c39', Integer, server_default=FetchedValue()),
    Column('c40', Integer, server_default=FetchedValue()),
    Column('c41', Integer, server_default=FetchedValue()),
    Column('c42', Integer, server_default=FetchedValue()),
    Column('c43', Integer, server_default=FetchedValue()),
    Column('c44', Integer, server_default=FetchedValue()),
    Column('c45', Integer, server_default=FetchedValue()),
    Column('c46', Integer, server_default=FetchedValue()),
    Column('c47', Integer, server_default=FetchedValue()),
    Column('c48', Integer, server_default=FetchedValue()),
    Column('c49', Integer, server_default=FetchedValue()),
    Column('c50', Integer, server_default=FetchedValue()),
    Column('c51', Integer, server_default=FetchedValue()),
    Column('c52', Integer, server_default=FetchedValue()),
    Column('c53', Integer, server_default=FetchedValue()),
    Column('c54', Integer, server_default=FetchedValue()),
    Column('c55', Integer, server_default=FetchedValue()),
    Column('c56', Integer, server_default=FetchedValue()),
    Column('c57', Integer, server_default=FetchedValue()),
    Column('c58', Integer, server_default=FetchedValue()),
    Column('c59', Integer, server_default=FetchedValue()),
    Column('c60', Integer, server_default=FetchedValue()),
    Column('c61', Integer, server_default=FetchedValue()),
    Column('c62', Integer, server_default=FetchedValue()),
    Column('c63', Integer, server_default=FetchedValue()),
    Column('c64', Integer, server_default=FetchedValue()),
    Column('c65', Integer, server_default=FetchedValue()),
    Column('c66', Integer, server_default=FetchedValue()),
    Column('c67', Integer, server_default=FetchedValue()),
    Column('c68', Integer, server_default=FetchedValue()),
    Column('c69', Integer, server_default=FetchedValue()),
    Column('c70', Integer, server_default=FetchedValue()),
    Column('c71', Integer, server_default=FetchedValue()),
    Column('c72', Integer, server_default=FetchedValue()),
    Column('c73', Integer, server_default=FetchedValue()),
    Column('c74', Integer, server_default=FetchedValue()),
    Column('c75', Integer, server_default=FetchedValue()),
    Column('c76', Integer, server_default=FetchedValue()),
    Column('c77', Integer, server_default=FetchedValue()),
    Column('c78', Integer, server_default=FetchedValue()),
    Column('c79', Integer, server_default=FetchedValue()),
    Column('c80', Integer, server_default=FetchedValue()),
    Column('c81', Integer, server_default=FetchedValue()),
    Column('c82', Integer, server_default=FetchedValue()),
    Column('c83', Integer, server_default=FetchedValue()),
    Column('c84', Integer, server_default=FetchedValue()),
    Column('c85', Integer, server_default=FetchedValue()),
    Column('c86', Integer, server_default=FetchedValue()),
    Column('c87', Integer, server_default=FetchedValue()),
    Column('c88', Integer, server_default=FetchedValue()),
    Column('c89', Integer, server_default=FetchedValue()),
    Column('c90', Integer, server_default=FetchedValue()),
    Column('c91', Integer, server_default=FetchedValue()),
    Column('c92', Integer, server_default=FetchedValue()),
    Column('c93', Integer, server_default=FetchedValue()),
    Column('c94', Integer, server_default=FetchedValue()),
    Column('c95', Integer, server_default=FetchedValue()),
    Column('c96', Integer, server_default=FetchedValue()),
    Column('c97', Integer, server_default=FetchedValue()),
    Column('c98', Integer, server_default=FetchedValue()),
    Column('c99', Integer, server_default=FetchedValue()),
    Column('c100', Integer, server_default=FetchedValue()),
    Column('c101', Integer, server_default=FetchedValue()),
    Column('c102', Integer, server_default=FetchedValue()),
    Column('c103', Integer, server_default=FetchedValue()),
    Column('c104', Integer, server_default=FetchedValue()),
    Column('c105', Integer, server_default=FetchedValue()),
    Column('c106', Integer, server_default=FetchedValue()),
    Column('c107', Integer, server_default=FetchedValue()),
    Column('c108', Integer, server_default=FetchedValue()),
    Column('c109', Integer, server_default=FetchedValue()),
    Column('c110', Integer, server_default=FetchedValue()),
    Column('c111', Integer, server_default=FetchedValue()),
    Column('c112', Integer, server_default=FetchedValue()),
    Column('c113', Integer, server_default=FetchedValue()),
    Column('c114', Integer, server_default=FetchedValue()),
    Column('c115', Integer, server_default=FetchedValue()),
    Column('c116', Integer, server_default=FetchedValue()),
    Column('c117', Integer, server_default=FetchedValue()),
    Column('c118', Integer, server_default=FetchedValue()),
    Column('c119', Integer, server_default=FetchedValue()),
    Column('c120', Integer, server_default=FetchedValue()),
    Column('c121', Integer, server_default=FetchedValue()),
    Column('c122', Integer, server_default=FetchedValue()),
    Column('c123', Integer, server_default=FetchedValue()),
    Column('c124', Integer, server_default=FetchedValue()),
    Column('c125', Integer, server_default=FetchedValue()),
    Column('c126', Integer, server_default=FetchedValue()),
    Column('c127', Integer, server_default=FetchedValue()),
    Column('c128', Integer, server_default=FetchedValue()),
    Column('c129', Integer, server_default=FetchedValue()),
    Column('c130', Integer, server_default=FetchedValue()),
    Column('c131', Integer, server_default=FetchedValue()),
    Column('c132', Integer, server_default=FetchedValue()),
    Column('c133', Integer, server_default=FetchedValue()),
    Column('c134', Integer, server_default=FetchedValue()),
    Column('c135', Integer, server_default=FetchedValue()),
    Column('c136', Integer, server_default=FetchedValue()),
    Column('c137', Integer, server_default=FetchedValue()),
    Column('c138', Integer, server_default=FetchedValue()),
    Column('c139', Integer, server_default=FetchedValue()),
    Column('c140', Integer, server_default=FetchedValue()),
    Column('c141', Integer, server_default=FetchedValue()),
    Column('c142', Integer, server_default=FetchedValue()),
    Column('c143', Integer, server_default=FetchedValue()),
    Column('c144', Integer, server_default=FetchedValue()),
    Column('c_count', Integer, server_default=FetchedValue()),
    Column('u_count', Integer, server_default=FetchedValue()),
    Column('z_count', Integer, server_default=FetchedValue()),
    Column('weekend', Integer, server_default=FetchedValue()),
    Column('create_time', BigInteger, server_default=FetchedValue())
)


t_tab_user_capacity = Table(
    'tab_user_capacity', metadata,
    Column('user_name', String(80, 'utf8_bin')),
    Column('occupy_capacity', Float, server_default=FetchedValue()),
    Column('device_id', String(40, 'utf8_bin'))
)


class TabUserFavorite(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_favorite'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    template_name = Column(String(200, 'utf8_bin'))
    content = Column(String(2000, 'utf8_bin'))
    type = Column(String(100, 'utf8_bin'))


t_tab_user_group_relation = Table(
    'tab_user_group_relation', metadata,
    Column('user_id', ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('group_id', ForeignKey('tab_user_groups.group_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabUserGroup(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_groups'

    group_id = Column(Integer, primary_key=True)
    group_name = Column(String(128, 'utf8_bin'))
    description = Column(String(1000, 'utf8_bin'))
    create_time = Column(DateTime)
    update_time = Column(DateTime)

    man_nodes = relationship('TabManApprovalNode', secondary='tab_man_nodes_groups_relation', backref='tab_user_groups')
    tokens = relationship('TabToken', secondary='tab_token_groups_relation', backref='tab_user_groups')
    users = relationship('TabBasicUser', secondary='tab_user_group_relation', backref='tab_user_groups')


class TabUserOnlineRuntime(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_online_runtime'

    id = Column(Integer, primary_key=True)
    dev_id = Column(String(40, 'utf8_bin'))
    zone_name = Column(String(40, 'utf8_bin'))
    user_name = Column(String(80, 'utf8_bin'))
    client_ip = Column(String(20, 'utf8_bin'))
    login_time = Column(DateTime)
    logout_time = Column(DateTime)


t_tab_user_performance = Table(
    'tab_user_performance', metadata,
    Column('style', String(6, 'utf8_bin')),
    Column('type', String(7, 'utf8_bin')),
    Column('value', Integer)
)


class TabUserQueryTemplate(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_query_template'

    id = Column(Integer, primary_key=True)
    name = Column(String(100, 'utf8_bin'), unique=True)
    user_names = Column(String(500, 'utf8_bin'))
    user_group_ids = Column(String(200, 'utf8_bin'))
    user_enables = Column(String(100, 'utf8_bin'))
    create_time_begin = Column(DateTime)
    create_time_end = Column(DateTime)
    real_names = Column(String(500, 'utf8_bin'))
    emails = Column(String(500, 'utf8_bin'))
    update_time_begin = Column(DateTime)
    update_time_end = Column(DateTime)
    key_words = Column(String(100, 'utf8_bin'))
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    role_ids = Column(String(200, 'utf8_bin'))
    zone_ids = Column(String(200, 'utf8_bin'))
    realm_name = Column(String(100, 'utf8_bin'))


class TabUserZoneApplication(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_zone_applications'
    __table_args__ = (
        ForeignKeyConstraint(['zone_id', 'user_id'], ['tab_user_zone_relation.zone_id', 'tab_user_zone_relation.user_id'], ondelete='CASCADE'),
        Index('FK_Reference_83', 'zone_id', 'user_id')
    )

    user_id = Column(Integer, primary_key=True, nullable=False)
    zone_id = Column(Integer, primary_key=True, nullable=False)
    loginname = Column(String(80, 'utf8_bin'))
    realm_name = Column(String(40, 'utf8_bin'))
    protocol = Column(String(20, 'utf8_bin'))
    ip = Column(String(30, 'utf8_bin'), primary_key=True, nullable=False)
    server_type = Column(Integer, primary_key=True, nullable=False)
    pool_id = Column(String(36, 'utf8_bin'))

    zone = relationship('TabUserZoneRelation', primaryjoin='and_(TabUserZoneApplication.zone_id == TabUserZoneRelation.zone_id, TabUserZoneApplication.user_id == TabUserZoneRelation.user_id)', backref='tab_user_zone_applications')


class TabUserZoneAudititemRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_zone_audititem_relation'
    __table_args__ = (
        ForeignKeyConstraint(['zone_id', 'user_id'], ['tab_user_zone_relation.zone_id', 'tab_user_zone_relation.user_id'], ondelete='CASCADE'),
        Index('FK_Reference_27', 'zone_id', 'user_id')
    )

    user_id = Column(Integer, primary_key=True, nullable=False)
    zone_id = Column(Integer, primary_key=True, nullable=False)
    audit_item_id = Column(ForeignKey('tab_audit_items.audit_item_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    enable = Column(Integer, server_default=FetchedValue())

    audit_item = relationship('TabAuditItem', primaryjoin='TabUserZoneAudititemRelation.audit_item_id == TabAuditItem.audit_item_id', backref='tab_user_zone_audititem_relations')
    zone = relationship('TabUserZoneRelation', primaryjoin='and_(TabUserZoneAudititemRelation.zone_id == TabUserZoneRelation.zone_id, TabUserZoneAudititemRelation.user_id == TabUserZoneRelation.user_id)', backref='tab_user_zone_audititem_relations')


class TabUserZoneRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_zone_relation'

    zone_id = Column(ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    user_id = Column(ForeignKey('tab_basic_users.user_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    stop_login = Column(Integer, server_default=FetchedValue())
    special_audit = Column(Integer, server_default=FetchedValue())
    security_item = Column(Integer, server_default=FetchedValue())
    audit_item = Column(Integer, server_default=FetchedValue())

    user = relationship('TabBasicUser', primaryjoin='TabUserZoneRelation.user_id == TabBasicUser.user_id', backref='tab_user_zone_relations')
    zone = relationship('TabZone', primaryjoin='TabUserZoneRelation.zone_id == TabZone.zone_id', backref='tab_user_zone_relations')


class TabUserZoneSecurityitemRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_zone_securityitem_relation'
    __table_args__ = (
        ForeignKeyConstraint(['zone_id', 'user_id'], ['tab_user_zone_relation.zone_id', 'tab_user_zone_relation.user_id'], ondelete='CASCADE'),
        Index('FK_Reference_21', 'zone_id', 'user_id')
    )

    user_id = Column(Integer, primary_key=True, nullable=False)
    zone_id = Column(Integer, primary_key=True, nullable=False)
    security_item_id = Column(ForeignKey('tab_security_items.security_item_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    enable = Column(Integer, server_default=FetchedValue())

    security_item = relationship('TabSecurityItem', primaryjoin='TabUserZoneSecurityitemRelation.security_item_id == TabSecurityItem.security_item_id', backref='tab_user_zone_securityitem_relations')
    zone = relationship('TabUserZoneRelation', primaryjoin='and_(TabUserZoneSecurityitemRelation.zone_id == TabUserZoneRelation.zone_id, TabUserZoneSecurityitemRelation.user_id == TabUserZoneRelation.user_id)', backref='tab_user_zone_securityitem_relations')


class TabUserZoneSenioritemRelation(BaseAttach, DB_BASE):
    __tablename__ = 'tab_user_zone_senioritem_relation'
    __table_args__ = (
        ForeignKeyConstraint(['zone_id', 'role_id', 'systemuser_id'], ['tab_systemuser_zone_relation.zone_id', 'tab_systemuser_zone_relation.role_id', 'tab_systemuser_zone_relation.systemuser_id']),
        Index('FK_Reference_105', 'zone_id', 'role_id', 'systemuser_id')
    )

    systemuser_id = Column(Integer, primary_key=True, nullable=False)
    zone_id = Column(Integer, primary_key=True, nullable=False)
    senior_item_id = Column(ForeignKey('tab_senior_items.senior_item_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    enable = Column(Integer, nullable=False, server_default=FetchedValue())
    role_id = Column(Integer)

    senior_item = relationship('TabSeniorItem', primaryjoin='TabUserZoneSenioritemRelation.senior_item_id == TabSeniorItem.senior_item_id', backref='tab_user_zone_senioritem_relations')
    zone = relationship('TabSystemuserZoneRelation', primaryjoin='and_(TabUserZoneSenioritemRelation.zone_id == TabSystemuserZoneRelation.zone_id, TabUserZoneSenioritemRelation.role_id == TabSystemuserZoneRelation.role_id, TabUserZoneSenioritemRelation.systemuser_id == TabSystemuserZoneRelation.systemuser_id)', backref='tab_user_zone_senioritem_relations')


class TabViolationRawLog(BaseAttach, DB_BASE):
    __tablename__ = 'tab_violation_raw_log'

    log_id = Column(String(50, 'utf8_bin'), primary_key=True, nullable=False)
    type_id = Column(ForeignKey('tab_rules_running.rule_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    record_id = Column(String(50, 'utf8_bin'), primary_key=True, nullable=False)
    create_time = Column(DateTime)
    type_name = Column(String(50, 'utf8_bin'))
    sensor_id = Column(String(50, 'utf8_bin'))
    user_name = Column(String(50, 'utf8_bin'))
    ip = Column(String(50, 'utf8_bin'))
    ipv6 = Column(String(50, 'utf8_bin'))
    mac = Column(String(50, 'utf8_bin'))
    mask = Column(String(50, 'utf8_bin'))
    mask_ip = Column(String(50, 'utf8_bin'))
    computer = Column(String(50, 'utf8_bin'))
    os = Column(String(50, 'utf8_bin'))
    message = Column(Text(collation='utf8_bin'))

    type = relationship('TabRulesRunning', primaryjoin='TabViolationRawLog.type_id == TabRulesRunning.rule_id', backref='tab_violation_raw_logs')


class TabViolationRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_violation_record'

    type_id = Column(ForeignKey('tab_rules_running.rule_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    record_id = Column(String(50, 'utf8_bin'), primary_key=True, nullable=False)
    create_time = Column(DateTime)
    type_name = Column(String(50, 'utf8_bin'))
    rule_type = Column(String(50, 'utf8_bin'), nullable=False)
    rule_name = Column(String(100, 'utf8_bin'), nullable=False)
    sensor_id = Column(String(50, 'utf8_bin'))
    user_name = Column(String(50, 'utf8_bin'))
    ip = Column(String(50, 'utf8_bin'))
    ipv6 = Column(String(50, 'utf8_bin'))
    mac = Column(String(50, 'utf8_bin'))
    mask = Column(String(50, 'utf8_bin'))
    mask_ip = Column(String(50, 'utf8_bin'))
    computer = Column(String(50, 'utf8_bin'))
    os = Column(String(50, 'utf8_bin'))
    log_count = Column(Integer)
    illegal_condition = Column(Text(collation='utf8_bin'))
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    message = Column(Text(collation='utf8_bin'))
    alarm_msg = Column(String(1000, 'utf8_bin'))
    alarm_rel_id = Column(String(100, 'utf8_bin'))
    relevance_ids = Column(Text(collation='utf8_bin'))
    relevance_sensors = Column(Text(collation='utf8_bin'))
    relevance_users = Column(Text(collation='utf8_bin'))

    type = relationship('TabRulesRunning', primaryjoin='TabViolationRecord.type_id == TabRulesRunning.rule_id', backref='tab_violation_records')


class TabVsftpChannelConfig(BaseAttach, DB_BASE):
    __tablename__ = 'tab_vsftp_channel_config'

    id = Column(Integer, primary_key=True)
    source_zone_id = Column(ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), index=True)
    destination_zone_id = Column(ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), index=True)

    destination_zone = relationship('TabZone', primaryjoin='TabVsftpChannelConfig.destination_zone_id == TabZone.zone_id', backref='tabzone_tab_vsftp_channel_configs')
    source_zone = relationship('TabZone', primaryjoin='TabVsftpChannelConfig.source_zone_id == TabZone.zone_id', backref='tabzone_tab_vsftp_channel_configs_0')


class TabWhiteUser(BaseAttach, DB_BASE):
    __tablename__ = 'tab_white_user'

    id = Column(Integer, primary_key=True)
    user_name = Column(Text(collation='utf8_bin'))
    ip = Column(String(20, 'utf8_bin'))
    mask = Column(String(20, 'utf8_bin'))
    begin_time = Column(String(10, 'utf8_bin'))
    end_time = Column(String(10, 'utf8_bin'))
    begin_day = Column(String(15, 'utf8_bin'))
    end_day = Column(String(15, 'utf8_bin'))
    type = Column(String(30, 'utf8_bin'))
    service = Column(String(20, 'utf8_bin'))
    enable = Column(Integer, server_default=FetchedValue())
    description = Column(String(100, 'utf8_bin'))
    is_default = Column(Integer, server_default=FetchedValue())
    operate_time = Column(String(100, 'utf8_bin'))


class TabWhitelist(BaseAttach, DB_BASE):
    __tablename__ = 'tab_whitelist'
    __table_args__ = (
        Index('AK_Key_2', 'item', 'type'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(256, 'utf8_bin'))
    item = Column(String(30, 'utf8_bin'))
    mask = Column(String(30, 'utf8_bin'))
    type = Column(Integer)


class TabWorkDay(BaseAttach, DB_BASE):
    __tablename__ = 'tab_work_day'

    yearmonth = Column(Integer, primary_key=True)
    day = Column(Integer)


class TabWorkTime(BaseAttach, DB_BASE):
    __tablename__ = 'tab_work_time'

    id = Column(Integer, primary_key=True)
    begin_time = Column(String(10, 'utf8_bin'))
    end_time = Column(String(10, 'utf8_bin'))


class TabWsaServerManage(BaseAttach, DB_BASE):
    __tablename__ = 'tab_wsa_server_manage'

    server_manage_id = Column(Integer, primary_key=True)
    zone_id = Column(ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), nullable=False, index=True)
    visitor_url = Column(String(255, 'utf8_bin'))
    visitor_port = Column(Integer)
    server_url = Column(String(255, 'utf8_bin'))
    server_port = Column(Integer)
    visitor_ssl_flag = Column(Integer, server_default=FetchedValue())
    server_desc = Column(String(255, 'utf8_bin'))
    server_status = Column(Integer, server_default=FetchedValue())
    ssl_certificate = Column(String(255, 'utf8_bin'))
    ssl_security = Column(String(255, 'utf8_bin'))
    ssl_protocal = Column(String(255, 'utf8_bin'))
    ssl_encryption_algorithm = Column(String(255, 'utf8_bin'))
    valid = Column(Integer)
    server_ssl_flag = Column(Integer, server_default=FetchedValue())

    zone = relationship('TabZone', primaryjoin='TabWsaServerManage.zone_id == TabZone.zone_id', backref='tab_wsa_server_manages')


class TabWsaWorkDay(BaseAttach, DB_BASE):
    __tablename__ = 'tab_wsa_work_day'

    yearmonth = Column(Integer, primary_key=True)
    day = Column(Integer)


class TabWsaWorkTime(BaseAttach, DB_BASE):
    __tablename__ = 'tab_wsa_work_time'

    id = Column(Integer, primary_key=True)
    begin_time = Column(String(10, 'utf8_bin'))
    end_time = Column(String(10, 'utf8_bin'))


class TabYearSensorActivityRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_year_sensor_activity_record'
    __table_args__ = (
        Index('Index_3', 'user_name', 'zone_name'),
    )

    id = Column(Integer, primary_key=True)
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    user_name = Column(String(80, 'utf8_bin'), index=True)
    zone_name = Column(String(40, 'utf8_bin'), index=True)
    time = Column(DateTime, nullable=False, server_default=FetchedValue())
    time_span = Column(Integer)
    process_index = Column(BigInteger, server_default=FetchedValue())
    data_index = Column(BigInteger, server_default=FetchedValue())
    io_index = Column(BigInteger, server_default=FetchedValue())
    source_node_id = Column(String(36, 'utf8_bin'))


class TabYearUserActivityRecord(BaseAttach, DB_BASE):
    __tablename__ = 'tab_year_user_activity_record'
    __table_args__ = (
        Index('Index_3', 'user_name', 'zone_name'),
    )

    id = Column(Integer, primary_key=True)
    source_guid = Column(String(36, 'utf8_bin'))
    source_type = Column(Integer)
    user_name = Column(String(80, 'utf8_bin'), index=True)
    zone_name = Column(String(40, 'utf8_bin'), index=True)
    time = Column(DateTime, nullable=False, server_default=FetchedValue())
    time_span = Column(Integer)
    keyboard_index = Column(BigInteger, server_default=FetchedValue())
    mouse_index = Column(BigInteger, server_default=FetchedValue())
    screen_index = Column(BigInteger, server_default=FetchedValue())
    source_node_id = Column(String(36, 'utf8_bin'))


t_tab_zone_audititem_relation = Table(
    'tab_zone_audititem_relation', metadata,
    Column('zone_id', ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('audit_item_id', ForeignKey('tab_audit_items.audit_item_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabZoneCapacity(BaseAttach, DB_BASE):
    __tablename__ = 'tab_zone_capacity'

    id = Column(Integer, primary_key=True)
    zone_name = Column(String(40, 'utf8_bin'))
    capacity = Column(Float)
    device_id = Column(String(40, 'utf8_bin'))


class TabZoneCluster(BaseAttach, DB_BASE):
    __tablename__ = 'tab_zone_cluster'

    id = Column(Integer, primary_key=True)
    network_name = Column(String(40, 'utf8_bin'))
    cluster_ip = Column(String(20, 'utf8_bin'))
    vmac = Column(String(20, 'utf8_bin'))


t_tab_zone_network_relation = Table(
    'tab_zone_network_relation', metadata,
    Column('zone_id', ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('network_id', ForeignKey('tab_networks.network_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


t_tab_zone_securityitem_relation = Table(
    'tab_zone_securityitem_relation', metadata,
    Column('zone_id', ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), primary_key=True, nullable=False),
    Column('security_item_id', ForeignKey('tab_security_items.security_item_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
)


class TabZone(BaseAttach, DB_BASE):
    __tablename__ = 'tab_zones'

    zone_id = Column(Integer, primary_key=True)
    zone_name = Column(String(40, 'utf8_bin'), nullable=False, unique=True)
    description = Column(String(1000, 'utf8_bin'))
    enable = Column(Integer, server_default=FetchedValue())
    audit_enable = Column(Integer, server_default=FetchedValue())
    screen_audit_quota = Column(Integer)
    log_audit_quota = Column(Integer)
    quota_policy = Column(String(20, 'utf8_bin'))
    sftpport = Column(Integer)
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    configed = Column(Integer, server_default=FetchedValue())
    screen_quota_unit = Column(String(10, 'utf8_bin'))
    log_quota_unit = Column(String(10, 'utf8_bin'))
    zone_desktop_expiration_days = Column(Integer, server_default=FetchedValue())


t_tab_zones_mount = Table(
    'tab_zones_mount', metadata,
    Column('zone_id', ForeignKey('tab_zones.zone_id', ondelete='CASCADE'), nullable=False, index=True),
    Column('protocol', String(20, 'utf8_bin')),
    Column('path', String(255, 'utf8_bin')),
    Column('user', String(255, 'utf8_bin')),
    Column('password', String(255, 'utf8_bin')),
    Column('domain_name', String(255, 'utf8_bin')),
    Column('kdc_server_name', String(255, 'utf8_bin')),
    Column('kdc_server_ip', String(255, 'utf8_bin')),
    Column('admin_server_name', String(255, 'utf8_bin')),
    Column('admin_server_ip', String(255, 'utf8_bin')),
    Column('samba_name', String(255, 'utf8_bin')),
    Column('samba_ip', String(255, 'utf8_bin'))
)


class TbTemplate(BaseAttach, DB_BASE):
    __tablename__ = 'tb_templates'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    template_name = Column(String(100, 'utf8_bin'))
    use_image = Column(String(100, 'utf8_bin'))
    template_type = Column(Integer)
    kvm_parameters = Column(String(1000, 'utf8_bin'))


class TabFileAnalysis(BaseAttach, DB_BASE):
    __tablename__ = 'tab_file_analysis'

    id = Column(Integer, primary_key=True)
    rule_name = Column(String(128), unique=True, nullable=False)
    uuid = Column(String(64), unique=True, nullable=False)
    sensor_group_ids = Column(String(128), default='-1')
    file_type = Column(String(64))
    name_keyword = Column(String(256))
    content_keyword = Column(String(256))
    operating_program = Column(String(64))
    operating_type = Column(String(64))
    file_size_type = Column(String(64))
    file_size = Column(String(128))
    alarm = Column(Integer, nullable=False, default=0)
    operator = Column(String(64), nullable=False)
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    create_time = Column(DateTime, nullable=False, default=datetime.now)


class TabSensorApplication(BaseAttach, DB_BASE):
    __tablename__ = 'tab_sensor_application'

    id = Column(Integer, primary_key=True)
    ip = Column(String(64), nullable=False, unique=True)
    applicant = Column(String(128))
    department = Column(String(128))
    phone = Column(String(64))
    device_type = Column(String(128))
    sys_type = Column(String(64))
    reason = Column(Text(collation='utf8_bin'))
    interval = Column(Integer)  # in days, one day = 1, one week = 7, permanent = -1
    create_time = Column(DateTime, nullable=False, default=datetime.now)
    update_time = Column(DateTime, nullable=False, default=datetime.now,
                         onupdate=datetime.now)
    pass_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(Integer, nullable=False, default=0)


#DB_BASE.metadata.create_all(DB_ENGINE)

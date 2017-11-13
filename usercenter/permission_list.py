#_*_coding:utf-8_*_
from usercenter import custom_perm_logic
from usercenter import custom_permission_func

#权限样式 app_权限名字
'''


        ('db_list', '可以访问 数据库列表页'),
        ('deploy_list','部署管理'),
        ('deploy_add','添加部署配置'),
        ('deploy_change','修改部署配置'),
        ('deploy_delete', '删除部署配置'),
        ('cert_list', '证书管理'),
        ('cert_add', '添加证书'),
        ('cert_change', '修改证书'),
        ('cert_delete', '删除证书'),
'''
perm_dic={
    'usercenter_db_list':['db_list',['GET',],[],{},],
    'usercenter_db_execute_sql': ['execute_sql', ['POST', ], [], {}, ],
    'usercenter_db_svn_update': ['svn_update', ['POST', ], [], {}, ],

    'usercenter_cert_list': ['certmgr_index', ['GET',], [], {}, ],
    'usercenter_cert_add': ['certmgr_table_add', ['GET','POST'], [], {}, ],
    'usercenter_cert_change': ['certmgr_table_change', ['GET','POST'], [], {}, ],
    'usercenter_cert_delete': ['certmgr_index', ['POST',], [], {}, ],

    'usercenter_releasemgr_list': ['releasemgr_index', ['GET',], [], {}, ],
    'usercenter_releasemgr_add': ['releasemgr_table_add', ['GET','POST'], [], {}, ],
    'usercenter_releasemgr_change': ['releasemgr_table_change', ['GET','POST'], [], {}, ],
    'usercenter_releasemgr_delete': ['releasemgr_index', ['POST',], [], {}, ],

    'usercenter_deploy_list': ['kingadmin_index', ['GET', ], [], {}, ],
    'usercenter_deploy_add': ['table_add', ['GET', 'POST'], [], {}, ],
    'usercenter_deploy_change': ['table_change', ['GET', 'POST'], [], {}, ],
    'usercenter_deploy_delete': ['kingadmin_index', ['POST',], [], {}, ],

    'usercenter_jenkins_server_list': ['jenkinsserver_list', ['GET', ], [], {}, ],
    'usercenter_jenkins_job_detail': ['job_detail', ['GET','POST' ], [], {}, custom_permission_func.check_job_obj_permission ],



}
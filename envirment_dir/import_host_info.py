from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory,Host,Group
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.inventory import Inventory,Host,Group

import os
import sys
import traceback
import yaml
import os
import sys
basedir = (os.path.sep).join(os.path.abspath(__file__).split(os.path.sep)[:-2])
print basedir
sys.path.append(basedir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'pub_cmdb.settings'
import django

django.setup()
from cmdb.models import *

class AnsibleApi2(object):
    def __init__(self,host_file_path,group_var_path):
        self.host_file_path = host_file_path
        # self.Options = namedtuple('Options', ['connection','module_path', 'forks', 'timeout',  'remote_user',
        #         'ask_pass', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
        #         'scp_extra_args', 'become', 'become_method', 'become_user', 'ask_value_pass', 'verbosity',
        #         'check', 'listhosts', 'listtasks', 'listtags', 'syntax','tags'])
        #
        # self.options = self.Options(connection='smart', module_path=None, forks=5, timeout=10,
        #                        remote_user=None, ask_pass=False, private_key_file=None, ssh_common_args=None,
        #                        ssh_extra_args=None,
        #                        sftp_extra_args=None, scp_extra_args=None, become=None, become_method=None,
        #                        become_user=None, ask_value_pass=False, verbosity=None, check=False, listhosts=False,
        #                        listtasks=False, listtags=False, syntax=False,tags=self.tags_str)

        self.Options = namedtuple('Options',
                             ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path', 'forks',
                              'private_key_file', 'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
                              'scp_extra_args', 'become', 'become_method', 'become_user', 'remote_user', 'verbosity',
                              'check','tags'])
        self.options = self.Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh',
                          module_path=None, forks=100, private_key_file=None, ssh_common_args=None, ssh_extra_args=None,
                          sftp_extra_args=None, scp_extra_args=None, become=False, become_method=None, become_user=None,
                          remote_user=None, verbosity=None, check=False,tags=None)

        # self.Options = namedtuple('Options', ['listhosts', 'listtasks','forks', 'become', 'become_method', 'become_user', 'check'])
        # self.options = self.Options(listhosts=False, listtasks=True, forks=10, become=None, become_method=None, become_user='root', check=False)


        self.variable_manager = VariableManager()
        self.loader = DataLoader()

        # self.variable_manager.add_group_vars_file()

        self.passwords = {}
        # self.host_list = ['server02',]
        # self.group_var_file_path = group_var_file
        # self.group_var_file_path = 'group_vars/all_84'
        self.group_var_file_path = group_var_path
        self.variable_manager.add_group_vars_file(self.group_var_file_path,self.loader)
        # self.variable_manager.
        # print self.variable_manager._group_vars_files,11111111111111111
        self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager,host_list=self.host_file_path)

        # self.init_inventory()
        self.variable_manager.set_inventory(self.inventory)
        # print self.inventory.get_groups(),111111111
        # for group_name, group_obj in self.inventory.get_groups().items():
        #     print group_name,group_obj
        #     print type(group_obj)
        #     print group_obj.hosts
        #
        # sys.exit()
        # self.variable_manager.set_host_variable()

        # self.results_callback = ResultsCollector()
        l= []
        for h in  self.inventory.get_hosts():

            print h.__dict__
            t = Hosts(ipaddr=h.name,host_type=0)
            l.append(t)
        Hosts.objects.bulk_create(l)
        #
        # g_list = []
        # h_list = []
        # for g in  self.inventory.get_groups():
        #
        #     if len(g.split('_',1)) > 1:
        #         group_name,app_foot = g.split('_',1)
        #         h_list.append(JavaAppFoot(foot_name=app_foot))
        #     else:
        #         group_name = g
        #
        #     print group_name
        #     g_list.append(group_name)
        #
        #
        # g_tuple = set(g_list)
        # temp = []
        # for g in g_tuple:
        #     temp.append(Group(name=g))
        # JavaAppFoot.objects.bulk_create(h_list)
        # Group.objects.bulk_create(temp)

    def run_model(self,command_args,hosts):
        print 'host list: ',self.inventory.get_hosts()
        play_source = dict(
            name="Ansible Play",
            hosts=hosts,
            gather_facts='no',
            tasks=[
                dict(action=dict(module='shell', args=command_args), register='shell_out'),
                # dict(action=dict(module='shell', args=command_args)),
                dict(action=dict(module='debug', args='var=shell_out.stdout_lines'))
            ]
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        qm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                # stdout_callback='default',
            )
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()


    def run_playbook(self,play_book,extra_vars):
        try:
            playbook_path = play_book # modify here, change playbook
            self.variable_manager.extra_vars=extra_vars
            if not os.path.exists(playbook_path):
                sys.exit('[INFO] The playbook does not exist')

            passwords = {}
            executor = PlaybookExecutor(
                playbooks=[playbook_path],
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=passwords,
            )
            # executor._tqm._stdout_callback = self.results_callback
            # code = executor.run()
            # stats = executor._tqm._stats
            # hosts = sorted(stats)
            code = executor.run()
            stats = executor._tqm._stats
            hosts = sorted(stats.processed.keys())
            result = [{h: stats.summarize(h)} for h in hosts]
            results = {'code': code, 'result': result, 'playbook': playbook_path}
            return results

        except Exception as e:
            msg = traceback.format_exc()
            sys.exit(msg)


if __name__ == "__main__":
    AnsibleApi2("147/hosts_147","147/group_vars_147/all")
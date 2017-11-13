# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from __future__ import unicode_literals
from django.contrib.auth.models import PermissionsMixin,Permission,_user_get_all_permissions,_user_has_perm,_user_has_module_perms
# from myauth import PermissionsMixin,Permission,_user_get_all_permissions,_user_has_perm,_user_has_module_perms
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
# from myauth import AbstractBaseUser, BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import Group
# from jenkinsmgr.models import JenkinsJob




# class GroupProfile(models.Model):
#     group = models.OneToOneField(Group, unique=True)
#     a = models.CharField(max_length=100)
#     b = models.CharField(max_length=100)

Group.add_to_class('alias', models.CharField(max_length=64,blank=True,null=True))
Group.add_to_class('email', models.EmailField(blank=True,null=True))
# Group.add_to_class('jenkins_job',models.ManyToManyField(jenkinssmgr_models.JenkinsJob,blank=True,null=True))
# Group.add_to_class('detail', models.CharField(max_length=100,blank=True,null=True))

# from django.contrib.auth.models import (
#     BaseUserManager, AbstractBaseUser
# )


class MyUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user







class MyUser(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(
        verbose_name='username ',
        max_length=255,
        unique=True,
    )

    alias = models.CharField(max_length=64,blank=True,null=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    gender_choice = (
        (0,'female'),
        (1,'male')
    )
    gender = models.PositiveIntegerField(choices=gender_choice,default=0)

    objects = MyUserManager()


    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return self.username

    def get_short_name(self):
        # The user is identified by their email address
        return self.username

    def __str__(self):              # __unicode__ on Python 2
        return self.username

    def has_perm(self, perm, obj=None):
        if self.is_admin:
            return True

        return super(MyUser, self).has_perm(perm,obj=obj)
        # "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        # print perm
        # print self.groups.permissions,111111111111111
        # # print self.user_permissions,11111111

        # return _user_has_perm(self, perm, obj)

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     # return self.is_admin
    #     return self.is_active
    #
    # @property
    # def is_superuser(self):
    #    # "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_admin
    #


    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

        permissions = (
            ('db_list', '可以访问 数据库列表页'),
            ('db_execute_sql', '数据库执行sql权限'),
            ('db_svn_update', '更新数据库脚本svn目录'),
            ('deploy_list','部署管理'),
            ('deploy_add','添加部署配置'),
            ('deploy_change','修改部署配置'),
            ('deploy_delete', '删除部署配置'),
            ('cert_list', '证书管理'),
            ('cert_add', '添加证书'),
            ('cert_change', '修改证书'),
            ('cert_delete', '删除证书'),
            ('releasemgr_list', '发布计划管理'),
            ('releasemgr_add', '添加发布计划'),
            ('releasemgr_change', '修改发布计划'),
            ('releasemgr_delete', '删除发布计划'),
            ('jenkins_server_list', 'jenkins管理'),
            ('jenkins_job_detail', 'jenkins job操作'),
            ('jenkins_admin', 'jenkins管理员'),

        )



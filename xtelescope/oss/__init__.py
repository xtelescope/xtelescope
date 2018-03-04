# coding: utf-8
from .aliyun_oss_wrapper import AliyunOSSWrapper
from .qiniu_oss_wrapper import QiniuOSSWrapper


def use(vendor):
    if vendor == "aliyun":
        return AliyunOSSWrapper()
    elif vendor == 'qiniu':
        return QiniuOSSWrapper()

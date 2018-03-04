# coding: utf-8
from .oss_base_wrapper import OSSBaseWrapper
import qiniu


class QiniuOSSWrapper(OSSBaseWrapper):
    def __init__(self):
        super().__init__()

    def get_auth(self, access_key, secret_key):
        raise NotImplementedError()

    def get_service(self, endpoint):
        raise NotImplementedError()

    def get_best_endpoint(self):
        raise NotImplementedError()

    def get_bucket(self, bucket_name):
        raise NotImplementedError()
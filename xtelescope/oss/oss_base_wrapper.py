# coding: utf-8
from abc import ABCMeta, abstractmethod


class BaseBucket:
    """
    an Auth object, an endpoint, a name defines a bucket
    """
    __metaclass__ = ABCMeta

    def __init__(self, auth_object, endpoint, bucket_name):
        self.auth_object = auth_object
        self.endpoint = endpoint
        self.name = bucket_name

    @abstractmethod
    def put(self, local_file_path, target_file_name):
        raise NotImplementedError()


class OSSBaseWrapper:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.auth = None
        self.service = None
        self.endpoint = ""

    def __getitem__(self, bucket_name):
        return self.get_bucket(bucket_name)

    def prepare(self, access_key, secret_key, endpoint=None):
        self.auth = self.get_auth(access_key, secret_key)
        if endpoint is None:
            self.endpoint = self.get_best_endpoint()
        else:
            self.endpoint = endpoint
        self.service = self.get_service(endpoint)

    @abstractmethod
    def get_auth(self, access_key, secret_key):
        raise NotImplementedError()

    @abstractmethod
    def get_service(self, endpoint):
        raise NotImplementedError()

    @abstractmethod
    def get_best_endpoint(self):
        raise NotImplementedError()

    @abstractmethod
    def get_bucket(self, bucket_name):
        raise NotImplementedError()

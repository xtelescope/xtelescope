from .oss_base_wrapper import OSSBaseWrapper, BaseBucket
from collections import defaultdict
import oss2
from oss2 import Bucket


class AliyunBucket(BaseBucket, Bucket):
    def __init__(self, auth_object, endpoint, bucket_name):
        super().__init__(auth_object, endpoint, bucket_name)

    def put(self, local_file_path, target_file_name):
        self.put_object_from_file(local_file_path, target_file_name)


class AliyunOSSWrapper(OSSBaseWrapper):
    def __init__(self):
        super().__init__()

    def get_auth(self, access_key, secret_key):
        return oss2.Auth(access_key, secret_key)

    def get_service(self, endpoint):
        return oss2.Service(self.auth, endpoint)

    def get_best_endpoint(self):
        raise NotImplementedError()

    def get_bucket(self, bucket_name):
        return Bucket(auth=self.auth, endpoint=self.endpoint, bucket_name=bucket_name)


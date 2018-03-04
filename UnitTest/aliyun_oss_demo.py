# coding: utf-8
import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))

from xtelescope import config
import xtelescope.oss

oss_service = config["oss"]
access_key = config["oss_access_key"]
secret_key = config["oss_secret_key"]

oss = xtelescope.oss.use(oss_service)
oss.prepare(access_key, secret_key, endpoint=config["oss_endpoint"])

bucket = oss.get_bucket("open-luna")

# 查看权限
print(bucket.get_bucket_acl().acl)

# 也可以用字典方式访问bucket
bucket = oss["open-luna"]

from itertools import islice
import oss2
for b in islice(oss2.ObjectIterator(bucket), 10):
    print(b.key)

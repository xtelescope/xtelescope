# coding: utf-8
import os
import logging
import threading
import time
from openastro.image import Image
import shutil
import stomp

# 业务代码，因此与xtelescope有强耦合也没关系吧
from xtelescope import config as cfg
import xtelescope.oss
from datetime import datetime
import json


class FitToThumbnail:

    def __init__(self, logger_name="auto_thumbnail", bucket_name="open-luna", device_name="ALT-zsy"):
        self.device_name = device_name
        self.cfg = cfg
        self.logger = logging.getLogger(logger_name)

        self.fits_root_path = self.cfg["fits_root_path"]        # 未处理fit路径
        self.thumbnail_root_path = self.cfg["thumbnail_root_path"]  # 存放缩略图路径
        self.thumbnail_width = self.cfg["thumbnail_width"]
        self.thumbnail_height = self.cfg["thumbnail_height"]
        self.bayer_pattern = self.cfg["bayer_pattern"]
        self.processed_fits_path = self.cfg["processed_fits_path"]  # 处理完毕后fit图片的存放路径

        self.bucket_name = bucket_name
        oss_service = cfg["oss"]
        access_key = cfg["oss_access_key"]
        secret_key = cfg["oss_secret_key"]
        self.oss = xtelescope.oss.use(oss_service)
        self.oss.prepare(access_key, secret_key, endpoint=cfg["oss_endpoint"])

        # TODO: 暂时没有添加文件日志句柄
        self.logfile = self.cfg["logfile"]
        self.loglevel = self.cfg["loglevel"]

        """
        将logging设置为DEBUG，用于调试，生产环境可以设置为INFO甚至WARNING
        """
        formatter = logging.Formatter(
            '[%(levelname)s] %(asctime)s - %(name)s - %(lineno)d - %(message)s'
        )
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.info(
            "Config Loaded: {}".format(self.cfg)
        )

        self.conn_send = stomp.Connection10([('msg.xtelescope.net', 61613)], auto_content_length=False)
        self.conn_send.start()
        self.conn_send.connect([('msg.xtelescope.net', 61613)], wait=True)

    def walk_dirs(self, path="."):
        for root, dirs, files in os.walk(path):
            for name in files:
                image_path = os.path.join(root, name)
                print(image_path)
                self.image_handler(image_path)

    def image_handler(self, image_path):
        directory, image_name = os.path.split(image_path)
        image = Image(directory, image_name)
        image.bayer_to_rgb(
            self.bayer_pattern
        )
        img_backup = image.image_data
        image.resize(
            width=self.thumbnail_width,
            height=self.thumbnail_height
        ).save_to(
            directory=self.thumbnail_root_path,
            image_name=os.path.splitext(image_name)[0] + "_thumbnail.png"
        )
        image.image_data = img_backup
        image.center_crop(
            self.thumbnail_width,
            self.thumbnail_height
        ).save_to(
            directory=self.thumbnail_root_path,
            image_name=os.path.splitext(image_name)[0] + "_thumbnail_center_crop.png"
        )
        shutil.move(image_path, self.processed_fits_path)

        # 将图片上传oss
        # TODO: need to handle possible Exceptions
        # TODO: 断点续传
        # TODO: use threadings
        bucket = self.oss[self.bucket_name]
        public_base_url = "https://" + self.bucket_name + "." + self.cfg["oss_endpoint"] + "/"
        # original fits
        bucket.put_object_from_file(
            os.path.join(self.processed_fits_path, image_name),
            image_name
        )
        image_url = public_base_url + image_name
        msg_to_send = {
            "messageTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "msgType": "数据处理",
            "deviceName": self.device_name,
            "deviceColor": "#FFAA00",
            "cameraImage": "",
            "messageColor": "green",
            "ossURL": image_url
        }
        self.conn_send.send('/topic/euipment_status', body=json.dumps(msg_to_send), headers={'type': 'textMessage'})

        # thumbnail
        thumbnail_name = os.path.splitext(image_name)[0] + "_thumbnail.png"
        bucket.put_object_from_file(
            os.path.join(
                self.thumbnail_root_path,
                thumbnail_name
            ),
            thumbnail_name
        )
        image_url = public_base_url + thumbnail_name
        msg_to_send = {
            "messageTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "msgType": "预览图",
            "deviceName": self.device_name,
            "deviceColor": "#FFAA00",
            "messageColor": "green",
            "ossURL": image_url
        }
        self.conn_send.send('/topic/euipment_status', body=json.dumps(msg_to_send), headers={'type': 'textMessage'})

        thumbnail_name = os.path.splitext(image_name)[0] + "_thumbnail_center_crop.png"
        bucket.put_object_from_file(
            os.path.join(
                self.thumbnail_root_path,
                thumbnail_name
            ),
            thumbnail_name
        )
        image_url = public_base_url + thumbnail_name
        msg_to_send = {
            "messageTime": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "msgType": "预览图",
            "deviceName": self.device_name,
            "deviceColor": "#FFAA00",
            "messageColor": "green",
            "ossURL": image_url
        }
        self.conn_send.send('/topic/euipment_status', body=json.dumps(msg_to_send), headers={'type': 'textMessage'})

        self.logger.info("{} processed".format(image_path))

    def check_config(self, config="config.json"):
        # 读取配置
        while True:
            time.sleep(3)
            try:
                self.cfg = cfg.reload()
                thumbnail_width = self.cfg["thumbnail_width"]
                thumbnail_height = self.cfg["thumbnail_height"]
                fits_root_path = self.cfg["fits_root_path"]
                thumbnail_root_path = self.cfg["thumbnail_root_path"]
                processed_fits_path = self.cfg["processed_fits_path"]
                if not os.path.isdir(fits_root_path):
                    self.logger.error(
                        "fits_root_path error: {}.\n"
                        "Please check your config file:".format(fits_root_path)
                    )
                elif fits_root_path != self.fits_root_path:
                    self.logger.info(
                        "fits_root_path changed from {} to {}".format(self.fits_root_path, fits_root_path)
                    )
                    self.fits_root_path = fits_root_path

                if not os.path.isdir(processed_fits_path):
                    self.logger.error(
                        "fits_root_path error: {}.\n"
                        "Please check your config file:".format(processed_fits_path)
                    )
                elif processed_fits_path != self.processed_fits_path:
                    self.logger.info(
                        "processed_fits_path changed from {} to {}".format(self.processed_fits_path, processed_fits_path)
                    )
                    self.processed_fits_path = processed_fits_path

                if not os.path.isdir(thumbnail_root_path):
                    self.logger.error(
                        "thumbnail_root_path error: {}.\n"
                        "Please check your config file:".format(thumbnail_root_path)
                    )
                elif thumbnail_root_path != self.thumbnail_root_path:
                    self.logger.info(
                        "thumbnail_root_path changed from {} to {}".format(self.thumbnail_root_path, thumbnail_root_path)
                    )
                    self.thumbnail_root_path = thumbnail_root_path

                if thumbnail_width != self.thumbnail_width:
                    self.logger.info(
                        "thumbnail_width changed from: {} to {}".format(self.thumbnail_width, thumbnail_width)
                    )
                    self.thumbnail_width = thumbnail_width

                if thumbnail_height != self.thumbnail_height:
                    self.logger.info(
                        "thumbnail_height changed from:{} to {}".format(
                            self.thumbnail_height,
                            thumbnail_height
                        )
                    )
                    self.thumbnail_height = thumbnail_height

            except Exception as e:
                self.logger.error(e)

    def start(self,):
        # 开启一个线程轮询config，如果有变化会更新设置
        thread_config = threading.Thread(target=self.check_config, args=("config.json",), daemon=True)
        thread_config.start()
        while True:
            self.walk_dirs(self.fits_root_path)
            time.sleep(5)


if __name__ == '__main__':
    # 设置屏幕输出句柄
    worker = FitToThumbnail(
        logger_name="auto_thumbnail",
        bucket_name="open-luna"
    )
    worker.start()

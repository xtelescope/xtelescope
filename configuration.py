# coding: utf-8
import json
import os
# In order to avoid carelessly pushing sensitive information(account, password, secret key, etc...) to git,
# it is recommended to use this script to generate a `config.json`


def input_with_default(text, key, default, options=None):
    global config
    if key in config:
        default = config[key]
    else:
        if isinstance(options, list):
            default = options[0]

    if options is None:
        choice = input(text + " (default:{}): ".format(default))
        if choice == "":
            return default
        else:
            return choice
    else:
        choice = None
        while choice not in options:
            choice = input(text + "{} (default:{}): ".format(options, default))
            if choice == "":
                return default
        return choice

if __name__ == "__main__":
    global config
    with open("config.json", "r") as cfg:
        try:
            config = json.load(cfg)
        except Exception as e:
            config = dict()
    print(config)
    print("Generating xtelescope config:")
    config["oss"] = input_with_default("Select OSS service", "oss", "aliyun", options=["aliyun", "qiniu"])
    config["oss_access_key"] = input_with_default("OSS access_key", "oss_access_key", "", options=None)
    config["oss_secret_key"] = input_with_default("OSS secret_key", "oss_secret_key", "", options=None)
    config["oss_endpoint"] = input_with_default("OSS endpoint", "oss_endpoint", "", options=None)

    config["fits_root_path"] = input_with_default("Input fits_root_path", "fits_root_path", "",)
    config["thumbnail_root_path"] = input_with_default("Input thumbnail_root_path", "thumbnail_root_path", "",)
    config["processed_fits_path"] = input_with_default("Input processed_fits_path", "processed_fits_path", "",)
    config["thumbnail_width"] = input_with_default("Input thumbnail_width", "thumbnail_width", 640,)
    config["thumbnail_height"] = input_with_default("Input thumbnail_height", "thumbnail_height", 480,)
    config["bayer_pattern"] = input_with_default("Input bayer pattern", "bayer_pattern", "bggr", options=["bggr", "rggb", "grbg", "gbrg"])

    config["logfile"] = input_with_default("Input logfile", "logfile", "logs/xtelescope.log")
    config["loglevel"] = input_with_default("Input log level", "loglevel", "info")

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)


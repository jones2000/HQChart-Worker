# -*- coding: utf-8 -*-#
import hashlib
import json
import logging
import os
import shutil
import zipfile
import requests

from hqchartPy2.core.tools import get_current_date
from hqchartPy2.extention import CDN_DATA_CONFIG, progress_bar, DataFileType


class SyncDataTask(object):
    def __init__(self):
        self.latestDataDate = None  # 数据最新的日期
        self.counts = 0  # 已经处理过的文件总数
        self.ttlCounts = 0  # 总文件数
        self.status = False  # 数据同步状态
        self.msg = ""  # 同步信息

    def get_data_count(self, base_dir, dType):
        """
        获取数据的总记录数
        :param base_dir:
        :param dType:
        :return:
        """
        key = CDN_DATA_CONFIG[dType].get("filename")
        file_name = os.path.join(base_dir, key)
        data = self.load_json(filename=file_name)
        if data is None:
            return 0
        if dType in [DataFileType.DAY_KLINE_FILE_TYPE,DataFileType.MIN_KLINE_FILE_TYPE]:
            return len(data["data"])
        elif dType in [DataFileType.FINANCE_FILE_TYPE,DataFileType.CAPITAL_FILE_TYPE]:
            return len(data.keys())
        elif dType in [DataFileType.SYMBOLE_FILE_TYPE]:
            return len(data["symbollist"])

    @staticmethod
    def download_data_file_from_cdn(url, filepath, filename):
        """
        从cdn下载文件
        :param url:
        :param filepath: 文件存放的路径
        :param filename: 文件名称
        :return:
        """
        try:
            logging.info(msg="正在下载文件:{filename},url:{url}".format(filename=filename, url=url))
            response = requests.get(url=url)
            if not os.path.exists(filepath):
                os.makedirs(filepath)
            fullpath = os.path.join(filepath, filename)
            fp = open(fullpath, "wb")
            for item in response.iter_content(chunk_size=400 * 1024):
                fp.write(item)
            fp.close()
            return True,None
        except Exception as e:
            print(str(e))
            return False,str(e)
        finally:
            if fp:
                fp.close()

    @staticmethod
    def hashs(file_name, type="md5", block_size=64 * 1024):
        """
        计算文件的md5值
        Support md5(), sha1(), sha224(), sha256(), sha384(), sha512(), blake2b(), blake2s(),
        sha3_224, sha3_256, sha3_384, sha3_512, shake_128, and shake_256
        :param file_name:
        :param type:
        :param block_size:
        :return:
        """
        with open(file_name, 'rb') as file:
            hash = hashlib.new(type, b"")
            while True:
                data = file.read(block_size)
                if not data:
                    break
                hash.update(data)
            return hash.hexdigest()

    @staticmethod
    def unzip(base_dir, filename):
        """
        解压缩zip文件
        :param base_dir:
        :param filename:
        :return:
        """
        extract_dir = os.path.join(base_dir, 'tmp')
        if not os.path.exists(base_dir):
            os.makedirs(extract_dir)
        full_path = os.path.join(base_dir, filename)
        fp = None
        try:
            fp = zipfile.ZipFile(full_path)
            for fitem in fp.namelist():
                fp.extract(fitem, extract_dir)
            fp.close()
            return True,None
        except Exception as e:
            print(str(e))
            return False,str(e)
        finally:
            if fp:
                fp.close()
        return True

    @staticmethod
    def load_json(filename):
        fp = None
        try:
            fp = open(filename,encoding="utf8")
            json_data = json.load(fp=fp)
            fp.close()
            return json_data
        except Exception as e:
            return None
        finally:
            if fp:
                fp.close()
        return None

    @staticmethod
    def merge_json(src, tgt, dtype=DataFileType.MIN_KLINE_FILE_TYPE):
        """
        将src的json文件合并到tgt的json文件中，并对数据项进行去重
        :param src: 新增的数据文件
        :param tgt: 原始数据的文件，
        :param dtype: 数据文件类型，默认是分钟K线
        :return:
        """
        try:
            tgt_json = SyncDataTask.load_json(tgt)
            src_json = SyncDataTask.load_json(src)
            if src_json is None or len(src_json["data"]) == 0:
                return True
            if tgt_json and len(tgt_json["data"]) > 0 and src_json["data"][-1][0] <= tgt_json["data"][-1][
                0]:  # 数据已经合并过，无需合并
                return True
            if tgt_json is None or len(tgt_json["data"]) == 0:
                tgt_json = src_json
            else:  # 合并文件
                if src_json["data"][0][0] <= tgt_json["data"][-1][0]:
                    tgt_json["data"].extend(src_json["data"])
                    # 去重处理
                    delrepeated_map = {}
                    for item in tgt_json["data"]:
                        if dtype == DataFileType.MIN_KLINE_FILE_TYPE:
                            key = str(item[0]) + "_" + str(item[8])
                        else:
                            key = str(item[0])
                        delrepeated_map[key] = item
                    tgt_json["data"] = list(delrepeated_map.values())
                    tgt_json["count"] = len(tgt_json["data"])
                else:
                    tgt_json["data"].extend(src_json["data"])
            with open(tgt, "w",encoding="utf-8") as fp:
                fp.write(json.dumps(tgt_json, indent=1, ensure_ascii=False))
            return True
        except Exception as e:
            return False

    def get_remote_meta_info(self, meta_url):
        """
        :param meta_url:
        :return:
        """
        try:
            return requests.get(url=meta_url).json()
        except Exception as e:
            print(str(e))
        return {}

    def get_local_meta_info(self, base_dir):
        """
        获取本地的metainfo信息
        :param meta_url:
        :return:
        """
        fp = None
        try:
            metafile = os.path.join(base_dir, "metainfo.json")
            fp = open(metafile)
            data = json.load(fp)
            fp.close()
            return data
        except Exception as e:
            return {}
        finally:
            if fp:
                fp.close()
        return {}

    def update_local_meta_info(self, base_dir, data):
        """
        更新本地metainfo文件
        :param meta_url:
        :return:
        """
        fp = None
        try:
            metafile = os.path.join(base_dir, "metainfo.json")
            fp = open(metafile, "w",encoding="utf-8")
            fp.write(json.dumps(data, indent=1, ensure_ascii=False))
            fp.close()
            return True
        except Exception as e:
            print(str(e))
        finally:
            if fp:
                fp.close()
        return {}

    def sync_kline_data_file(self, base_dir, dType):
        """
        同步K线数据文件
        :param dType:
        :return:
        """
        try:
            cdn_url = CDN_DATA_CONFIG[dType]["url"]
            remote_meta_filename = CDN_DATA_CONFIG[dType]["metainfo"]
            meta_url = cdn_url + remote_meta_filename
            meta_info = self.get_remote_meta_info(meta_url=meta_url)
            file_list = meta_info["file_list"]
            locale_meta_info = self.get_local_meta_info(base_dir=base_dir)
            # 同步进度条
            progress_bar[dType]["taskname"] = "开始同步数据..."
            progress_bar[dType]["syncStatus"]  = 1  #正在处理中
            progress_bar[dType]["total"] = 0
            progress_bar[dType]["cur"] = 0
            progress_bar[dType]["percent"] = 0

            #遍历远程的文件列表
            for item in file_list:
                logging.info(msg=item)
                filename = item.get("filename")  # 压缩包名称
                progress_bar[dType]["taskname"] = "处理数据文件:{filename}".format(filename=filename)
                if int(item["end"]) <= int(locale_meta_info.get("latest_date", 0)):
                    self.msg = "文件{}已经被同步到本地，无需做任何操作".format(filename)
                    continue
                file_prefix = str(filename).split(".")[0]
                fileurl = CDN_DATA_CONFIG[dType]["url"] + filename
                progress_bar[dType]["total"] = 0
                progress_bar[dType]["cur"] = 0
                progress_bar[dType]["percent"] = 0

                #判断本地是否存在zip文件包，如果不存在，则从网络上下载，如果存在，且md5值和远程一致，则不用下载，直接跳过
                fullpath = os.path.join(base_dir, filename)
                if not os.path.exists(fullpath) or self.hashs(file_name=fullpath) != item.get("md5"):
                    # 下载文件
                    ret,msg = self.download_data_file_from_cdn(url=fileurl, filename=filename, filepath=base_dir)
                    progress_bar[dType]["taskname"] = "下载文件:{filename}".format(filename=filename)
                    if not ret:
                        self.msg = "文件:{filename}下载失败,地址:{fileurl}".format(filename=filename, fileurl=fileurl)
                        progress_bar[dType]["syncStatus"] = 3
                        progress_bar[dType]["msg"] = "数据文件:{filename}下载失败:{msg}".format(filename=filename,msg=msg)
                        self.status = False
                        return False

                # 解压文件
                ret,msg = self.unzip(base_dir=base_dir, filename=filename)
                progress_bar[dType]["taskname"] = "解压文件:{filename}到目录：{base_dir}".format(filename=filename,base_dir=base_dir)
                if not ret:
                    self.status = False
                    self.msg = "文件:{}解压失败".format(filename)
                    progress_bar[dType]["syncStatus"] = 3
                    progress_bar[dType]["msg"] = "文件:{filename}解压失败:{msg}".format(filename=filename,
                                                                                                    msg=msg)
                    return False,

                # 将新增的数据文件合并到指标计算系统中的数据文件内
                extracted_path = os.path.join(base_dir, 'tmp', file_prefix)
                sub_file_list = os.listdir(extracted_path)
                self.ttlCounts = len(sub_file_list)
                progress_bar[dType]["taskname"] = "合并数据文件:{}".format(filename)
                progress_bar[dType]["total"] = len(sub_file_list)
                for sfile in sub_file_list:
                    progress_bar[dType]["cur"] += 1
                    progress_bar[dType]["percent"] = round(
                        progress_bar[dType]["cur"] * 1.0 / progress_bar[dType]["total"] * 1.0, 2) * 100

                    src_filename = os.path.join(base_dir, sfile)
                    new_filename = os.path.join(base_dir, 'tmp', file_prefix, sfile)
                    if not os.path.exists(src_filename): #源文件不存在，则直接复制
                        shutil.copyfile(src=new_filename, dst=src_filename)
                    else:  # 源文件存在，则合并json文件
                        self.merge_json(src=new_filename, tgt=src_filename, dtype=dType)
                shutil.rmtree(path=extracted_path)
                locale_meta_info["latest_date"] = item["end"]
                locale_meta_info["filename"] = item["filename"]
                # 更新本地metainfo
                self.update_local_meta_info(base_dir=base_dir, data=locale_meta_info)
                self.msg = "文件{}已成功同步到本地".format(filename)
            # 获取数据总记录数
            self.counts = self.get_data_count(base_dir, dType)
            self.latestDataDate = item["end"]
            progress_bar[dType]["syncStatus"] = 2  #处理成功
            progress_bar[dType]["percent"] = 100  # 处理成功
            progress_bar[dType]["msg"] = "所有数据文件都已同步到本地"  # 处理成功
            progress_bar[DataFileType(item.type)]["isCache"] = False
            return True
        except Exception as e:
            self.status = False
            progress_bar[dType]["syncStatus"] = 3  # 处理失败
            progress_bar[dType]["msg"] = str(e)  # 处理失败
            self.msg = str(e)
            return False
        return True

    def sync_system_data_file(self, dataType,base_dir):
        """
        同步码表数据文件
        :param dType:
        :return:
        """
        try:
            filename = CDN_DATA_CONFIG[dataType]["filename"]
            cdn_url = CDN_DATA_CONFIG[dataType]["url"]
            progress_bar[dataType]["taskname"] = "处理数据文件:{filename}".format(filename=filename)
            progress_bar[dataType]["syncStatus"] = 1
            # 下载文件
            ret,msg = self.download_data_file_from_cdn(url=cdn_url, filename=filename, filepath=base_dir)
            if not ret:
                self.msg = "文件:{filename}下载失败,地址:{fileurl}".format(filename=filename, fileurl=cdn_url)
                progress_bar[dataType]["syncStatus"] = 3
                progress_bar[dataType]["msg"] = self.msg
                self.status = False
                return False
            self.counts = self.get_data_count(base_dir=base_dir, dType=dataType)
            self.latestDataDate = get_current_date(format="%Y%m%d")
            self.msg = "文件{}已成功同步到本地".format(filename)
            progress_bar[dataType]["syncStatus"] = 2
            progress_bar[dataType]["msg"] = self.msg
            progress_bar[dataType]["isCache"] = False
            return True
        except Exception as e:
            self.status = False
            self.msg = str(e)
            return False
        return True


if __name__ == '__main__':

    msg = DataFileType.DAY_KLINE_FILE_TYPE
    print(type(msg))
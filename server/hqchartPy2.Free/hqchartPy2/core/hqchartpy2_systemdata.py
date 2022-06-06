#
#	Copyright (c) 2021 jones
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	开源项目 https://github.com/jones2000/HQChart
#
#	jones_2000@163.com
#
#	分钟K数据类


import os
import json
import datetime
import logging
from enum import Enum, auto

import requests
from sqlalchemy import true

from hqchartPy2.extention import DataFileType, CDN_DATA_CONFIG


class SYMBOL_DATA_INDEX(Enum):
    SYMBOL_ID = 0  #证券代码
    NAME_ID = 1    #证券名称
    TYPE_ID = 2    #类型
    PINYIN_ID = 3  #拼音

    MAX_COUNT = auto()


class SymbolDataCache(object):
    # 缓存码表数据
    m_Cache = {}  # 1分钟K线缓存
    m_bLoadFinished = False  # 缓存是否加载完成
    m_CachePath = None

    def SetCachePath(path):
        SymbolDataCache.m_CachePath = path

    # 加载缓存
    @staticmethod
    def LoadCache():
        SymbolDataCache.m_bLoadFinished = False
        path = SymbolDataCache.m_CachePath
        log = "[SystemDataCache::LoadCache] start load stock list data. path='{0}' .....".format(path)
        print(log)
        SymbolDataCache.ReadDataFile()

    # 读取K线文件
    @staticmethod
    def ReadDataFile():
        kdataFile = "{0}/symbol.json".format(SymbolDataCache.m_CachePath)  # 码表数据
        try:
            with open(kdataFile, encoding='utf-8') as f:
                data = json.load(f)
                SymbolDataCache.m_Cache = data
                return data
        except:
            return None
        return None

    @staticmethod
    def search_symbol(key):
        """
        模糊搜索股票信息，如股票代码，股票名称，股票的拼音简称
        :param key:
        :return:
        """
        all_stock_list = SymbolDataCache.m_Cache["symbollist"]
        result = []
        priority_list = []
        key = str(key).upper()
        for item in all_stock_list:
            tmpItem = {"symbol": item[SYMBOL_DATA_INDEX.SYMBOL_ID.value], "name": item[SYMBOL_DATA_INDEX.NAME_ID.value],"type":item[SYMBOL_DATA_INDEX.TYPE_ID.value]}
            if str(item[SYMBOL_DATA_INDEX.SYMBOL_ID.value])[:-3].startswith(key) \
                    or str(item[SYMBOL_DATA_INDEX.NAME_ID.value]).startswith(key) \
                    or str(item[SYMBOL_DATA_INDEX.PINYIN_ID.value]).startswith(key):
                priority_list.append(tmpItem)
                continue
            if key in str(item[SYMBOL_DATA_INDEX.SYMBOL_ID.value])[:-3] \
                    or key in str(item[SYMBOL_DATA_INDEX.NAME_ID.value]) \
                    or key in str(item[SYMBOL_DATA_INDEX.PINYIN_ID.value]):
                result.append(tmpItem)
        priority_list.extend(result)
        return priority_list[:100]

    @staticmethod
    def get_block_list():
        """
        获取板块列表
        :param key:
        :return:
        """
        m_Cache = SymbolDataCache.m_Cache
        result = {}
        for btype in m_Cache:
            if btype in("symbollist","metainfo"):
                continue
            if btype not in result:
                result[btype] = []
            for blkid in m_Cache[btype]:
                item = {"id":blkid,"name":m_Cache[btype][blkid]["name"]}
                result[btype].append(item)
        result["market"].append({"id":"symbollist","name":"全部A股"})
        return result,m_Cache["metainfo"]

    @staticmethod
    def get_block_members_by_id(block_id):
        """
        获取板块的成分股列表
        :return:
        """
        m_Cache = SymbolDataCache.m_Cache
        for btype in m_Cache:
            if btype == "symbollist":
                return [item[SYMBOL_DATA_INDEX.SYMBOL_ID.value] for item in m_Cache["symbollist"]]
            if block_id in m_Cache[btype]:
                return [item[SYMBOL_DATA_INDEX.SYMBOL_ID.value] for item in m_Cache[btype][block_id].get("members")]
        return []

    @staticmethod
    def get_symbol_table():
        """
        获取码表,
        :return:dict.eg:{"000001.sz":"平安银行"}
        """
        m_Cache = SymbolDataCache.m_Cache
        result = {}
        for item in m_Cache["symbollist"]:
            result[item[SYMBOL_DATA_INDEX.SYMBOL_ID.value]] = item[SYMBOL_DATA_INDEX.NAME_ID.value]
        return result

    @staticmethod
    def get_symbol_list():
        """
        获取码表,
        :return:dict.eg:{"000001.sz":"平安银行"}
        """
        m_Cache = SymbolDataCache.m_Cache
        data_list = []
        for item in m_Cache["symbollist"]:
            data_list.append({"symbol":item[SYMBOL_DATA_INDEX.SYMBOL_ID.value],"name":item[SYMBOL_DATA_INDEX.NAME_ID.value]})
        return data_list

class FinanceDataCache(object):
    # 缓存财务数据和股本数据
    m_Cache = {
        DataFileType.FINANCE_FILE_TYPE: {},#财务数据
        DataFileType.CAPITAL_FILE_TYPE: {} #股本数据
    }
    m_CachePath = {
        DataFileType.FINANCE_FILE_TYPE:None,
        DataFileType.CAPITAL_FILE_TYPE:None
    }

    def SetCachePath(dataType,path):
        FinanceDataCache.m_CachePath[dataType] = path

    # 加载缓存
    @staticmethod
    def LoadCache(dataType):
        path = FinanceDataCache.m_CachePath[dataType]
        if path is None:
            log = "[FinanceDataCache::LoadCache:{}] 数据目录为空，请先设置数据目录.....".format(dataType)
            print(log)
            return False
        log = "[FinanceDataCache::LoadCache] start load data. path='{0}' .....".format(path)
        logging.info(msg=log)
        filename = CDN_DATA_CONFIG[dataType].get("filename")
        fullpath = os.path.join(path,filename)
        data = FinanceDataCache.ReadDataFile(fullpath)
        if data is not None:
            FinanceDataCache.m_Cache[dataType] = data

    # 读取K线文件
    @staticmethod
    def ReadDataFile(filePath):
        try:
            with open(filePath, encoding='utf-8') as f:
                data = json.load(f)
                return data
        except:
            return None
        return None

    @staticmethod
    def GetDataByType(dataType,symbol):
        """
        获取指定股票的财务数据或者股本数据
        :param dataType:
        :param symbol:
        :return:
        """
        if dataType not in [DataFileType.CAPITAL_FILE_TYPE,DataFileType.FINANCE_FILE_TYPE]:
            return None
        data = FinanceDataCache.m_Cache[dataType].get(symbol,None)
        return data

# TestCase()
if __name__ == '__main__':
    SymbolDataCache.SetCachePath("D:\hqchartPy2\data\symbol")
    SymbolDataCache.LoadCache()
    member_list = SymbolDataCache.get_block_members_by_id(block_id="STARM")
    for item in member_list:
        body = {
            "Right": 1,
            "Period": 0,
            "Symbol": item,
            "StartDate":20210101,
            "EndDate":20220330
        }
        try:
            resp = requests.post(url="http://192.168.0.118:8712/api/DayKLine",json=body).json()
            if len(resp["data"]) == 0:
                print(item)
        except Exception as e:
            print(item)
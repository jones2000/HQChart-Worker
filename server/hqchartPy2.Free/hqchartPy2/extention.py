from concurrent.futures.thread import ThreadPoolExecutor
from enum import Enum, unique

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

#线程池大小
executor = ThreadPoolExecutor(4)

#默认服务端口
service_port = 8712
python_version = 1.2
@unique
class DataFileType(Enum):
    """
    数据文件类型
    """
    #日K数据文件
    DAY_KLINE_FILE_TYPE = 1
    #分钟K线数据
    MIN_KLINE_FILE_TYPE = 2
    #码表数据文件
    SYMBOLE_FILE_TYPE = 3
    # 财务数据
    FINANCE_FILE_TYPE = 4
    # 股本数据
    CAPITAL_FILE_TYPE = 5


DATA_FILE_TYPE_META = {
    DataFileType.DAY_KLINE_FILE_TYPE: "日K数据",
    DataFileType.MIN_KLINE_FILE_TYPE: "分钟K数据",
    DataFileType.SYMBOLE_FILE_TYPE: "码表数据",
    DataFileType.FINANCE_FILE_TYPE: "财务数据",
    DataFileType.CAPITAL_FILE_TYPE:"股本数据"
}

# 最新一期财务数据字典的Key值
FINANCE_META_INFO={
"FINANCE(9)": "资产负债率%",
"FINANCE(10)": "总资产",
"FINANCE(11)": "流动资产",
"FINANCE(12)":"固定资产",
"FINANCE(13)":"无形资产",
"FINANCE(15)":"流动负债",
"FINANCE(16)":"少数股东权益",
"FINANCE(17)":"资本公积金",
"FINANCE(18)" :"每股公积金",
"FINANCE(19)" :"股东权益(净资产)",
"FINANCE(20)" :"营业收入",
"FINANCE(21)" :"营业成本",
"FINANCE(22)" :"应收帐款",
"FINANCE(23)" :"营业利润",
"FINANCE(24)" :"投资收益",
"FINANCE(25)" :"经营现金流量",
"FINANCE(26)" :"总现金流量",
"FINANCE(27)" :"存货",
"FINANCE(28)" :"利润总额",
"FINANCE(29)" :"税后利润",
"FINANCE(30)" :"净利润",
"FINANCE(31)" :"未分配利润",
"FINANCE(32)" :"每股未分配利润",
"FINANCE(33)" :"每股收益",
"FINANCE(34)" :"每股净资产",
"FINANCE(35)" :"季报中调整后的每股净资产",
"FINANCE(36)" :"股东权益比",
"FINANCE(37)" :"第几季报",
"FINANCE(38)" :"每股收益",
"FINANCE(40)" :"流通市值",
"FINANCE(41)" :"AB股总市值",
"FINANCE(42)" :"上市的天数",
"FINANCE(43)" :"利润同比%",
"FINANCE(44)" :"主营收入同比增长率",
"FINANCE(45)":"股息率%",
"FINANCE(55)":"研发费用",
"FINANCE(57)" :"货币资金",
"FINANCE(58)":"预收账款",
}
LATEST_FINACE_DICT_KEYS = [
    'FINANCE(9)', 'FINANCE(10)', 'FINANCE(11)', 'FINANCE(12)', 'FINANCE(13)', 'FINANCE(14)', 'FINANCE(15)',
    'FINANCE(16)', 'FINANCE(17)', 'FINANCE(18)', 'FINANCE(19)', 'FINANCE(20)', 'FINANCE(21)', 'FINANCE(22)',
    'FINANCE(23)', 'FINANCE(24)', 'FINANCE(25)', 'FINANCE(26)', 'FINANCE(27)', 'FINANCE(28)', 'FINANCE(29)',
    'FINANCE(30)', 'FINANCE(31)', 'FINANCE(32)', 'FINANCE(33)', 'FINANCE(34)', 'FINANCE(36)', 'FINANCE(38)',
    'FINANCE(43)', 'FINANCE(44)', 'FINANCE(45)',
    'FINANCE(55)', 'FINANCE(57)', 'FINANCE(58)'
]

"""
股本数据
"""
CAPITAL_META_INFO={
    "CAPITAL":"当前流通股本",
    "TOTALCAPITAL":"当前总股本",
    "FINANCE(1)":"总股本",
    "FINANCE(7)":"流通股本"
}
ALL_CAPITAL_DICT_KEYS = [
    'FINANCE(1)', 'FINANCE(7)'
]

#数据文件在CDN上的地址
CDN_DATA_CONFIG = {
    DataFileType.MIN_KLINE_FILE_TYPE: {
        "url": "http://cdndata.umydata.com/hqchart_data/minute/",
        "metainfo": "metainfo.json",
        "filename":"000001.sh.json"
    },
    DataFileType.DAY_KLINE_FILE_TYPE: {
        "url": "http://cdndata.umydata.com/hqchart_data/day/",
        "metainfo": "metainfo.json",
        "filename":"000001.sh.json"
    },
    DataFileType.SYMBOLE_FILE_TYPE: {
        "url": "http://cdndata.umydata.com/hqchart_data/symbol/symbol.json",
        "filename":"symbol.json"
    },
    DataFileType.FINANCE_FILE_TYPE: {
        "url": "http://cdndata.umydata.com/hqchart_data/finance/finance.json",
        "filename":"finance.json"
    },
    DataFileType.CAPITAL_FILE_TYPE: {
        "url": "http://cdndata.umydata.com/hqchart_data/finance/capital.json",
        "filename":"capital.json"
    }
}


#数据同步进度条
progress_bar = {
    DataFileType.DAY_KLINE_FILE_TYPE:{
        "syncStatus":0,
        "loadStatus":0,
        "isCache":False,
        "taskname":"开始同步数据...",
        "total":0,
        "cur":0,
        "percent":0
    },
    DataFileType.MIN_KLINE_FILE_TYPE: {
        "syncStatus":0,
        "loadStatus":0,
        "isCache":False,
        "taskname": "开始同步数据...",
        "total": 0,
        "cur": 0,
        "percent": 0
    },
    DataFileType.SYMBOLE_FILE_TYPE: {
        "syncStatus": 0,
        "loadStatus":0,
        "isCache":False,
        "taskname": "开始同步数据...",
        "total": 0,
        "cur": 0,
        "percent": 0
    },
    DataFileType.FINANCE_FILE_TYPE: {
        "syncStatus": 0,
        "loadStatus": 0,
        "isCache": False,
        "taskname": "开始同步数据...",
        "total": 0,
        "cur": 0,
        "percent": 0
    },
    DataFileType.CAPITAL_FILE_TYPE: {
        "syncStatus": 0,
        "loadStatus": 0,
        "isCache": False,
        "taskname": "开始同步数据...",
        "total": 0,
        "cur": 0,
        "percent": 0
    },

    "RUNALLPOLICY":{
        "status":0,
        "taskname":"开始运行策略...",
        "total":0,
        "cur":0,
        "percent":0
    }
}

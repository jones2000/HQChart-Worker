#
#	Copyright (c) 2021 jones
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	开源项目 https://github.com/jones2000/HQChart
#
#	jones_2000@163.com
#
#	hqchartPy2数据对接类

import json
import time

from hqchartPy2.core.hqchartpy2_fast import IHQData
from hqchartPy2.core.hqchartpy2_klinedata import KLineCache
from hqchartPy2.core.hqchartpy2_klineminutedata import MinuteKLineCache
from hqchartPy2.core.hqchartpy2_systemdata import FinanceDataCache
from hqchartPy2.extention import LATEST_FINACE_DICT_KEYS, DataFileType


class HQChartData(IHQData):
    def __init__(self):
        super(HQChartData, self).__init__()
        # 指定计算K线日期范围
        self.m_nStartDate = None
        self.m_nEndDate = None
        self.m_nCalculateCount = None  # 指定计算K线个数

    def SetDateRange(self, startDate, endDate):
        self.m_nStartDate = startDate
        self.m_nEndDate = endDate

    def GetKLineData(self, symbol, period, right, jobID):
        if (MinuteKLineCache.IsMinutePeriod(period)):
            return MinuteKLineCache.GetMinuteKLine(symbol, period, right, self.m_nStartDate, self.m_nEndDate,
                                                   self.m_nCalculateCount)
        return KLineCache.GetDayKLine(symbol, period, right, self.m_nStartDate, self.m_nEndDate, self.m_nCalculateCount)

    def GetFinance(self, symbol, id, period, right, kcount, jobID):
        #获取财务数据和股本数据
        finace_key = 'FINANCE({id})'.format(id=id)
        # 最新一期财务数据
        if finace_key in LATEST_FINACE_DICT_KEYS:
            # 从内存中获取最新一期财务数据
            finance_dict = FinanceDataCache.GetDataByType(dataType=DataFileType.FINANCE_FILE_TYPE,
                                                          symbol=symbol)
            if finance_dict is None or finace_key not in finance_dict:
                return {"error", "FINANCE({0})获取数据失败".format(id)}
            data = finance_dict.get(finace_key)
            if data is None:
                return {"error", "FINANCE({0})获取数据失败".format(id)}
            result = {"type": 0, "data": data}
            return result
        elif finace_key in (u'FINANCE(1)', u'FINANCE(7)'):
            # 从内存中获取历史所有的股本数据
            capital_dict = FinanceDataCache.GetDataByType(dataType=DataFileType.CAPITAL_FILE_TYPE,
                                                          symbol=symbol)
            if capital_dict is None or len(capital_dict.get(finace_key, [])) == 0:
                return {"error", "FINANCE({0})获取数据失败".format(id)}
            result = dict()
            result["type"] = 2
            result["data"] = capital_dict[finace_key]
            result["date"] = capital_dict["Date"]
            return result
        # TODO:其他数据后面自己加吧
        return {"error", "FINANCE({0})获取数据失败".format(id)}

    def GetDynainfo(self, symbol, id, period, right, kcount, jobID):
        data = {"type": 0, "data": 5}
        return data

    def GetCapital(self, symbol, period, right, kcount, jobID):
        finace_key = u"FINANCE(7)"
        # 从内存中获取历史所有的股本数据
        capital_dict = FinanceDataCache.GetDataByType(dataType=DataFileType.CAPITAL_FILE_TYPE,
                                                      symbol=symbol)
        if capital_dict is None or len(capital_dict.get(finace_key, [])) == 0:
            return {"error", "FINANCE({0})获取数据失败".format(id)}
        data = capital_dict[finace_key][-1]
        if data is None:
            return {"error", "FINANCE({0})获取数据失败".format(id)}
        result = dict()
        result["type"] = 0
        result["data"] = data
        return result

    def GetTotalCapital(self,symbol, period, right, kcount,jobID):
        finace_key = u"FINANCE(1)"
        # 从内存中获取历史所有的股本数据
        capital_dict = FinanceDataCache.GetDataByType(dataType=DataFileType.CAPITAL_FILE_TYPE,
                                                      symbol=symbol)
        if capital_dict is None or len(capital_dict.get(finace_key,[])) == 0:
            return {"error", "FINANCE({0})获取数据失败".format(id)}
        data = capital_dict[finace_key][-1]
        if data is None:
            return {"error", "FINANCE({0})获取数据失败".format(id)}
        result = dict()
        result["type"] = 0
        result["data"] = data
        return result

    # 历史所有的流通股 
    def GetHisCapital(self, symbol, period, right, kcount, jobID):
        finace_key = u"FINANCE(7)"
        # 从内存中获取历史所有的股本数据
        capital_dict = FinanceDataCache.GetDataByType(dataType=DataFileType.CAPITAL_FILE_TYPE,
                                                      symbol=symbol)
        if capital_dict is None or len(capital_dict.get(finace_key,[])) == 0:
            return {"error", "FINANCE({0})获取数据失败".format(id)}
        result = dict()
        result["type"] = 2
        result["date"] = capital_dict["Date"]
        result["data"] = capital_dict[finace_key]
        return result

    # 大盘数据
    def GetIndex(self, symbol, varName, period, right, kcount, jobID):
        if (varName == u'INDEXA'):  # 大盘成交额
            pass
        elif (varName == u'INDEXC'):  # 大盘收盘价
            pass
        elif (varName == u'INDEXH'):  # 大盘最高价
            pass
        elif (varName == u'INDEXL'):  # 大盘最低价
            pass
        elif (varName == u'INDEXO'):  # 大盘开盘价
            pass
        elif (varName == u'INDEXV'):  # 大盘成交量
            pass
        elif (varName == u'INDEXADV'):  # 上涨家数
            pass
        elif (varName == u'INDEXDEC'):  # 下跌家数
            pass

        # 测试数据
        pyCacheData = []
        for i in range(kcount):
            pyCacheData.append(2888.8 + i)
        data = {"type": 1, "data": pyCacheData}
        return data

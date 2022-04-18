#
#	Copyright (c) 2021 jones
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	开源项目 https://github.com/jones2000/HQChart
#
#	jones_2000@163.com
#
#   提供前端行情api数据 

import json
import time

# 日线数据
from hqchartPy2.core.hqchartpy2_klinedata import KLineCache
from hqchartPy2.core.hqchartpy2_klineminutedata import MinuteKLineCache


class DayKLineController(object):
    def __init__(self):
        self.m_strSymbol = None  # 股票代码
        self.m_nPeriod = 0  # 周期 目前只支持：0-日线；1-周线；2-月线；3-年线
        self.m_nRight = 0  # 复权
        self.m_nStartDate = None  # 开始日期
        self.m_nEndDate = None  # 截止日期
        self.m_Error = None
        self.m_Result = None

    def SetPostData(self, request):
        if (request.method != "POST"):
            self.m_Error = "only support 'Post' method."
            return False

        if (request.mimetype == "application/x-www-form-urlencoded"):
            requestData = request.form
        else:
            requestData = json.loads(request.get_data(as_text=True))

        strSymbol = requestData['Symbol']
        self.m_strSymbol = strSymbol

        # 可选参数
        if ("Period" in requestData):
            self.m_nPeriod = requestData["Period"]
        if ("Right" in requestData):
            self.m_nRight = requestData["Right"]
        if ("StartDate" in requestData):
            self.m_nStartDate = requestData["StartDate"]
        if ("EndDate" in requestData):
            self.m_nEndDate = requestData["EndDate"]
        # todo:检测参数有效性
        # self.m_Error="xxxxx错误提示"

        return True

    def Run(self):
        kData = KLineCache.GetDayKLineAPIData(self.m_strSymbol, self.m_nPeriod, self.m_nRight, self.m_nStartDate,
                                              self.m_nEndDate)
        if (kData == None):
            self.m_Error = "can't find {0} kline data.".format(self.m_strSymbol)
            return False

        self.m_Result = kData
        return True

    def GetResponseData(self):
        if (self.m_Error != None):
            responseData = {'code': 1, "data": [], "error": self.m_Error}
            return responseData

        responseData = self.m_Result
        responseData["code"] = 0  # 成功

        return responseData


# 分钟K线数据
class MinuteKLineController(object):
    def __init__(self):
        self.m_strSymbol = None  # 股票代码
        self.m_nPeriod = 0  # 周期 4=1分钟 5=5分钟 6=15分钟 7=30分钟 8=60分钟
        self.m_nRight = 0  # 复权
        self.m_nStartDate = None  # 开始日期
        self.m_nEndDate = None  # 截止日期
        self.m_Error = None
        self.m_Result = None

    def SetPostData(self, request):
        if (request.method != "POST"):
            self.m_Error = "only support 'Post' method."
            return False

        if (request.mimetype == "application/x-www-form-urlencoded"):
            requestData = request.form
        else:
            requestData = json.loads(request.get_data(as_text=True))

        strSymbol = requestData['Symbol']
        self.m_strSymbol = strSymbol

        # 可选参数
        if ("Period" in requestData):
            self.m_nPeriod = requestData["Period"]
        if ("Right" in requestData):
            self.m_nRight = requestData["Right"]
        if ("StartDate" in requestData):
            self.m_nStartDate = requestData["StartDate"]
        if ("EndDate" in requestData):
            self.m_nEndDate = requestData["EndDate"]
        # todo:检测参数有效性
        # self.m_Error="xxxxx错误提示"

        return True

    def Run(self):
        kData = MinuteKLineCache.GetMinuteKLineAPIData(self.m_strSymbol, self.m_nPeriod, self.m_nRight,
                                                       self.m_nStartDate, self.m_nEndDate)
        if (kData == None):
            self.m_Error = "can't find {0} kline data.".format(self.m_strSymbol)
            return False

        self.m_Result = kData
        return True

    def GetResponseData(self):
        if (self.m_Error != None):
            responseData = {'code': 1, "data": [], "error": self.m_Error}
            return responseData

        responseData = self.m_Result
        responseData["code"] = 0  # 成功

        return responseData

#
#	Copyright (c) 2021 jones
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	开源项目 https://github.com/jones2000/HQChart
#
#	jones_2000@163.com
#
#	日K数据类
import logging
import os
import json
import datetime
from enum import Enum, auto

from hqchartPy2.extention import progress_bar, DataFileType


class DAY_KLINE_DATA_INDEX(Enum):
    DATE_ID = 0   #日期
    YCLOSE_ID = 1 #昨日收盘价
    OPEN_ID = 2   #开盘价
    HIGH_ID = 3   #最高价
    LOW_ID = 4    #最低价
    CLOSE_ID = 5  #收盘价
    VOL_ID = 6    #成交量
    AMOUNT_ID = 7 #成交额

    MAX_COUNT = auto()


class KLineCache(object):
    # 日K缓存
    m_Cache = {}  # 日K缓存
    m_bLoadFinished = False  # 缓存是否加载完成
    m_CachePath = None

    @classmethod
    def SetCachePath(cls, path):
        KLineCache.m_CachePath = path

    # 加载缓存
    @classmethod
    def LoadCache(cls):
        KLineCache.m_bLoadFinished = False
        path = KLineCache.m_CachePath
        log = "[KLineCache::LoadCache] start load day kline data. path='{0}' .....".format(path)
        logging.info(msg=log)
        aryFiles = os.listdir(path)
        progress_bar[DataFileType.DAY_KLINE_FILE_TYPE]["taskname"] = "开始加载数据文件{cur}/{ttl}".format(cur=0,ttl=len(aryFiles))
        progress_bar[DataFileType.DAY_KLINE_FILE_TYPE]["total"] = len(aryFiles)
        for item in aryFiles:
            progress_bar[DataFileType.DAY_KLINE_FILE_TYPE]["cur"] += 1
            progress_bar[DataFileType.DAY_KLINE_FILE_TYPE]["taskname"] = "加载数据文件:{cur}/{ttl}".format(cur=progress_bar[DataFileType.DAY_KLINE_FILE_TYPE]["cur"],
                                                                                                      ttl=len(aryFiles))
            progress_bar[DataFileType.DAY_KLINE_FILE_TYPE]["percent"] = round(
                progress_bar[DataFileType.DAY_KLINE_FILE_TYPE]["cur"] * 1.0 / progress_bar[DataFileType.DAY_KLINE_FILE_TYPE]["total"] * 1.0, 2) * 100

            strFile = path + "/" + item
            if os.path.isdir(strFile) or item == 'metainfo.json' or not str(item).endswith("json"):
                continue
            KLineCache.load_kline_data_by_symbol(symbol_filename=strFile)
        progress_bar[DataFileType.DAY_KLINE_FILE_TYPE]["percent"] = 100
        KLineCache.m_bLoadFinished = True
        log = "[KLineCache::LoadCache] finish load day kline data. count={0}".format(len(KLineCache.m_Cache))
        logging.info(msg=log)
        return True

    @staticmethod
    def load_kline_data_by_symbol(symbol_filename):
        try:
            logging.info(msg=symbol_filename)
            with open(symbol_filename, encoding="utf-8") as f:
                kData = json.load(f)
                symbol = kData['symbol']
                name = kData["name"]
                dataCount = len(kData['data'])
                log = "[KLineCache::LoadCache] symbol={0}, name={1}, dataCount={2}".format(symbol, name,
                                                                                           dataCount)
                logging.info(msg=log)
                KLineCache.m_Cache[symbol.lower()] = kData
                return kData
        except Exception as e:
            log = "[KLineCache::LoadCache] load {symbol_filename} minute kline error:{msg}".format(
                symbol_filename=symbol_filename, msg=str(e))
            logging.error(msg=log)
            return None

    # 查找K线数据
    def GetDayKLineCache(symbol):
        if (KLineCache.m_bLoadFinished == False):
            return None
        if (symbol not in KLineCache.m_Cache):
            filename = "{}.json".format(symbol)
            filename = os.path.join(KLineCache.m_CachePath, filename)
            return KLineCache.load_kline_data_by_symbol(filename)
        return KLineCache.m_Cache[symbol]

    # 读取K线文件
    def ReadDayKLineFile(symbol):
        kdataFile = "{0}/{1}.json".format(KLineCache.m_CachePath, symbol)  # 日线数据
        try:
            with open(kdataFile, encoding='utf-8') as f:
                kData = json.load(f)
                symbol = kData["symbol"]
                if (symbol != None):
                    return kData
        except:
            log = "[KLineCache::ReadDayKLineFile] Error: read kline data failed.{0}".format(symbol)
            print(log)
            return None
        return None

    # 转换成HQChartPy数据格式
    def ConvertToHQChartData(kData, result):
        dataCount = len(kData['data'])
        aryDate = []
        aryClose = []
        aryYClose = []
        aryOpen = []
        aryHigh = []
        aryLow = []
        aryVol = []
        aryAmount = []

        for i in range(dataCount):
            item = kData['data'][i]
            aryDate.append(item[0])
            aryYClose.append(item[1])
            aryOpen.append(item[2])
            aryHigh.append(item[3])
            aryLow.append(item[4])
            aryClose.append(item[5])
            aryVol.append(item[6])
            aryAmount.append(item[7])

        result["count"] = dataCount
        result["date"] = aryDate
        # cacheData["time"]=aryTime
        result["yclose"] = aryYClose
        result["open"] = aryOpen
        result["high"] = aryHigh
        result["low"] = aryLow
        result["close"] = aryClose
        result["vol"] = aryVol
        result["amount"] = aryAmount

    # 拷贝数据
    def CopyKItem(kItem):
        newItem = [0] * DAY_KLINE_DATA_INDEX.MAX_COUNT.value
        newItem[DAY_KLINE_DATA_INDEX.DATE_ID.value] = kItem[DAY_KLINE_DATA_INDEX.DATE_ID.value]
        newItem[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value] = kItem[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value]
        newItem[DAY_KLINE_DATA_INDEX.OPEN_ID.value] = kItem[DAY_KLINE_DATA_INDEX.OPEN_ID.value]
        newItem[DAY_KLINE_DATA_INDEX.HIGH_ID.value] = kItem[DAY_KLINE_DATA_INDEX.HIGH_ID.value]
        newItem[DAY_KLINE_DATA_INDEX.LOW_ID.value] = kItem[DAY_KLINE_DATA_INDEX.LOW_ID.value]
        newItem[DAY_KLINE_DATA_INDEX.CLOSE_ID.value] = kItem[DAY_KLINE_DATA_INDEX.CLOSE_ID.value]
        newItem[DAY_KLINE_DATA_INDEX.VOL_ID.value] = kItem[DAY_KLINE_DATA_INDEX.VOL_ID.value]
        newItem[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value] = kItem[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value]

        return newItem

    def CopyRightKItem(kItem, seed):
        newItem = [0] * DAY_KLINE_DATA_INDEX.MAX_COUNT.value
        newItem[DAY_KLINE_DATA_INDEX.DATE_ID.value] = kItem[DAY_KLINE_DATA_INDEX.DATE_ID.value]
        newItem[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value] = kItem[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value] * seed
        newItem[DAY_KLINE_DATA_INDEX.OPEN_ID.value] = kItem[DAY_KLINE_DATA_INDEX.OPEN_ID.value] * seed
        newItem[DAY_KLINE_DATA_INDEX.HIGH_ID.value] = kItem[DAY_KLINE_DATA_INDEX.HIGH_ID.value] * seed
        newItem[DAY_KLINE_DATA_INDEX.LOW_ID.value] = kItem[DAY_KLINE_DATA_INDEX.LOW_ID.value] * seed
        newItem[DAY_KLINE_DATA_INDEX.CLOSE_ID.value] = kItem[DAY_KLINE_DATA_INDEX.CLOSE_ID.value] * seed
        newItem[DAY_KLINE_DATA_INDEX.VOL_ID.value] = kItem[DAY_KLINE_DATA_INDEX.VOL_ID.value]
        newItem[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value] = kItem[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value]

        return newItem

    # 获取星期5
    def GetFirday(value):
        date = datetime.datetime.strptime(str(value), '%Y%m%d')
        day = date.weekday()
        if day == 4:
            return value

        date += datetime.timedelta(days=4 - day)
        fridayDate = date.year * 10000 + date.month * 100 + date.day
        return fridayDate

    # 计算复权
    def CalculateRight(aryData, right):
        result = []
        if len(aryData) <= 0:
            return result

        result = [None] * len(aryData)
        if right == 1:
            count = len(aryData)
            index = count - 1
            seed = 1  # 复权系数
            kItem = aryData[index]
            yClose = kItem[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value]
            result[index] = KLineCache.CopyKItem(kItem)

            for i in range(index - 1, -1, -1):
                index = i
                kItem = aryData[index]
                if yClose != kItem[DAY_KLINE_DATA_INDEX.CLOSE_ID.value]:
                    break

                result[index] = KLineCache.CopyKItem(kItem)
                yClose = kItem[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value]

            for i in range(index, -1, -1):
                index = i
                kItem = aryData[index]
                value = kItem[DAY_KLINE_DATA_INDEX.CLOSE_ID.value]
                if yClose != value and value > 0.0000001:
                    seed *= yClose / value

                result[index] = KLineCache.CopyRightKItem(kItem, seed)
                yClose = kItem[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value]

        elif right in (2,3):
            index = 0
            seed = 1
            kItem = aryData[index]
            close = kItem[DAY_KLINE_DATA_INDEX.CLOSE_ID.value]
            result[index] = KLineCache.CopyKItem(kItem)

            for i in range(len(aryData)):
                index = i
                kItem = aryData[index]
                if close != kItem[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value]:
                    break

                result[index] = KLineCache.CopyKItem(kItem)
                close = kItem[DAY_KLINE_DATA_INDEX.CLOSE_ID.value]

            for i in range(index, len(aryData)):
                index = i
                kItem = aryData[index]
                value = kItem[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value]
                if close != value and value > 0.000001:
                    seed *= close / value

                result[index] = KLineCache.CopyRightKItem(kItem, seed)
                close = kItem[DAY_KLINE_DATA_INDEX.CLOSE_ID.value]

        return result

    # 计算周期 目前只支持 1=周 2=月 3=年
    def CalculatePeriod(aryData, period):
        result = []
        startDate = 0
        newData = None
        for dayData in aryData:
            isNewData = False
            value = dayData[DAY_KLINE_DATA_INDEX.DATE_ID.value]
            if period == 1:  # 周线
                fridayDate = KLineCache.GetFirday(value)
                if fridayDate != startDate:
                    isNewData = True
                    startDate = fridayDate

            elif period == 2:  # 月线
                if int(value / 100) != int(startDate / 100):
                    isNewData = True
                    startDate = value
            elif period == 3:  # 年线
                if int(value / 10000) != int(startDate / 10000):
                    isNewData = True
                    startDate = value

            if isNewData:
                newData = [0] * DAY_KLINE_DATA_INDEX.MAX_COUNT.value
                newData[DAY_KLINE_DATA_INDEX.DATE_ID.value] = dayData[DAY_KLINE_DATA_INDEX.DATE_ID.value]
                result.append(newData)

                if (dayData[DAY_KLINE_DATA_INDEX.OPEN_ID.value] == None or dayData[
                    DAY_KLINE_DATA_INDEX.CLOSE_ID.value] == None):
                    continue

                newData[DAY_KLINE_DATA_INDEX.OPEN_ID.value] = dayData[DAY_KLINE_DATA_INDEX.OPEN_ID.value]
                newData[DAY_KLINE_DATA_INDEX.HIGH_ID.value] = dayData[DAY_KLINE_DATA_INDEX.HIGH_ID.value]
                newData[DAY_KLINE_DATA_INDEX.LOW_ID.value] = dayData[DAY_KLINE_DATA_INDEX.LOW_ID.value]
                newData[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value] = dayData[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value]
                newData[DAY_KLINE_DATA_INDEX.CLOSE_ID.value] = dayData[DAY_KLINE_DATA_INDEX.CLOSE_ID.value]
                newData[DAY_KLINE_DATA_INDEX.VOL_ID.value] = dayData[DAY_KLINE_DATA_INDEX.VOL_ID.value]
                newData[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value] = dayData[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value]
                # newData.FlowCapital=dayData.FlowCapital
            else:
                if newData == None:
                    continue
                if dayData[DAY_KLINE_DATA_INDEX.OPEN_ID.value] == None or dayData[
                    DAY_KLINE_DATA_INDEX.CLOSE_ID.value] == None:
                    continue

                if newData[DAY_KLINE_DATA_INDEX.OPEN_ID.value] == None or newData[
                    DAY_KLINE_DATA_INDEX.CLOSE_ID.value] == None:
                    newData[DAY_KLINE_DATA_INDEX.OPEN_ID.value] = dayData[DAY_KLINE_DATA_INDEX.OPEN_ID.value]
                    newData[DAY_KLINE_DATA_INDEX.HIGH_ID.value] = dayData[DAY_KLINE_DATA_INDEX.HIGH_ID.value]
                    newData[DAY_KLINE_DATA_INDEX.LOW_ID.value] = dayData[DAY_KLINE_DATA_INDEX.LOW_ID.value]
                    newData[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value] = dayData[DAY_KLINE_DATA_INDEX.YCLOSE_ID.value]
                    newData[DAY_KLINE_DATA_INDEX.CLOSE_ID.value] = dayData[DAY_KLINE_DATA_INDEX.CLOSE_ID.value]
                    newData[DAY_KLINE_DATA_INDEX.VOL_ID.value] = dayData[DAY_KLINE_DATA_INDEX.VOL_ID.value]
                    newData[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value] = dayData[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value]
                    # newData.FlowCapital=dayData.FlowCapital
                else:
                    if newData[DAY_KLINE_DATA_INDEX.HIGH_ID.value] < dayData[DAY_KLINE_DATA_INDEX.HIGH_ID.value]:
                        newData[DAY_KLINE_DATA_INDEX.HIGH_ID.value] = dayData[DAY_KLINE_DATA_INDEX.HIGH_ID.value]
                    if newData[DAY_KLINE_DATA_INDEX.LOW_ID.value] > dayData[DAY_KLINE_DATA_INDEX.LOW_ID.value]:
                        newData[DAY_KLINE_DATA_INDEX.LOW_ID.value] = dayData[DAY_KLINE_DATA_INDEX.LOW_ID.value]

                    newData[DAY_KLINE_DATA_INDEX.CLOSE_ID.value] = dayData[DAY_KLINE_DATA_INDEX.CLOSE_ID.value]
                    newData[DAY_KLINE_DATA_INDEX.VOL_ID.value] += dayData[DAY_KLINE_DATA_INDEX.VOL_ID.value]
                    newData[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value] += dayData[DAY_KLINE_DATA_INDEX.AMOUNT_ID.value]
                    # newData.FlowCapital+=dayData.FlowCapital
                    newData[DAY_KLINE_DATA_INDEX.DATE_ID.value] = dayData[DAY_KLINE_DATA_INDEX.DATE_ID.value]

        return result

    # right: 1=前复权 2=后复权-简单 3=后复权-完成 0=不复权
    # period: 0=日 1=周 2=月 3=年 9=季 21=双周 22=半年
    def GetDayKLine(symbol, period=0, right=0, startDate=None, endDate=None, nCalculateCount=None):
        srcKData = KLineCache.GetDayKLineCache(symbol)
        if (srcKData == None):
            srcKData = KLineCache.ReadDayKLineFile(symbol)
        if (srcKData == None):
            log = "[KLineCache::GetDayKLine] Error: get kline data failed.{0}".format(symbol)
            print(log)
            return None

        dataCount = len(srcKData["data"])
        result = {}
        result['symbol'] = srcKData['symbol']
        result['name'] = srcKData['name']
        result['period'] = period
        result['right'] = right

        # 指定计算个数
        if (nCalculateCount != None and nCalculateCount > 0 and dataCount > nCalculateCount):
            if (right == 0 or right == 1 or right == 2):  # 截取数据
                aryData = srcKData["data"][-nCalculateCount:]
                if (period == 0 and right == 0):
                    kData = {'data': aryData}
                    KLineCache.ConvertToHQChartData(kData, result)
                    return result
                if (right == 1 or right == 2 ):
                    aryData = KLineCache.CalculateRight(aryData, right)

                # 计算周期
                if (period == 1 or period == 2 or period == 3 or period == 9 or period == 21 or period == 22):
                    aryData = KLineCache.CalculatePeriod(aryData, period)

                kData = {}
                kData['data'] = aryData
                KLineCache.ConvertToHQChartData(kData, result)
                return result

            if (right == 3):  # 后复权-完成 先算复权数据 再截取数据
                kData = {}
                aryData = srcKData["data"]
                aryData = KLineCache.CalculateRight(aryData, right)
                aryData = aryData[-nCalculateCount:]

                # 计算周期
                if (period == 1 or period == 2 or period == 3 or period == 9 or period == 21 or period == 22):
                    aryData = KLineCache.CalculatePeriod(aryData, period)

                kData['data'] = aryData
                KLineCache.ConvertToHQChartData(kData, result)
                return result

        if (period == 0 and right == 0):
            # 根据日期进行过滤
            kData = {}
            kData["data"] = KLineCache.FilterByDate(srcKData["data"], startDate, endDate)
            KLineCache.ConvertToHQChartData(kData, result)
            return result

        kData = {}
        aryData = srcKData["data"]
        # 计算复权
        if (right in (1,2,3) ):
            if(right == 1 or right == 2): #前复权,或者后复权-简单,先过滤数据，后计算复权
                aryData = KLineCache.FilterByDate(aryData,startDate,endDate)
                aryData = KLineCache.CalculateRight(aryData, right)
            else:
                aryData = KLineCache.CalculateRight(aryData, right)
                #计算完后复权后，再截取数据
                aryData = KLineCache.FilterByDate(aryData, startDate, endDate)

        # 计算周期
        if (period == 1 or period == 2 or period == 3 or period == 9 or period == 21 or period == 22):
            aryData = KLineCache.CalculatePeriod(aryData, period)

        kData['data'] = aryData
        KLineCache.ConvertToHQChartData(kData, result)
        return result

    # 根据日期过滤数据
    def FilterByDate(kArray, startDate, endDate):
        if startDate is None and endDate is None:
            return kArray
        if startDate is None and endDate is not None:
            startDate = 19910101
        if startDate is not None and endDate is None:
            endDate = 29991231
        expectedArray = []
        for item in kArray:
            if item[DAY_KLINE_DATA_INDEX.DATE_ID.value] >= startDate and item[
                DAY_KLINE_DATA_INDEX.DATE_ID.value] <= endDate:
                expectedArray.append(item)
        return expectedArray

    def GetDayKLineAPIData(symbol, period=0, right=0, startDate=None, endDate=None):
        srcKData = KLineCache.GetDayKLineCache(symbol)
        if (srcKData == None):
            srcKData = KLineCache.ReadDayKLineFile(symbol)
        if (srcKData == None):
            log = "[KLineCache::GetDayKLine] Error: get kline data failed.{0}".format(symbol)
            print(log)
            return None

        kData = {"name": srcKData["name"], "symbol": srcKData["symbol"]}
        if (period == 0 and right == 0):
            aryData = srcKData["data"]
            aryData = KLineCache.FilterByDate(aryData, startDate, endDate)
            kData['data'] = aryData
            return kData

        aryData = srcKData["data"]
        # 计算复权
        if (right == 1 or right == 2):
            aryData = KLineCache.CalculateRight(aryData, right)

        # 计算周期
        if (period == 1 or period == 2 or period == 3 or period == 9 or period == 21 or period == 22):
            aryData = KLineCache.CalculatePeriod(aryData, period)
        # 日期过滤
        aryData = KLineCache.FilterByDate(aryData, startDate, endDate)
        kData['data'] = aryData
        return kData


def TestCase():
    KLineCache.SetCachePath("../data/kdata/0")
    KLineCache.LoadCache()
    test = KLineCache.GetDayKLine("600000.sh")
    test2 = KLineCache.GetDayKLine("000001.sz", 2, 1)

# TestCase()

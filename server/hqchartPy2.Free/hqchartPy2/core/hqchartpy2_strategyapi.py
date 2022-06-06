import copy
import datetime
import json
import logging
import time
import uuid

from flask import current_app
from hqchartPy2.core.hqchart2_syncklinedata_from_cdn import SyncDataTask, DataFileType
from hqchartPy2.core.hqchartpy2_fast import FastHQChart
from hqchartPy2.core.hqchartpy2_hqchartdata import HQChartData
from hqchartPy2.core.hqchartpy2_hqchartresult import HQChartResult
from hqchartPy2.core.hqchartpy2_klinedata import KLineCache
from hqchartPy2.core.hqchartpy2_klineminutedata import MinuteKLineCache
from hqchartPy2.core.hqchartpy2_public import RequestMixin
from hqchartPy2.core.hqchartpy2_run import IHQChartPyRun, HQPolicyResult
from hqchartPy2.core.hqchartpy2_systemdata import SymbolDataCache, FinanceDataCache
from hqchartPy2.core.tools import get_current_date
from hqchartPy2.extention import db, executor, progress_bar, DATA_FILE_TYPE_META, FINANCE_META_INFO, CAPITAL_META_INFO
from hqchartPy2.models.strategy import Strategy, StrategyArgument, StrategyGroup, \
    HqchartDataStatus, Algorithm, AlgorithmGroup, StockGroup, Stock, AlgorithmResult


class StrategyController(RequestMixin):
    """
    指标相关类api
    """

    def delete(self, strategyId):
        StrategyArgument.query.filter_by(strategyId=strategyId).delete()
        ret = Strategy.query.filter_by(id=strategyId).delete()
        db.session.commit()
        return {
            "code": 200,
            "msg": "delete success"
        }

    def create(self):
        """
        创建策略
        :param request:
        :return:
        """
        requestData = self.request_body
        strategyObj = Strategy()
        strategyObj.name = requestData["name"]
        strategyObj.groupId = requestData["groupId"]
        strategyObj.script = requestData["script"]
        strategyObj.outArgs = requestData["outArgs"]
        strategyObj.description = requestData["description"]
        strategyObj.isMainIndex = requestData["isMainIndex"]
        strategyObj.floatPrecision = requestData["floatPrecision"]
        # 可选参数
        if ("args" in requestData):
            args = requestData["args"]
            strategyObj.args = []
            for argument in args:
                strategyArg = StrategyArgument(name=argument["name"], defaultVal=argument["defaultVal"],
                                               minVal=argument["minVal"], maxVal=argument["maxVal"])
                strategyObj.args.append(strategyArg)
        db.session.add(strategyObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "create success",
            "data": strategyObj.to_dict()
        }

    def update(self, strategyId):
        requestData = self.request_body
        strategyObj = Strategy.query.get(strategyId)
        if "name" in requestData:
            strategyObj.name = requestData["name"]
        if "script" in requestData:
            strategyObj.script = requestData["script"]
        if "description" in requestData:
            strategyObj.description = requestData["description"]
        if "isMainIndex" in requestData:
            strategyObj.isMainIndex = requestData["isMainIndex"]
        if "floatPrecision" in requestData:
            strategyObj.floatPrecision = requestData["floatPrecision"]
        if "outArgs" in requestData:
            strategyObj.outArgs = requestData["outArgs"]
        # 可选参数
        if ("args" in requestData):
            argument_list = requestData["args"]
            for argument_item in argument_list:
                if "id" in argument_item:
                    strategyArg = strategyObj.args.filter_by(id=argument_item["id"])
                    if "delete" in argument_item and argument_item["delete"]:
                        strategyArg.delete()
                    else:
                        update = {}
                        if "name" in argument_item:
                            update[StrategyArgument.name] = argument_item["name"]
                        if "defaultVal" in argument_item:
                            update[StrategyArgument.defaultVal] = argument_item["defaultVal"]
                        if "minVal" in argument_item:
                            update[StrategyArgument.minVal] = argument_item["minVal"]
                        if "maxVal" in argument_item:
                            update[StrategyArgument.maxVal] = argument_item["maxVal"]
                        strategyArg.update(update)
                else:
                    strategyArg = StrategyArgument()
                    strategyArg.strategyId = strategyId
                    if "name" in argument_item:
                        strategyArg.name = argument_item["name"]
                    if "defaultVal" in argument_item:
                        strategyArg.defaultVal = argument_item["defaultVal"]
                    if "minVal" in argument_item:
                        strategyArg.minVal = argument_item["minVal"]
                    if "maxVal" in argument_item:
                        strategyArg.maxVal = argument_item["maxVal"]
                    strategyObj.args.append(strategyArg)
        db.session.add(strategyObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "create success",
            "data": strategyObj.to_dict()
        }

    def get(self, strategyId):
        strategy = Strategy.query.get(strategyId)
        if strategy is None:
            return {
                "code": 200,
                "data": None,
                "msg": "Strategy is not found"
            }
        return {
            "code": 200,
            "msg": "success",
            "data": strategy.to_dict()
        }

    def list(self):
        strategy_list = Strategy.query.all()
        if strategy_list is None:
            return {
                "code": 200,
                "msg": "query success",
                "data": [],
                "count": 0
            }
        return {
            "code": 200,
            "msg": "success",
            "count": len(strategy_list),
            "data": [strategy.to_dict() for strategy in strategy_list]
        }

    def list_by_groupId(self, groupId):
        strategy_list = Strategy.query.filter_by(groupId=groupId)
        # print(strategy_list)
        if strategy_list is None:
            return {
                "code": 200,
                "msg": "query success",
                "data": [],
                "count": 0
            }
        return {
            "code": 200,
            "msg": "success",
            "count": strategy_list.count(),
            "data": [strategy.to_dict() for strategy in strategy_list]
        }


class StrategyGroupController(RequestMixin):
    """
    指标分组类API
    """

    def delete(self, groupId):
        strategy_list = Strategy.query.filter_by(groupId=groupId)
        for strategy in strategy_list:
            strategy.args.delete()
            # strategy.delete()
        Strategy.query.filter_by(groupId=groupId).delete()
        ret = StrategyGroup.query.filter_by(id=groupId).delete()
        db.session.commit()
        return {
            "code": 200,
            "msg": "delete success"
        }

    def create(self):
        """
        创建策略
        :param request:
        :return:
        """
        requestData = self.request_body
        strategyGroupObj = StrategyGroup()
        strategyGroupObj.name = requestData["name"]
        db.session.add(strategyGroupObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "create success",
            "data": strategyGroupObj.to_dict()
        }

    def update(self, groupId):
        requestData = self.request_body
        strategyGroupObj = StrategyGroup.query.get(groupId)
        strategyGroupObj.name = requestData["name"]
        # strategyGroupObj.update()
        db.session.add(strategyGroupObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "create success",
            "data": strategyGroupObj.to_dict()
        }

    def get(self, groupId):
        strategyGroup = StrategyGroup.query.get(groupId)
        if strategyGroup is None:
            return {
                "code": 200,
                "data": None,
                "msg": "Strategy is not found"
            }
        return {
            "code": 200,
            "msg": "success",
            "data": strategyGroup.to_dict()
        }

    def list(self):
        strategyGroup_list = StrategyGroup.query.all()
        if strategyGroup_list is None:
            return {
                "code": 200,
                "msg": "query success",
                "data": [],
                "count": 0
            }
        return {
            "code": 200,
            "msg": "success",
            "count": len(strategyGroup_list),
            "data": [strategy.to_dict() for strategy in strategyGroup_list]
        }

class DataController(RequestMixin):
    """
    数据设置类API
    """

    def set_cache_path(self,dataType,dataPath):
        # 设置数据缓存路径
        if DataFileType.SYMBOLE_FILE_TYPE.value == dataType:
            SymbolDataCache.SetCachePath(dataPath)
        # 设置数据缓存路径
        if DataFileType.DAY_KLINE_FILE_TYPE.value == dataType:
            KLineCache.SetCachePath(dataPath)
        # 设置数据缓存路径
        if DataFileType.MIN_KLINE_FILE_TYPE.value == dataType:
            MinuteKLineCache.SetCachePath(dataPath)
        if DataFileType.FINANCE_FILE_TYPE.value == dataType:
            FinanceDataCache.SetCachePath(DataFileType.FINANCE_FILE_TYPE,dataPath)
        if DataFileType.CAPITAL_FILE_TYPE.value == dataType:
            FinanceDataCache.SetCachePath(DataFileType.CAPITAL_FILE_TYPE,dataPath)

    def update(self):
        data_list = self.request_body.get("data")
        ret_list = []
        for item in data_list:
            dataType = item.get("type")  # 数据类型
            dataPath = item.get("dataPath")  # 文件路径
            dataStatusObj = HqchartDataStatus.query.filter_by(type=dataType).first()
            if dataStatusObj is None:
                dataStatusObj = HqchartDataStatus()
            self.set_cache_path(dataType,dataPath)
            dataStatusObj.dataPath = dataPath
            db.session.add(dataStatusObj)
            db.session.commit()
            ret_list.append(dataStatusObj)
        return {
            "code": 200,
            "msg": "success",
            "data": [item.to_dict() for item in ret_list]
        }

    def get(self):
        strategyGroup_list = HqchartDataStatus.query.all()
        if strategyGroup_list is None or len(strategyGroup_list) == 0:
            strategyGroup_list = []
            for dtype in DATA_FILE_TYPE_META:
                dataObj = HqchartDataStatus()
                dataObj.type = dtype.value
                dataObj.name = DATA_FILE_TYPE_META[dtype]
                dataObj.dataPath = None
                dataObj.counts = 0
                strategyGroup_list.append(dataObj)
            db.session.bulk_save_objects(strategyGroup_list)
            db.session.commit()
        data = []
        for item in strategyGroup_list:
            _item = item.to_dict()
            progress = progress_bar[DataFileType(item.type)]
            _item["percent"] = round(progress.get("percent"))
            _item["cur"] = progress.get("cur")
            _item["total"] = progress.get("total")
            _item["taskname"] = progress.get("taskname")
            _item["loadStatus"] = progress.get("loadStatus")
            _item["syncStatus"] = progress.get("syncStatus")
            _item["isCache"] = progress.get("isCache")
            _item["msg"] = progress.get("msg")
            data.append(_item)
        return {
            "code": 200,
            "msg": "success",
            "count": len(strategyGroup_list),
            "data": data,
        }

    def __sync_data_file(self, dataStatusObj, app):
        task = SyncDataTask()
        with app.app_context():
            try:
                if dataStatusObj.type in [DataFileType.DAY_KLINE_FILE_TYPE.value, DataFileType.MIN_KLINE_FILE_TYPE.value]:

                    result = task.sync_kline_data_file(base_dir=dataStatusObj.dataPath,
                                                       dType=DataFileType(dataStatusObj.type))
                else:  # 同步码表文件
                    result = task.sync_system_data_file(dataType=DataFileType(dataStatusObj.type),base_dir=dataStatusObj.dataPath)
                if result is True:
                    dataStatusObj.syncStatus = 2
                else:
                    dataStatusObj.syncStatus = 3
                dataStatusObj.counts = task.counts
                dataStatusObj.latestDataDate = task.latestDataDate
                dataStatusObj.updateTime = datetime.datetime.now()
                dataStatusObj.syncMsg = task.msg
            except Exception as e:
                dataStatusObj.syncStatus = 3
                dataStatusObj.syncMsg = str(e)
            finally:
                try:
                    db.session.add(dataStatusObj)
                    db.session.commit()
                except Exception as e:
                    print(str(e))

    def sync_data(self):
        """
        数据同步
        :return:
        """
        dataType = self.request_body.get("type")  # 数据类型
        dataStatusObj = HqchartDataStatus.query.filter_by(type=dataType).first()
        if dataStatusObj.dataPath is None or dataStatusObj.dataPath == "":
            return {
                "code":-1,
                "msg":"数据存储目录为空，请先设置数据存储目录"
            }
        status = progress_bar[DataFileType(dataType)]["syncStatus"]
        if status is None or status != 1:
            app = current_app._get_current_object()
            ret = executor.submit(self.__sync_data_file, dataStatusObj, app)
            return {
                "code": 200,
                "msg": "数据同步请求提交成功,数据正在同步中",
                "syncStatus": 1
            }
        else:
            return {
                "code": -1,
                "msg": "error,数据正在同步中，请勿重复提交"
            }

    def __load_data_task(self, dataType, app):
        with app.app_context():
            try:
                progress_bar[DataFileType(dataType)]["percent"] = 0
                progress_bar[DataFileType(dataType)]["cur"] = 0
                progress_bar[DataFileType(dataType)]["total"] = 0
                progress_bar[DataFileType(dataType)]["taskname"] = "开始加载数据..."
                dataStatusObj = HqchartDataStatus.query.filter_by(type=dataType).first()
                if dataType == DataFileType.SYMBOLE_FILE_TYPE.value:
                    SymbolDataCache.LoadCache()
                if dataType == DataFileType.MIN_KLINE_FILE_TYPE.value:
                    MinuteKLineCache.LoadCache()
                if dataType == DataFileType.DAY_KLINE_FILE_TYPE.value:
                    KLineCache.LoadCache()
                if dataType in [DataFileType.CAPITAL_FILE_TYPE.value,DataFileType.FINANCE_FILE_TYPE.value]:
                    FinanceDataCache.LoadCache(DataFileType(dataType))
                progress_bar[DataFileType(dataType)]["percent"] = 100
                progress_bar[DataFileType(dataType)]["loadStatus"] = 2
                progress_bar[DataFileType(dataType)]["isCache"] = True
                dataStatusObj.loadTime = datetime.datetime.now()
                db.session.add(dataStatusObj)
                db.session.commit()
            except Exception as e:
                logging.error(msg=str(e))
                progress_bar[DataFileType(dataType)]["loadStatus"] = 3

    def load_data(self):
        """
        数据加载
        :return:
        """
        dataType = self.request_body.get("type")  # 数据类型

        status = progress_bar[DataFileType(dataType)]["loadStatus"]
        syncStatus = progress_bar[DataFileType(dataType)]["syncStatus"]
        if syncStatus == 1:
            return {
                "code": -1,
                "msg": "error,数据正在同步中，同步完毕后再加载"
            }
        if status is None or status != 1:
            progress_bar[DataFileType(dataType)]["loadStatus"] = 1
            app = current_app._get_current_object()
            executor.submit(self.__load_data_task,dataType,app)
            return {
                "code": 200,
                "msg": "数据加载请求提交成功,数据正在加载中",
                "loadStatus": 1
            }
        else:
            return {
                "code": 200,
                "msg": "error,数据正在加载中，请勿重复提交"
            }


class AlgorithmController(RequestMixin):
    """
    策略相关类api
    """

    def delete(self, algorithmId):
        AlgorithmResult.query.filter_by(algorithmId=algorithmId).delete()
        ret = Algorithm.query.filter_by(id=algorithmId).delete()
        db.session.commit()
        return {
            "code": 200,
            "msg": "delete success"
        }

    def create(self):
        """
        创建策略
        :param request:
        :return:
        """
        requestData = self.request_body
        algorithmObj = Algorithm()
        algorithmObj.name = requestData["name"]
        algorithmObj.groupId = requestData["groupId"]
        algorithmObj.right = requestData.get("right",0)
        algorithmObj.period = requestData["period"]
        algorithmObj.strategies = requestData["strategies"]
        algorithmObj.stockPool = requestData.get("stockPool", "[]")
        algorithmObj.desc = requestData.get("desc", "")
        db.session.add(algorithmObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "create success",
            "data": algorithmObj.to_dict()
        }

    def update(self, algorithmId):
        requestData = self.request_body
        algorithmObj = Algorithm.query.get(algorithmId)
        if algorithmObj is None:
            return {
                "code": 200,
                "data": None,
                "msg": "Algorithm is not found"
            }
        if "name" in requestData:
            algorithmObj.name = requestData["name"]
        if "groupId" in requestData:
            algorithmObj.groupId = requestData["groupId"]
        if "right" in requestData:
            algorithmObj.right = requestData.get("right",0)
        if "period" in requestData:
            algorithmObj.period = requestData["period"]
        if "strategies" in requestData:
            algorithmObj.strategies = requestData["strategies"]
        if "stockPool" in requestData:
            algorithmObj.stockPool = requestData.get("stockPool", [])
        if "status" in requestData:
            algorithmObj.status = requestData.get("status")
        if "desc" in requestData:
            algorithmObj.desc = requestData.get("desc")
        db.session.add(algorithmObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "update success",
            "data": algorithmObj.to_dict()
        }

    def get(self, algorithmId):
        strategy = Algorithm.query.get(algorithmId)
        if strategy is None:
            return {
                "code": 200,
                "data": None,
                "msg": "Algorithm is not found"
            }
        return {
            "code": 200,
            "msg": "success",
            "data": strategy.to_dict()
        }

    def list(self):
        algorithm_list = Algorithm.query.all()
        if algorithm_list is None:
            return {
                "code": 200,
                "msg": "query success",
                "data": [],
                "count": 0
            }
        return {
            "code": 200,
            "msg": "success",
            "count": len(algorithm_list),
            "data": [algorithm.to_dict() for algorithm in algorithm_list]
        }


class AlgorithmGroupController(RequestMixin):
    """
    策略分组类API
    """

    def delete(self, groupId):
        Algorithm.query.filter_by(groupId=groupId).delete()
        ret = AlgorithmGroup.query.filter_by(id=groupId).delete()
        db.session.commit()
        return {
            "code": 200,
            "msg": "delete success"
        }

    def create(self):
        """
        创建策略
        :param request:
        :return:
        """
        requestData = self.request_body
        strategyGroupObj = AlgorithmGroup()
        strategyGroupObj.name = requestData["name"]
        db.session.add(strategyGroupObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "create success",
            "data": strategyGroupObj.to_dict()
        }

    def update(self, groupId):
        requestData = self.request_body
        strategyGroupObj = AlgorithmGroup.query.get(groupId)
        strategyGroupObj.name = requestData["name"]
        # strategyGroupObj.update()
        db.session.add(strategyGroupObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "create success",
            "data": strategyGroupObj.to_dict()
        }

    def get(self, groupId):
        strategyGroup = AlgorithmGroup.query.get(groupId)
        if strategyGroup is None:
            return {
                "code": 200,
                "data": None,
                "msg": "Strategy is not found"
            }
        return {
            "code": 200,
            "msg": "success",
            "data": strategyGroup.to_dict()
        }

    def list(self):
        strategyGroup_list = AlgorithmGroup.query.all()
        if strategyGroup_list is None:
            return {
                "code": 200,
                "msg": "query success",
                "data": [],
                "count": 0
            }
        if "status" in self.request_body:
            status = int(self.request_body["status"])
            return {
                "code": 200,
                "msg": "success",
                "count": len(strategyGroup_list),
                "data": [item.filter_by_algorithms_status_to_dict(status)for item in strategyGroup_list]
            }
        else:
            return {
                "code": 200,
                "msg": "success",
                "count": len(strategyGroup_list),
                "data": [item.to_dict()for item in strategyGroup_list]
            }


class PolicyRunner(RequestMixin,IHQChartPyRun):

    def get_symbol_list(self, stockPoolList):
        """
        根据股票池ID获取股票列表
        :param stockPoolList:
        :return:
        """
        symbol_list = []
        for item in stockPoolList:
            stockPoolId = item.get("id")
            stockPoolType = item.get("type")
            if stockPoolType == "SYS":  # 系统股票池（行业，地域和市场之类的板块）
                member_list = SymbolDataCache.get_block_members_by_id(block_id=stockPoolId)
                symbol_list.extend(member_list)
            elif stockPoolType == "DIY":
                query_set = Stock.query.filter_by(groupId=stockPoolId)
                for item in query_set:
                    symbol_list.append(item.symbol)
        # 去重处理
        symbol_list = list(set(symbol_list))
        return symbol_list

    def get_policy_config(self,policyObj):
        """
        :param policyObj: dict 策略信息
        :return:
        """
        policyBody = {}
        #获取需要运行的股票列表
        symbolList = self.get_symbol_list(stockPoolList=policyObj["stockPool"])
        policyBody["symbolList"] = symbolList
        policyBody["AryIndex"] = [{"Args":item.get("args"),"Script":item.get("script"),"ID":item.get("id")} for item in policyObj["strategies"]]
        policyOutVarList = [{"outArgs":item.get("outArgs"),"ID":item.get("id"),"Name":item.get("name")} for item in policyObj["strategies"]]
        policyBody["OutCount"] = 1
        policyBody["Right"] = policyObj["right"]
        policyBody["Period"] = policyObj["period"]
        return policyBody,policyOutVarList

    @staticmethod
    def get_policy_running_config(policyConfig,indexItem, id) :

        if ("Script" not in indexItem):
            return None

        runConfig={
            # 系统指标名字
            # "Name":"MA",
            "Script":indexItem["Script"],
            # 脚本参数
            "Args":None,
            # 周期 复权
            "Period":policyConfig.get("Period"),
            "Right":policyConfig.get("Right"),

            "Symbol":policyConfig.get("symbolList"),
            # "OutCount":1,
            "OutCount":policyConfig.get("OutCount",1),
            #jobID (可选)
            "JobID":str(id)
        }

        if ("Args" in indexItem):
            runConfig["Args"]=indexItem["Args"]

        if ("ID" in indexItem):
            runConfig["ID"]=id

        return json.dumps(runConfig)    # 运行配置项

    def RunStatus(self):
        return {
            "code":200,
            "status":progress_bar["RUNALLPOLICY"]["status"],
            "taskname": progress_bar["RUNALLPOLICY"]["taskname"],
            "percent": progress_bar["RUNALLPOLICY"]["percent"]
        }

    def RunResult(self,PolicyId):
        resultObj = AlgorithmResult.query.filter_by(algorithmId=PolicyId).first()
        if resultObj is not None:
            return {
                "Code":0,
                "Data":resultObj.to_dict()
            }
        else:
            return {
                "Code":-1,
                "Msg":"未查询到执行结果，请先运行策略",
                "Data":None
            }

    def RunOne(self):
        request_data = self.request_body
        policyId = request_data["PolicyId"]
        policyObj = Algorithm.query.get(policyId)
        if policyObj is None:
            result = {
                "Code":-1,
                "Data":None,
                "Msg":"策略：{}不存在".format(policyId)
            }
            return result
        try:
            policyConfig, policyVarList = self.get_policy_config(policyObj=policyObj.to_dict())
            m_HQData = HQChartData()
            stockTable = SymbolDataCache.get_symbol_table()
            # result = self.execute_policy(m_HQData,policyConfig,policyVarList,stockTable)
            futuer = executor.submit(self.execute_policy,m_HQData,policyConfig,policyVarList,stockTable)
            result = futuer.result()
            # 写数据库
            algorithmResultObj = AlgorithmResult.query.filter_by(algorithmId=policyObj.id).first()
            if algorithmResultObj is None:
                algorithmResultObj = AlgorithmResult()
            algorithmResultObj.status = 2
            algorithmResultObj.algorithmId = policyObj.id
            algorithmResultObj.updateTime = datetime.datetime.now()
            algorithmResultObj.ticket = result["Ticket"]
            algorithmResultObj.result = result["Data"]
            result["Code"] = 0
            db.session.add(algorithmResultObj)
            db.session.commit()
            return {
                    "Code":0,
                    "Data":algorithmResultObj.to_dict()
            }
        except Exception as e:
            logging.info(msg=str(e))
            db.session.rollback()
            return {
                "Code":-1,
                "Msg":"策略运行失败"
            }

    def __RunAllPolicy(self,query_set,app):
        with app.app_context():
            progress_bar["RUNALLPOLICY"]["total"] = len(query_set)
            progress_bar["RUNALLPOLICY"]["cur"] = 0
            progress_bar["RUNALLPOLICY"]["percent"] = 0
            progress_bar["RUNALLPOLICY"]["taskname"] = "开始执行策略"
            m_HQData = HQChartData()
            for policyObj in query_set:
                try:
                    progress_bar["RUNALLPOLICY"]["taskname"] = "开始执行策略:{}".format(policyObj["name"])
                    progress_bar["RUNALLPOLICY"]["cur"] += 1
                    policyConfig, policyVarList = self.get_policy_config(policyObj=policyObj)
                    stockTable = SymbolDataCache.get_symbol_table()
                    result = self.execute_policy(m_HQData, policyConfig, policyVarList, stockTable)
                    #写数据库
                    algorithmResultObj = AlgorithmResult.query.filter_by(algorithmId=policyObj["id"]).first()
                    if algorithmResultObj is None:
                        algorithmResultObj = AlgorithmResult()
                    algorithmResultObj.status = 2
                    algorithmResultObj.algorithmId = policyObj["id"]
                    algorithmResultObj.updateTime = datetime.datetime.now()
                    algorithmResultObj.ticket = result["Ticket"]
                    algorithmResultObj.result = result["Data"]
                    db.session.add(algorithmResultObj)
                    db.session.commit()
                    progress_bar["RUNALLPOLICY"]["percent"] = round(progress_bar["RUNALLPOLICY"]["cur"]*1.0/progress_bar["RUNALLPOLICY"]["total"]*1.0,2)*100
                except Exception as e:
                    logging.info(msg=str(e))
                    continue
            progress_bar["RUNALLPOLICY"]["percent"] = 100
            progress_bar["RUNALLPOLICY"]["status"] = 2

    def RunAll(self):
        app = current_app._get_current_object()
        if progress_bar["RUNALLPOLICY"]["status"] != 1:
            progress_bar["RUNALLPOLICY"]["status"] = 1
            query_set = Algorithm.query.filter_by(status=1).all()
            if query_set is None or len(query_set) == 0:
                progress_bar["RUNALLPOLICY"]["status"] = 2
                return {"code":200,"msg":"没有需要执行的策略,请先创建策略或者发布策略"}
            policy_list = []
            for item in query_set:
                policy_list.append(item.to_dict())
            ret = executor.submit(self.__RunAllPolicy, policy_list, app)
            return {"code":200,"msg":"策略执行已提交，请耐心等待结果"}
        else:
            return {"code":-1,"msg":"策略正在执行中，请不要重复提交"}

    def execute_policy(self,m_HQData,policyConfig,policyVarList,stockTable):
        """
        执行策略
        :return:
        """
        #存储执行结果
        m_Result = HQPolicyResult()

        m_StartTime = time.process_time()
        for i,item in enumerate(policyConfig["AryIndex"]):
            jsConfig = self.get_policy_running_config(policyConfig,item, i)  # 运行配置项
            if (jsConfig == None):
                continue
            runStart = time.process_time()
            res = FastHQChart.Run(jsConfig, m_HQData, proSuccess=m_Result.RunSuccess, procFailed= m_Result.RunFailed)
            self.m_nRunTick = (time.process_time() - runStart)

        m_nRunTick = (time.process_time() - m_StartTime)
        result = self.get_response_data(policyOutVarList=policyVarList,m_Result=m_Result,stockTable=stockTable)
        return {"Ticket":m_nRunTick,"Data":result}

    def get_response_data(self,policyOutVarList,m_Result,stockTable):
        """
        获取返回结果
        :param policyOutVarList:
        :param m_Result:
                {
            "688001.sh": [
                {
                    "Data": "{\"Period\":0,\"Right\":1,\"Symbol\":\"688001.sh\",\"Args\":[{\"M1\":5.0},{\"M2\":10.0}],\"Date\":[20220330],\"OutVar\":[{\"Name\":\"VOL\",\"Data\":[9729.21],\"Type\":0,\"Attribute\":[\"VOLSTICK\"]},{\"Name\":\"MA1\",\"Data\":[9888.795999999997],\"Type\":0},{\"Name\":\"MA2\",\"Data\":[9412.991000000053],\"Type\":0}]}",
                    "ID": "0"
                }
            ],
            "688002.sh": [
                {
                    "Data": "{\"Period\":0,\"Right\":1,\"Symbol\":\"688002.sh\",\"Args\":[{\"M1\":5.0},{\"M2\":10.0}],\"Date\":[20220330],\"OutVar\":[{\"Name\":\"VOL\",\"Data\":[25657.48],\"Type\":0,\"Attribute\":[\"VOLSTICK\"]},{\"Name\":\"MA1\",\"Data\":[25356.726000000042],\"Type\":0},{\"Name\":\"MA2\",\"Data\":[25997.16500000006],\"Type\":0}]}",
                    "ID": "0"
                }
            ]
        }
        :param stockTable:
        :return:
        """
        result = {}
        for symbol in m_Result.Result:
            try:
                retDataList = m_Result.Result[symbol]
                stockItem = {}
                stockItem["symbolName"] = stockTable.get(symbol,"") #股票名称
                for retItem in retDataList:
                    policyId = int(retItem.get("ID"))#指标序号
                    policyName = policyOutVarList[policyId].get("Name") #指标名称
                    policyRetData = json.loads(retItem.get("Data"))
                    if len(policyRetData["Date"]) == 0:
                        continue
                    dataItem = {"Data":{}}
                    dataItem["Data"]["Date"] = policyRetData["Date"]
                    dataItem["Data"]["Time"] = policyRetData.get("Time",None)
                    dataItem["ID"] = policyId
                    dataItem["Name"] = policyName
                    for item in policyRetData["OutVar"]:
                        if item.get("Type") != 0:
                            continue
                        dataItem["Data"][item["Name"]] = item["Data"] #输出参数的值
                    stockItem[policyId] = dataItem
                #判断是否符合条件，如果符合条件则添加到结果dict中
                if self.filter_result(data=stockItem,policyOutVarList=policyOutVarList):
                    result[symbol] = stockItem
            except Exception as e:
                logging.error(msg=str(e))
                logging.error(msg=symbol)
                continue
        return result

    def filter_result(self,data,policyOutVarList):
        """
        "outArgs": [{
		"Name": "VOL",
		"Condition1": "",
		"Condition2": "",
		"ConditionValue1": "",
		"ConditionValue2": ""
	}, {
		"Name": "MA1",
		"Condition1": "",
		"Condition2": "",
		"ConditionValue1": "",
		"ConditionValue2": ""
	}, {
		"Name": "MA2",
		"Condition1": "",
		"Condition2": "",
		"ConditionValue1": "",
		"ConditionValue2": ""
	}]
        :param data:
        :param conditionList:
        :return:
        """
        for IndexId,item in enumerate(policyOutVarList):
            policyName = item.get("Name") #指标名称
            condtions = item.get("outArgs")
            for condItem in condtions:
                if isinstance(condItem,str):
                    continue
                outArgName = condItem.get("Name")
                outArgValue = data[IndexId]["Data"][outArgName][-1] #参数值
                if condItem.get("Condition1") != "" and condItem.get("ConditionValue1") != "":
                    strExpress = "{left} {operator} {right}".format(left=outArgValue,operator=condItem["Condition1"],right=condItem.get("ConditionValue1"))
                    if eval(strExpress) is False:
                        return False
                if condItem.get("Condition2") != "" and condItem.get("ConditionValue2") != "":
                    strExpress = "{left} {operator} {right}".format(left=outArgValue,operator=condItem["Condition2"],right=condItem.get("ConditionValue2"))
                    if eval(strExpress) is False:
                        return False
        return True


class StockGroupController(RequestMixin):
    """
    股票池分组类API
    """
    def delete(self, groupId):
        Stock.query.filter_by(groupId=groupId).delete()
        ret = StockGroup.query.filter_by(id=groupId).delete()
        db.session.commit()
        return {
            "code": 200,
            "msg": "delete success"
        }

    def create(self):
        """
        创建股票池
        :param request:
        :return:
        """
        requestData = self.request_body
        stockGroupObj = StockGroup()
        stockGroupObj.name = requestData["name"]
        db.session.add(stockGroupObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "create success",
            "data": stockGroupObj.to_dict()
        }

    def update(self, groupId):
        requestData = self.request_body
        stockGroupObj = StockGroup.query.get(groupId)
        stockGroupObj.name = requestData["name"]
        db.session.add(stockGroupObj)
        db.session.commit()
        return {
            "code": 200,
            "msg": "create success",
            "data": stockGroupObj.to_dict()
        }

    def get(self, groupId):
        stockGroup = StockGroup.query.get(groupId)
        if stockGroup is None:
            return {
                "code": 200,
                "data": None,
                "msg": "Strategy is not found"
            }
        return {
            "code": 200,
            "msg": "success",
            "data": stockGroup.to_dict()
        }

    def list(self):
        stockGroup_list = StockGroup.query.all()
        if stockGroup_list is None:
            return {
                "code": 200,
                "msg": "query success",
                "data": [],
                "count": 0
            }
        return {
            "code": 200,
            "msg": "success",
            "count": len(stockGroup_list),
            "data": [strategy.to_dict() for strategy in stockGroup_list]
        }

    def add_stock(self,groupId):
        """
        添加股票
        :param groupId:
        :return:
        """
        try:
            request_data = self.request_body
            if str(request_data["symbol"]).strip() == "":
                return {
                    "code": -1,
                    "msg": "证券代码不能为空",
                }
            symbol = request_data["symbol"]
            stockObj = Stock.query.filter_by(groupId=groupId,symbol=symbol).first()
            if stockObj is None:
                stockObj = Stock()
            stockObj.name = request_data.get("name")
            stockObj.symbol = request_data.get("symbol")
            stockObj.groupId = groupId
            stockObj.date = request_data.get("date",int(get_current_date(format="%Y%m%d")))
            db.session.add(stockObj)
            db.session.commit()
            return {
                "code": 200,
                "msg": "add success",
                "data": stockObj.to_dict()
            }
        except Exception as e:
            db.session.rollback()
            return {
                "code":500,
                "msg":str(e)
            }

    def delete_stock(self,groupId,stockId):
        """
        刪除股票
        :param groupId:
        :return:
        """
        try:
            Stock.query.filter_by(groupId=groupId,id=stockId).delete()
            db.session.commit()
            return {
                "code": 200,
                "msg": "create success",
            }
        except Exception as e:
            db.session.rollback()
            return {
                "code":500,
                "msg":str(e)
            }


class StockInfoController(RequestMixin):
    """
    股票相关API
    """
    def search(self):
        """
        键盘精灵
        :return:
        """
        request_data = self.request_body
        searchKey = request_data.get("key")
        data_list = SymbolDataCache.search_symbol(key=searchKey)
        return {
            "code": 200,
            "data": data_list,
            "count":len(data_list)
        }

    def get_sys_block_list(self):
        """
        键盘精灵
        :return:
        """
        data_list,metainfo = SymbolDataCache.get_block_list()
        return {
            "code": 200,
            "data": data_list,
            "metainfo":metainfo
        }

    def get_symbol_list(self):
        """
        码表
        :return:
        """
        data_list = SymbolDataCache.get_symbol_list()
        return {
            "code":200,
            "data":data_list,
            "count":len(data_list)
        }


class FinanceDataController(RequestMixin):
    """
    财务数据和股本数据相关API
    """
    def get_finance(self):
        """
        键盘精灵
        :return:
        """
        request_data = self.request_body
        symbol = request_data.get("symbol")
        data = FinanceDataCache.GetDataByType(DataFileType.FINANCE_FILE_TYPE,symbol)
        return {
            "code": 200,
            "data": data,
            "metainfo":FINANCE_META_INFO
        }

    def get_capital(self):
        """
        股本数据
        :return:
        """
        request_data = self.request_body
        symbol = request_data.get("symbol")
        data = FinanceDataCache.GetDataByType(DataFileType.CAPITAL_FILE_TYPE,symbol)
        return {
            "code": 200,
            "data": data,
            "metainfo":CAPITAL_META_INFO
        }

    def get_symbol_list(self):
        """
        码表
        :return:
        """
        data_list = SymbolDataCache.get_symbol_list()
        return {
            "code":200,
            "data":data_list,
            "count":len(data_list)
        }
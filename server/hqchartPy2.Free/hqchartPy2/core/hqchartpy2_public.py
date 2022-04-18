# -*- coding: utf-8 -*-#
import json
from pydoc import doc

from hqchartPy2.core.hqchartpy2_systemdata import SymbolDataCache
from hqchartPy2.models.strategy import Stock


class RequestMixin(object):

    def __init__(self, request):
        self.request = request
        self.request_body = self.__request_preprocess()

    def __request_preprocess(self):
        requestData = {}
        for name,value in self.request.args.items():
            requestData[name] = value

        if (self.request.mimetype == "application/x-www-form-urlencoded"):
            requestData = self.request.form
        elif(self.request.mimetype == "application/json"):
            try:
                requestData = json.loads(self.request.get_data(as_text=True))
            except Exception as e:
                requestData = {}
        return requestData


class PolicyRunMixin(object):

    def get_symbol_list(self,stockPoolList):
        """
        根据股票池ID获取股票列表
        :param stockPoolList:
        :return:
        """
        symbol_list = []
        for item in stockPoolList:
            stockPoolId = item.get("id")
            stockPoolType = item.get("type")
            if stockPoolType == "SYS":#系统股票池（行业，地域和市场之类的板块）
                member_list = SymbolDataCache.get_block_members_by_id(block_id=stockPoolId)
                symbol_list.extend(member_list)
            elif stockPoolType == "DIY":
                query_set = Stock.query.filter_by(groupId=stockPoolId)
                for item in query_set:
                    symbol_list.append(item.symbol)
        # 去重处理
        symbol_list = list(set(symbol_list))
        return symbol_list

if __name__ == '__main__':
    data = " 100 >= 1001"
    ret = eval(data)
    print(ret)
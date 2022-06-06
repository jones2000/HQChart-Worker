from flask import request, jsonify, render_template, Blueprint
from flask_cors import CORS
import socket
import platform
from hqchartPy2.core.hqchartpy2_fast import FastHQChart
from hqchartPy2.core.hqchartpy2_klinedata import KLineCache
from hqchartPy2.core.hqchartpy2_run import HQChartPySimpleRun, HQChartPyMultiRun, HQChartPyPolicyRun
from hqchartPy2.core.hqchartpy2_hqapidata import DayKLineController, MinuteKLineController
from hqchartPy2.core.hqchartpy2_strategyapi import StrategyController, StrategyGroupController, \
    DataController, AlgorithmController, AlgorithmGroupController, \
    StockGroupController, StockInfoController, PolicyRunner, FinanceDataController

from hqchartPy2.extention import service_port,python_version

hqchart_api = Blueprint("api", __name__, url_prefix="/api", template_folder="templates")
CORS(hqchart_api, supports_credentials=True)  # 跨域


@hqchart_api.route('/about/info', methods=['GET'])
def version():
    """
    版本
    :return:
    """
    plate_version = platform.platform()
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    ret_data = {
        "version": FastHQChart.GetVersion(),
        "plateVersion": plate_version,
        "pythonVersion":python_version,
        "host": ip,
        "port": service_port,
    }
    return jsonify(ret_data)



#==============================指标相关API---BEGIN =========================================

# 创建指标
@hqchart_api.route('/strategy/create', methods=["POST", "PUT"])
def create_strategy():
    controller = StrategyController(request=request)
    responseData = controller.create()
    return jsonify(responseData)


# 删除指标
@hqchart_api.route('/strategy/<int:strategyId>', methods=["DELETE"])
def delete_strategy(strategyId):
    controller = StrategyController(request=request)
    responseData = controller.delete(strategyId)
    return jsonify(responseData)


# 修改指标
@hqchart_api.route('/strategy/<int:strategyId>', methods=["PATCH", "POST"])
def update_strategy(strategyId):
    controller = StrategyController(request=request)
    responseData = controller.update(strategyId)
    return jsonify(responseData)


# 查询指标详情
@hqchart_api.route('/strategy/<int:strategyId>', methods=["GET"])
def get_strategy(strategyId):
    controller = StrategyController(request=request)
    responseData = controller.get(strategyId)
    return jsonify(responseData)

# 指标列表查询
@hqchart_api.route('/strategy/list', methods=["GET"])
def strategy_list():
    controller = StrategyController(request=request)
    responseData = controller.list()
    return jsonify(responseData)


# 通过分组查询指标列表
@hqchart_api.route('/strategy/<int:groupId>/list', methods=["GET"])
def strategy_list_by_groupId(groupId):
    controller = StrategyController(request=request)
    responseData = controller.list_by_groupId(groupId)
    return jsonify(responseData)

# 创建指标分组
@hqchart_api.route('/group/create', methods=['POST', 'PUT'])
def group_create():
    controller = StrategyGroupController(request=request)
    responseData = controller.create()
    return jsonify(responseData)

#删除指标分组
@hqchart_api.route('/group/<int:groupId>', methods=['DELETE'])
def group_delete(groupId):
    controller = StrategyGroupController(request=request)
    responseData = controller.delete(groupId)
    return jsonify(responseData)


# 修改指标分组名称
@hqchart_api.route('/group/<int:groupId>', methods=["PATCH", "POST"])
def update_group(groupId):
    controller = StrategyGroupController(request=request)
    responseData = controller.update(groupId)
    return jsonify(responseData)


# 查询指标分组
@hqchart_api.route('/group/<int:groupId>', methods=["GET"])
def get_group(groupId):
    controller = StrategyGroupController(request=request)
    responseData = controller.get(groupId)
    return jsonify(responseData)


# 指标分组列表查询
@hqchart_api.route('/group/list', methods=["GET"])
def group_list():
    controller = StrategyGroupController(request=request)
    responseData = controller.list()
    return jsonify(responseData)


# 单指标运行
@hqchart_api.route('/Run', methods=['POST', "GET"])
def single_run():
    pyRun = HQChartPySimpleRun()
    if (pyRun.SetPostData(request)):
        pyRun.Run()

    responseData = pyRun.GetResponseData()
    return jsonify(responseData)


# 批量指标计算
@hqchart_api.route('/RunAll', methods=['POST', "GET"])
def multiple_run():
    pyRun = HQChartPyMultiRun()
    if (pyRun.SetPostData(request)):
        pyRun.Run()

    responseData = pyRun.GetResponseData()
    return jsonify(responseData)

#===================================指标相关API--END===================================

#===================================数据配置相关类API==================================

#数据文件存放路径设置相关API
@hqchart_api.route('/data/path', methods=["PATCH", "POST"])
def update_config():
    controller = DataController(request=request)
    responseData = controller.update()
    return jsonify(responseData)


#数据同步状态以及进度条
@hqchart_api.route('/data/status', methods=["GET"])
def data_status():
    controller = DataController(request=request)
    responseData = controller.get()
    return jsonify(responseData)

#数据加载到缓存中
@hqchart_api.route('/data/load', methods=["POST"])
def load_data():
    controller = DataController(request=request)
    responseData = controller.load_data()
    return jsonify(responseData)

#从CDN同步数据到本地，并合并数据文件
@hqchart_api.route('/data/sync', methods=["POST"])
def sync_data():
    controller = DataController(request=request)
    responseData = controller.sync_data()
    return jsonify(responseData)

#===================================数据配置相关类API--END==================================

#===================================策略相关API-BEGIN=======================================
# 创建策略
@hqchart_api.route('/algorithm/create', methods=["POST", "PUT"])
def create_algorithm():
    controller = AlgorithmController(request=request)
    responseData = controller.create()
    return jsonify(responseData)


# 删除策略
@hqchart_api.route('/algorithm/<int:algorithmId>', methods=["DELETE"])
def delete_algorithm(algorithmId):
    controller = AlgorithmController(request=request)
    responseData = controller.delete(algorithmId)
    return jsonify(responseData)


# 修改策略
@hqchart_api.route('/algorithm/<int:algorithmId>', methods=["PATCH", "POST"])
def update_algorithm(algorithmId):
    controller = AlgorithmController(request=request)
    responseData = controller.update(algorithmId)
    return jsonify(responseData)


# 查询策略详情
@hqchart_api.route('/algorithm/<int:algorithmId>', methods=["GET"])
def get_algorithm(algorithmId):
    controller = AlgorithmController(request=request)
    responseData = controller.get(algorithmId)
    return jsonify(responseData)


# 列表查询策略
@hqchart_api.route('/algorithm/list', methods=["GET"])
def algorithm_list():
    controller = AlgorithmController(request=request)
    responseData = controller.list()
    return jsonify(responseData)

# 创建策略分组
@hqchart_api.route('/algorithm/group/create', methods=['POST', 'PUT'])
def algorithm_group_create():
    controller = AlgorithmGroupController(request=request)
    responseData = controller.create()
    return jsonify(responseData)

#删除策略分组
@hqchart_api.route('/algorithm/group/<int:groupId>', methods=['DELETE'])
def algorithm_group_delete(groupId):
    controller = AlgorithmGroupController(request=request)
    responseData = controller.delete(groupId)
    return jsonify(responseData)

# 修改策略分组
@hqchart_api.route('/algorithm/group/<int:groupId>', methods=["PATCH", "POST"])
def update_algorithm_group(groupId):
    controller = AlgorithmGroupController(request=request)
    responseData = controller.update(groupId)
    return jsonify(responseData)


# 查询策略分组详情
@hqchart_api.route('/algorithm/group/<int:groupId>', methods=["GET"])
def get_algorithm_group(groupId):
    controller = AlgorithmGroupController(request=request)
    responseData = controller.get(groupId)
    return jsonify(responseData)


# 列表查询策略
@hqchart_api.route('/algorithm/group/list', methods=["GET"])
def algorithm_group_list():
    controller = AlgorithmGroupController(request=request)
    responseData = controller.list()
    return jsonify(responseData)


# 策略计算
@hqchart_api.route('/Policy', methods=['POST', "GET"])
def Policy_Run():
    pyRun = HQChartPyPolicyRun()
    if (pyRun.SetPostData(request)):
        pyRun.Run()

    responseData = pyRun.GetResponseData()
    return jsonify(responseData)


# 运行所有策略，并将结果写入数据库表
@hqchart_api.route('/Policy/RunAll', methods=['POST', "GET"])
def Policy_RunAll():
    pyRun = PolicyRunner(request)
    responseData = pyRun.RunAll()
    return jsonify(responseData)


# 运行指定策略，并将结果写入数据库表
@hqchart_api.route('/Policy/RunById', methods=['POST', "GET"])
def Policy_Run_ByPolicyId():
    pyRun = PolicyRunner(request)
    responseData = pyRun.RunOne()
    return jsonify(responseData)

# 策略运行状态
@hqchart_api.route('/Policy/RunStatus', methods=['POST', "GET"])
def Policy_RunStatus():
    pyRun = PolicyRunner(request)
    responseData = pyRun.RunStatus()
    return jsonify(responseData)


# 策略运行結果
@hqchart_api.route('/Policy/<int:PolicyId>/RunResult', methods=['POST', "GET"])
def Policy_Run_Result(PolicyId):
    pyRun = PolicyRunner(request)
    responseData = pyRun.RunResult(PolicyId)
    return jsonify(responseData)

#===================================策略相关API-END=======================================


#===================================股票池相关API-BEGIN===================================
@hqchart_api.route('/stock/group/create', methods=['POST', 'PUT'])
def stock_group_create():
    """
    创建股票池
    :return:
    """
    controller = StockGroupController(request=request)
    responseData = controller.create()
    return jsonify(responseData)


@hqchart_api.route('/stock/group/<int:groupId>', methods=['DELETE'])
def stock_group_delete(groupId):
    """
    删除股票池
    :param groupId:
    :return:
    """
    controller = StockGroupController(request=request)
    responseData = controller.delete(groupId)
    return jsonify(responseData)


# 修改股票池名称
@hqchart_api.route('/stock/group/<int:groupId>', methods=["PATCH", "POST"])
def update_stock_group(groupId):
    controller = StockGroupController(request=request)
    responseData = controller.update(groupId)
    return jsonify(responseData)


# 查询股票池成分
@hqchart_api.route('/stock/group/<int:groupId>', methods=["GET"])
def get_stock_group(groupId):
    controller = StockGroupController(request=request)
    responseData = controller.get(groupId)
    return jsonify(responseData)


# 股票池列表查询
@hqchart_api.route('/stock/group/list', methods=["GET"])
def stock_group_list():
    controller = StockGroupController(request=request)
    responseData = controller.list()
    return jsonify(responseData)


# 在股票池中添加股票成员
@hqchart_api.route('/stock/group/<int:groupId>/member/add', methods=["PATCH", "POST"])
def add_stock_to_stock_group(groupId):
    controller = StockGroupController(request=request)
    responseData = controller.add_stock(groupId)
    return jsonify(responseData)


# 在股票池中删除股票成员
@hqchart_api.route('/stock/group/<int:groupId>/member/delete/<int:stockId>', methods=["delete", "POST"])
def delete_stock_from_stock_group(groupId,stockId):
    controller = StockGroupController(request=request)
    responseData = controller.delete_stock(groupId,stockId)
    return jsonify(responseData)

#===================================股票池相关API-END===================================

#===================================数据相关API ========================================

# 前端K线数据
@hqchart_api.route('/DayKLine', methods=['POST', "HEAD", "OPTIONS"])
def day_kline():
    controller = DayKLineController()
    if (controller.SetPostData(request)):
        controller.Run()
    responseData = controller.GetResponseData()
    return jsonify(responseData)


#分钟K线数据
@hqchart_api.route('/MinuteKLine', methods=['POST','HEAD', "GET"])
def MinuteKLine():
    controller=MinuteKLineController()
    if (controller.SetPostData(request)):
        controller.Run()
    responseData=controller.GetResponseData()
    return jsonify(responseData)

# 键盘精灵
@hqchart_api.route('/stock/search', methods=["POST"])
def search_stock():
    controller = StockInfoController(request=request)
    responseData = controller.search()
    return jsonify(responseData)

# 获取板块信息
@hqchart_api.route('/stock/blocklist', methods=["GET","POST"])
def sys_blocklist():
    controller = StockInfoController(request=request)
    responseData = controller.get_sys_block_list()
    return jsonify(responseData)

# 获取码表信息
@hqchart_api.route('/stock/symbollist', methods=["GET"])
def stock_symbollist():
    controller = StockInfoController(request=request)
    responseData = controller.get_symbol_list()
    return jsonify(responseData)

# 获取股票财务数据
@hqchart_api.route('/stock/finance', methods=["GET"])
def stock_finance():
    controller = FinanceDataController(request=request)
    responseData = controller.get_finance()
    return jsonify(responseData)

# 获取股票股本数据
@hqchart_api.route('/stock/capital', methods=["GET"])
def stock_capital():
    controller = FinanceDataController(request=request)
    responseData = controller.get_capital()
    return jsonify(responseData)


if __name__ == '__main__':
    FastHQChart.Initialization(None)  # 初始化

    # 初始化缓存
    KLineCache.SetCachePath("../data/kdata/0")
    KLineCache.LoadCache()
    hqchart_api.run(host='0.0.0.0', port=8712, debug=False)

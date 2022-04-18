import datetime

from hqchartPy2.core.tools import datetime_format
from hqchartPy2.extention import db


class StrategyGroup(db.Model):
    """
    指标分组
    """
    __tablename__ = 'hqchart_strategy_group'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    strategies = db.relationship("Strategy", back_populates="group")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "strategies": [item.to_dict() for item in self.strategies]
        }


class Strategy(db.Model):
    """
    策略指标
    """
    __tablename__ = 'hqchart_strategy'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), comment="指标名称")
    groupId = db.Column(db.Integer, db.ForeignKey('hqchart_strategy_group.id'),
                        comment="分组ID")
    description = db.Column(db.String(128), comment="指标描述")
    isMainIndex = db.Column(db.Boolean, comment="是否是主指标")
    floatPrecision = db.Column(db.String(1), comment="浮点数精度")
    script = db.Column(db.Text, comment="策略代码")
    args = db.relationship('StrategyArgument', backref='strategy', lazy='dynamic')
    outArgs = db.Column(db.JSON,comment="输出参数，是数组",default="[]")
    group = db.relationship("StrategyGroup", back_populates="strategies")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "groupId": self.groupId,
            "groupName": self.group.name if self.group else None,
            "description": self.description,
            "isMainIndex": self.isMainIndex,
            "floatPrecision": self.floatPrecision,
            "outArgs":self.outArgs,
            "script": self.script,
            "args": [arg.to_dict() for arg in self.args]
        }


class StrategyArgument(db.Model):
    """
    指标参数
    """
    __tablename__ = 'hqchart_strategy_argument'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    strategyId = db.Column(db.Integer, db.ForeignKey('hqchart_strategy.id'),
                           comment="指标ID")
    name = db.Column(db.String(128), comment="参数名称")
    defaultVal = db.Column(db.Integer, comment="参数值")
    minVal = db.Column(db.Integer, comment="最小值")
    maxVal = db.Column(db.Integer, comment="最大值")

    def to_dict(self):
        return {
            "id": self.id,
            "strategyId": self.strategyId,
            "name": self.name,
            "defaultVal": self.defaultVal,
            "minVal": self.minVal,
            "maxVal": self.maxVal
        }

    def __repr__(self):
        return {
            "id": self.id,
            "strategyId": self.strategyId,
            "name": self.name,
            "defaultVal": self.defaultVal,
            "minVal": self.minVal,
            "maxVal": self.maxVal
        }


class AlgorithmGroup(db.Model):
    """
    策略分组
    """
    __tablename__ = 'hqchart_algorithm_group'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    algorithms = db.relationship("Algorithm", back_populates="group")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "algorithms": [{"id": item.id, "name": item.name} for item in self.algorithms]
        }

    def filter_by_algorithms_status_to_dict(self,status):
        data = {"id":self.id,"name":self.name,"algorithms":[]}
        for item in self.algorithms:
            if item.status == status:
                data["algorithms"].append({"id": item.id, "name": item.name})
        return data


class Algorithm(db.Model):
    """
    选股策略
    """
    __tablename__ = 'hqchart_algorithm'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), comment="策略名称")
    groupId = db.Column(db.Integer, db.ForeignKey('hqchart_algorithm_group.id'),
                        comment="分组ID")
    period = db.Column(db.Integer,comment="周期",default=0)
    right = db.Column(db.Integer,comment="复权",default=0)
    strategies = db.Column(db.JSON,comment="策略指标",default=[])
    stockPool = db.Column(db.JSON,default=[],comment="股票池,最多50个，以逗号隔开")
    status = db.Column(db.Integer,comment="状态(0-测试;1-发布;2-停用)",default=0,)
    group = db.relationship("AlgorithmGroup", back_populates="algorithms")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "groupId": self.groupId,
            "groupName": self.group.name if self.group else None,
            "period": self.period,
            "right": self.right,
            "strategies": self.strategies,
            "stockPool": self.stockPool,
            "status":self.status
        }


class AlgorithmResult(db.Model):
    """
    选股策略结果
    """
    __tablename__ = 'hqchart_algorithm_result'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    algorithmId = db.Column(db.Integer,db.ForeignKey('hqchart_algorithm.id'), comment="策略ID",doc="策略ID",unique=True)
    ticket = db.Column(db.Integer,comment="花费时间")
    status = db.Column(db.Integer,comment="执行状态（0-初始；1-执行成功；2-执行失败）",)
    result = db.Column(db.JSON,comment="执行结果")
    updateTime = db.Column(db.DateTime,comment="最后执行时间")

    def to_dict(self):
        return {
            "id": self.id,
            "algorithmId": self.algorithmId,
            "ticket":self.ticket,
            "result":self.result,
            "status":self.status,
            "updateTime":self.updateTime.strftime("%Y-%m-%d %H:%M:%S") if self.updateTime else None,
        }


class HqchartDataStatus(db.Model):
    """
    数据文件配置及状态
    """
    __tablename__ = 'hqchart_data_status'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="ID", doc="ID")
    type = db.Column(db.Integer, nullable=False, comment="数据类别", doc="数据类别")
    name = db.Column(db.String(64), nullable=False, comment="数据类别名称")
    counts = db.Column(db.Integer, nullable=False, default=0, comment="数据总条数")
    dataPath = db.Column(db.String(128), nullable=True, comment="数据存放目录")
    latestDataDate = db.Column(db.Integer, nullable=True, comment="数据的最新日期，K线以上证指数为准，码表以财务数据为准")
    loadTime = db.Column(db.DateTime, comment="最后加载时间")
    updateTime = db.Column(db.DateTime, comment="最后更新时间")

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "counts": self.counts,
            "dataPath": self.dataPath,
            "latestDataDate": self.latestDataDate,
            "loadTime": self.loadTime.strftime("%Y-%m-%d %H:%M:%S") if self.loadTime else None,
            "updateTime": self.updateTime.strftime("%Y-%m-%d %H:%M:%S") if self.updateTime else None,
        }


class HqChartAccountInfo(db.Model):
    __tablename__ = 'hqchart_count_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="ID")
    account = db.Column(db.String(64), nullable=False, comment="账号", doc="账号")
    password = db.Column(db.String(64), nullable=False, comment="密码")

    def to_dict(self):
        return {
            "id": self.id,
            "account": self.account
        }


class StockGroup(db.Model):
    """
    自定义股票池
    """
    __tablename__ = 'hqchart_stock_group'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    members = db.relationship("Stock", back_populates="group")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "members": [{"id": item.id,"symbol":item.symbol, "name": item.name,"date":item.date} for item in self.members]
        }


class Stock(db.Model):
    """
    自定义股票池的股票成员
    """
    __tablename__ = 'hqchart_stock'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    groupId = db.Column(db.Integer,db.ForeignKey('hqchart_stock_group.id'),nullable=False,comment="股票池分组ID")
    symbol = db.Column(db.String(16),nullable=False,comment="证券代码")
    name = db.Column(db.String(32), nullable=False, comment="证券名称")
    date = db.Column(db.Integer,nullable=False,comment="证券加入日期")
    group = db.relationship("StockGroup", back_populates="members")

    __table_args__ = (
        db.UniqueConstraint('groupId', 'symbol', name='idx_groupId_symbol'),
    )
    def to_dict(self):
        return {
            "id": self.id,
            "groupId":self.groupId,
            "groupName": self.group.name,
            "date": self.date,
            "symbol": self.symbol,
            "name": self.name
        }
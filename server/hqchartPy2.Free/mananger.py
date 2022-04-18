#!/usr/bin/env python
from flask_cors import CORS
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from hqchartPy2 import create_app
from hqchartPy2.core.hqchart2_syncklinedata_from_cdn import DataFileType
from hqchartPy2.core.hqchartpy2_klineminutedata import MinuteKLineCache
from hqchartPy2.core.hqchartpy2_systemdata import SymbolDataCache, FinanceDataCache
from hqchartPy2.extention import db, service_port, DATA_FILE_TYPE_META
from hqchartPy2.core.hqchartpy2_fast import FastHQChart
from hqchartPy2.core.hqchartpy2_klinedata import KLineCache
from hqchartPy2.models.strategy import *

# app = create_app("development")
app = create_app("production")

manager = Manager(app)
migrate = Migrate(app, db)
migrate.init_app(app)
manager.add_command('db', MigrateCommand)


def init_data():
    #初始化数据目录
    query_set = HqchartDataStatus.query.all()
    if len(query_set) == 0:
        for dataType in DATA_FILE_TYPE_META:
            dataObj =  HqchartDataStatus()
            dataObj.dataPath = ""
            dataObj.type = dataType.value
            dataObj.name = DATA_FILE_TYPE_META[dataType]
            db.session.add(dataObj)
            db.session.commit()

    for item in query_set:
        if item is None:
            continue
        if item.type == DataFileType.DAY_KLINE_FILE_TYPE.value:
            KLineCache.SetCachePath(item.dataPath)
        if item.type == DataFileType.MIN_KLINE_FILE_TYPE.value:
            MinuteKLineCache.SetCachePath(item.dataPath)
        if item.type == DataFileType.SYMBOLE_FILE_TYPE.value:
            SymbolDataCache.SetCachePath(item.dataPath)
            SymbolDataCache.LoadCache()
        if item.type in [DataFileType.FINANCE_FILE_TYPE.value,DataFileType.CAPITAL_FILE_TYPE.value]:
            FinanceDataCache.SetCachePath(DataFileType(item.type),item.dataPath)
            FinanceDataCache.LoadCache(DataFileType(item.type))


@manager.command
def runserver():
    FastHQChart.Initialization(None)  # 初始化

    init_data()

    CORS(app, supports_credentials=True)

    app.run(host='0.0.0.0', port=service_port, debug=False)
    # http_server = WSGIServer(('', 8712), app)
    # http_server.serve_forever()

if __name__ == '__main__':
    manager.run()
    db.create_all()
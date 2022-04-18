from .api import hqchart_api
from .front import hqchart_front

# 蓝本默认配置
DEFAULT_BLUEPRINT = (
    # (蓝本，前缀)
    (hqchart_front, ''),
    (hqchart_api, '/api'),
)


# 封装函数配置蓝本
def config_blueprint(app):
    for blueprint, url_prefix in DEFAULT_BLUEPRINT:
        app.register_blueprint(blueprint, url_prefix=url_prefix)

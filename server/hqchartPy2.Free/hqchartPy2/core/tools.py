import datetime
import time as tm


def date_range_list(start, end, freq='D', format='%Y%m%d'):
    """
    生成日期时间序列
    :param start: 开始日期
    :param end:   结束日期
    :param freq: 周期（Y-年，M-月，D-日，M-月，H-小时，MIN-分钟，S-秒）n+freq 表示间隔多少个周期eg.5Min 表示间隔5分钟
    :param format: 生成的日期序列的格式。eg."%Y-%m-%d %H:%M:%S"
    :return:
    """
    import pandas as pd
    df = pd.date_range(start=str(start), end=str(end), freq=freq).to_pydatetime()
    date_list = []
    for date in df:
        date_list.append(datetime_format(date=date, srcformat='%Y-%m-%d %H:%M:%S', tgtformat=format))
    return date_list


def get_current_date(format='%Y-%m-%d'):
    """
    获取当前日期
    ------------
    returns：
        date：YYYY-mm-dd
    """
    return tm.strftime(format, tm.localtime(tm.time()))


def calac_date_time(date, years=0, days=0, format="%Y-%m-%d"):
    """
    计算日期偏移后的日期
    ------------
    :param
        date:  str
            基准日期，格式为由format制定
        years：int
            偏移的年数,如果向前偏移，则填负数
        days: 偏移的天数，如果向前偏移，则填负数
        format: 日期格式
    :returns
        string：格式由format指定
    """
    if years != 0:
        date = str(int(str(date)[:4]) + int(years)) + str(date)[4:]
    date = datetime.datetime.strptime(str(date), format)
    delta = datetime.timedelta(days=days)
    date = date + delta
    return date.strftime(format)


def datetime_format(date, srcformat='%Y-%m-%d', tgtformat='%Y%m%d'):
    """
    将一种格式的时间字符串转化为另外一种时间的字符串
    ------------
    returns：
        string：格式由tgtformat指定
    """
    return tm.strftime(tgtformat, tm.strptime(str(date), srcformat))


def timestamp_to_datetime(timestamp=None, format='%Y-%m-%d'):
    """
    时间戳转化为字符串日期
    ------------
    :param timestamp 时间戳
    :format string 格式 eg. %Y-%m-%d
    returns：
        date：YYYY-mm-dd
    """
    import time as tm
    if timestamp is None:
        timestamp = tm.time()
    return tm.strftime(format, tm.localtime(timestamp))

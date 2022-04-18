# -*- coding: utf-8 -*-#

# ===============================================================================
# Name:         __init__.py
# Description:  
# Author:       mayn
# Date:         2021/11/24
# ===============================================================================
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def scheduler():
    print
    "edit your code here"
    pass


if __name__ == '__main__':
    begin = time.time()
    reload(sys)
    sys.setdefaultencoding("utf-8")
    scheduler()
    end = time.time()
    logging.info(msg="total take {seconds} seconds to execute ! ".format(seconds=end - begin))
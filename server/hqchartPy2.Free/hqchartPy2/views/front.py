from flask import Blueprint, render_template

from hqchartPy2.core.hqchartpy2_fast import FastHQChart

hqchart_front = Blueprint("index", __name__, url_prefix="", template_folder="templates")


@hqchart_front.route("/", methods=["GET"])
def index():
    """
    首页
    :return:
    """
    return render_template("index.html")

@hqchart_front.route("/userAgreement.html", methods=["GET"])
def userAgreement():
    """
    首页
    :return:
    """
    return render_template("userAgreement.html")


@hqchart_front.route("/privacyStatement.html", methods=["GET"])
def privacyStatement():
    """
    首页
    :return:
    """
    return render_template("privacyStatement.html")

@hqchart_front.route("/detailData.html", methods=["GET"])
def detailData():
    """
    首页
    :return:
    """
    return render_template("detailData.html")
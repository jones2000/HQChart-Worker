import axios from 'axios'
import {getCookie} from "./tools"
import { Message } from 'element-ui';

var instance = axios.create({
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
    // "Authorization": 'Basic ' + tools.getCookie('token')
  },
  // transformResponse: [function (res) {
  //     // 在此转码数据
  //     return res;
  // }],
});
instance.interceptors.response.use(function (response) {
  return response.data;
}, function (error) {
  console.log("对响应错误做点什么",error);
  return Promise.reject(error);
});
instance.interceptors.request.use(function (config) {
  // console.log('请求配置', config);
  const url = config.url
  if(url.indexOf('/api/data/sync') > -1){
    if(getCookie('token')){
      return config
    }else{
      Message({
        message: '请先登录',
        type: 'error'
      })
      return Promise.reject('请先登录');  
    }
  }
  return config
}, function (error) {
  console.log("对req错误做点什么",error);
  return Promise.reject(error);
});

var post = function (apiurl, data, fn,err) {
  return instance.post(apiurl, data).then(res => {
    fn(res)
    return res;
  }).catch(e => {
    err && err(e);
  });
}
var get = function (url, data, fn,err) {
  return instance.get(url, data).then(res => {
    // console.log(`fn:${fn}`);
      fn(res)
      return res;
  }).catch(e => {
    err && err(e);
  });
}

var patch = function(url, data, fn, err) {
  return instance.patch(url, data).then(res => {
    fn(res)
    return res
  }).catch(e => {
    err && err(e);
  });
}

var dele = function (url, fn, err) {
  return instance.delete(url).then(res => {
    // console.log(`fn:${fn}`);
      fn(res)
      return res;
  }).catch(e => {
    err && err(e);
  });
}

// const assemblApi1 = "https://webapicache.zealink.com";
// const assemblApi2 = "https://webapi.zealink.com";
// const assemblApi3 = "https://projectcache.zealink.com";
// const assemblAliyun = "http://beigo.oss-cn-beijing.aliyuncs.com/";
// const cAPIHost = 'http://192.168.0.109:8088'

const useApiHost = 'http://192.168.0.118:8712'

const env = false//false：开发环境，true：生产环境
function apiHost(api){
  // const env = true 
  if(!env){
    return useApiHost + api
  }
  return api
}

function translateUrl(url){
  // const env = true //false：开发环境，true：生产环境
  if(!env){
    return url
  }
  return '/admin'+url
}

const zhHost = 'http://py-hqchar-api.umydata.com'



const urlObj = {
  //方法
  post,
  get,
  patch,
  dele,
  apiHost,

  //api url
  apiStrategyCreate: apiHost('/api/strategy/create'), //新建策略 post,put
  apiStrategyOpr: apiHost('/api/strategy/'), //删除策略 delete请求；修改策略 post请求；策略详情 get请求
  apiStrategyList: apiHost('/api/strategy/list'), //列表查询 get请求
  
  apiGroupCreate: apiHost('/api/group/create'),
  apiGroupOpr: apiHost('/api/group/'), //删除分组 delete请求; 查询分组 get;
  apiGroupList: apiHost('/api/group/list'),// 分组列表查询 get请求

  apiHqchartAccount: apiHost('/api/hqchart/account'), //设置账号
  apiHqchartConfig: apiHost('/api/data/path'), //设置数据文件路径
  apiAboutInfo: apiHost('/api/about/info'), //获取基本信息
  apiDataStatus: apiHost('/api/data/status'), //获取数据状态
  apiDataSync: apiHost('/api/data/sync'),// 同步数据
  apiDataLoad: apiHost('/api/data/load'), //加载数据
  apiRun: apiHost('/api/Run'), //执行指标
  apiDayKLine: apiHost('/api/DayKLine'), //日线
  apiMinuteKLine: apiHost('/api/MinuteKLine'), //分钟k线
  //编辑策略
  apiAlgorithmCreate: apiHost('/api/algorithm/create'), //创建选股策略
  apiAlgorithmlist: apiHost('/api/algorithm/list'), //列表查询选股策略
  apiAlgorithmByIndex: apiHost('/api/algorithm/'), //+id patch-修改选股策略 get-查询 delete-删除
  apiAlgorithmGroupList: apiHost('/api/algorithm/group/list'), //查询所有策略-左侧树结构

  apiAlgorithmGroupCreate: apiHost('/api/algorithm/group/create'), //策略-组-创建
  apiAlgorithmGroupById: apiHost('/api/algorithm/group/'), //+id 更新-patch del-删除

  apiAlgorithmPolicy: apiHost('/api/Policy'), //执行-选股策略


  apiLogin: zhHost + '/api/Login', //登录
  apiGetVerificationCode: zhHost + '/api/GetVerificationCode', //登录
  apiRegister: zhHost + '/api/Register', //登录

  //股票池接口
  apiStockGroupCreate: apiHost('/api/stock/group/create'), //创建股票池
  apiStockGroup: apiHost('/api/stock/group/') , //+id 操作股票池;+id + /member/add 股票池添加成员; +id + /member/delete/+id 股票池删除成员
  apiStockGroupList: apiHost('/api/stock/group/list'), //股票池列表
  apiStockSearch: apiHost('/api/stock/search'), //搜索股票

  apiStockBlocklist: apiHost('/api/stock/blocklist'), //板块列表-不包括自定义股票池

  //策略运行接口
  apiPolicyRunById: apiHost('/api/Policy/RunById'),//运行策略通过ID
  apiPolicyRunAll: apiHost('/api/Policy/RunAll'),//运行所有策略
  // apiAlgorithmPolicy: apiHost('/api/Policy'),//+id/RunResult策略执行结果
  apiPolicyRunStatus: apiHost('/api/Policy/RunStatus'),//策略执行状态

  //查看数据接口
  apiStockSymbollist:apiHost('/api/stock/symbollist'), //码表数据
  apiStockFinance:apiHost('/api/stock/finance'), //?symbol=000001.sz 财务数据
  apiStockCapital:apiHost('/api/stock/capital'), //?symbol=000001.sz 股本数据

}

export default urlObj;
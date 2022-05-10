<template>
  <div class="indexEditWrap" ref="indexEditWrap">
    <div class="left">
      <category-list ref="categorylist" 
        @changeCategory='changeCategory'
        @deleteStrategy='deleteStrategy'
        @changeStrategyName='changeStrategyName'
        ></category-list>
    </div>
    <div class="right">
      <div class="rightContentWrap">
        <div class="spaceBox" ref='spaceBox' v-if="editableTabs.length > 0"></div>
        <el-tabs v-model="editableTabsValue" type="card" closable @tab-remove="removeTab" @tab-click="handleTabClick">
          <el-tab-pane
            v-for="item in editableTabs"
            :key="item.name"
            :label="item.title"
            :name="item.name"
          > 
            <!-- {{item.content}} -->
          </el-tab-pane>
        </el-tabs>
        <div class="commonTabContentWrap" v-loading='loading' v-if="editableTabs.length > 0">
          <div class="editorWrap" ref='editorWrap'>
            <div class="klineConditonWrap">
              <div class="selectInfoWrap">
                <div class="oneLineWrap">
                  <span class="labelPeriod">周&emsp;&emsp;期：</span>
                  <el-select v-model="kLineChart.Period" value-key='Value' placeholder="请选择" size="small" @change='changePeriod'>
                    <el-option
                      v-for="item in PeroidOptions"
                      :key="item.Value"
                      :label="item.Text"
                      :value="item">
                    </el-option>
                  </el-select>
                  <span class="timeRange">&nbsp;K线范围：</span>
                  <el-select class="dataNum" v-model="dataNum" placeholder="请选择" size="small">
                    <el-option
                      v-for="item in filterDataNumOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value">
                    </el-option>
                  </el-select>
                </div>
                <div class="oneLineWrap">
                  <span class="labelRight">复权方式：</span>
                  <el-select v-model="kLineChart.Right.Value" placeholder="请选择" :disabled='rightsOptionsDisabled' size="small" @change='changeRight'>
                    <el-option
                      v-for="(item, index) in RightOptions"
                      :key="index"
                      :label="item"
                      :value="index">
                    </el-option>
                  </el-select>
                  <span class="labelSymbol">股票代码：</span>
                  <el-select
                    class="stockSearchSelect"
                    v-model="inputValue"
                    size="small"
                    value-key='symbol'
                    filterable
                    remote
                    reserve-keyword
                    placeholder="请输入股票代码或简称"
                    :remote-method="remoteMethod"
                    :loading="searchLoading">
                    <el-option
                      v-for="item in resultOptions"
                      :key="item.symbol"
                      :label="item.name"
                      :value="item">
                      {{item.symbol}}&emsp;{{item.name}}
                    </el-option>
                  </el-select>
                </div>
              </div>
              <div class="paramsEditWrap">
                <table class="editTable">
                  <thead>
                    <tr>
                      <td>参数名称</td>
                      <td>最小</td>
                      <td>最大</td>
                      <td>缺省</td>
                      <td></td>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for='(row,rowIndex) in filterCurrentList' :key="rowIndex">
                      <td><div class="box name"><input type="text" v-model='row.name.value'></div></td>
                      <td><div class="box min"><input type="text" v-model='row.min.value'></div></td>
                      <td><div class="box max"><input type="text" v-model='row.max.value'></div></td>
                      <td><div class="box defVale"><input type="text" v-model='row.value.value'></div></td>
                      <td>
                        <button type="default" v-show="rowIndex === filterCurrentList.length - 1" @click="addRow"><i class="el-icon-plus strongFont"></i></button>
                        <button type="default" v-show="rowIndex > 2"><i class="el-icon-minus strongFont" @click="deleteRow(rowIndex)"></i></button>
                      </td>
                    </tr>
                    <tr v-if="filterCurrentList.length === 0">
                      <td colspan="5">
                        <div class="noData"><button type="default" @click="addRow"><i class="el-icon-plus strongFont"></i></button></div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div class="paramsBtnsWrap">
              <el-button type="primary" size="small" @click="preExecOrSave('exec')">执行</el-button>
              <el-button type="default" size="small" @click="preExecOrSave('save')">保存</el-button>
              <!-- <el-button type="default" size="small" @click="deleteFun">删除</el-button> -->
            </div>
          </div>
          <div class="codeWrap">
            <h3>指标编辑</h3>
            <div class="code">
              <codemirror ref="myCm" v-model="CurrentCode" :options="CMOptions"></codemirror>
            </div>
          </div>
        </div>
        <div class="noData" v-else>还未选择指标</div>
      </div>
      <!-- rightContentWrap end -->
    </div>

    <el-dialog
      title=""
      :visible.sync="dialogVisible"
      :close-on-click-modal='false'
      @close='closeKlineDialog'
      width="60%"
    >
      <div v-loading='indexDataLoading'>
        <el-tabs class="elTabsRun" v-model="activeName" @tab-click="handleResultClick">
          <el-tab-pane label="运行结果" name="first"></el-tab-pane>
          <el-tab-pane label="数据表格" name="second"></el-tab-pane>
        </el-tabs>

        <div class="kline" ref="kline" v-show="activeName === 'first'"></div>
        <div class="tableWrapInDialog" v-show="activeName === 'second'">
          <el-table
            ref='klineDataTable'
            :data="pageTableData"
            size='midium'
            height="550"
            style="width: 100%">
            <el-table-column
              v-for="(item, index) in headerList"
              :key="index"
              :prop="item.prop"
              :label="item.label"
              :width="item.width"
              :align="item.align"
            >
            </el-table-column>
          </el-table>

          <div class="paginationWrapInDialog">
            <el-pagination
              background
              :page-size='paginationObj.PageSize'
              layout="prev, pager, next"
              :total="paginationObj.total"
              @current-change='currentChange'
            >
            </el-pagination>
          </div>
        </div>
        
      </div>
      
      
      <span slot="footer" class="dialog-footer">
        <!-- <el-button @click="dialogVisible = false">取 消</el-button> -->
        <!-- <el-button type="primary" @click="dialogVisible = false">确 定</el-button> -->
      </span>
    </el-dialog>
  </div>
</template>

<script>
  import HQChart from 'hqchart'
  import 'hqchart/src/jscommon/umychart.resource/css/tools.css'
  import 'hqchart/src/jscommon/umychart.resource/font/iconfont.css'
  
  import CategoryList from './categoryList.vue'
  import {find,findIndex,debounce} from 'lodash'
  import Service from './categoryService.js'

  import {codemirror} from 'vue-codemirror'
  import 'codemirror/lib/codemirror.css'
  //mode下javascript.js文件需要按照readme.txt修改一下
  import 'codemirror/mode/javascript/javascript.js'
  // import 'codemirror/theme/base16-light.css'
  import 'codemirror/addon/display/autorefresh' //及时自动更新，配置里面也需要设置autoRefresh为true
  import urlObj from '../../../utils/urlObj'
  import StockStringFormat from '../../../utils/stockstringformat'
  import moment from 'moment'
import { setCookie, getDateForApi } from '../../../utils/tools'

  const JSChart = HQChart.Chart.JSChart
  // console.log('HQChart::', HQChart);

  function DefaultData(){}
  DefaultData.GetListData = function() {
      var dataAry = [];
      for(let i = 0; i < 3; ++i){
          let item = DefaultData.GetListItem()
          dataAry.push(item);
      }
      return dataAry;
  }

  DefaultData.GetListItem = () => ({
    id: -1,
    delete: false, //是否要删除
    strategyId: -1, //所属策略的id
    name:{isEdit:false,value:''},
    min:{isEdit:false,value:''},
    max:{isEdit:false,value:''},
    value:{isEdit:false,value:''}
  })

  DefaultData.getKlineOption = () => {
    const option= {
      Type:'历史K线图',   //创建图形类型
      
      Windows: //窗口指标
      [
          {Index:"MA", Modify:false,Change:false},
          {Index:"VOL", Modify:false,Change:false}
          // {Index:"RSI", Modify:false,Change:false}, 
      ], 
      
      Symbol:'600000.sh',
      IsApiPeriod:true,
      IsAutoUpdate:false,       //是自动更新数据
      //TradeIndex: {Index:'交易系统-BIAS'},    //交易系统

      IsShowRightMenu:true,          //右键菜单
      IsShowCorssCursorInfo:true,    //是否显示十字光标的刻度信息

      KLine:  //K线设置
      {
          DragMode:1,                 //拖拽模式 0 禁止拖拽 1 数据拖拽 2 区间选择
          Right:0,                    //复权 0 不复权 1 前复权 2 后复权
          Period:0,                   //周期 0 日线 1 周线 2 月线 3 年线 
          MaxReqeustDataCount:1000,   //数据个数
          PageSize:50,               //一屏显示多少数据
          //Info:["互动易","大宗交易",'龙虎榜',"调研","业绩预告","公告"],       //信息地雷
          IsShowTooltip:true,                 //是否显示K线提示信息
      },

      KLineTitle: //标题设置
      {
          IsShowName:true,       //显示股票名称
          IsShowSettingInfo:true //显示周期/复权
      },

      Border: //边框
      {
          Left:1,         //左边间距
          Right:50,       //右边间距
          Bottom:25,      //底部间距
          Top:25          //顶部间距
      },
      
      Frame:  //子框架设置
      [
          {SplitCount:3,StringFormat:0, IsShowLeftText:false},
          {SplitCount:2,StringFormat:0, IsShowLeftText:false},
          {SplitCount:2,StringFormat:0, IsShowLeftText:false}
      ]
    }
    return option
  }

export default {
  name: 'IndexEdit',
  data () {
    return {
      defaultActiveIndex:'AAA-1',
      loading: false,

      editableTabsValue: '0',
      editableTabs: [],
      tabIndex: 0,

      CurrentList: [],
      CurrentCode:'',
      CMOptions: {
        tabSize: 4,
        mode: 'text/javascript',
        lineNumbers: true,
        line: true,
        // theme: 'base16-light'
      },
      ScriptIndexList: [],

      isCheckTab: false,

      dialogVisible: false,

      // Symbol: '000001.sz',
      inputValue: {
        name: "浦发银行",
        symbol: "600000.sh",
        type: "EQA"
      },
      searchLoading: false,
      resultOptions: [],
      isMainIndex: false,
      kLineChart: {
        Option: DefaultData.getKlineOption(),
        Chart: null,
        Period: {
          Text: '日线',
          Value: 0,
          Period: 0,
          noRightData: false,
          dateType: null
        },
        Right: {
          Text: '不复权',
          Value: 0
        },
        isChangeRight: false //是否能切换复权
      },
      paginationObj: {
        total: 1,
        PageSize: 30,
        PageIndex: 1
      },
      /*
      0=日线 1=周线 2=月线 3=年线 9=季线 21=双周 [40001-50000) 自定义日线
4=1分钟 5=5分钟 6=15分钟 7=30分钟 8=60分钟 11=120分钟 12=240分钟 [20001-30000) 自定义分钟
      */
      PeroidOptions: [
        {Text:"日线",Value:0},
        {Text:"周线",Value:1},
        {Text:"月线",Value:2},
        {Text:"季线",Value:9},
        {Text:"年线",Value:3},
        {Text:"1分钟",Value:4},
        {Text:"5分钟",Value:5},
        {Text:"15分钟",Value:6},
        {Text:"30分钟",Value:7},
        {Text:"60分钟",Value:8}
        // {
        //   Text: '日线-全部',
        //   Value: 0,
        //   Period: 0,
        //   noRightData: false,
        //   dateType: 'dayDate'
        // }
        
      ],
      dataNumOptions:[
        {label:"一周",value:7},
        {label:"一月",value:30},
        {label:"3月",value:90},
        {label:"半年",value:180},
        {label:"1年",value:365},
        {label:"3年",value:1095},
        {label:"6年",value:2190},
        {label:"全部",value:10000},
      ],
      dataNumOptionsMinute:[
        {label:"1天",value:1},
        {label:"2天",value:2},
        {label:"3天",value:3},
        {label:"4天",value:4},
        {label:"5天",value:5},
        {label:"半个月",value:15},
        {label:"1个月",value:30},
        {label:"3个月",value:90},
        {label:"全部",value:10000},
      ],
      filterDataNumOptions: [],
      dataNum: 180,
      rightsOptionsDisabled: false,
      RightOptions: ['不复权','前复权','后复权(简单)','后复权(完成)'],
      headerList: [],
      tableData: [],
      pageTableData: [],
      indexDataLoading: false,
      timer: null,
      isCodeHasError: false,
      oprType: '', //执行 或 保存
      storageIndexLists: [],
      explainArguments: [], //解析后的指标-参数name
      activeName: 'first' //执行，对话框中，tab选中
    }
  },
  components: {
    codemirror,
    CategoryList
  },
  watch: {
    'kLineChart.Period'(newValue){
      let value = newValue.Value
      if(value === 4 ||value === 5|| value === 6|| value === 7 || value===8) { //分钟
        this.rightsOptionsDisabled = true
        this.kLineChart.Right.Text = '不复权'
        this.kLineChart.Right.Value = 0

        this.filterDataNumOptions = [...this.dataNumOptionsMinute]
        this.dataNum = 4
      }else{
        this.rightsOptionsDisabled = false

        this.filterDataNumOptions = [...this.dataNumOptions]
        this.dataNum = 180
      }
    }
    // editableTabsValue: function(newValue){
    //   console.log('???',newValue);
    // }
  },
  computed: {
    filterCurrentList(){
      return this.CurrentList.filter(item => !item.delete)
    }
  },
  mounted() {

    const defaultLable = this.inputValue.name
    this.remoteMethod(defaultLable);//标签赋值前先调用远程搜索函数


    this.filterDataNumOptions = [...this.dataNumOptions]
    this.dataNum = 180

    this.kLineChart.Period = {...this.PeroidOptions[0]}

    this.storageIndexLists = localStorage.getItem('st_index_lists') ? JSON.parse(localStorage.getItem('st_index_lists')) : []

    window.onresize = debounce(() => {
      if(this.kLineChart.Chart){
        this.kLineChart.Chart.OnSize()
      }
    },1000)
  },
  methods: {
    remoteMethod(query){
      if (query !== '') {
        this.searchLoading = true;
        urlObj.post(urlObj.apiStockSearch, {key: query}, res => {
          this.searchLoading = false;
          this.resultOptions = res.data
        })
      } else {
        this.resultOptions = [];
      }
    },
    closeKlineDialog(){
      // debugger
      if (this.kLineChart.Chart) 
      {
          this.kLineChart.Chart.ChartDestory();    //停止定时器
          this.kLineChart.Chart=null;
      }
      this.ClearDivDOM()
      // this.kLineChart.Chart.JSChartContainer = null
      // this.kLineChart.Chart = null
    },
    ClearDivDOM()     
    {
      const klineDom = this.$refs.kline
        while (klineDom.hasChildNodes()) 
        {
            klineDom.removeChild(klineDom.lastChild);
        }　
    },
    currentChange(page){
      this.paginationObj.PageIndex = page

      // debugger
      // console.log(this.tableData);
      const start = (this.paginationObj.PageIndex - 1) * this.paginationObj.PageSize
      let end = (this.paginationObj.PageIndex * this.paginationObj.PageSize) > this.paginationObj.total ? 
                this.paginationObj.total : this.paginationObj.PageIndex * this.paginationObj.PageSize
      this.pageTableData = this.tableData.slice(start, end)

      this.$nextTick(() => { //table回到顶部
        this.$refs.klineDataTable.bodyWrapper.scrollTop = 0
      })
    },
    handleResultClick(tab, event) {
    },
    changePeriod(item){
      this.kLineChart.Period = item
      // this.kLineChart.Period.Text = item.Text
      // this.kLineChart.Period.Value = item.Value
      if(item.noRightData){
        this.kLineChart.isChangeRight = true
        this.kLineChart.Right.Text = '不复权'
        this.kLineChart.Right.Value = 0
      }else{
        this.kLineChart.isChangeRight = false
      }
    },
    changeRight(value){
      // debugger
      const Text = this.RightOptions[value]
      this.kLineChart.Right.Text = Text
      this.kLineChart.Right.Value = value
    },
    createKlineChart(indexData, data){
      console.log('createKlineChart');
      this.kLineChart.Chart=JSChart.Init(this.$refs.kline)
      this.OnSize();  //让K线全屏
      this.kLineChart.Option.KLine.Period = data.Period
      this.kLineChart.Option.KLine.Right = data.Right
      this.kLineChart.Option.Symbol = this.inputValue.symbol
      this.kLineChart.Option.NetworkFilter = this.NetworkFilter
      this.kLineChart.Option.Windows.splice(1,1,indexData)
      this.kLineChart.Chart.SetOption(this.kLineChart.Option);  //设置K线配置
    },
    indexRun(data){
      this.dialogVisible = true
      this.activeName = 'first'
      this.$nextTick(() => {
        const indexName = this.editableTabs[this.editableTabsValue - 1].title
        const indexData = {
          API:{Name:indexName,Script:data.Script, Args:data.Args, Url:urlObj.apiRun ,Version:2},
          Window:{ Close:false, Change:false, Overlay:true, Close:true}
        }
        if(this.kLineChart.Chart === null){
          this.createKlineChart(indexData, data)
        }
        // else{
        //   console.log('方法', this.kLineChart.Chart.OnSize);
        //   this.kLineChart.Chart.OnSize()
        //   const jSChartContainer = this.kLineChart.Chart.JSChartContainer
        //   if(jSChartContainer.Right !== this.kLineChart.Right.Value){
        //     this.kLineChart.Chart.ChangeRight(this.kLineChart.Right.Value);
        //   }
        //   if(jSChartContainer.Symbol !== this.inputValue.symobl){
        //     this.kLineChart.Chart.ChangeSymbol(this.inputValue.symobl);
        //   }
        //   this.kLineChart.Chart.ChangePeriod(this.kLineChart.Period.Period);
        //   this.kLineChart.Chart.ChangeIndex(1,indexName,indexData);
        // }
        
      })
    },
    OnSize()  //自适应大小调整
    {
        const widthPrecent = 0.6
        const paddingLeftRight = 20 * 2
        const kline = this.$refs.kline
        var height= 600
        var width = window.innerWidth * widthPrecent - paddingLeftRight
        kline.style.width=width+'px';
        kline.style.height=height+'px';
        console.log('宽高：', width);
        if(this.kLineChart.Chart){
          this.kLineChart.Chart.OnSize()
        }
        
    },
    changeStrategyName(categoryid, title){
      const target = find(this.editableTabs, item => item.category.categoryid ===categoryid)
      const index = findIndex(this.editableTabs, item => item.category.categoryid ===categoryid)
      if(!target) return false
      target.title = title
      this.editableTabs.splice(index, 1, target)
      // console.log('....',this.editableTabs);
    },
    deleteStrategy(categoryid) {
      //tabs直接删除即可
      const target = find(this.editableTabs, item => item.category.categoryid ===categoryid)
      if(!target) return false
      const targetName = target.name
      this.removeTab(targetName)
    },
    changeCategory(category, categoryid, from){
      if(from === 'elTab'){
        this.isCheckTab = true
      }else{
        this.isCheckTab = false
      }
      if(this.isCheckTab) return //仅是tab切换的时候不去请求接口
      this.loading = true
      Service.queryOneStrategyDetail(category, this.getStrategyDetail)
    },
    getStrategyDetail(category, res){ //获取选中策略的详情
      this.loading = false
      category.args = res.data.args ? res.data.args : []
      category.script = res.data.script
      let args = []
      //如果长度>=3,直接转换；否则，把有参数的替换，空参数列保留
      if(category.args.length >= 3){
        args = category.args.map(item => {
          let arg = DefaultData.GetListItem()
          arg.id = item.id
          arg.strategyId = item.strategyId
          arg.name.value = item.name
          arg.min.value = item.minVal
          arg.max.value = item.maxVal
          arg.value.value = item.defaultVal
          return arg
        })
      }else{
        args = DefaultData.GetListData()
        for (let i = 0; i < category.args.length; i++) {
          let arg = args[i]
          let item = category.args[i]
          arg.id = item.id
          arg.strategyId = item.strategyId
          arg.name.value = item.name
          arg.min.value = item.minVal
          arg.max.value = item.maxVal
          arg.value.value = item.defaultVal
        }
      }
      
      const position = findIndex(this.editableTabs, item => item.category.categoryid === category.categoryid)
      if(position === -1){
        this.addTab(this.editableTabsValue, category, args)
      }else{
        this.editableTabsValue = this.editableTabs[position].name
      }
      this.CurrentList = args
      this.CurrentCode = category.script
    },
    NetworkFilter(data, callback)
    {
        console.log('[NetworkFilter] data', data);
        switch(data.Name)
        {
            case 'APIScriptIndex::ExecuteScript':
                this.ExecuteScript(data, callback);
                break;

            case 'KLineChartContainer::RequestHistoryData':                 //日线全量数据下载
                this.RequestHistoryData(data,callback);
                break;

            case 'KLineChartContainer::RequestFlowCapitalData':             //流通股本
                this.RequestFlowCapitalData(data,callback);
                break;

            
            // case "KLineChartContainer::RequestRealtimeData": //日线增量
            //   this.GetRealKlineData(data, callback);
            //   break;
            // case 'KLineChartContainer::RequestDragDayData': //日K线拖拽自动下载历史数据
            //   this.GetDragDayData(data, callback)
            //   break;

            case "KLineChartContainer::ReqeustHistoryMinuteData":
              this.GetHistoryMinuteData(data, callback);
              break;
            // case "KLineChartContainer::RequestMinuteRealtimeData":
            //   this.GetRealMinuteData(data, callback);
            //   break;
            // case 'KLineChartContainer::RequestDragMinuteData': //分钟K线拖拽自动下载历史数据
            //   this.getDragMinuteData(data,callback)
            //   break;

            // case 'MinuteChartContainer::RequestMinuteData': //最新分时图
            //   this.getMinuteData(data,callback)
            //   break;

            // case "JSSymbolData::GetSymbolPeriodData":  //跨周期数据
            //   GetSymbolPeriodData(data, callback);
            //   break;
            // case "JSSymbolData::GetFinanceData": //财务数据
            //   GetFinanceData(data, callback);
            //   break;
        }
    },
    GetHistoryMinuteData(data, callback){
      data.PreventDefault=true;
      var self=this;
      var symbol=data.Request.Data.symbol;
      var period=data.Request.Data.period;
      var right=data.Request.Data.right;
      var dayCount=data.Self.MaxReqeustDataCount;
      var url=urlObj.apiMinuteKLine;

      const {StartDate,EndDate} = this.getRunDateRange()
      var postData={ Right:right, Period:period, Symbol:symbol,StartDate,EndDate };
      // if(this.kLineChart.Period.dateType === 'minuteDate'){
      //   const dateRange = this.getRunDateRange()
      //   if(dateRange.StartDate && dateRange.EndDate){
      //     postData.StartDate = dateRange.StartDate
      //     postData.EndDate = dateRange.EndDate
      //   }
      // }

      urlObj.post(url, postData, recvData => {
        this.RecvMinuteHistoryData(recvData, data, callback);
      })
    },
    RecvMinuteHistoryData (recvData, data, callback){
      if(recvData.data.length === 0){
        this.$message('暂无该时间段数据')
      }
      var hqChartData=recvData
      console.log("[KLineChart::RecvHistoryMinuteData] hqChartData", hqChartData);
      callback(hqChartData);
    },
    ExecuteScript(data,callback) //执行计算指标
    {
        data.PreventDefault=true;

        var symobl=data.Request.Data.symbol;
        var period=data.Request.Data.period;
        var right=data.Request.Data.right;
        var script=data.Request.Data.script;
        // var dateRange=data.Request.Data.DateRange;
        var args=data.Request.Data.args;

        // debugger
        
        var url=urlObj.apiRun;
        var postData=
        {  
            Symbol:symobl,        //股票代码
            Script:script,        //脚本
            Period:period,        //周期
            Right:right,          //复权
            Args:[]
        };
        if (args && Array.isArray(args)) 
        {
            for(var i=0;i<args.length;++i)
            {
                var item=args[i];
                postData.Args.push({ Name:item.name, Value:item.value });
            }
        }
        const dateRange2 = this.getRunDateRange()
        if(dateRange2.StartDate && dateRange2.EndDate){
          postData.StartDate = dateRange2.StartDate
          postData.EndDate = dateRange2.EndDate
        }
                
        urlObj.post(url, postData, recvData => {
          this.RecvExecuteScript(recvData, callback, period);
        })
        
    },
    RecvExecuteScript(recvData, callback, period)
    {
        if (recvData.Code!=0)
        {
            this.$message.error(recvData.Error);
            return ;
        }
        const isMinuteKLinePeriod = period > 3 ? true : false
        let OutVar = recvData.OutVar.filter(item => item.Type === 0 && item.Data)
        recvData.OutVar = OutVar
        //整理表头
        this.headerList = OutVar.map((item, index) => ({
          prop: item.Name,
          label: item.Name,
          width: index === OutVar.length - 1 ? '':'180',
          align: 'right'
        }))
        if(isMinuteKLinePeriod){
          this.headerList.unshift({
            prop: 'Time',
            label: '时间',
            width: '180',
            align: 'left'
          })
        }
        this.headerList.unshift({
          prop: 'Date',
          label: '日期',
          width: '180',
          align: 'left'
        })
        //整理内容
        const colsProps = isMinuteKLinePeriod ? ['Date', 'Time'] : ['Date']
        OutVar.forEach(item => {
          colsProps.push(item.Name)
        })

        this.tableData.splice(0, this.tableData.length) //清空数组
        recvData.Date.forEach((item, index) => {
          const rowData = {}
          colsProps.forEach(propName => {
            if(!isMinuteKLinePeriod){ //日线
              if(propName === 'Date'){
                rowData[propName] = recvData.Date[index]
              }else{
                rowData[propName] = find(OutVar, {Name: propName}).Data[index] ? Number(find(OutVar, {Name: propName}).Data[index]).toFixed(2) : '--'
              }
            }else{ //分钟k线
              // debugger
              if(propName === 'Date'){
                rowData[propName] = recvData.Date[index]
              }else if(propName === 'Time'){
                rowData[propName] = StockStringFormat.FormatTimeString(recvData.Time[index])
              }else{
                rowData[propName] = find(OutVar, {Name: propName}).Data[index] ? Number(find(OutVar, {Name: propName}).Data[index]).toFixed(2) : '--'
              }
            }
            
          })

          this.tableData.push(rowData)
          
        })
        this.tableData = this.tableData.reverse()
        this.paginationObj.total = this.tableData.length
        const start = (this.paginationObj.PageIndex - 1) * this.paginationObj.PageSize
        let end = (this.paginationObj.PageIndex * this.paginationObj.PageSize) > this.paginationObj.total ? 
                  this.paginationObj.total : this.paginationObj.PageIndex * this.paginationObj.PageSize
        this.pageTableData = this.tableData.slice(start, end)
        console.log('[NetworkFilter::RecvExecuteScript] data ', recvData);
        callback(recvData);
    },
    RequestHistoryData(data,callback)
    {
        data.PreventDefault=true;
        var self=this;
        var symbol=data.Request.Data.symbol;
        var period=data.Request.Data.period;
        var right=data.Request.Data.right;
        var dayCount=data.Self.MaxReqeustDataCount;
        var url=urlObj.apiDayKLine;

        const {StartDate,EndDate} = this.getRunDateRange()
        var postData={ Right:right, Period:period, Symbol:symbol,StartDate,EndDate };
        // if(this.kLineChart.Period.dateType === 'dayDate'){
        //   const dateRange = this.getRunDateRange()
        //   if(dateRange.StartDate && dateRange.EndDate){
        //     postData.StartDate = dateRange.StartDate
        //     postData.EndDate = dateRange.EndDate
        //   }
        // }
        urlObj.post(url, postData, recvData => {
          this.RecvHistoryData(recvData, data, callback);
        })
    },
    getRunDateRange(){
      const EndDate = parseInt(moment().format('YYYYMMDD'))
      const dayCount = this.dataNum
      const StartDate = parseInt(moment().subtract(dayCount,'days').format('YYYYMMDD')) ;//xx天前
      return {
        StartDate,
        EndDate
      }
    },
    RecvHistoryData(recvData, data, callback)   //接收历史分钟数据
    {
      if(recvData.data.length === 0){
        this.$message('暂无该时间段数据')
      }
        var hqChartData=recvData
        console.log("[KLineChart::RecvHistoryData] hqChartData", hqChartData);
        callback(hqChartData);
    },
    RequestFlowCapitalData(data,callback)
    {
        data.PreventDefault=true;
        var hqChartData={code:0, stock:[]}; //如果没有数据就填空
        callback(hqChartData);
    },
    exec() {
      var args = this.filterCurrentList.filter(item => item.name.value !== '')
      args = args.map(item => ({
        "Name": item.name.value,
        "Value": Number(item.value.value)
      }))
      const data = {
        "Symbol": this.inputValue.symbol,
        "Script": this.CurrentCode, //"T:MA(C,M1);\nT2:MA(C,M2);"
        "Period": this.kLineChart.Period.Value,
        "Right": this.kLineChart.Right.Value,
        "Args": args
      }
      // debugger
      this.indexRun(data)
    },
    beforeExecCheck(){
      //1.指标脚本不能为空
      if(this.CurrentCode === ''){
        this.$message('请填写指标脚本')
        return false
      }
      //2.仅执行指标时，判断是否填了股票代码
      if(this.oprType === 'exec' && this.inputValue.symbol.length < 9){
        this.$message('请输入完整的股票代码')
        return false
      }

      //3.参数名或者参数值，一个为空，一个有值时，提示
      let nameValue = false
      this.CurrentList.forEach(item => {
        if((item.name.value && !item.value.value) || (!item.name.value && item.value.value)){
          nameValue = true
          return
        }
      })
      if(nameValue) {
        this.$message('请将参数填写完整')
        return false
      }

      return true
    },
    preExecOrSave(oprType){
      this.oprType = oprType
      //1.基础检查 2.通达信语法检测
      if(!this.beforeExecCheck()) return
      this.explainScript(this.CurrentCode)
    },
    checkArgDelete(arg){ //判断是否是被删除的参数
      //1.明确是需要删除的，不做其他判断
      if(arg.delete) return true 
      //2.id存在，并且名称和值都是空
      if(arg.id && !arg.name.value && !arg.value.value){
        return true
      }
      return false
    },
    getNewArgsForApi(category){
      const args = []
      for (let i = 0; i < this.CurrentList.length; i++) {
        const arg = this.CurrentList[i];
        let queryItem = {
          "defaultVal": parseInt(arg.value.value),
          "id": arg.id > -1 ? arg.id : undefined,
          "maxVal": arg.max.value == '' ? null: parseInt(arg.max.value),
          "minVal": arg.min.value == '' ? null: parseInt(arg.min.value),
          "name": arg.name.value,
          "strategyId": category.categoryid,
          "delete": this.checkArgDelete(arg)
        }
        args.push(queryItem)
      }
      return args
    },
    save() { //保存按钮时统一修改策略
      const {category} = find(this.editableTabs, {name: this.editableTabsValue})
      let newData = {
        args: [],
        script: ''
      }
      newData.args = this.getNewArgsForApi(category)
      //将修改后的脚本更新到category里面
      newData.script = this.CurrentCode
      this.updateOneStrategy(category, newData, this, null, this.explainArguments)
    },
    updateOneStrategy(category, newData, vueC, callback, explainArguments){ //explainArguments - 通达信语法解析出来的
      let needNOticeParent = false
      if(vueC && vueC.text && category.name !== vueC.text) needNOticeParent = true
      const data = {
        "outArgs": explainArguments || [],
        "args": newData ? (newData.args ? newData.args : category.args) : category.args,
        "description": "",
        "floatPrecision": "0",
        "id": category.categoryid,
        "isMainIndex": false,
        "name": vueC ? ( vueC.text ? vueC.text : category.name) : category.name,
        "script": newData ? (newData.script ? newData.script : category.script) : category.script,
      }
      urlObj.post(`${urlObj.apiStrategyOpr}${category.categoryid}`, data, res => {
        if(res.code === 200){
          //保存指标到缓存
          data.args = res.data.args
          const idx = findIndex(this.storageIndexLists, {id: data.id})
          if(idx === -1){
            this.storageIndexLists.push(data)
          }else{
            this.storageIndexLists.splice(idx, 1, data)
          }
          localStorage.setItem('st_index_lists', JSON.stringify(this.storageIndexLists))

          //修改数样式
          category.name = res.data.name
          category.args = res.data.args
          category.script = res.data.script
          category.editing = false
          
          if(needNOticeParent && vueC.$el.className === 'category-wrap') { //必须是子组件
            vueC.$emit('changeStrategyName', category.categoryid, vueC.text)
          }
          
          if(vueC && vueC.sending) vueC.sending = false
          if(vueC && vueC.text) vueC.text = ''  //除了数组件，有可能其他组件也有text，注意不能取相似的名字
          //可能需要切换选中
          if(callback) callback([category.groupId, category.categoryid])
          vueC.$message('修改成功')

          this.getCurrentList(res.data.args)
        }else{
          vueC.$message('修改失败')
        }
      })
    },
    getCurrentList(apiArgs){ //获取页面展示的参数列表
      let args = []
      if(apiArgs.length <= 3){
        args = DefaultData.GetListData()
        for (let i = 0; i < apiArgs.length; i++) {
          let arg = args[i]
          let item = apiArgs[i]
          arg.id = item.id
          arg.strategyId = item.strategyId
          arg.name.value = item.name
          arg.min.value = item.minVal
          arg.max.value = item.maxVal
          arg.value.value = item.defaultVal
        }
      }else{
        for (let i = 0; i < apiArgs.length; i++) {
          let item = apiArgs[i]
          args.push({
            id:item.id,
            strategyId:item.strategyId,
            name: {
              value:item.name
            },
            min: {
              value:item.minVal
            },
            max: {
              value:item.maxVal
            },
            value: {
              value:item.defaultVal
            },
            delete: false
          })
        }
      }
      
      this.CurrentList = args
    },
    // deleteFun() {
    //   console.log('deleteFun');
    // },
    addRow () {
      const item = DefaultData.GetListItem()
      this.CurrentList.push(item)
    },
    explainScript(scriptStr){
      // scriptStr="T:MA(C,10);" //测试
      const JSComplier = HQChart.Chart.JSComplier
      const list = this.filterCurrentList.filter(item => item.name.value !== '')
      const args = list.map(item => ({
        Name: item.name.value,
        Value: item.value.value
      }))
      // debugger
      const option = {
        Arguments: args,
        Callback: this.explainScriptCallback
      }
      JSComplier.Explain(scriptStr, option, this.explainScriptErrorCallback)
    },
    explainScriptCallback(data){
      console.log("[Explain] data ", data);
      const newData = data.filter(item => item.Type === 0 && item.IsOut !== false)
      this.explainArguments = newData.map(item => item.Name)
      for(var i in data)
      {
          var item=data[i];	//每一句翻译好的语句
          
      }
      // console.log('显示的参数::', this.explainArguments);
      console.log("语法正确")
      this.isCodeHasError = false

      switch(this.oprType){
        case "exec":
          this.exec()
          break;
        case "save":
          this.save()
          break;
      }
    },
    explainScriptErrorCallback(error, data){
      console.log("[Explain] error, data ", error, data);
      this.$message.error(`语法错误: 行号:${error.LineNumber}, ${error.Description}`)
      this.isCodeHasError = true
    },
    deleteRow(rowIndex) {
      let row = this.CurrentList[rowIndex]
      row.delete = true
      this.CurrentList.splice(rowIndex, 1, row)
    },
    addTab(targetName, category, args) {
      let newTabName = ++this.tabIndex + '';
      this.editableTabs.push({
        title: category.name,
        name: newTabName,
        list: args,
        code: category.script,
        category
      });
      this.editableTabsValue = newTabName;
    },
    handleTabClick(tab, event){
      this.isCheckTab = true

      const paneName = tab.paneName
      const tabData = find(this.editableTabs, item => item.name === paneName)
      this.CurrentList = tabData.list
      this.CurrentCode = tabData.code

      this.$refs.categorylist.checkCategory([tabData.category.groupId, tabData.category.categoryid], 'elTab')
    },
    removeTab(targetName) {
      let tabs = this.editableTabs;
      let activeName = this.editableTabsValue;
      if (activeName === targetName) {
        tabs.forEach((tab, index) => {
          if (tab.name === targetName) {
            let nextTab = tabs[index + 1] || tabs[index - 1];
            if (nextTab) {
              activeName = nextTab.name;
            }
          }
        });
      }
      
      this.editableTabsValue = activeName;
      this.editableTabs = tabs.filter(tab => tab.name !== targetName);

      // console.log('@@@',this.editableTabsValue);
      if(this.editableTabs.length > 0){
        const tab = find(this.editableTabs, item => item.name === this.editableTabsValue)
        this.CurrentList = tab.list
        this.CurrentCode = tab.code
        this.$refs.categorylist.checkCategory([tab.category.groupId, tab.category.categoryid], 'elTab')
      }else{
        this.$refs.categorylist.checkCategory()
      }
    },
  }
}
</script>

<style lang="less">
@import '../../../assets/css/commonStyle.less';

.elTabsRun{
  margin-top: -30px;
}

.kline{
  width: 100%;
  position: relative;
}

.tableWrapInDialog{
  height: 600px;

  .paginationWrapInDialog{
    width: 100%;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.indexEditWrap{
  width: 100%;
  height: 100%;
  position: relative;

  .el-dialog__footer{
    padding: 0;
  }

  @leftWidth: 240px;

  .left,
  .right{
    position: absolute;
    top: 0;
    height: 100%;
    box-sizing: border-box;
  }

  .left{
    left: 0;
    width: @leftWidth;
    border-right: @contentBorder;
    overflow-y: auto;
    overflow-x: hidden;

    .el-menu {
      border-right: none;
      min-height: 100%;

      .el-menu-item, .el-submenu__title {
        height: 33px;
        line-height: 33px;
      }
    }
  }
  .right{
    left: @leftWidth;
    width: calc(100% - @leftWidth);

    .rightContentWrap{
      height: 100%;

      .spaceBox{
        width: 100%;
        height: 7px;
        background-color: #f7f8f9;
      }

      // .el-tabs{
      //   height: calc(100% - 7px);
      // }
      // .el-tabs__content {
      //   height: calc(100% - 31px - 15px);
        
      //   .el-tab-pane{
      //     height: 100%;
      //   }
      // }

      .el-tabs--card>.el-tabs__header {
        border-bottom: @contentBorder;
        background-color: #f7f8f9;
      }

      .el-tabs--card>.el-tabs__header .el-tabs__item {
        height: 30px;
        line-height: 30px;
      }

      .el-tabs--card>.el-tabs__header .el-tabs__item.is-active {
        border-bottom-color: @contentBorder;
        background-color: #fff;
      }

      .commonTabContentWrap{
        height: calc(100% - 7px - 31px - 15px);
        // background-color: coral;
        @editWrapHeight: 342px;

        .editorWrap{
          display: flex;
          padding: 0 10px;
          height: @editWrapHeight;

          @selectInfoWrapHeight: 84px;
          .selectInfoWrap{
            height: @selectInfoWrapHeight;

            .oneLineWrap{
              width: 100%;
              height: 42px;
              display: flex;
              align-items: center;

              .timeRange,
              .labelSymbol{
                padding-left: 55px;
              }

              .el-input{
                width: 100px;
                // display: inl;
              }

              .el-select {
                .el-input{
                  width: 140px;
                  // display: inl;
                }
              }
            }
          }

          .paramsEditWrap{
            width:592px;
            height: calc(100% - @selectInfoWrapHeight);
            box-sizing: border-box;
            background-color: #f7f8f9;
            overflow-y: auto;
            border: @contentBorder;
            /* padding-left: 7px;
            padding-bottom: 16px; */

            .editTable{
              width: 100%;
              border-spacing: 0;
              border: none;
              border-collapse: collapse;

              .noData{
                text-align: center;
                padding-top: 40px;
              }
              
              .strongFont{
                font-weight: bold;
              }

              tr>td:nth-child(1),
              tr>td:nth-child(2),
              tr>td:nth-child(3),
              tr>td:nth-child(4){
                width: 107px;
              }
              // td{
              //   border: @contentBorder;
              // }

              thead td{
                line-height: 32px;
                text-align: center;
              }

              .box{
                // width: 100%;
                padding: 5px;
                height: 35px;
                text-align: center;
                box-sizing: border-box;

                input[type='text']{
                  width: 78px;
                  box-sizing: border-box;
                  height: 100%;
                  border: @contentBorder;
                  outline: none;
                  text-align: center;
                  vertical-align: top;

                  &:focus{
                    border: solid 1px #2196f3;
                  }
                }
              }
              
            }

            .addBtn{
              cursor: pointer;
              width: 26px;
              height: 26px;
              line-height: 26px;
              text-align: center;
              background-color: #efefef;
              border-radius: 3px;
              border: solid 1px #dcdcdc;
              margin-left: 10px;

              .el-icon-plus{
                font-weight: 700;
                color: #666;
                font-size: 23px;
              }
            }
          }

          .paramsBtnsWrap{
            height: 42px;
            display: flex;
            padding-left: 22px;
            align-items: center;
            // padding-top: 8px;
          }
          
        }

        .codeWrap{
          height: calc(100% - @editWrapHeight);
          padding: 10px;
          box-sizing: border-box;
          h3{
            height: 18px;
            line-height: 18px;
            padding-top: 5px;
            padding-bottom: 15px;
          }
          .code {
            height: calc(100% - 18px - 20px);
            border: @contentBorder;
            box-sizing: border-box;

              .vue-codemirror{
                height: 100%;
              }
              .CodeMirror{
                height: 100%;
                // font-family: monospace;
              }
          }
        }
      }

      .commonTabContentWrap + .noData{
        padding-top: 100px;
        color: #666;
        text-align: center;
      }
      
    }
  }
}

</style>
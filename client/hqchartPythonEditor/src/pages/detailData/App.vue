<template>
  <div class="detailDataWrap">
    <div class="symbolWrap" ref='symbolWrap' v-if="dataType !== 3">
      <div class="top">
        <div class="searchWrap">
          <!-- <el-button type="primary" size="small" v-if="!isShowStockSearch" @click="showStockSearchFun">股票查询</el-button> -->
          <StockSearch
            :isShowBtn='false'
            :noPadding='true'
            btnText='确定'
            @addSymbol='addSymbol'
          ></StockSearch>
        </div>
        <div class="datePickerWrap" v-if="dataType === 2">
          <el-date-picker
            v-model="valueDate1"
            format='yyyy-MM-dd'
            value-format='yyyyMMdd'
            size="small"
            type="date"
            @change='changeDate'
            placeholder="选择日期">
          </el-date-picker>
        </div>
        
      </div>
      <div class="bottom">
        <div class="symbolInfo">
          <div class="symbol">{{oprStockObj.symbol}}</div>
          <div class="name">{{oprStockObj.name}}</div>
        </div>
        <div class="dateInfoWrap" v-if="dataType === 2 || dataType === 1">
          <span>数据开始日期：{{kLineSummaryInfo.startDate}}</span>&emsp;<span>数据截止日期：{{kLineSummaryInfo.endDate}}</span>
        </div>
        <div class="countsWrap" v-if="dataType === 2 || dataType === 1">
          <span>共{{kLineSummaryInfo.counts}}条数据</span>
        </div>
      </div>
      
    </div>
    <div class="mainWrap" ref="mainWrap" v-loading='loading'>
      <div class="tableWrap" v-if="dataType !== 4 && dataType !== 3 && dataType !== 5">
        <el-table
          class="resultTable"
          ref="resultTable"
          :data="pageTableData"
          size='medium'
          style="width: 100%;height:100%"
          height="100%"
          >
          <el-table-column
            v-for="(col, indexCol) in resultTableHeader"
            :key="indexCol"
            :prop="col.prop"
            :label="col.label"
            :sortable='col.sortable'
            :width="col.width"
            :align="col.align"
            :class-name="col.className"
            :label-class-name="col.labelClassName"
            >
          </el-table-column>
        </el-table>
      </div>
      <div class="paginationWrap" v-if="dataType !== 4 && dataType !== 3 && dataType !== 5">
        <el-pagination
          background
          :page-size='paginationObj.PageSize'
          layout="prev, pager, next"
          :total="paginationObj.total"
          @current-change='currentChange'
        >
        </el-pagination>
      </div>

      <MultiLabletable v-if="dataType === 4" :symbol='oprStockObj.symbol'></MultiLabletable>
      <MultiColTable v-if="dataType === 3 || dataType === 5" :symbol='oprStockObj.symbol' :apiDataType='dataType'></MultiColTable>
    </div>
  </div>
</template>

<script>
import StockSearch from '../../components/stockSearch.vue'
import MultiLabletable from '../../components/multiLabletable.vue'
import MultiColTable from '../../components/multiColTable.vue'
import { getURLParams } from '../../utils/tools'
import urlObj from '../../utils/urlObj'
import {find, findIndex} from 'lodash'
// import moment from 'moment'

export default {
  components: {
    MultiLabletable,
    MultiColTable,
    StockSearch
  },
  data () {
    return {
      loading: false,
      oprStockObj: {
        name: "浦发银行",
        symbol: "600000.sh",
        type: "EQA"
      },
      klineDataFromApi: [ //api数据结构说明，不会用到页面数据显示
        {
          idName: 'DATE_ID ',
          Text: '日期',
          index: 0
        },
        {
          idName: 'YCLOSE_ID ',
          Text: '昨日收盘价',
          index: 1
        },
        {
          idName: 'OPEN_ID ',
          Text: '开盘价',
          index: 2
        },
        {
          idName: 'HIGH_ID ',
          Text: '最高价',
          index: 3
        },
        {
          idName: 'LOW_ID ',
          Text: '最低价',
          index: 4
        },
        {
          idName: 'CLOSE_ID ',
          Text: '收盘价',
          index: 5
        },
        {
          idName: 'VOL_ID ',
          Text: '成交量',
          index: 6
        },
        {
          idName: 'AMOUNT_ID  ',
          Text: '成交额',
          index: 7
        },
        // {
        //   idName: 'TIME_ID ', //1分钟才有的字段
        //   Text: '日期',
        //   index: 8
        // }
      ],
      isShowStockSearch: false,
      pageTableData: [],
      resultTableData: [],
      filterResultTableData: [],
      resultTableHeader: [],
      paginationObj: { //表格分页
        total: 1,
        PageSize: 30,
        PageIndex: 1
      },
      valueDate1: '', //日期
      kLineSummaryInfo: {
        startDate: '--',
        endDate: '--',
        counts: 0
      },
      dataType: 1 //对应url上的type
    }
  },
  mounted(){
    this.dataType = getURLParams('type') ? parseInt(getURLParams('type')) : 1
    this.queryApiData()
    
    if(this.dataType === 3){ //码表需要隐藏头部，重新计算表格高度
      this.onSize()
    }
  },

  methods: {
    onSize(){
      const mainWrap = this.$refs.mainWrap
      const height = window.innerHeight
      mainWrap.style.height = height + 'px'
    },
    getKLineSummaryInfo(resultData){
      if(resultData.length > 0){
        this.kLineSummaryInfo.startDate = resultData[0][0]
        this.kLineSummaryInfo.endDate = resultData[resultData.length - 1][0]
        this.kLineSummaryInfo.counts = resultData.length
      }else{
        this.kLineSummaryInfo.startDate = '--'
        this.kLineSummaryInfo.endDate = '--'
        this.kLineSummaryInfo.counts = 0
      }
    },
    changeDate(){
      this.filterResultTableData = this.getFilterResultTableData()
      //初始化分页数据
      this.initPaginationData()
      // this.getMinuteKLineData(date, date)
      // console.log('选择日期', );
    },
    queryApiData(){ //获取数据
      switch(this.dataType) {
        case 1:  //日K数据
          this.getDayKLineData()
          break;
        case 2:   //分钟K数据
          this.getMinuteKLineData()
          break;
        case 3:   //码表数据
          // this.getCodeListData()
          break;
        case 4:   //财务数据，放到插件里面处理
          break;
        case 5:   //股本数据
          // this.getCapitalData()
          break;
      }
    },
    addSymbol(inputValue){
      this.oprStockObj = inputValue

      this.isShowStockSearch = false

      //重新获取相应数据，k线数据，财务数据，股本数据
      if(this.dataType !== 3){
        this.queryApiData()
      }

    },
    showStockSearchFun(){
      this.isShowStockSearch = true
    },
    // getCapitalData(){
    //   this.loading = true
    //   urlObj.get(`${urlObj.apiStockCapital}?symbol=${this.oprStockObj.symbol}`, {}, res => {
    //     this.loading = false
    //     const {data, metainfo} = res
    //     this.resultTableHeader = this.getCapitalTableHeader(data, metainfo)
    //     this.resultTableData = this.getCapitalTableData(data)

    //     //初始化分页数据
    //     this.initPaginationData()
    //   }, res => {
    //     this.loading = false
    //     this.$message('接口状态异常')
    //   })

      
    // },
    // getCapitalTableHeader(data, metainfo){
    //   metainfo.Date = '日期' //手动加上
    //   const keysAry = [...Object.keys(data)]
    //   const header = []
    //   keysAry.forEach(key => {
    //     header.push({
    //       prop: key,
    //       label: metainfo[key],
    //       sortable: true,
    //       width: key !== 'Date' ? 280 : 100,
    //       align: key !== 'Date' ? 'right' : 'left'
    //     })
    //   })

    //   return header
    // },
    // getCapitalTableData(data){
    //   const len = data.Date.length
    //   const keysAry = [...Object.keys(data)]
    //   const tableData = []
    //   for (let index = 0; index < len; index++) {
    //     let tableRow = {}
    //     for (let j = 0; j < keysAry.length; j++) {
    //       const keyName = keysAry[j];
    //       tableRow[keyName] = keyName !== 'Date' ? Number(data[keyName][index]).toFixed(2) : data[keyName][index]
    //     }
    //     tableData.push(tableRow)
    //   }

    //   return tableData
    // },
    // getCodeListData(){
    //   this.loading = true
    //   urlObj.get(urlObj.apiStockSymbollist, {}, res => {
    //     this.loading = false
    //     const resultData = res.data
    //     this.resultTableHeader = this.getCodeLisHeader()
    //     this.resultTableData = resultData

    //     //初始化分页数据
    //     this.initPaginationData()
    //   }, res => {
    //     this.loading = false
    //     this.$message('接口状态异常')
    //   })

      
    // },
    // getCodeLisHeader(){
    //   let header = [
    //     {
    //       prop: 'symbol',
    //       label: '证券代码',
    //       sortable: true,
    //       align: 'left',
    //       width: 120
    //     },
    //     {
    //       prop: 'name',
    //       label: '证券名称',
    //       align: 'left',
    //       width: 120
    //     }
    //   ]
    //   return header
    // },
    getMinuteKLineData(StartDate, EndDate){
      this.loading = true
      const data = {
        "Right": 0,
        "Period": 4, 
        "Symbol": this.oprStockObj.symbol
      }
      urlObj.post(urlObj.apiMinuteKLine, data, res => {
        try {
          this.loading = false
          const resultData = res.data
          this.resultTableHeader = this.getKlineTableHeader('minute')
          this.resultTableData = this.getKlineTableData(resultData).reverse()
          this.filterResultTableData = this.getFilterResultTableData()

          //获取总结数据
          this.getKLineSummaryInfo(resultData)

          //初始化分页数据
          this.initPaginationData()
        } catch (error) {
          this.$message(error.message)
        }
       
      }, res => {
        this.loading = false
        this.$message('接口状态异常')
      })

      
    },
    getDayKLineData(){
      this.loading = true
      const data = {
        "Right": 0,
        "Period": 0, 
        "Symbol": this.oprStockObj.symbol,
      }
      urlObj.post(urlObj.apiDayKLine, data, res => {
        try {
          this.loading = false
          const resultData = res.data
          this.resultTableHeader = this.getKlineTableHeader()
          this.resultTableData = this.getKlineTableData(resultData).reverse()
          this.filterResultTableData = this.getFilterResultTableData()
          //获取总结数据
          this.getKLineSummaryInfo(resultData)
          //初始化分页数据
          this.initPaginationData()
        } catch (error) {
          this.$message(error.message)  
        }
      }, res => {
        this.loading = false
        this.$message('接口状态异常')
      })
      
      
    },
    getFilterResultTableData(){
      if(this.valueDate1 === '') return this.resultTableData

      const date = parseInt(this.valueDate1)
      const filterResultTableData = this.resultTableData.filter(item => item.date === date)
      return filterResultTableData || []
    },
    initPaginationData(){ //初始化分页数据
      this.paginationObj.total = this.filterResultTableData.length
      this.paginationObj.PageIndex = 1
      const {PageIndex, total, PageSize} = this.paginationObj
      const start = (PageIndex - 1) * PageSize
      let end = (PageIndex * PageSize) > total ? 
                total : PageIndex * PageSize
      this.pageTableData = this.filterResultTableData.slice(start, end)

      this.$nextTick(() => {
        if(this.$refs.resultTable) {
          this.$refs.resultTable.doLayout()
        }
      })
    },
    getKlineTableHeader(type){ //type 表示是日线还是1分钟
      let header = [
        {
          prop: 'date',
          label: '日期',
          sortable: true,
          width: 90,
          align: 'left'
        },
        {
          prop: 'yClose',
          label: '昨日收盘价',
          sortable: true,
          width: 120,
          align: 'right'
        },
        {
          prop: 'open',
          label: '开盘价',
          sortable: true,
          width: 100,
          align: 'right'
        },
        {
          prop: 'high',
          label: '最高价',
          sortable: true,
          width: 100,
          align: 'right'
        },
        {
          prop: 'low',
          label: '最低价',
          sortable: true,
          width: 100,
          align: 'right'
        },
        {
          prop: 'close',
          label: '收盘价',
          sortable: true,
          width: 100,
          align: 'right'
        },
        {
          prop: 'vol',
          label: '成交量',
          sortable: true,
          width: 160,
          align: 'right'
        },
        {
          prop: 'amount',
          label: '成交额',
          sortable: true,
          width: 160,
          align: 'right'
        },
      ]

      if(type === 'minute'){
        const timeHeder = {
          prop: 'time',
          label: '时间',
          sortable: true,
          width: 130,
          align: 'left',
          className: "timeCol",
          labelClassName: "timeCol"
        }
        header.splice(1, 0, timeHeder)
      }

      return header
    },
    getKlineTableData(data){
      let tableData = []
      if(data && data.length > 0) {
        tableData = data.map(values => {
          if(values.length === 8){ //日线
            return {
              date: values[0],
              yClose: Number(values[1]).toFixed(2),
              open:  Number(values[2]).toFixed(2),
              high:  Number(values[3]).toFixed(2),
              low:  Number(values[4]).toFixed(2),
              close:  Number(values[5]).toFixed(2),
              vol:  Number(values[6]).toFixed(2),
              amount:  Number(values[7]).toFixed(2),
            }
          }else if(values.length === 9){ //1分钟
            return {
              date: values[0],
              yClose: Number(values[1]).toFixed(2),
              open:  Number(values[2]).toFixed(2),
              high:  Number(values[3]).toFixed(2),
              low:  Number(values[4]).toFixed(2),
              close:  Number(values[5]).toFixed(2),
              vol:  Number(values[6]).toFixed(2),
              amount:  Number(values[7]).toFixed(2),
              time: values[8]
            }
          }

          return {}
        })
      }

      return tableData
    },
    currentChange(page){ //点击分页
      this.paginationObj.PageIndex = page

      const {PageIndex, total, PageSize} = this.paginationObj
      const start = (PageIndex - 1) * PageSize
      let end = (PageIndex * PageSize) > total ? 
                total : PageIndex * PageSize
      this.pageTableData = this.filterResultTableData.slice(start, end)

      this.$nextTick(() => { //table回到顶部
        this.$refs.resultTable.bodyWrapper.scrollTop = 0
      })
    },
  }
}
</script>

<style lang="less">
.detailDataWrap{
  width: 100%;
  height: 100%;
  color: #606266;

  .symbolWrap{
    height: 80px;
    box-sizing: border-box;
    padding: 0 15px;
    // border-bottom: 1px solid #EBEEF5;

    .top,
    .bottom{
      height: 40px;
      box-sizing: border-box;
      display: flex;
    }

    .symbol,
    .name{
      line-height: 40px;
    }

    .name {
      padding-left: 15px;
    }

    .searchWrap,
    .datePickerWrap,
    .symbolInfo,
    .dateInfoWrap,
    .countsWrap{
      height: 100%;
      box-sizing: border-box;
      display: flex;
      align-items: center;
    }

    .datePickerWrap,
    .countsWrap
    {
      padding-left: 15px;
    }
    .dateInfoWrap{
      padding-left: 20px;
    }
  }

  .mainWrap{
    width: 100%;
    height: calc(100% - 80px);

    .tableWrap{
      width: 100%;
      height: calc(100% - 50px);

      .resultTable {
        th {
          padding: 0 !important;
          height: 30px;
          line-height: 30px;
          &.timeCol{
            padding-left: 55px !important;
          }
        }
        td {
          padding: 0 !important;
          height: 30px;
          line-height: 30px;
          &.timeCol{
            padding-left: 55px !important;
          }
        }
      }
    }

    .paginationWrap{
      width: 100%;
      height: 50px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}
</style>
<template>
  <div class="strategyEditWrap" ref="strategyEditWrap">
    <div class="left">
      <category-list ref="categorylist"
        parentCompName='strategyEdit'
        @changeCategory='changeCategory'
        @delStockStrategy='delStockStrategy'
        @changeStrategyName='changeStrategyName'
        @addStockStrategy='addStockStrategy'
        @addStockStrategyGroup='addStockStrategyGroup'
        @editChildNode='editChildNode'
        @editParentNode='editParentNode'
        @refreshtablesize='refreshtablesize'
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
        <!-- tabs 内容区  -->
        <div class="commonTabContentWrap" v-if="editableTabs.length > 0">
          <div class="tabContentLeft" v-loading='loading'>
            <div class="oprWrap">
              <div class="selectWrap">
                股票池：<span class="poolItem" v-for="(pool, indexP) in currentStrategyInfo.pageData.stockPool" :key="indexP">{{pool.name}}</span>
                <el-button type="default" size="small" @click="goSelectStockPool">选择股票池</el-button>
                
              </div>
              <div class="btns">
                <el-button type="primary" size="small" @click="saveStrategyFun">保存策略</el-button>
                <el-button type="primary" size="small" @click="execStrategyFun">执行策略</el-button>
              </div>
            </div>
            <div class="select-line">
              <div class="one-select">
                <div class="label">周期：</div>
                <el-select class="period" v-model="currentStrategyInfo.pageData.period" placeholder="请选择" size="small" @change="changePeriod">
                  <el-option
                    v-for="item in periodOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                  </el-option>
                </el-select>
              </div>
              <div class="one-select">
                <div class="label">复权：</div>
                <el-select class="stock-reversion" v-model="currentStrategyInfo.pageData.right" placeholder="请选择" :disabled='rightsOptionsDisabled' size="small" @change="changeRight">
                  <el-option
                    v-for="item in rightsOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                  </el-option>
                </el-select>
              </div>
              <div class="one-select">
                <div class="label">K线范围：</div>
                <el-select class="dataNum" v-model="dataNum" placeholder="请选择" size="small" @change="changeNum">
                  <el-option
                    v-for="item in filterDataNumOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                  </el-option>
                </el-select>
              </div>
            </div>
            <div class="descWrap">
              <div class="label">
                描述信息：
              </div>
              <el-input
                type="textarea"
                :rows="2"
                placeholder="请输入描述信息内容"
                :maxlength='255'
                class="resizeNone"
                v-model="currentStrategyInfo.pageData.desc">
              </el-input>
            </div>
            <div class="addIndexBtnWrap">
              <el-button type="primary" size="small" class="addIndexBtn" @click="openDialog">+添加指标</el-button>
              <div class="statusWrap">状态：
                <el-select class="dataNum" v-model="currentStrategyInfo.pageData.status" placeholder="请选择" size="small" @change="changeNum">
                  <el-option
                    v-for="item in statusAry"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                  </el-option>
                </el-select>
              </div>
            </div>
            <div class="indexDetailList">
              <div class="selectItem" v-for="(item, idx) in currentStrategyInfo.pageData.strategies" :key="idx">
                <div class="selctTitle">
                  <div class="name">{{item.name}}</div>
                  <div class="delBtn" @click="delOneIndexInStrategy(idx)">删除</div>
                </div>
                
                <div class="selectContent">

                  <div class="paramsEditWrap" v-if="item.args.length > 0">
                    <div class="paramsTitle">参数<i :class="item.argsOpend ? 'el-icon-caret-top' : 'el-icon-caret-bottom'" @click="openArgs(item)"></i></div>
                    <table class="editTable" v-show="item.argsOpend">
                      <thead>
                        <tr>
                          <td>参数名称</td>
                          <td>参数值</td>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for='(row,rowIndex) in item.args' :key="rowIndex">
                          <td><div class="box name"><input type="text" v-model='row.Name'></div></td>
                          <td><div class="box defVale"><input type="number" v-model='row.Value'></div></td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <div class="one-select" v-for="(el,index) in item.outArgs" :key="index">
                    <div class="type-name">{{el.Name}}</div>

                    <el-select v-model="el.Condition1" placeholder="请选择" class="operator" @change="operatorChange(el,1)">
                      <el-option
                        v-for="item in operatorOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value">
                      </el-option>
                    </el-select>

                    <el-input class="operator-Value" v-model="el.ConditionValue1" type="number" placeholder="请输入" ></el-input>

                    <span class="andText">与</span>

                    <el-select v-model="el.Condition2" placeholder="请选择" class="operator" @change="operatorChange(el,2)">
                      <el-option
                        v-for="item in operatorOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value">
                      </el-option>
                    </el-select>

                    <el-input class="operator-Value" v-model="el.ConditionValue2" type="number" placeholder="请输入"></el-input>
                  </div>

                  <div class="noData" v-if="item.outArgs.length === 0">暂无数据</div>
                </div>
              </div>
              
              
            </div>
          </div>
          <div class="tabContentRight" ref='tabContentRight' v-loading='execResultLoading'>
            <div class="titleCss">
              <div>
                执行结果:
                <span class="" v-if="currentStrategyInfo.rightResultData.resultTableData.length !== 0">
                  <span>共<span class="red">【{{currentStrategyInfo.rightResultData.filterResultTableData.length}}】</span>只股票，</span>
                  <span>耗时：<span class="green">{{currentStrategyInfo.rightResultData.totalTime}}</span>毫秒,</span>
                  <span>计算耗时：<span class="green">{{currentStrategyInfo.rightResultData.apiTicket}}</span>秒</span>
                </span>
              </div>
              <div class="title-right">
                <el-checkbox v-model="ischeckedResult">只显示筛选结果</el-checkbox>
                <!-- <el-button type="primary" size="small" @click="showSelect" :disabled='stockTitle.length<=0'>筛选</el-button> -->
                <!-- <el-button type="primary" size="small" @click="downloadExcel" :disabled='stockTitle.length<=0'>导出</el-button> -->
                <!-- <div class="downloadExcel" :class="stockTitle.length<=0 ? 'noClick':'clickCss'" @click="downloadExcel">导出</div> -->
              </div>
            </div>
            <div class="resultTableWrap">
              <div class="mainContentWrap" v-if="currentStrategyInfo.rightResultData.resultTableData.length !== 0">
                <div class="elTableWrap">
                  <el-table
                    ref="resultTable"
                    :data="currentStrategyInfo.rightResultData.pageTableData"
                    size='medium'
                    style="width: 100%;height:100%"
                    height="100%"
                    :row-class-name="tableRowClassName"
                    >
                    <el-table-column
                      label="序号"
                      type="index"
                      width="80"
                    >
                    </el-table-column>
                    <el-table-column
                      prop="symbol"
                      label="代码"
                      sortable
                      width="120">
                    </el-table-column>
                    <el-table-column
                      prop="date"
                      label="日期"
                      sortable
                      width="120">
                    </el-table-column>
                    <el-table-column
                      prop="time"
                      label="时间"
                      width="120">
                    </el-table-column>
                    <el-table-column :label="header.label" v-for="(header, index) in currentStrategyInfo.rightResultData.resultTableHeader" :key="index" align="center">
                      <el-table-column
                        v-for="(col, indexCol) in header.children"
                        :key="indexCol"
                        :prop="col.prop"
                        :label="col.label"
                        :sortable='col.sortable'
                        :width="col.width"
                        :align="col.align"
                        >
                      </el-table-column>
                    </el-table-column>
                  </el-table>
                </div>
                <div class="paginationWrapInDialog">
                  <el-pagination
                    background
                    :page-size='currentStrategyInfo.rightResultData.paginationObj.PageSize'
                    layout="prev, pager, next"
                    :total="currentStrategyInfo.rightResultData.paginationObj.total"
                    @current-change='currentChange'
                  >
                  </el-pagination>
                </div>
              </div>
              
              <div class="noData" v-else>暂无数据</div>
            </div>
            
            
          </div>
        </div>
        <div class="noData" v-else>还未选择策略</div>
      </div>
      <!-- rightContentWrap end -->
    </div>

    <el-dialog
      title="选择指标"
      :visible.sync="dialogVisible"
      width="700px">
        <index-search @selectOneIndex='selectOneIndex'></index-search>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false" size="small">取 消</el-button>
        <el-button type="primary" @click="confirmSelectIndexsFun" size="small">确 定</el-button>
      </span>
    </el-dialog>

    <!-- 选择股票池 -->
    <el-dialog
      title=""
      :visible.sync="showDialog"
      width="600px">
        <div v-loading='selectBlockLoading'>
          <el-tabs class="elTabsRun" v-model="blockActiveName" @tab-click="handleResultClick">
            <el-tab-pane v-for="(tabItem, indexTab) in blockEditableTabs" :key="indexTab" :label="tabItem.title" :name="tabItem.name"></el-tab-pane>
          </el-tabs>

          <div class="blocksWrap" v-if="currentBlockData.content">
            <div class="blocks">
              <div class="item" v-for="(block, indexB) in currentBlockData.content" :key="indexB" 
                :class="{active: blockActiveId === block.id}"
                @click="selectOneBlock(block)"
              >{{block.name}}</div>
            </div>
          </div>
          <div class="noData" v-else>暂无数据</div>
          
        </div>

      <span slot="footer" class="dialog-footer">
        <el-button @click="showDialog = false" size="small">取 消</el-button>
        <el-button type="primary" @click="confirmSelectStockPool" size="small">确 定</el-button>
      </span>
    </el-dialog>

    
  </div>
</template>

<script>
import CategoryList from './categoryListForStrategy.vue'
import {find,findIndex} from 'lodash'
import urlObj from '../../../utils/urlObj'
import moment from 'moment'
import $ from 'jquery'
import IndexSearch from '../../../components/indexSearch.vue'

function DefaultData(){}

DefaultData.TabPageData = () => {
  return {
    title: 'default',
    name: '',
    id: '',
    pageData: {
      "groupId": null,
      "groupName": "",
      "id": null,
      "name": "",
      "period": 0,
      "right": 0,
      "status": 0,
      "stockPool": [
          // {
          //     "id": "000016.sh",
          //     "name": "上证50",
          //     "type": "SYS"
          // }
      ],
      "strategies": [
        //   {
        //     "args": [
        //         {
        //             "Name": "M1",
        //             "Value": 5
        //         },
        //         {
        //             "Name": "M2",
        //             "Value": 13
        //         }
        //     ],
        //     "id": 53,
        //     "name": "VOL2",
        // argsOpend: false
        //     "outArgs": [
        //         {
        //             "Condition1": "",
        //             "Condition2": "",
        //             "ConditionValue1": "",
        //             "ConditionValue2": "",
        //             "Name": "VOL"
        //         }
        //     ],
        //     "script": "VOL:VOL,VOLSTICK;\nMA1:MA(VOL,M1);\nMA2:MA(VOL,M2);"
        // }
      ]
    },
    rightResultData: { //右侧需要展示的数据
      totalTime: 0,
      apiTicket: 0,
      resultTableHeader: [],
      resultTableData: [],
      filterResultTableData: [],
      pageTableData: [],
      paginationObj: {
        total: 5,
        PageSize: 30,
        PageIndex: 1
      }
    }
  }
}

export default {
  name: 'StrategyEdit',
  components: {
    IndexSearch,
    CategoryList
  },
  computed: {
    // filterResultTableData: function(){
    //   return this.ischeckedResult ? this.resultTableData.filter(item => item.isFillCondition) : this.resultTableData
    // },
    currentBlockData: function(){ //板块数据
      return find(this.blockEditableTabs, {name: this.blockActiveName}) || {}
    },
    currentStrategyInfo: function(){
      // console.log('计算一下：',this.editableTabs,this.editableTabsValue, find(this.editableTabs, {name: this.editableTabsValue}));
      return find(this.editableTabs, {name: this.editableTabsValue}) || DefaultData.TabPageData()
    }
  },
  data(){
    return {
      showDialog: false,
      selectBlockLoading: false,
      blockActiveName: '0', //tab
      blockActiveId: '000300.sh', //选中 板块
      blockTabIndex: 0,
      blockSelectObj: {
        id: null,
        name: null,
        type: null
      },
      blockEditableTabs:[],
      editableTabs: [],
      editableTabsValue: '0',
      tabIndex: 0,
      
      //指标参数列表
      indexDetailList:[],

      ischeckedResult: false, //筛选结果
      
      periodValue: 0,
      rightsValue: 0,
      periodOptions:[
        {label:"日线",value:0},
        {label:"周线",value:1},
        {label:"月线",value:2},
        {label:"季线",value:9},
        {label:"年线",value:3},
        {label:"1分钟",value:4},
        {label:"5分钟",value:5},
        {label:"15分钟",value:6},
        {label:"30分钟",value:7},
        {label:"60分钟",value:8},
      ],
      rightsOptions:[
        {label:"不复权",value:0},
        {label:"前复权",value:1},
        {label:"后复权(简单)",value:2},
        {label:"后复权(完成)",value:3},
      ],
      rightsOptionsDisabled: false,
      dataNum: 180,
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
      statusAry:[
        {label:"测试",value:0},
        {label:"发布",value:1},
        {label:"停用",value:2},
      ],
      filterDataNumOptions: [],
      storageIndexLists: [], //缓存中的指标列表
      selectIndexAry: [], //选中的指标，目前界面只能选一个指标
      dialogVisible: false,
      checkList: [], //checkbox 选中项 label
      welfareOptions: [], //checkbox 选中项 value
      operatorOptions:[
        {label:"",value:''},
        {label:"等于",value:'=='},
        {label:"不等于",value:'!='},
        {label:"大于",value:'>'},
        {label:"大于或等于",value:'>='},
        {label:"小于",value:'<'},
        {label:"小于或等于",value:'<='},
      ],

      //右侧结果列表
      isgetResult:true,
      allStockList:[],
      totalTime: 0,
      apiTicket: 0,
      stockTitle:[],
      stockList:[],

      isCheckTab: false, //是否点击tab切换
      loading: false,

      paginationObj: { //表格分页
        total: 1,
        PageSize: 30,
        PageIndex: 1
      },

      resultTableHeader: [
        // {
        //   label: 'KDJ',
        //   children: [
        //     {
        //       prop: 'KDJ-K',
        //       label: 'K',
        //       sortable: true,
        //       width: '120',
        //       align: 'left'
        //     }
        //   ]
        // }
      ],
      tableHeight: 300,
      pageTableData: [],
      filterResultTableData: [],
      resultTableData: [
        // {
        //   symbol: '000001.sz',
        //   date: '20201010',
        //   'KDJ-K': 1,
        //   'KDJ-D': 5,
        //   'KDJ-J': 10,
        //   'MA-MA5': 2,
        //   'MA-MA10': 8,
        //   'MA-MA20': 15
        // }
      ],
      execResultLoading: false
    }
  },
  watch: {
    ischeckedResult(value){
      const {resultTableData,paginationObj} = this.currentStrategyInfo.rightResultData
      const filterResultTableData = this.getFilterResultTableData(resultTableData)
      paginationObj.PageIndex = 1
      paginationObj.total = filterResultTableData.length
      const pageTableData = this.initPaginationData(filterResultTableData, paginationObj)

      this.resetTablePageDataForCheck(filterResultTableData,pageTableData,paginationObj)
      this.$nextTick(() => { //table回到顶部
        if(this.$refs.resultTable) this.$refs.resultTable.bodyWrapper.scrollTop = 0
      })
    },
    'currentStrategyInfo.pageData.period'(value){
      if(value === 4 ||value === 5|| value === 6|| value === 7 || value===8) { //分钟
        this.rightsOptionsDisabled = true
        this.currentStrategyInfo.pageData.right = 0

        this.filterDataNumOptions = [...this.dataNumOptionsMinute]
        this.dataNum = 4
      }else{
        this.rightsOptionsDisabled = false

        this.filterDataNumOptions = [...this.dataNumOptions]
        this.dataNum = 180
      }
    }
  },
  mounted(){
    this.filterDataNumOptions = [...this.dataNumOptions]
    this.dataNum = 180

    // this.queryAllIndexData()

    // this.storageIndexLists = localStorage.getItem('st_index_lists') ? JSON.parse(localStorage.getItem('st_index_lists')) : []
    
  },
  methods: {
    getFilterResultTableData(resultTableData){
      return this.ischeckedResult ? resultTableData.filter(item => item.isFillCondition) : resultTableData
    },
    selectOneIndex(item){
      this.selectIndexAry.splice(0, this.selectIndexAry.length)
      this.selectIndexAry.push(item)
    },
    openArgs(item){
      item.argsOpend = !item.argsOpend
    },
    selectOneBlock(block){
      this.blockActiveId = block.id
      //修改页面数据 ...
      this.blockSelectObj.id = block.id
      this.blockSelectObj.name = block.name
      this.blockSelectObj.type = this.currentBlockData.type
    },
    goSelectStockPool(){ //获取所有可选板块
      this.showDialog = true
      
      if(this.blockEditableTabs.length > 0){
        //已经请求过数据，不需要再请求
        return
      }

      this.selectBlockLoading = true
      const p1 = new Promise((resolve, rejcet) => {
        urlObj.get(urlObj.apiStockBlocklist, {}, res => {
          if(res.code === 200){
            resolve(res)
          }else{
            rejcet(res)
          }
        })
      })
      const p2 = new Promise((resolve, rejcet) => {
        urlObj.get(urlObj.apiStockGroupList, {}, res => {
          if(res.code === 200){
            resolve(res)
          }else{
            rejcet(res)
          }
        })
      })

      Promise.all([p1,p2])
      .then(resAry => {
        this.selectBlockLoading = false

        const part1Data = resAry[0].data //其他板块
        const part1Metainfo = resAry[0].metainfo //其他板块
        const part2Data = resAry[1].data //自定义股票池

        const part1BlockKeys = Object.keys(part1Data)
        for (const key of part1BlockKeys) {
          const blockItem = {
            title: part1Metainfo[key],
            keyText: key,
            name: this.blockTabIndex + '',
            content: part1Data[key],
            type: 'SYS'
          }
          this.blockEditableTabs.push(blockItem)
          this.blockTabIndex++
        }

        //自定义股票池加入到数组
        const lastBlockItem = {
          title: '自定义股票池',
          keyText: 'customStockPool',
          name: this.blockTabIndex + '',
          content: part2Data,
          type: 'DIY'
        }
        this.blockEditableTabs.push(lastBlockItem)
        this.blockTabIndex++
      })
      .catch(resAry => {
        this.selectBlockLoading = false
        console.log('获取板块数据异常');
      })
    },
    handleResultClick(){

    },
    confirmSelectStockPool(){ //确认选中股票池
      this.showDialog = false
      if(Array.isArray(this.currentStrategyInfo.pageData.stockPool)){
        this.currentStrategyInfo.pageData.stockPool.splice(0, 1, this.blockSelectObj)
      }
    },
    getCheckboxValue(e){
      console.log('选中信息', e);
    },
    delOneIndexInStrategy(index){ //删除指标
      this.currentStrategyInfo.pageData.strategies.splice(index, 1)
    },
    confirmSelectIndexsFun(){ //确认选择的指标
      this.dialogVisible = false
      const selectIndexs = [...this.selectIndexAry]
      // debugger
      selectIndexs.forEach(item => {
        /**
         * defaultVal: "1"
            delete: false
            id: 24
            maxVal: ""
            minVal: ""
            name: "N"
            strategyId: 44
         */
        let outArgsList = []
        if(Array.isArray(item.outArgs)){
          outArgsList = item.outArgs.map(arg => ({
            Name: arg,
            Condition1: '',
            ConditionValue1: '',
            Condition2: '',
            ConditionValue2: ''
          }))
        }

        const listObj = {
          name: item.name, 
          id: item.id, 
          args: [], 
          script: item.script || '', 
          outArgs: outArgsList || [],
          argsOpend: false
        }
        if(Array.isArray(item.args)){
          listObj.args = item.args.map(item => ({
            Name: item.name,
            Value: parseInt(item.defaultVal)
          }))
        }
        
        this.currentStrategyInfo.pageData.strategies.push(listObj)
      })
    },
    openDialog(){
      this.dialogVisible = true
    },
    tableRowClassName({row, rowIndex}) {
      if (row.isFillCondition) {
        return 'selecting-row';
      }
      return '';
    },
    checkBeforeExec(){
      if(this.currentStrategyInfo.pageData.strategies.length === 0){
        this.$message('请为策略添加指标')
        return false
      }

      let flag = true
      //提示参数填写完整
      this.currentStrategyInfo.pageData.strategies.forEach(strategy => {
        strategy.outArgs.forEach(outArg => {
          if((outArg.Condition1 && !outArg.ConditionValue1) || (!outArg.Condition1 && outArg.ConditionValue1)){
            flag = false
          }
          if((outArg.Condition2 && !outArg.ConditionValue2) || (!outArg.Condition2 && outArg.ConditionValue2)){
            flag = false
          }
        })
      });
      if(!flag) {
        this.$message('筛选条件填写不完整')
      }
      return flag
    },
    formatStringToObject(data) {
      return typeof data === 'string' ? JSON.parse(data) : data
    },
    getPolicyByIndexList(){ //最后一步，根据顺序，重置id
      const policy = this.currentStrategyInfo.pageData.strategies.map((item, index) => {
        const args = item.args.map(arg => ({
          "Name": arg.Name,
          "Value": parseInt(arg.Value)
        }))
        const script = item.script || ''
        const id = index + ''
        const name = item.name
        return {
          "Name": name || '',
          "Script":script,
          "Args":args,
          "ID":id
        }
      })

      return policy
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
    recvExecData(sendDate, res, data){ //处理执行结果数据
    // debugger
      let getDate = (new Date()).getTime();
      let totalTime = getDate - sendDate;
      if(totalTime - 50 > 20){
        totalTime = totalTime  - 50;
      }
      let apiTicket = Number(res.Tick).toFixed(3)
      
      const keysAry = [...Object.keys(res.Data)]
      
      let resultTableHeader = []
      let resultTableData= []
      let filterResultTableData = []
      let pageTableData = []

      if(keysAry.length > 0){
        resultTableHeader = this.getTableHearder(res.Data, data)
        resultTableData = this.getTableData(res.Data, data)
        this.flagTableData(resultTableData) //给符合条件的行，加上标记
        
        filterResultTableData = this.getFilterResultTableData(resultTableData)
        
        //初始化分页数据
        pageTableData = this.initPaginationData(filterResultTableData, this.currentStrategyInfo.rightResultData.paginationObj)

        //填充数据
        this.currentStrategyInfo.rightResultData.totalTime = totalTime
        this.currentStrategyInfo.rightResultData.apiTicket = apiTicket
        this.currentStrategyInfo.rightResultData.resultTableHeader = resultTableHeader
        this.currentStrategyInfo.rightResultData.resultTableData = resultTableData
        const {paginationObj} = this.currentStrategyInfo.rightResultData
        paginationObj.total = filterResultTableData.length
        paginationObj.PageIndex = 1
        this.resetTablePageDataForCheck(filterResultTableData,pageTableData,paginationObj)
        this.$nextTick(() => {
          this.OnSize()
        })
      }
    },
    resetTablePageDataForCheck(filterResultTableData,pageTableData,paginationObj){ //筛选时重置表格数据和分页数据
      this.currentStrategyInfo.rightResultData.filterResultTableData = filterResultTableData
      this.currentStrategyInfo.rightResultData.pageTableData = pageTableData
      this.currentStrategyInfo.rightResultData.paginationObj = paginationObj
    },
    execStrategyFun(){
      const result = this.checkBeforeExec()
      if(!result) return

      const policy = [...this.getPolicyByIndexList()]

      //获取时间段
      const {StartDate, EndDate} = this.getRunDateRange()
      
      const data = {
        "Period": this.currentStrategyInfo.pageData.period,
        "Right": this.currentStrategyInfo.pageData.right,
        "stockPool": this.currentStrategyInfo.pageData.stockPool,
        StartDate,
        EndDate,
        // "CalcCount": 4,
        "OutCount":1,
        "Policy": policy || []
      }
      let sendDate = (new Date()).getTime();
      this.execResultLoading = true
      urlObj.post(urlObj.apiAlgorithmPolicy,data, res => {
        this.execResultLoading = false
        
        if(res.Code === 0){
          this.recvExecData(sendDate, res, data)
          
        }else{
          this.$message('执行异常')
          // this.execResultLoading = false
          // this.resultTableHeader.splice(0, this.resultTableHeader.length)
          // this.resultTableData.splice(0, this.resultTableData.length)
        }
        
      }, res => {
        this.$message.error('执行失败')
        this.execResultLoading = false
        this.resultTableHeader.splice(0, this.resultTableHeader.length)
        this.resultTableData.splice(0, this.resultTableData.length)
      })
    },
    initPaginationData(filterResultTableData, paginationObj){ //初始化分页数据
      let {total,PageIndex,PageSize} = paginationObj
      total = filterResultTableData.length
      const start = (PageIndex - 1) * PageSize
      let end = (PageIndex * PageSize) > total ? 
                total : PageIndex * PageSize
      return filterResultTableData.slice(start, end) || []
    },
    currentChange(page){ //点击分页
      this.currentStrategyInfo.rightResultData.paginationObj.PageIndex = page

      const {paginationObj, filterResultTableData} = this.currentStrategyInfo.rightResultData
      const {PageIndex,PageSize,total} = paginationObj
      const start = (PageIndex - 1) * PageSize
      let end = (PageIndex * PageSize) > total ? 
                total : PageIndex * PageSize
      this.currentStrategyInfo.rightResultData.pageTableData = filterResultTableData.slice(start, end)

      this.$nextTick(() => { //table回到顶部
        this.$refs.resultTable.bodyWrapper.scrollTop = 0
      })
    },
    flagTableData(resultTableData){
      let conditionAry = [ //筛选条件合集
        // {
        //   text: 't1-T', //指标名-参数名
        // Condition1: ">", Condition2: "<", ConditionValue1: "20", ConditionValue2: "50"
        // }
      ]
      for (let i = 0; i < this.currentStrategyInfo.pageData.strategies.length; i++) {
        const oneIndexList = this.currentStrategyInfo.pageData.strategies[i];
        const indexName = oneIndexList.name
        // const {}
        for (let j = 0; j < oneIndexList.outArgs.length; j++) {
          const outVarItem = oneIndexList.outArgs[j];
          const typeName = outVarItem.Name
          const text = `${indexName}-${typeName}`
          let conditionObj = {
            text
          }
          if(outVarItem.Condition1&&outVarItem.ConditionValue1){
            conditionObj.Condition1 = outVarItem.Condition1
            conditionObj.ConditionValue1 = outVarItem.ConditionValue1
          }
          if(outVarItem.Condition2&&outVarItem.ConditionValue2){
            conditionObj.Condition2 = outVarItem.Condition2
            conditionObj.ConditionValue2 = outVarItem.ConditionValue2
          }
          if([...Object.keys(conditionObj)].length > 1){
            conditionAry.push(conditionObj)
          }
        }
      }

      // console.log('筛选条件', conditionAry);

      //开始筛选
      resultTableData.forEach(row => {
        let isFillCondition = true
        for (let index = 0; index < conditionAry.length; index++) {
          const {text,Condition1,ConditionValue1,Condition2,ConditionValue2} = conditionAry[index];
          if(row[text] == '--') { //字段值不存在，置为false，直接跳出判断
            isFillCondition = false
            break
          }
          // console.log('筛选条件', Condition1,ConditionValue1,Condition2,ConditionValue2);
          let filterStr= ''
          if(Condition1&&ConditionValue1){
            filterStr = `${row[text]}${Condition1}${ConditionValue1}`
          }
          if(Condition2&&ConditionValue2){
            filterStr = `${row[text]}${Condition2}${ConditionValue2}`
          }
          if(Condition1&&ConditionValue1&&Condition2&&ConditionValue2){
            filterStr = `${row[text]}${Condition1}${ConditionValue1}&&${row[text]}${Condition2}${ConditionValue2}`
          }
          // console.log('拼接条件：', filterStr);
          if(eval(filterStr)){
            isFillCondition = true
          }else{
            isFillCondition = false
            break
          }
        }

        this.$set(row, 'isFillCondition', isFillCondition)
      })
      // console.log('添加状态后：', this.resultTableData);
    },
    saveStrategyFun(){
      const result = this.checkBeforeExec()
      if(!result) return
      const data = {...this.currentStrategyInfo.pageData}
      urlObj.patch(`${urlObj.apiAlgorithmByIndex}${this.currentStrategyInfo.id}`, data, res => {
        if(res.code === 200){
          
          this.$message('保存成功')
        }else{
          this.$message('保存失败')
        }
      })
    },
    refreshtablesize(){
      this.$nextTick(() => {
        if(this.$refs.resultTable){
          this.$refs.resultTable.doLayout()
        }
      })
    },
    editParentNode(category, text){
      const data = {
        "name": text
      }
      urlObj.patch(`${urlObj.apiAlgorithmGroupById}${category.categoryid}`, data, res => {
        if(res.code === 200){
          category.name = res.data.name
          category.editing = false

          this.$nextTick(() => {
            this.$refs.categorylist.changeDataByParent(false,'','')
          })

          this.$message('编辑成功')
        }else{
          this.$message('编辑失败')
        }
        
      })
    },
    editChildNode(categoryList, currentOperateCategoryIds, text){
      const group = find(categoryList, {categoryid: currentOperateCategoryIds[0]})
      const child = find(group.children, {categoryid: currentOperateCategoryIds[1]})
      const index = findIndex(group.children, {categoryid: currentOperateCategoryIds[1]})
      const data = {"name": text}
      urlObj.patch(`${urlObj.apiAlgorithmByIndex}${child.categoryid}`, data, res => {
        if(res.code === 200){
          child.editing = false
          child.name = res.data.name
          group.children.splice(index, 1, child)
          
          
          this.$nextTick(() => {
            this.$refs.categorylist.changeDataByParent(false,'','')
            // debugger
            this.$refs.categorylist.checkCategory([group.categoryid, child.categoryid])
          })

          //获取包含的指标-详情
          this.getIndexParmsByStrategies(res.data)
          // this.updateTabs(res.data)
          
          this.$message('编辑成功')
        }else{
          this.$message('编辑失败')
        }
      })
    },
    delStockStrategy(categoryList,category,newCategory){//删除 策略 或 策略组
      //category，newCategory，是删除子节点-策略
      //其他category存在，newCategory不存在，是删除父节点-组
      // debugger
      let url = '', isDelParent = false
      if(category && newCategory){
        isDelParent = false
        url = `${urlObj.apiAlgorithmByIndex}${newCategory.categoryid}`
      }else{
        isDelParent = true
        url = `${urlObj.apiAlgorithmGroupById}${category.categoryid}`
      }
      urlObj.dele(url, res => {
        if(res.code === 200){
          // debugger
          let index = -1
          if(isDelParent){//如果删除父节点，重新选中有子节点的，第一个子节点
            index = findIndex(categoryList, {categoryid: category.categoryid})
            categoryList.splice(index, 1)

            //重新选中
            this.$nextTick(() => {
              this.$refs.categorylist.checkNewAfterDelete([category.categoryid])
            })
            
          }else{//如果删除子节点，看是否有兄弟节点，选第一个兄弟节点
            const parent = category.children
            index = findIndex(parent, {categoryid: newCategory.categoryid})
            parent.splice(index, 1)
            if(parent.length === 0){
              this.$set(parent, 'isdelete', true)
            }

            // debugger
            console.log('afjief::', this.editableTabs);
            let index = findIndex(this.editableTabs, {id: newCategory.categoryid})
            this.editableTabs.splice(index, 1)
            //重新选中
            this.$nextTick(() => {
              this.$refs.categorylist.checkNewAfterDelete([category.categoryid, newCategory.categoryid])
            })
          }

          this.$message('删除成功')
        }else{
          this.$message('删除异常')
        }
      },
      // res => {
      //   this.$message.error('删除失败')
      // }
      )
    },
    addStockStrategyGroup(newCategory, text){ //新建组
      const data = {
        "name": text
      }
      urlObj.post(urlObj.apiAlgorithmGroupCreate, data, res => {
        if(res.code === 200){
          newCategory.categoryid = res.data.id
          newCategory.name = res.data.name
          newCategory.creating = false
          // category.editing = false
          // debugger

          this.$nextTick(() => {
            this.$refs.categorylist.changeDataByParent(false,'','')
            // debugger
            // this.$refs.categorylist.checkCategory([category.categoryid, newCategory.categoryid])
          })
          
          // callback([category.groupId, category.categoryid])
          this.$message('创建成功')
        }else{
          this.$message('创建失败')
        }
      })
    },
    addStockStrategy(category,newCategory,text){ //新建策略
      console.log('ccc::', category, text);
      const data = DefaultData.TabPageData().pageData
      data.name = text
      data.groupId = category.categoryid
      data.stockPool = [ //默认
        {
          id: '000300.sh',
          name: '沪深300',
          type: 'SYS'
        }
      ]
      // const data = {
      //   "right": 0,
      //   "name": text,
      //   "groupId": category.categoryid,
      //   "stockPool":[ //默认
      //     {
      //       id: '000300.sh',
      //       name: '沪深300',
      //       type: 'SYS'
      //     }
      //   ],
      //   "stockPoolType": 0,
      //   "period": 0,
      //   "strategies":[]
      // }
      // debugger
      urlObj.post(urlObj.apiAlgorithmCreate, data, res => {
        if(res.code === 200){
          newCategory.categoryid = res.data.id
          newCategory.name = res.data.name
          newCategory.creating = false
          // category.editing = false
          // debugger

          this.$nextTick(() => {
            this.$refs.categorylist.changeDataByParent(false,'','')
            // debugger
            this.$refs.categorylist.checkCategory([category.categoryid, newCategory.categoryid])
            // this.$refs.categorylist.hideInput(category.categoryid)
          })
          
          // callback([category.groupId, category.categoryid])
          this.$message('创建成功')
        }else{
          this.$message('创建失败')
        }
      })
    },
    getTableHearder(data, queryData){//整理得到表头---
      const symbol = Object.keys(data) ? [...Object.keys(data)][0] : ''
      let resultTableHeader = []
      data[symbol].forEach(oneIndexData => {
        const Data = this.formatStringToObject(oneIndexData.Data)
        // console.log('data:', Data);
        const ID = parseInt(oneIndexData.ID)
        // console.log('ID:', ID);
        const indexId = ID
        const indexName = queryData.Policy[indexId].Name || 'test'
        
        const children = []
        Data.OutVar.forEach(outVarItem => {
          if(outVarItem.Type == 0){
            const paramName = outVarItem.Name || 'test'
            children.push({
              prop: `${indexName}-${paramName}`,
              label: paramName,
              sortable: true,
              width: '120',
              align: 'right'
            })
          }
        })

        const headerItem = {
          label: indexName,
          children
        }
        // console.log('headerItem::', headerItem);
        resultTableHeader.push(headerItem)
      })
      return resultTableHeader
    },
    getTableData(data, queryData){//整理表格数据---
      let tableData = []
      const symbolAry = [...Object.keys(data)]
      for (let index = 0; index < symbolAry.length; index++) {
        const symbol = symbolAry[index];
        const rowData = data[symbol]
        const rowItem = {
          symbol,
          date: '',
          time: '',
          isFillCondition: true //是否需要显示状态
        }
        for (let j = 0; j < rowData.length; j++) {
          const oneIndexDataRow = rowData[j];
          const newData = this.formatStringToObject(oneIndexDataRow.Data)
          const newID = parseInt(oneIndexDataRow.ID)
          const indexName = queryData.Policy[newID].Name
          rowItem.date = newData.Date[0] ? newData.Date[0] : '--' 
          rowItem.time = newData.Time&&newData.Time[0] ? newData.Time[0] : '--'

          for (let m = 0; m < newData.OutVar.length; m++) {
            const outVarItem = newData.OutVar[m];
            if(outVarItem.Type == 0){
              const argName = outVarItem.Name
              rowItem[`${indexName}-${argName}`] = outVarItem.Data.length > 0 && outVarItem.Data[0] !== null ? Number(outVarItem.Data[0]).toFixed(2) : '--'
            }
          }
        }

        tableData.push(rowItem)
      }

      return tableData
    },
    OnSize(){
      const tabContentRight = this.$refs.tabContentRight
      const tableHeight = tabContentRight.clientHeight - 50
      this.tableHeight = tableHeight
      this.$nextTick(() => {
        if(this.$refs.resultTable) this.$refs.resultTable.doLayout()
      })
      // console.log('Z???', this.tableHeight);
    },
    changeRight(){

    },
    changeNum(){

    },
    changePeriod(){

    },
    operatorChange(){

    },
    showSelect(){

    },
    sortFun(){

    },
    downloadExcel(){

    },
    gotoHqchart(){

    },
    changeCategory(categoryList,category,from){
      // debugger
      if(from === 'elTab'){
        this.isCheckTab = true
      }else{
        this.isCheckTab = false
      }
      if(this.isCheckTab) return //仅是tab切换的时候不去请求接口
      this.loading = true
      this.queryOneStrategyDetail(category)
    },
    queryOneStrategyDetail(category){
      urlObj.get(`${urlObj.apiAlgorithmByIndex}${category.categoryid}`, {}, res => {
        this.loading = false
        if(res.code === 200){
          const index = findIndex(this.editableTabs, {id: res.data.id})
          console.log('tab中idnex：', index);
          if(index > -1){
            //已经存在,切换选中
            this.editableTabsValue = this.editableTabs[index].name
          }else{
            let tabItem = DefaultData.TabPageData()
            tabItem.title = res.data.name
            tabItem.name = this.tabIndex+''
            tabItem.id = res.data.id
            tabItem.pageData = res.data

            this.editableTabs.push(tabItem)
            this.editableTabsValue = tabItem.name
            this.tabIndex++
          }
          console.log('this.editableTabs：', this.editableTabs);
          // this.getIndexParmsByStrategies(res.data)
          
        }
      })
    },
    deleteStrategy(categoryid){
      //tabs直接删除即可
      // const target = find(this.editableTabs, item => item.category.categoryid ===categoryid)
      // if(!target) return false
      // const targetName = target.name
      // this.removeTab(targetName)
    },
    changeStrategyName(categoryid, title){
      // const target = find(this.editableTabs, item => item.category.categoryid ===categoryid)
      // const index = findIndex(this.editableTabs, item => item.category.categoryid ===categoryid)
      // if(!target) return false
      // target.title = title
      // this.editableTabs.splice(index, 1, target)
      // console.log('....',this.editableTabs);
    },
    removeTab(targetName){
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
      
      this.editableTabsValue = activeName; //选中另外的tab
      this.editableTabs = tabs.filter(tab => tab.name !== targetName); //删除tab

      // console.log('@@@',this.editableTabsValue);
      if(this.editableTabs.length > 0){
        // const tab = find(this.editableTabs, {name: this.editableTabsValue})
        this.$refs.categorylist.checkCategory([this.currentStrategyInfo.pageData.groupId, this.currentStrategyInfo.pageData.id], 'elTab')
      }else{
        this.$refs.categorylist.checkCategory(null)
        this.tabIndex = 0 //重置为0，否则重新选中节点，其数据对不上
        //初始化数据
        // this.currentStrategyInfo = DefaultData.TabPageData()
      }
    },
    handleTabClick(tab, event){
      this.isCheckTab = true

      // const paneName = tab.paneName
      // const tabData = find(this.editableTabs, item => item.name === paneName)
      // this.currentStrategyInfo = tabData
      this.$refs.categorylist.checkCategory([this.currentStrategyInfo.pageData.groupId, this.currentStrategyInfo.pageData.categoryid], 'elTab')
    },
    
  }
}
</script>

<style lang='less'>
@import '../../../assets/css/commonStyle.less';

.elTabsRun{
  margin-top: -30px;
}

/**dialog checkbox-group */
.checkListWrap{
  width: 100%;
  height: 200px;
  overflow-y: auto;

  .checkItem{
    height: 40px;
    display: flex;
    align-items: center;
  }
}

.strategyEditWrap{
  width: 100%;
  height: 100%;
  position: relative;

  @leftWidth: 240px;

  .blocksWrap{
    height: 600px;
    overflow-y: auto;
    // background-color: yellow;

    .blocks{
      display: flex;
      flex-wrap: wrap;
      .item{
        padding: 0 10px;
        width: 112px;
        line-height: 32px;
        color: #50555f;
        cursor: pointer;

        &.active{
          color: #eb6100;
        }
      }
    }
  }

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
        width: 100%;
        height: calc(100% - 7px - 31px - 15px);
        display: flex;

        @tabContentLeftWidth: 660px;

        .tabContentLeft{
          width: @tabContentLeftWidth;
          height: 100%;
          box-sizing: border-box;
          padding: 0 22px;
          position: relative;

          &::after{
            content: '';
            position: absolute;
            top: -15px;
            right: 0;
            height: calc(100% + 15px);
            width: 1px;
            background-color: #d9d9d9;
          }

          .oprWrap{
            height: 42px;
            // padding-bottom: 9px;
            display: flex;
            justify-content: space-between;

            .poolItem{
              padding: 0 15px 0 5px;
            }
          }
          .select-line{
            height: 42px;
            width: 100%;
            display: flex;
            align-items: center;
            box-sizing: border-box;
            justify-content: space-between;

            .one-select{ /*周期，复权*/
              display: flex;
              align-items: center;
              
              &:last-child{
                margin-right: 0px;
              }
              .label{
                color: #000;
                font-size: 14px;
              }
              .el-select{
                height: 30px;
                .el-input__inner{
                  // color: #125fd9;
                  width: 80px;
                }
                .el-input__icon{
                  width: 14px;
                  line-height: 32px;
                }
                .el-input--suffix .el-input__inner{
                  padding-right: 16px;
                }
              }
              .dataNum{
                width: 80px;
                input{
                  padding: 0 0 0 15px;
                }
              }
            }
          }

          @descWrapHeight: 70px;
          .descWrap{
            height: @descWrapHeight;
            display: flex;
            align-items: center;
            // justify-content: space-between;

            .resizeNone{
              .el-textarea__inner{ //el_input中的隐藏属性
                resize: none;  //主要是这个样式
              }
            }

            .label{
              height: 100%;
              width: 80px;
              display: flex;
              align-items: flex-start;
              padding-top: 8px;
              box-sizing: border-box;
            }
            .el-textarea{
              width: calc(100% - 80px);
            }
          }
          // @symbolListHeight: 223px;
          // .symbolList{
          //   height: @symbolListHeight;
          // }
          @addIndexBtnWrapHeight: 52px;
          .addIndexBtnWrap{
            height: @addIndexBtnWrapHeight;
            display: flex;
            align-items: center;

            .statusWrap{
              margin-left: 200px;
            }
          }

          .indexDetailList{
            height: calc(100% - 42px - 42px - @addIndexBtnWrapHeight - @descWrapHeight);
            overflow-y: auto;
            margin: 0 -22px;
            padding: 0 22px;

            .selectItem{
              padding-bottom: 15px;
              position: relative;

              // &::after{
              //   content: '';
              //   position: absolute;
              //   bottom: 10px;
              //   left: 10%;
              //   width: 80%;
              //   height: 1px;
              //   background-color: #d9d9d9;
              // }

              .selctTitle{
                width: 100%;
                height: 24px;
                background-color: #fdefe5;
                border-radius: 3px 3px 0px 0px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: #eb6100;
                padding: 0 9px;
                font-size: 12px;
                box-sizing: border-box;

                .delBtn{
                  cursor: pointer;
                }
              }

              .selectContent{
                padding-top: 6px;
                padding-bottom: 6px;
                border: solid 1px #ffab70;

                .paramsEditWrap{
                  width: calc(100% - 30px);
                  // height:300px;
                  box-sizing: border-box;
                  background-color: #f7f8f9;
                  overflow-y: auto;
                  border: @contentBorder;
                  margin: 0 auto;
                  margin-bottom: 15px;
                  /* padding-left: 7px;
                  padding-bottom: 16px; */

                  .paramsTitle{
                    height: 30px;
                    display: flex;
                    box-sizing: border-box;
                    padding: 0 10px;
                    justify-content: space-between;
                    align-items: center;
                  }

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

                      input[type='text'],
                      input[type='number']
                      {
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

                .noData{
                  padding-top: 0;
                  padding-bottom: 10px;
                }

                .one-select{ /**筛选条件 */
                  width: 100%;
                  height: 32px;
                  margin-bottom: 2px;
                  display: flex;
                  align-items: center;
                  justify-content: space-between;
                  box-sizing: border-box;
                  padding: 0 15px;

                  &:last-child{
                    margin-bottom: 0;
                  }

                  .andText{
                    padding:  0 15px;
                  }
                }
                .type-name{
                  width: 65px;
                  height: 32px;
                  text-align: left;
                  line-height: 32px;
                  color: #73879c;
                  font-size: 14px;
                  overflow: hidden;
                }
                .operator{
                  width: 122px;
                  height: 32px;
                  background-color: #ffffff;
                  box-shadow: 0px 2px 5px 0px 
                    rgba(73, 74, 106, 0.14);
                  border-radius: 3px;
                  border: solid 1px #d7d8e0;
                  box-sizing: border-box;
                  font-size: 14px;
                  color: #3b3d65;
                  input{
                    border:none;
                  }
                  .el-input__icon{
                    line-height: 30px;
                  }
                }
                .operator-Value{
                  width: 107px;
                  height: 32px;
                  background-color: #fafafc;
                  box-shadow: inset 0px 5px 0px 0px 
                    #e7e7e7;
                  border-radius: 3px;
                  border: solid 1px #c3cad9;
                  box-sizing: border-box;
                  color: #3b3d65;
                  font-size: 14px;
                  input{
                    border:none;
                    padding-right: 0px;
                  }
                }
                .el-radio{
                  margin:0;
                  &:first-child{
                    margin-right: 12px;
                  }
                }
                .el-radio__label{
                  padding-left:4px;
                  color: #3b3d65;
                }
                .el-radio__input.is-checked .el-radio__inner{
                  border-color: #125fd9;
                  background: #125fd9;
                }
                .el-input__inner {
                  height: 29px;
                  line-height: 29px;
                }
              }
            }
          }
        }
        .tabContentRight{
          width: calc(100% - @tabContentLeftWidth);
          height: 100%;
          overflow-y: auto;

          .resultTableWrap{
            width: 100%;
            height: calc(100% - 50px);

            .mainContentWrap{
              height: 100%;

              .elTableWrap{
                width: 100%;
                height: calc(100% - 50px);
              }

              .paginationWrapInDialog{
                width: 100%;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
              }
            }

            
          }

          .titleCss{
            width: 100%;
            height: 50px;
            background-color: #ffffff;
            padding-left:16px;
            box-sizing: border-box;
            color: #666666;
            font-size: 14px;
            // border-bottom:1px solid #dcdcdc;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-right:16px;
            .title-right{
              display: flex;
            }
            .select-btn{
              // width: 75px;
              // height: 30px;
              // border-radius: 3px;
              // border: solid 1px #125fd9;
              // cursor: pointer;
              // box-sizing: border-box;
              // text-align: center;
              // line-height: 28px;
              // margin-right:10px;
              // font-size: 14px;
              // color: #125fd9;
              &.noClick{
                background: #909399;
                cursor:not-allowed;
                border:none;
                color:#fff;
              }
            }
            .downloadExcel{
              // width: 75px;
              // height: 30px;
              // border-radius: 4px;
              // color: #fff;
              // font-size: 14px;
              // text-align: center;
              // line-height: 30px;
              // margin-left: 8px;
              // padding:0 8px;
              // box-sizing: border-box;
              // &.clickCss{
              //   background-color: #125fd9;
              //   cursor: pointer;
              // }
              &.noClick{
                background: #909399;
                cursor:not-allowed;
              }
            }
          }
          .nodata{
            height: 40px;
            color: #666;
            font-size: 14px;
            text-align: center;
            width: 100%;
            line-height: 40px;
          }
        }
      }

    }
  }

}

</style>
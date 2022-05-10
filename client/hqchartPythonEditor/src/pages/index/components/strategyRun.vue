<template>
  <div class="strategyRunWrap">
    <div class="left">
      <div class="execAllWrap">
        <el-button type="primary" size="small" @click="execAllFun" :disabled='execAllObj.status === 1'>执行全部</el-button>
        <div class="progressWrap" v-if="execAllObj.status === 1">
          <span class="taskname">{{execAllObj.taskname}}</span>
          <el-progress :percentage="execAllObj.percent"></el-progress>
        </div>
      </div>
      <div class="categorylistWrap">
        <category-list ref="categorylist"
          @changeCategory='changeCategory'
          @refreshtablesize='OnSize'
        ></category-list>
      </div>
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
        <div class="commonTabContentWrap" ref='commonTabContentWrap' v-if="editableTabs.length > 0">
          <div class="descTextWrap" ref="descTextWrap" v-if="currentTabData.desc !== null">{{currentTabData.desc}}</div>
          <div class="titleCss">
            <div class="title-left">
              <div class="btnWrap">
                <el-button type="default" size="small" @click="reExecute">重新执行</el-button>
              </div>
              执行结果:
              <span class="">
                <span>共<span class="red">【{{currentTabData.resultTableData.length}}】</span>只股票，</span>
                <span>耗时：<span class="green">{{currentTabData.totalTime}}</span>毫秒,</span>
                <span>计算耗时：<span class="green">{{currentTabData.apiTicket}}</span>秒</span>
              </span>
            </div>
            <div class="title-right">
              最后执行时间：{{currentTabData.updateTime}}
            </div>
          </div>
          <div class="resultTableWrap" ref="resultTableWrap" v-loading='resultLoading' v-if="currentTabData.resultTableData.length > 0">
            <div class="elTableWrap" ref="elTableWrap">
              <el-table
                ref="resultTable"
                :data="currentTabData.pageTableData"
                size='medium'
                style="width: 100%;height:100%"
                height="100%"
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
                  prop="symbolName"
                  label="名称"
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
                <el-table-column :label="header.label" v-for="(header, index) in currentTabData.resultTableHeader" :key="index" align="center">
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
            <div class="paginationWrap" ref="paginationWrap">
              <el-pagination
                background
                :page-size='currentTabData.paginationObj.PageSize'
                layout="prev, pager, next"
                :total="currentTabData.paginationObj.total"
                @current-change='currentChange'
              >
              </el-pagination>
            </div>
          </div>          
          <div class="noData" v-else>暂无数据</div>
        </div>
        <div class="noData" v-else>还未选择策略</div>
      </div>
    </div>
  </div>
</template>

<script>
import CategoryList from './categoryListForRun.vue'
import {find, findIndex} from 'lodash'
import urlObj from '../../../utils/urlObj'
import moment from 'moment'

function DefaultData(){}
DefaultData.getTabPageData = () => {
  return {
    title: '',
    name: '',
    id: '',
    groupId: '',
    resultTableData: [],
    pageTableData: [],
    resultTableHeader: [],
    totalTime: '--',
    apiTicket: '--',
    updateTime: '--',
    desc: null,
    paginationObj: { //表格分页
      total: 1,
      PageSize: 30,
      PageIndex: 1
    },
  }
}

export default {
  name: 'StrategyRun',
  components: {
    CategoryList
  },
  computed: {
    currentTabData: function () {
      console.log('当前数据：', find(this.editableTabs, {name: this.editableTabsValue}));
      return find(this.editableTabs, {name: this.editableTabsValue}) || DefaultData.getTabPageData()
    }
  },
  watch: {
    'currentTabData.resultTableData'(){
      //截取分页数据 start
      this.currentTabData.paginationObj.total = this.currentTabData.resultTableData.length
      const {PageIndex, PageSize, total} = this.currentTabData.paginationObj
      const start = (PageIndex - 1) * PageSize
      let end = (PageIndex * PageSize) > total ? 
                total : PageIndex * PageSize
      this.currentTabData.pageTableData = this.currentTabData.resultTableData.slice(start, end)
    }
  },
  data(){
    return {
      editableTabs: [],
      editableTabsValue: '0',
      tabIndex: 0,
      timer: null,
      execAllObj: {
        "percent": 0,
        "status": 0, //1
        "taskname": ""
      },
      resultLoading: false,
      
    }
  },
  methods: {
    currentChange(page){ //点击分页
      this.currentTabData.paginationObj.PageIndex = page

      const {PageIndex, PageSize, total} = this.currentTabData.paginationObj
      const start = (PageIndex - 1) * PageSize
      let end = (PageIndex * PageSize) > total ? 
                total : PageIndex * PageSize
      this.currentTabData.pageTableData = this.currentTabData.resultTableData.slice(start, end)

      this.$nextTick(() => { //table回到顶部
        this.$refs.resultTable.bodyWrapper.scrollTop = 0
      })
    },
    reExecute(){
      this.resultLoading = true
      const data = {
        "PolicyId": this.currentTabData.id
      }
      let sendDate = (new Date()).getTime();
      urlObj.post(urlObj.apiPolicyRunById, data, res => {
        this.resultLoading = false
        // debugger
        let getDate = (new Date()).getTime();
        if(res.Code === 0){
          // const algorithmId = res.Data.algorithmId
          if([...Object.keys(res.Data.result)].length > 0){
            this.currentTabData.resultTableData = this.getResultTableData(res.Data.result)
            this.currentTabData.resultTableHeader = this.getResultTableHeader(res.Data.result)
          }

          this.currentTabData.totalTime = getDate - sendDate;
          if(this.currentTabData.totalTime - 50 > 20){
            this.currentTabData.totalTime = this.currentTabData.totalTime  - 50;
          }
          this.currentTabData.apiTicket = Number(res.Data.ticket).toFixed(3)
          this.currentTabData.updateTime = res.Data.updateTime
          // debugger
          this.currentTabData.desc = res.Data.desc

          this.OnSize() //重新计算高度

          this.$message('重新执行成功')
        }else{
          this.$message('重新执行异常')
        }
      }, res => {
        this.resultLoading = false
        this.$message.error('重新执行异常')
      })
    },
    OnSize(){
      this.$nextTick(() => {
        const commonTabContentWrap = this.$refs.commonTabContentWrap
        const descTextWrap = this.$refs.descTextWrap
        const resultTableWrap = this.$refs.resultTableWrap
        const resultTable = this.$refs.resultTable
        const paginationWrap = this.$refs.paginationWrap

        const titleCssHeight = 50
        let descTextWrapHeight = 0
        if(descTextWrap){
          descTextWrapHeight = descTextWrap.offsetHeight 
        }
        let paginationWrapHeight = 0
        if(paginationWrap){
          paginationWrapHeight = 50
        }
        // console.log('descTextWrap：：', descTextWrap.offsetHeight);
        const height = commonTabContentWrap.clientHeight - descTextWrapHeight - titleCssHeight - paginationWrapHeight
        // console.log('height::', height);
        resultTableWrap.style.height = height + 'px'
        if(resultTable){
          resultTable.doLayout()
        }
        
      })
    },
    execAllFun(){
      urlObj.post(urlObj.apiPolicyRunAll, null, res => {
        this.$message(res.msg)

        this.queryStaus()
      }, res => {
        this.$message.error('执行全部异常')
      })
    },
    queryStaus(){ //查询执行状态
      urlObj.get(urlObj.apiPolicyRunStatus, null, res => {
        if(res.code === 200){
          this.execAllObj.percent = res.percent
          this.execAllObj.status = res.status
          this.execAllObj.taskname = res.taskname
          if(this.timer === null){
            this.timer = setInterval(() => {
              this.queryStaus()
            }, 1000);
          }
          if(res.status !== 1){
            if(this.timer){
              clearInterval(this.timer)
              this.timer = null
            }
          }
          // if(res.status !== 1) return
          // if(this.timer === null){
          //   this.timer = setTimeout(() => {
          //     this.queryStaus()     
          //   }, 1000);

          // }else{
          //   clearTimeout(this.timer)
          //   this.timer = null
          // }

        }
      }, res => {
        this.$message.error('查询执行状态异常')
      })


      
      
    },
    changeCategory(category, categoryid, from){
      // console.log('changeCategory::', category, categoryid);
      let sendDate = (new Date()).getTime();
      urlObj.get(`${urlObj.apiAlgorithmPolicy}/${categoryid}/RunResult`, {}, res => {
        let getDate = (new Date()).getTime();
        if(res.Code === 0){
          // debugger
          const algorithmId = res.Data.algorithmId
          if(findIndex(this.editableTabs, {id: algorithmId}) === -1){
            let tabItem = DefaultData.getTabPageData()
            tabItem.title = category.name
            tabItem.name = this.tabIndex + ''
            tabItem.id = algorithmId
            tabItem.groupId = category.groupId
            
            if([...Object.keys(res.Data.result)].length > 0){
              tabItem.resultTableData = this.getResultTableData(res.Data.result)
              tabItem.resultTableHeader = this.getResultTableHeader(res.Data.result)
            }
            tabItem.totalTime = getDate - sendDate;
            if(tabItem.totalTime - 50 > 20){
              tabItem.totalTime = tabItem.totalTime  - 50;
            }
            tabItem.apiTicket = Number(res.Data.ticket).toFixed(3)
            tabItem.updateTime = res.Data.updateTime
            tabItem.desc = res.Data.desc

            this.editableTabs.push(tabItem)
            this.editableTabsValue = tabItem.name
            this.tabIndex++

            this.OnSize() //重新计算高度
          }else{
            // console.log(this.editableTabs, algorithmId);
            let tabItem = null
            this.editableTabs.forEach(tab => {
              if(tab.id === algorithmId){
                tabItem = tab
                this.editableTabsValue = tabItem.name
              }
            })
            this.OnSize() //重新计算高度
          }

          //刷新表格
          this.$nextTick(() => {
            if(this.$refs.resultTable) this.$refs.resultTable.doLayout()
          })
        }else if(res.Code === -1){ //未执行策略
          // return
          this.$message.error(res.Msg)
          const algorithmId = categoryid
          if(findIndex(this.editableTabs, {id: algorithmId}) === -1){
            let tabItem = DefaultData.getTabPageData()
            tabItem.title = category.name
            tabItem.name = this.tabIndex + ''
            tabItem.id = algorithmId
            tabItem.groupId = category.groupId

            this.editableTabs.push(tabItem)
            this.editableTabsValue = tabItem.name
            this.tabIndex++
          }else{
            let tabItem = find(this.editableTabs, {id: algorithmId})
            // console.log('查找tab', tabItem);
            this.editableTabsValue = tabItem.name
          }

        }else{
          this.$message.error('查询执行结果异常')  
        }
      }, res => {
        this.$message.error('查询执行结果异常')
      })
      
    },
    // recvResultData(res){ //处理结果数据
      
    // },
    getResultTableData(result){
      
      let tableData = []
      const stockAry = [...Object.keys(result)]
      stockAry.forEach(symbolStr => {
        const stockData = result[symbolStr]
        const rowItem = {
          symbol: symbolStr,
          symbolName: stockData['symbolName'],
          date: stockData['0'].Data.Date[0],
          time: stockData['0'].Data.Time ? stockData['0'].Data.Time[0] : '--'
          //...
        }
        const indexKeysAry = [...Object.keys(stockData)]
        indexKeysAry.splice(indexKeysAry.length - 1, 1) //不包含symbolName属性
        indexKeysAry.forEach(num => {
          const paramsData = stockData[num].Data
          const paramsKeysAry = [...Object.keys(paramsData)]
          const keyName = 'Date'
          const dateIndex = paramsKeysAry.indexOf(keyName)
          paramsKeysAry.splice(dateIndex,1)
          const keyNameTime = 'Time'
          const timeIndex = paramsKeysAry.indexOf(keyNameTime)
          if(timeIndex > -1) {
            paramsKeysAry.splice(timeIndex,1)
          }
          paramsKeysAry.forEach(paramsKeyStr => {
            rowItem[`${stockData[num].Name}-${paramsKeyStr}`] = paramsData[paramsKeyStr][0] !== null ? Number(paramsData[paramsKeyStr][0]).toFixed(2) : '--'
          })
        })

        tableData.push(rowItem)
      })
      return tableData
    },
    getResultTableHeader(result){
      // debugger
      let headerAry = []
      const stockAry = [...Object.keys(result)]
      const symbol = stockAry[0] 
      const stockObj = result[symbol]
      const indexKeysAry = [...Object.keys(stockObj)]
      indexKeysAry.splice(indexKeysAry.length - 1, 1) //不包含symbolName属性
      indexKeysAry.forEach(keyStr => {
        const indexData = stockObj[keyStr]
        let headerItem = {
          label: indexData.Name,
          children:[
            // {
            //         prop: 'KDJ-K',
            //         label: 'K',
            //         sortable: true,
            //         width: '120',
            //         align: 'right'
            //       }
              ]
        }
        const paramsKeysAry = [...Object.keys(indexData.Data)]
        const keyName = 'Date'
        const dateIndex = paramsKeysAry.indexOf(keyName)
        paramsKeysAry.splice(dateIndex,1) //去掉date，只获取指标参数
        const keyNameTime = 'Time'
        const timeIndex = paramsKeysAry.indexOf(keyNameTime)
        if(timeIndex > -1) {
          paramsKeysAry.splice(timeIndex,1)
        }
        paramsKeysAry.forEach(paramsKeyStr => {
          const childItem = {
            prop: `${indexData.Name}-${paramsKeyStr}`,
            label: paramsKeyStr,
            sortable: true,
            width: '120',
            align: 'right'
          }

          headerItem.children.push(childItem)
        })
        
        headerAry.push(headerItem)

      })

      return headerAry
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
        const tab = find(this.editableTabs, {name: this.editableTabsValue})
        this.$refs.categorylist.checkCategory([tab.groupId, tab.id], 'elTab')
      }else{
        this.$refs.categorylist.checkCategory(null)
      }
    },
    handleTabClick(tab, event){
      // console.log('ccc::', tab);
      const tabData = find(this.editableTabs, {name: tab.name})
      this.$refs.categorylist.checkCategory([tabData.groupId, tabData.id], 'elTab')
    },
  }
  
}
</script>

<style lang='less'>
@import '../../../assets/css/commonStyle.less';
.elTabsRun{
  margin-top: -30px;
}
.strategyRunWrap{
  width: 100%;
  height: 100%;
  position: relative;

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

    @execAllWrapHeight: 80px;
    .execAllWrap{
      height: @execAllWrapHeight;
      display: flex;
      flex-direction: column;
      // align-items: center;
      padding-left: 15px;
      padding-right: 15px;
      box-sizing: border-box;
      border-bottom: @contentBorder;
      padding-top: 8px;

      .progressWrap{
        height: 32px;
        width: 100%;
        display: flex;
        align-items: center;
        // padding-left: 15px;
        // padding-right: 15px;
        box-sizing: border-box;

        @tasknameWidth: 100px;
        .taskname{
          display: inline-block;
          // flex: 1;
          width: @tasknameWidth;
          // max-width: 260px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          margin-right: 10px;
          box-sizing: border-box;
        }

        .el-progress {
          width: calc(100% - @tasknameWidth);
        }
      }
    }

    .categorylistWrap{
      height: calc(100% - @execAllWrapHeight);
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

        .descTextWrap{
          // height: 30px;
          line-height: 22px;
          padding-left: 16px;
          padding-top: 4px;
          padding-bottom: 4px;
          color: #666666;
          padding-right: 16px;
        }

        .resultTableWrap{
          width: 100%;
          height: calc(100% - 50px - 30px);

          .elTableWrap{
            width: 100%;
            height: 100%;
          }

          .paginationWrap{
              width: 100%;
              height: 50px;
              display: flex;
              align-items: center;
              justify-content: center;
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

          .title-left{
            display: flex;
            height: 100%;
            align-items: center;

            .btnWrap{
              padding-right: 15px;
            }
          }

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

        // @inputWrapHeight: 47px;
        // .tableWrap{
        //   width: 100%;
        //   height: calc(100% - @inputWrapHeight);
        //   border-top: 1px solid #EBEEF5;
        //   box-sizing: border-box;

        //   .el-button--text{
        //     color: #eb6100;
        //     font-size: 14px;
        //   }
        // }
        
      }
    }
  }

}
</style>
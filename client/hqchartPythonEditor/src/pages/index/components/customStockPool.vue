<template>
  <div class="customStockPoolWrap">
    <div class="left">
      <category-list-for-stock-pool ref="categorylist"
        @changeCategory='changeCategory'
        @deleteCategory='deleteCategory'
        @refreshPoolName='refreshPoolName'
      ></category-list-for-stock-pool>
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
          <stock-search @addSymbol='addSymbol' :isShowBtn="true"></stock-search>
          
          <div class="tableWrap">
            <el-table
              ref="resultTable"
              :data="currentTabData.data.tableData"
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
                  label="股票代码"
                  sortable
                  width="120">
                </el-table-column>
                <el-table-column
                  prop="name"
                  label="股票名称"
                  sortable
                  width="120">
                </el-table-column>
                <el-table-column
                  prop="date"
                  sortable
                  label="日期"
                  width="120">
                </el-table-column>
                <el-table-column
                  label=""
                  >
                  <template slot-scope="scope">
                    <el-button
                      @click.native.prevent="deleteRow(scope.$index, currentTabData.data.tableData)"
                      type="text"
                      size="small">
                      移除
                    </el-button>
                  </template>
                </el-table-column>
            </el-table>
          </div>
          
        </div>
        <div class="noData" v-else>还未选择股票池</div>
      </div>
    </div>
  </div>
</template>

<script>
import CategoryListForStockPool from './categoryListForStockPool.vue'
import {find, findIndex} from 'lodash'
import urlObj from '../../../utils/urlObj'
import moment from 'moment'
import StockSearch from '../../../components/stockSearch.vue'

function DefaultData(){}
DefaultData.getTabData = function(){
  return {
    name: '',
    title: '',
    id: null,
    grandFatherId: null,
    data: {
      tableData: []
    }
  }
}

DefaultData.getGrandFatherId = () => {
  return 10000
}

export default {
  name: 'CustomStockPool',
  components: {
    StockSearch,
    CategoryListForStockPool
  },
  data () {
    return {
      addSymbolObj: {
        symbol: '',
        name: '',
        date: ''
      },
      inputValue: '',
      searchLoading: false,
      resultOptions: [],
      // timeout:  null,
      editableTabs: [
        // {
        //   name: '0',
        //   title: 'tab1',
        //   id: 29,
        //   grandFatherId: 3,
        //   data: {
        //     tableData: [
        //       {
        //         symbol: 'aaa',
        //         name: 'xxx', 
        //         date: 'ccc'
        //       },
        //       {
        //         symbol: 'hhh',
        //         name: 'xxx', 
        //         date: 'ccc'
        //       }
        //     ]
        //   }
        // }
      ],
      editableTabsValue: '0',
      tabIndex: 0
    }
  },
  computed: {
    currentTabData(){
      // console.log('fdddd', find(this.editableTabs, {name: this.editableTabsValue}));
      return find(this.editableTabs, {name: this.editableTabsValue}) || DefaultData.getTabData()
    }
  },
  mounted(){

  },
  methods: {
    remoteMethod(query){
      if (query !== '') {
        this.searchLoading = true;
        urlObj.post(urlObj.apiStockSearch, {key: query}, res => {
          this.searchLoading = false;
          this.resultOptions = res.data
        })
        // setTimeout(() => {
        //   
        // }, 200);
      } else {
        this.resultOptions = [];
      }
    },
    refreshPoolName(name){ //编辑已选中节点，更新tab名称
      const index = findIndex(this.editableTabs, {name: this.editableTabsValue})
      const tab = this.editableTabs[index]
      tab.title = name
      this.editableTabs.splice(index, 1, tab)
    },
    deleteCategory(parent, id, selectedId){
      // debugger
      //删除tabs里的tab
      const index = findIndex(this.editableTabs, {id})
      this.editableTabs.splice(index, 1)

      if(id !== selectedId) { //删除的不是选中项
        return
      }
      //选中未删除项
      if(parent.children.length > 0){
        this.$refs.categorylist.checkCategory([parent.categoryid, parent.children[0].categoryid])
      }else{
        this.$refs.categorylist.checkCategory(null)
      }
    },
    changeCategory(category, categoryid){
      // console.log('changeCategory::', category, categoryid);
      urlObj.get(`${urlObj.apiStockGroup}${categoryid}`, {}, res => {
        let tabItem = {
          name: this.tabIndex+'',
          title: category.name,
          id: category.categoryid,
          grandFatherId: DefaultData.getGrandFatherId(),
          data: {
            tableData: res.data.members
          }
        }
        if(findIndex(this.editableTabs, {id: tabItem.id}) === -1){
          this.editableTabs.push(tabItem)
          this.editableTabsValue = tabItem.name
          this.tabIndex++
        }else{
          console.log('从编辑来');
          tabItem = find(this.editableTabs, {id: categoryid}) 
          this.editableTabsValue = tabItem.name
        }
        // this.$message('查询成功')
      })
      
    },
    deleteRow(index, rows) { //删除行
      const row = rows[index]
      const groupId = this.currentTabData.id
      // console.log('>>>>',row);
      urlObj.dele(`${urlObj.apiStockGroup}${groupId}/member/delete/${row.id}`, res => {
        if(res.code === 200){
          rows.splice(index, 1);
          this.$message('删除成功')      
        }else{
          this.$message('删除失败')      
        }
      })
      // setTimeout(() => {
      //   rows.splice(index, 1);
      //   this.$message('删除成功')  
      // }, 1000);
      
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
        this.$refs.categorylist.checkCategory([10000, tab.id], 'elTab')
      }else{
        this.$refs.categorylist.checkCategory()
      }
    },
    handleTabClick(tab, event){
      console.log('ccc::', tab);
      const tabData = find(this.editableTabs, {name: tab.name})
      this.$nextTick(() => {
        this.$refs.categorylist.checkCategory([10000, tabData.id], 'elTab')
      })
    },
    // getPoolDetail(id){
    //   urlObj.get(`${urlObj.apiStockGroup}id`, {}, res => {

    //   })
    // },
    addSymbol(inputValue){
      this.inputValue = inputValue
      console.log('选中那个：', this.inputValue);
      const data = {
        name: this.inputValue.name,
        symbol: this.inputValue.symbol,
        date: parseInt(moment().format('YYYYMMDD'))
      }
      urlObj.post(`${urlObj.apiStockGroup}${this.currentTabData.id}/member/add`, data, res => {
        if(res.code === 200){
          this.$message('添加成功')
          data.id = res.data.id
          const index = findIndex(this.currentTabData.data.tableData, {id: data.id})
          if(index === -1){
            this.currentTabData.data.tableData.push(data)
          }
          
        }else{
          this.$message('请不要重复添加')
        }
      })
      
    }
  }
}
</script>

<style lang="less">
@import '../../../assets/css/commonStyle.less';
.elTabsRun{
  margin-top: -30px;
}
.customStockPoolWrap{
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

        @inputWrapHeight: 47px;
        .tableWrap{
          width: 100%;
          height: calc(100% - @inputWrapHeight);
          border-top: 1px solid #EBEEF5;
          box-sizing: border-box;

          .el-button--text{
            color: #eb6100;
            font-size: 14px;
          }
        }
        
      }
    }
  }
}
</style>

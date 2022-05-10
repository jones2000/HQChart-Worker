<template>
  <div class="boxsWrap" ref='boxsWrap'>
    <div class="tablesWrap">
      <div class="table" v-for="(oneTableData, indexTable) in currentPageTableData" :key="indexTable">
        <div class="row" v-for="(rowdata, indexRow) in oneTableData" :key="indexRow">
          <div class="col" v-for="(col, indexCol) in rowdata" :key="indexCol" :style="{width: col.width+'px', textAlign: col.align, paddingRight: col.paddingRight+'px', paddingLeft: col.paddingLeft+'px',}">{{col.text}}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import urlObj from '../utils/urlObj'
import {debounce} from 'lodash'

export default {
  name: 'MultiColTable',
  props: ['symbol','apiDataType'],
  data () {
    return {
      tableData: [],
      tableColWidths: [100,100],
      rowCount: 10,
      PageIndex: 1,
      pageSize: 10,
      currentPageTableData: [],
      firstTableWidth: 0, //调整padding前，table的宽度
      isNeedFillHorizon: false,
      headerAry: []
    }
  },
  mounted(){
    // const oneRowHeight = 31
    // this.rowCount = this.getRowCount(oneRowHeight)
    console.log('this.rowCount:', this.rowCount);

    this.queryApiData()

    window.onresize = debounce(
      () => { //重置水平间距
        this.currentPageTableData = this.getCurrentPageTableData()
        if(this.currentPageTableData.length > 0){
          this.resizeCol()
        }
      }
      ,500
    )
    window.onwheel = (e) => {
      if(e.deltaY > 0){
        //数据下一页
        this.getNextPage()
      }else{
        this.GetLastPage()
      }
      // console.log('滚轮滚动', e.deltaY);
    }
    window.onkeydown = (e) => {
      // console.log('键盘按下')
      var keyID = e.keyCode ? e.keyCode : e.which;
      switch(keyID)
      {
        case 38:    //up
          this.GetLastPage()
          //不让滚动条滚动
          this.preventDefaultFun()
          break;
        case 40:    //down
          this.getNextPage()
          //不让滚动条滚动
          this.preventDefaultFun()
          break;
      }
    }
  },
  watch: {
    symbol(){
      this.queryApiData()
    }
  },
  methods: {
    preventDefaultFun(e){
      if(e.preventDefault) e.preventDefault();
      else e.returnValue = false;
    },
    getPageCount(){ //分页页数
      let totalPage = 1
      const tableCount = this.getTableCount()
      const pageDataNum = this.rowCount * tableCount
      const len = this.tableData.length
      if(pageDataNum < len) {
        totalPage = len % pageDataNum === 0 ? len / pageDataNum : Math.floor(len / pageDataNum) + 1
      }

      return totalPage
    },
    getNextPage(){
      const page = this.PageIndex
      const totalPage = this.getPageCount()
      if(page + 1 <= totalPage){
        this.PageIndex = page + 1
        this.currentPageTableData = this.getCurrentPageTableData()
      }
    },
    GetLastPage(){
      const page = this.PageIndex
      if(page > 1){
        this.PageIndex = page - 1
        this.currentPageTableData = this.getCurrentPageTableData()
      }
    },
    getRowCount(rowHeight){
      const boxsWrap = this.$refs.boxsWrap
      return Math.floor(boxsWrap.clientHeight / rowHeight - 1) //预留一行，头部行
    },
    queryApiData(){
      switch(this.apiDataType){
        case 3: //码表
          this.isNeedFillHorizon = true
          this.getCodeListData()
          break;
        case 5:   //股本
          this.getCapitalData()
          break;
      }
    },
    getCapitalData(){
      urlObj.get(`${urlObj.apiStockCapital}?symbol=${this.symbol}`, {}, res => {
        try {
          const {data, metainfo} = res
          metainfo.Date = '日期'
          const newData = this.formatCapitalData(data)

          if(newData.length > 0){
            this.getTableData(newData, metainfo)
          }
        } catch (error) {
          this.$message(error.message)
        }
        

      }, res => {
        this.$message('接口状态异常')
      })
      
    },
    formatCapitalData(data){
      const len = data.Date.length
      const keysAry = [...Object.keys(data)]
      const tableData = []
      for (let index = 0; index < len; index++) {
        let tableRow = {}
        for (let j = 0; j < keysAry.length; j++) {
          const keyName = keysAry[j];
          tableRow[keyName] = keyName !== 'Date' ? Number(data[keyName][index]).toFixed(2) : data[keyName][index]
        }
        tableData.push(tableRow)
      }

      return tableData
    },
    getCodeListData(){
      urlObj.get(urlObj.apiStockSymbollist, {}, res => {
        const {data} = res
        if(data.length > 0){
          this.getTableData(data)
        }
      }, res => {
        this.$message('接口状态异常')
      })

      
    },
    getHeaderAry(rowObj, apiMetaInfo){ //通过对象的key，计算有多少列
      const keysAry = [...Object.keys(rowObj)]
      let metainfo = {
        symbol: '证券代码',
        name: '证券名称'
      }
      if(apiMetaInfo){
        metainfo = apiMetaInfo
      }
      let header = []
      keysAry.forEach((key, index) => {
        const text = metainfo[key]
        const colObj = this.getColObj(text, index, keysAry.length)
        header.push(colObj)
      })
      // console.log('header:', header);
      return header
    },
    getEmptyRow(rowObj){ //获取占位行
      const keysAry = [...Object.keys(rowObj)]
      const colCounts = keysAry.length
      const emptyRow = []
      for (let i = 0; i < colCounts; i++) {
        emptyRow.push('')
        
      }
      return emptyRow
    },
    getColObj(text, index, length){  //获取列显示值，样式
      let colObj
      switch(this.apiDataType){
        case 3: //码表
          colObj = {
            text,
            width: 70,
            align: 'left',
            paddingRight: 10,
            paddingLeft: 10,
          }
          break;
        case 5: 
          colObj = {
            text,
            width: index === 0 ? 80 : 130,
            align: index === 0 ? 'left' : 'right',
            paddingRight: 10,
            paddingLeft: 10,
          }
          break;
      }
      return colObj
    },
    setDefaultPading(paddingWidth){ //将padding重置
      // const oldPaddingWidth = this.currentPageTableData[0][0][0].paddingRight
      const oldPaddingWidth = 10
      const len = this.currentPageTableData.length
      for (let i = 0; i < len; i++) {
        const tableObj = this.currentPageTableData[i]
        const len2 = tableObj.length
        for (let j = 0; j < len2; j++) {
          const rowObj = tableObj[j];
          const len3 = rowObj.length
          for (let k = 0; k < len3; k++) {
            const colObj = rowObj[k];
            colObj.paddingRight = oldPaddingWidth + paddingWidth
            colObj.paddingLeft = oldPaddingWidth + paddingWidth

            // console.log('colObj：', colObj);
          }
        }
        
      }
    },
    getCurrentPageTableData(){ //截取当前页数据
      const pageTableData = []
      const oneRowHeight = 31
      const rowCount = this.getRowCount(oneRowHeight)
      this.rowCount = rowCount
      const page = this.PageIndex
      const tableData = this.tableData
      let tableCount = this.getTableCount()
      
      
      const pageSize = tableCount * this.rowCount
      this.pageSize = pageSize
      const start = (page - 1) * pageSize
      const end = page * pageSize > tableData.length ? tableData.length : page * pageSize
      const contentData = tableData.slice(start, end)
      // debugger
      // console.log('contentData:', contentData.length, rowCount, contentData.length / rowCount === 0);
      const realTableCount = contentData.length % rowCount === 0 ? contentData.length / rowCount : Math.floor(contentData.length / rowCount)+1
      if(realTableCount <= tableCount){
        tableCount = realTableCount
      }
      // console.log('real tableCount:', tableCount)
      for (let i = 0; i < tableCount; i++) {
        const contentDataItemStart = i * rowCount
        const contentDataItemEnd = (i + 1) * rowCount
        let contentDataItem = contentData.slice(contentDataItemStart, contentDataItemEnd)
        contentDataItem.unshift(this.headerAry)
        pageTableData.push(contentDataItem)
      }
      return pageTableData
    },
    getTableCount(){ //当前页可以显示的表的数量
      const tableWidth = this.firstTableWidth !== 0 ? this.firstTableWidth : this.getOneTableWidth()
      // console.log('tableWidth::', tableWidth);
      const count = tableWidth !== 0 ? Math.floor(window.innerWidth / tableWidth) : 0
      return count
    },
    getOneTableWidth(){ //获取一个表的宽度
      let tableWidth = 0

      if(this.tableData.length > 0){
        const rowData = this.tableData[0]
        for (let i = 0; i < rowData.length; i++) {
          const colObj = rowData[i];
          tableWidth += colObj.width + colObj.paddingRight + colObj.paddingLeft
        }

        const borderWidth = 1
        tableWidth += borderWidth
        // console.log('tableWidth::', tableWidth);
      }

      this.firstTableWidth = tableWidth
      return tableWidth
    },
    getColsCountInOneTable(){ //一个表有几列
      let count = 0
      if(this.tableData.length > 0){
        count = this.tableData[0].length
      }
      return count
    },
    resizeCol(){//重置水平间距
    // return
    // debugger
      const tableWidth = this.firstTableWidth !== 0 ? this.firstTableWidth : this.getOneTableWidth()
      const tableCount = this.getTableCount()
      const realWidth = tableCount * tableWidth
      const paddingNum = this.getColsCountInOneTable() * 2 * tableCount
      const paddingWidth = (window.innerWidth - realWidth) / paddingNum
      // console.log('增加的padding:', paddingWidth);
      this.setDefaultPading(paddingWidth)
      // const oldPaddingWidth = this.currentPageTableData[0][0][0].paddingRight
      // // console.log('oldPaddingWidth:', oldPaddingWidth);
      // const len = this.currentPageTableData.length
      // for (let i = 0; i < len; i++) {
      //   const tableObj = this.currentPageTableData[i]
      //   const len2 = tableObj.length
      //   for (let j = 0; j < len2; j++) {
      //     const rowObj = tableObj[j];
      //     const len3 = rowObj.length
      //     for (let k = 0; k < len3; k++) {
      //       const colObj = rowObj[k];
      //       colObj.paddingRight = oldPaddingWidth + paddingWidth
      //       colObj.paddingLeft = oldPaddingWidth + paddingWidth

      //       // console.log('colObj：', colObj);
      //     }
      //   }
        
      // }
    },
    addEmptyRowForLastTable(needAddRowCount, rowObj, lastTable){ //给最后一个表添加空行
      //最后一个表，不足rowCount，其他行补空值
      if(needAddRowCount > 0){
        // let needAddRow = (i + 1) * this.rowCount - counts
        // let lastTable = this.tableData[this.tableData.length - 1]
        for (let j = 0; j < needAddRowCount; j++) {
          const emptyRow = this.getEmptyRow(rowObj)
          lastTable.push(emptyRow)
        }
        // this.tableData.splice(this.tableData.length - 1, 1, lastTable)
      }
    },

    getTableData(newData, metainfo){
      // debugger
      const headerAry = this.getHeaderAry(newData[0], metainfo)
      this.headerAry = headerAry
      this.tableData = newData.map(row => {
        let cols = []
        let rowKeysAry = [...Object.keys(row)]
        let rowKeyLen = rowKeysAry.length
        for (let j = 0; j < rowKeyLen; j++) {
          const rowKeyItem = rowKeysAry[j];
          const text = row[rowKeyItem]
          const colObj = this.getColObj(text, j, rowKeyLen)
          cols.push(colObj)
        }
        return cols
      })
      // console.log('this.tableData', this.tableData);
      this.currentPageTableData = this.getCurrentPageTableData()
      // console.log('this.currentPageTableData:', this.currentPageTableData);
      if(this.isNeedFillHorizon){
        this.resizeCol() //调整列宽，尽量铺满横屏
      }

    }
  }

}
</script>

<style lang="less" scoped>
.boxsWrap{
  width: 100%;
  height: 100%;
  overflow: auto;
  font-size: 14px;
  color: #606266;

  .tablesWrap{
    display: flex;

    .table{
      border-top: 1px solid #EBEEF5;
      border-bottom: 1px solid #EBEEF5;
      border-right: 1px solid #EBEEF5;

      &:nth-child(n+2){
        border-left: none;
      }

      .row {
        border-bottom: 1px solid #EBEEF5;
        display: flex;

        &:last-child{
          border-bottom: none;
          border-right: none;
        }

        .col {
          // box-sizing: border-box;
          line-height: 30px;
          height: 30px;
          padding:  0 10px;
          // width: 100px; //根据实际需要来，可以会变宽



          
        }
      }
    }
  }


}
</style>
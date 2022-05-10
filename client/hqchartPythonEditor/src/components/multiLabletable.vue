<template>
  <div class="boxsWrap" ref='boxsWrap'>
    <div class="tablesWrap">
      <div class="table" v-for="(oneTableData, indexTable) in tableData" :key="indexTable">
        <div class="row" v-for="(rowdata, indexRow) in oneTableData" :key="indexRow">
          <div class="col label">{{rowdata.label}}</div>
          <div class="col value">{{rowdata.value}}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import urlObj from '../utils/urlObj'

export default {
  name: 'MultiLabletable',
  props: ['symbol'],
  data () {
    return {
      tableData: [
        // [
        //   {
        //     label: '飞飞飞凤凤',
        //     value: '1122'
        //   },
        //   {
        //     label: '飞飞飞凤凤',
        //     value: '1122'
        //   },
        //   {
        //     label: '飞飞飞凤凤',
        //     value: '1122'
        //   },
        // ]
      ],
      labelWidth: 280,
      valueWidth: 200,
      rowCount: 15,
    }
  },
  mounted(){
    this.getFinaceData()
  },
  watch: {
    symbol(){
      this.getFinaceData()
    }
  },
  methods: {
    getFinaceData(){
      urlObj.get(`${urlObj.apiStockFinance}?symbol=${this.symbol}`, {}, res => {
        const {data, metainfo} = res
        const keysAry = [...Object.keys(data)]
        let newData = []
        keysAry.forEach(key => {
          newData.push(
            {
              label: key !== 'Date' ? `${key}(${metainfo[key]})` : '日期',
              value: data[key] !== null ? (key !== 'Date' ? Number(data[key]).toFixed(2) : data[key]) : '--'
            }
          )
        })


        this.getTableData(newData)
      }, res => {
        this.$message('接口状态异常')
      })

      

    },
    getTableData(newData){
      this.tableData = []
      let counts = newData.length
      let tableCount = counts /this.rowCount === 0 ? counts /this.rowCount : parseInt(counts /this.rowCount) + 1
      for (let i = 0; i < tableCount; i++) {
        const startIndex = i * this.rowCount
        let endIndex = (i + 1) * this.rowCount
        if(endIndex > counts) {
          endIndex = counts
        }
        const rows = newData.slice(startIndex, endIndex)
        this.tableData.push(rows)

        //最后一个表，不足rowCount，其他行补空值
        if((i + 1) * this.rowCount > counts){
          let needAddRow = (i + 1) * this.rowCount - counts
          let lastTable = this.tableData[this.tableData.length - 1]
          for (let j = 0; j < needAddRow; j++) {
            lastTable.push({
              label: '',
              value: ''
            })
          }
          this.tableData.splice(this.tableData.length - 1, 1, lastTable)
        }

      }

      console.log(this.tableData);
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

      &:nth-child(n+2){
        border-left: none;
      }

      .row {
        border-bottom: 1px solid #EBEEF5;
        display: flex;

        &:last-child{
          border-bottom: none;
        }

        .col {
          box-sizing: border-box;
          line-height: 30px;
          height: 30px;
          padding:  0 10px;
        }

        .label{
          width: 280px;  
        }
        .value{
          width: 200px;
          text-align: right;
          padding-right: 60px;
        }
      }
    }
  }


}
</style>
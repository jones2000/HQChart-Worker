<template>
  <div class="indexSearchWrap">
    <div class="target-content">
      <div class="target-left">
          <input type="text" placeholder="请输入" v-model="inputValue">
          <div class="groupWrap">
            <ul>
              <li :class="{'active-list': index === groupIndex}" v-for="(item, index) in indexData" :key="index" @click="changeGroup(index)">{{item.name}}</li>
              <!-- <li>超买超卖型</li>
              <li>趋势型</li>
              <li>成交量型</li>
              <li>均线型</li>
              <li>路径型</li> -->
              
            </ul>
          </div>
          
      </div>
      <div class="target-right">
          <ul v-if="filterStrategies.length > 0">
            <li v-for="(item, index) in filterStrategies" :key="index" :class="{'active-list':activeIndexId === item.id}" @click="selectOneIndex(item)">{{item.name}}</li>
            <!-- <li id="市场择时" class="active-list">市场择时</li>
            <li id="融资占比">融资占比</li> -->
          </ul>
          <div class="noData" v-else>暂无数据</div>
      </div>
    </div>
  </div>
</template>

<script>
import urlObj from '../utils/urlObj'

export default {
  name: 'IndexSearch',
  computed: {
    // filterStrategies(){
    //   const currentGroupObj = this.indexData[this.groupIndex]
    //   const result = currentGroupObj ? currentGroupObj.strategies : []
    //   return result;
    // }
  },
  watch: {
    inputValue(query){
      let result = []
      this.indexData.forEach(group => {
        group.strategies.forEach(item => {
          var reg = new RegExp(query,'i');
          if(item.name.search(reg) > -1){
            result.push(item)
          }
        })
      })
      this.groupIndex = -1
      this.filterStrategies = result
    }
  },
  data () {
    return {
      groupIndex: 0,
      activeIndexId: 44,
      inputValue: '',
      filterStrategies: [],
      indexData: [
        // {
        //     "id": 23,
        //     "name": "财务因子策略",
        //     "strategies": []
        // }
      ]
    }
  },
  mounted(){
    urlObj.get(urlObj.apiGroupList, {}, res => {
      if(res.code === 200){
        this.indexData = res.data
        this.filterStrategies = this.indexData[this.groupIndex].strategies
      }else{
        console.log('获取指标数据异常');
        this.indexData = []
        this.filterStrategies = []
      }

    }, res => {
      console.log('获取指标数据异常');
      this.indexData = []
      this.filterStrategies = []
    })
  },
  methods: {
    changeGroup(index){
      this.groupIndex = index
      this.filterStrategies = this.indexData[this.groupIndex].strategies
    },
    selectOneIndex(item){
      this.activeIndexId = item.id
      this.$emit('selectOneIndex', item)
    }
  }
}
</script>

<style lang="less" scoped>
.indexSearchWrap{
  width: 100%;
  height: 600px;
  border: 1px solid #c8d2db;

  .target-content{
      height:100%;
      display: flex;
  }
  .target-left{
      width:200px;
      height: 100%;
      border-right: 1px solid #c8d2db;
      box-sizing: border-box;

      .groupWrap{
        height: calc(100% - 40px);
        overflow: auto;
        border-top:1px solid #c8d2db;
      }
  }

  .target-left input{
      margin-left: 10px;
      height: 40px;
      line-height: 40px;
      border: none;
      font-size: 14px;
  }
  .target-left ul{
      border-top: none;
      list-style: none;
      padding:10px;
      box-sizing: border-box;
  }
  .target-left ul li{
      font-size: 13px;
      line-height: 30px;
      color: #757d81;
      cursor: pointer;
  }
  .active-list{
      color: #1295d9!important;
  }

  .target-right{
      width: calc(100% - 200px);
      height: 100%;
      overflow-y: auto;

      .noData{
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
      }
  }
  .target-right ul{
    width: 100%;
    max-height: 100%;
      // width: 590px;
      // max-height: 450px;
      // overflow: auto;
      padding-top: 10px;
      padding-left: 20px;
      box-sizing: border-box;

      &::after{
        content: '';
        width: 0;
        height: 0;
        clear: both;
      }
  }
  .target-right ul li{
      // display: inline-block;
      margin-top: 5px;
      margin-left: 10px;
      list-style: none;
      width: 175px;
      line-height: 30px;
      text-align: left;
      float: left;
      cursor: pointer;
  }
}
</style>
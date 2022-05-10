<template>
  <div class="inputWrap" :class="{noPaddingStyle:noPadding}">
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
      :loading="searchLoading"
      @change="selectStockFun"
      >
      <el-option
        v-for="item in resultOptions"
        :key="item.symbol"
        :label="item.name"
        :value="item">
        {{item.symbol}}&emsp;{{item.name}}
      </el-option>
    </el-select>
    <el-button size="small" type="primary" @click='addSymbol' v-if="isShowBtn">{{btnText ? btnText : '添加'}}</el-button>
  </div>
  
</template>

<script>
import urlObj from '../utils/urlObj'

export default {
  name: 'StockSearch',
  props: ['isShowBtn', 'btnText', 'noPadding'],
  data () {
    return {
      inputValue: {
        id: '',
        name: '',
        symbol: ''
      },
      searchLoading: false,
      resultOptions: []
    }
  },
  methods: {
    selectStockFun(){
      if(!this.isShowBtn){
        this.$emit('addSymbol', this.inputValue)
      }
      // console.log('选中哪个：', this.inputValue);
    },
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
    addSymbol(){
      // console.log('现在是什么：', this.inputValue);
      if(this.inputValue.id !== '' && this.inputValue.name !== '' && this.inputValue.symbol !== '') {
        this.$emit('addSymbol', this.inputValue)
      }else{
        this.$message('请搜索股票')
      }
        
    },
    // selectOptionFun(item){
    //   console.log('选择谁:', item);
    // }
  }
}
</script>

<style lang="less">
@inputWrapHeight: 47px;
.inputWrap{
  display: flex;
  justify-content: flex-end;
  height: @inputWrapHeight;
  align-items: center;
  padding: 0 12px 15px 12px;
  box-sizing: border-box;

  &.noPaddingStyle{
    padding: 0;
  }

  .el-input{
    width: 204px;
    margin-right: 4px;
  }
}
</style>
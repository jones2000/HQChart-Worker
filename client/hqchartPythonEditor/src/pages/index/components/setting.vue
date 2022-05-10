<template>
  <div class="settingWrap">
    <div class="panelWrap">
      <div class="title">数据设置</div>
      <el-form ref="form" label-width="123px" size="small" label-position="left">
        <el-form-item :label="`${formItem.name}目录：`" v-for="(formItem, index) in form" :key="index">
          <el-input v-model="formItem.dataPath"></el-input><file-path :index='index' :domId='`seletdata${index}`' @getpath='getDatapath'></file-path>
        </el-form-item>
        <!-- <el-form-item label="分钟K线数据目录:">
          <el-input v-model="form.minutePath"></el-input><file-path domId='seletminute' @getpath='geMinutepath'></file-path>
        </el-form-item>
        <el-form-item label="码表数据目录:">
          <el-input v-model="form.codeTablePath"></el-input><file-path domId='seletCodeTable' @getpath='getCodeTablepath'></file-path>
        </el-form-item> -->
        <el-form-item>
          <el-button type="primary" @click="onSubmit">保存</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import FilePath from '../../../components/filePath.vue'
// import urlObj from '../../../utils/urlObj.js'
import Service from './categoryService.js'
export default {
  components: {
    FilePath
  },
  name: 'Setting',
  data() {
    return {
      form: []
    }
  },
  mounted() {
    Service.getHqchartConfig(this)
  },
  methods: {
    getDatapath(value, index){
      this.form[index].dataPath = value
    },
    // geMinutepath(value){
    //   this.form.minutePath = value
    // },
    // getCodeTablepath(value){
    //   this.form.codeTablePath = value
    // },
    onSubmit() {
      // const formData = {
      //   codeTablePath: this.formatpath(this.form.codeTablePath),
      //   dataPath: this.formatpath(this.form.dataPath),
      //   minutePath: this.formatpath(this.form.minutePath)
      // }
      Service.saveHqchartConfig(this.form, this)
    },
    formatpath(str){
      return str.replace(/\\/g, '\\')
    }
  }
  
}
</script>

<style lang='less'>
@import '../../../assets/css/commonStyle.less';

.settingWrap{
  .panelWrap{
    padding: 48px 0 24px 0;
    margin-left: 119px;
    margin-right: 119px;
    border-bottom: @contentBorder;

    .title{
      font-weight: bold;
      line-height: 1;
      margin-bottom: 22px;
      padding-left: 4px;
    }

    .list{
      line-height: 40px;
      color: #526075;
      padding-left: 5px;

      .item{
        display: flex;
        .name{
          width: 93px;
          display: inline-block;
        }

        >div:first-child{
          padding-right: 25px;
        }
        .btnsWrap{
          padding-left: 57px;
        }
      }
    }

    .el-form-item--small .el-form-item__content{
      display: flex;
      align-items: center;
    }

    .el-form-item{
      padding-left: 5px;
    }

    .el-input{
      width: 316px;
      margin-right: 17px;
    }

    .el-input.is-active .el-input__inner, .el-input__inner:focus {
      border-color: #f19149;
    }

    .el-button--primary {
      background-color: #eb6100;
      box-shadow: -1px 6px 10px 0px 
        rgba(235, 97, 0, 0.26);
      border-radius: 4px;
      border: solid 1px #de432d;
    }
  }
}
</style>
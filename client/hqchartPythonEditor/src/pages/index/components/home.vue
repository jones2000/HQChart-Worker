<template>
  <div class="homeWrap" v-loading='loading'>
    <div class="panelWrap">
      <div class="title">基本信息</div>
      <div class="list">
        <div class="item">Hqchartpy2版本号：{{baseInfo.version}}</div>
        <div class="item">平台版本号：{{baseInfo.plateVersion}}</div>
        <div class="item">服务地址：{{baseInfo.host}}</div>
        <div class="item">端口：{{baseInfo.port}}</div>
        <div class="item">页面版本号：19250</div>
        <div class="item">py后台版本号：{{baseInfo.pythonVersion}}</div>
      </div>
    </div>
    <div class="panelWrap">
      <div class="title">数据状态</div>
      <div class="list">
        <div class="item" v-for="(status, index) in dataStatusAry" :key="index">
          <div><span class="name">{{status.name}}：</span><span class="count">{{status.counts}}</span>条&emsp;加载时间：{{status.loadTime || '--'}}</div>
          <div>最后更新时间：{{status.updateTime}}</div>
          <div class="isSaveWrap">缓存：{{status.isCache ? '是' : '否'}}</div>
          <div class="btnsWrap">
            <el-button type="primary" size="small" @click="synchronizationFun(status)" :disabled='status.syncStatus === 1 || status.loadStatus === 1'>同步</el-button>
            <el-button type="default" size="small" @click="loadingFun(status)" :disabled='status.loadStatus === 1 || status.syncStatus === 1'>加载</el-button>
            <el-button type="default" size="small" @click="goToDetailData(status)">浏览</el-button>
          </div>
          <div class="redText" v-if="status.type === 1 && status.loadStatus !== 1 && status.syncStatus !== 1">日线数据全部加载到内存需要2.5G以上的内存</div>
          <div class="progressWrap" v-if="status.syncStatus === 1 || (status.loadStatus === 1 && (status.type === 1 || status.type === 2))">
            <span class="taskname">{{status.taskname}}</span>
            <el-progress :percentage="status.percent"></el-progress>
          </div>
        </div>
      </div>
    </div>
    <div class="panelWrap">
      <div class="title">权限信息<span class="versionType">免费版</span></div>
      <el-form ref="form" :model="form" :rules="loginRules" label-width="85px" size="small">
        <el-form-item label="数据账号" prop="accout">
          <el-input v-model="form.accout" placeholder="请输入账号" :disabled='isLogin'></el-input>
        </el-form-item>
        <el-form-item label="数据密码" prop="psw">
          <el-input type="password" v-model="form.psw" placeholder="请输入密码" :disabled='isLogin'></el-input>
        </el-form-item>
        <el-form-item label="">
          <el-checkbox v-model="form.isSelectedAgreement" :disabled='isLogin'>我已阅读并同意 <span class="btn" @click="seeAgreementFun('one')">《隐私政策》</span>与<span class="btn" @click="seeAgreementFun('two')">《用户服务协议》</span></el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loginBtnFun">{{isLogin ? '退出':'登录'}}</el-button>
          <el-button type="default" @click="dialogVisible=true">注册</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="bottomWrap">
      郑重声明：本网站所刊载的所有资料及图表仅供参考使用。投资者依据本网站提供的信息、资料及图表进行金融、证券等投资所造成的盈亏与本网站无关。
    </div>

    <!-- 注册对话框 -->
    <el-dialog
      title="注册"
      :visible.sync="dialogVisible"
      width="30%"
    >
      <el-form class="registerForm" ref="registerForm" :rules="registerRules" :model="registerForm" label-width="72px" size="small">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="registerForm.phone" placeholder="请输入手机号"></el-input>
        </el-form-item>
        <el-form-item label="验证码" class="codeWrap" prop="code">
          <el-input v-model="registerForm.code" placeholder="请输入验证码"></el-input><el-button type="primary" @click="getCode">获取验证码</el-button>
        </el-form-item>
        <el-form-item label="密码" prop="psw">
          <el-input type="password" v-model="registerForm.psw" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label="">
          <el-checkbox v-model="registerForm.isSelectedAgreement">我已阅读并同意 <span class="btn" @click="seeAgreementFun('one')">《隐私政策》</span>与<span class="btn" @click="seeAgreementFun('two')">《用户服务协议》</span></el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit('registerForm', goRegister)">提交</el-button>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <!-- <el-button @click="dialogVisible = false">取 消</el-button> -->
        <!-- <el-button type="primary" @click="dialogVisible = false">确 定</el-button> -->
      </span>
    </el-dialog>


  </div>
</template>

<script>
import urlObj from '../../../utils/urlObj.js'
import Service from './categoryService.js'
import {clearCookie, getCookie, setCookie} from '../../../utils/tools'
import axios from 'axios'

function encode(str){
  return window.btoa(str)
}
function decode(str){
  return window.atob(str)
}

export default {
  name: 'Home',
  data () {
    return {
      form: {
        accout: '', //18672388569
        psw: '', //123456
        isSelectedAgreement: false
      },
      loginRules:{
        accout: [
          { required: true, message: '账号不能为空', trigger: 'blur' }
        ],
        psw: [
          { required: true, message: '密码不能为空', trigger: 'blur' }
        ]
      },
      registerForm: {
        phone: '',
        code: '',
        psw: '',
        isSelectedAgreement: true
      },
      registerRules:{
        phone: [
          { required: true, message: '手机号不能为空', trigger: 'blur' }
        ],
        code: [
          { required: true, message: '验证码不能为空', trigger: 'blur' }
        ],
        psw: [
          { required: true, message: '密码不能为空', trigger: 'blur' }
        ]
        // isSelectedAgreement: [
        //   { required: true, message: '同意协议', trigger: 'blur' }
        // ]
      },
      baseInfo: {
        host: '',
        port: 0,
        version: '',
        plateVersion: ''
      },
      loading: false,
      dataSyncStatus:['未同步','同步中','同步完成','同步失败'], //对应：syncStatus
      dataLoadStatus:['未加载','加载中','加载完成','加载失败'], //对应：loadStatus
      dataStatusAry: [],
      dialogVisible: false,
      isLogin: false,
      isSelectedAgreement: true,
      statusTimer: null,
      syncAry: [], //里面放入type值,记录‘同步’和‘加载’
      hasStatusData: false //是否已经拿到状态数据
    }
  },
  mounted() {
    // console.log('base64 加密测试：', encode('123456'));
    // console.log('base64 解密测试', decode('MTIzNDU2'));
    this.isLogin = getCookie('token') ? true : false
    // debugger
    if(!this.isLogin){
      //填充账号信息
      const account = localStorage.getItem('account') ? JSON.parse(localStorage.getItem('account')) : null
      if(account){
        this.form.accout = account.UserId
        this.form.psw = decode(account.Password)
      }
    }

    this.loading = true
    Service.getBaseInfo(this)
    Service.getDataStatus(this)

    
  },
  methods: {
    seeAgreementFun(type){
      switch(type){
        case 'one':
          window.open('./privacyStatement.html', '_blank')
          break;
        case 'two':
          window.open('./userAgreement.html', '_blank')
          break;
      }
      
    },
    loginBtnFun(){
      if(this.isLogin){
        this.exit()
      }else{
        if(!this.form.isSelectedAgreement){
          this.$message('请阅读并同意隐私政策与用户服务协议')
          return
        }
        this.onSubmit('form', this.goLogin)
      }
    },
    exit(){
      clearCookie('token')
      this.isLogin = false
    },
    onSubmit(formName, callback) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          // debugger
          callback()
        } else {
          // console.log('error submit!!');
          return false;
        }
      });
      
    },
    goLogin(){
      const data = {
        UserId: this.form.accout, 
        Password: encode(this.form.psw) //
      }
      axios.post(urlObj.apiLogin, data)
      .then(res => {
        res = res.data
        if(res.code === 0){
          this.isLogin = true
          setCookie('token', res.token)
          localStorage.setItem('account',JSON.stringify({UserId: this.form.accout,Password: encode(this.form.psw)}))
          if(!res.message) this.$message('登录成功')
          // location.reload()
          // console.log(res.Message);
        }else{
          this.$message.error(res.message)
        }
      })
      .catch(res => this.$message.error(res.message))
    },
    synchronizationFun(status) {
      if(status.syncStatus === 1) {
        this.$message(this.dataSyncStatus[status.syncStatus])
        return
      }
      const data = {
        type: status.type
      }
      Service.dataSync(data,this,status)
    },
    loadingFun(status) {
      if(status.loadStatus === 1) {
        this.$message(this.dataLoadStatus[status.loadStatus])
        return
      }
      const data = {
        type: status.type
      }
      Service.apiDataLoad(data,this,status)
    },
    goToDetailData(status){
      let type = status.type
      // if(type == 5) {
      //   type = 'a5' //解决url上type=5时，input不能输入的问题
      // }
      window.open(`./detailData.html?type=${type}`)
    },
    getCode(){
      const data = {
        "Phone": this.registerForm.phone,
        "Type": 10 //10:注册，10:登录，10:找回密码
      }
      axios.post(urlObj.apiGetVerificationCode, data)
      .then(res => {
        res = res.data
        if(res.code === 0){
          this.$message(res.message)
        }else{
          this.$message.error(res.message)
        }
      })
      .catch(res => this.$message.error(res.message))
    },
    goRegister(){
      if(!this.registerForm.isSelectedAgreement){
        this.$message('请阅读并同意隐私政策与用户服务协议')
        return
      }
      const data = {
        "Phone": this.registerForm.phone,
        "Password": encode(this.registerForm.psw),
        "VerificationCode": this.registerForm.code
      }
      axios.post(urlObj.apiRegister, data)
      .then(res => {
        this.dialogVisible = false
        res = res.data
        if(res.code === 0){
          this.$message(res.message)
        }else{
          this.$message.error(res.message)
        }
      })
      .catch(res => this.$message.error(res.message))
    }
  }
}
</script>

<style lang="less">
@import '../../../assets/css/commonStyle.less';

.homeWrap{
  font-size: 14px;
	color: #333;

  .bottomWrap{
    height: 30px;
    padding: 0 15px;
    font-size: 14px;
    color: red;
    box-sizing: border-box;
    border-top: @contentBorder;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .el-form-item .seeAgreementLink {
    color: #409EFF;
    cursor: pointer;
  }

  .panelWrap{
    padding: 48px 0 24px 0;
    margin-left: 119px;
    margin-right: 119px;
    border-bottom: @contentBorder;

    &:nth-child(3){
      border-bottom: none;
    }

    .btn{
      color: #eb6100;
      cursor: pointer;
    }

    .title{
      font-weight: bold;
      line-height: 1;
      margin-bottom: 22px;
      padding-left: 4px;

      .versionType{
        margin-left: 15px;
        color: red;
        font-size: 16px;
      }
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

        .count{
          width: 48px;
          display: inline-block;
        }

        .isSaveWrap{
          padding-left: 25px;
        }

        >div:first-child{
          padding-right: 25px;
        }
        .btnsWrap{
          padding-left: 57px;
        }
        .redText{
          padding-left: 25px;
          padding-right: 25px;
          color: red;
        }

        .progressWrap{
          width: 300px;
          display: flex;
          height: 40px;
          align-items: center;
          padding-left: 15px;
          box-sizing: border-box;

          @tasknameWidth: 200px;
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
            // width: 100%;
            width: calc(100% - @tasknameWidth);
          }
        }
      }
    }

    input[type='text'],
    input[type='password']
    {
      width: 250px;
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

    .el-button--primary.is-disabled{
      opacity: 0.5;
    }
  }

  .registerForm{
    .codeWrap .el-input{
      width: calc(100% - 102px);
      margin-right: 9px;
    }
    .btn{
      color: #eb6100;
      cursor: pointer;
    }
  }
}

</style>
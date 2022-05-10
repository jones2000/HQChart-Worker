<template>
  <div class="app">
    <div class="topWrap">
      <div class="logoWrap">
        <img src="../../assets/images/logo.png" alt="logo">
      </div>
      <div class="tabs">
        <div class="tab" v-for="(tab, index) in tabsAry" :key="index" :class="{active: activeIndex === index}" @click="changeTab(index,tab)">{{tab.Text}}</div>
      </div>
    </div>
     
    <div class="content" ref="content">
      <router-view></router-view>
    </div>
    <div class="bottomWrap" v-show="isShowBottomWrap">
      郑重声明：本网站所刊载的所有资料及图表仅供参考使用。投资者依据本网站提供的信息、资料及图表进行金融、证券等投资所造成的盈亏与本网站无关。
    </div>
  </div>
</template>

<script>
import * as Tools from '../../utils/tools.js'
export default {
  data () {
    return {
      tabsAry: [
        {
          Text: '首页(状态)',
          Link: '/home'
        },
        {
          Text: '设置',
          Link: '/setting'
        },
        {
          Text: '指标编辑',
          Link: '/indexEdit'
        },
        {
          Text: '策略编辑',
          Link: '/strategyEdit'
        },
        {
          Text: '策略运行',
          Link: '/strategyRun'
        },
        {
          Text: '自定义股票池',
          Link: '/customStockPool'
        },
      ],
      activeIndex: 0,
      isShowBottomWrap: true
    }
  },
  mounted() {
    if(Tools.getCookie('activeIndex')) {
      this.activeIndex = parseInt(Tools.getCookie('activeIndex')) 
      let link = this.tabsAry[this.activeIndex].Link
      this.$router.replace(link)
    }
    
    if(this.$route.path === '/home'){
      this.isShowBottomWrap = false
      //重新设置内容区高度
      this.$nextTick(() => {
        this.$refs.content.style.height = window.innerHeight - 44 + 'px'
      })
    }else{
      this.isShowBottomWrap = true
      this.$nextTick(() => {
        this.$refs.content.style.height = window.innerHeight - 44 - 30 + 'px'
      })
    }
  },
  updated(){
    if(this.$route.path === '/home'){
      this.isShowBottomWrap = false
      //重新设置内容区高度
      this.$nextTick(() => {
        this.$refs.content.style.height = window.innerHeight - 44 + 'px'
      })
    }else{
      this.isShowBottomWrap = true
      this.$nextTick(() => {
        this.$refs.content.style.height = window.innerHeight - 44 - 30 + 'px'
      })
    }
  },
  methods: {
    changeTab(index,tab) {
      this.activeIndex = index
      Tools.setCookie('activeIndex', this.activeIndex)
      this.$router.replace(tab.Link)
    }
  }
}
</script>

<style lang="less">
@import '../../assets/css/commonStyle.less';

.app{
  height: 100%;

  .topWrap{
    display: flex;
    height: 44px;
    width: 100%;
    border-bottom: @contentBorder;
    box-sizing: border-box;

    .logoWrap{
      width: 120px;
      height: 100%;
      background-color: #de432d;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .tabs{
      width: 100%;
      height: 43px;
      display: flex;
      padding: 0 30px;
      box-sizing: border-box;

      .tab{
        height: 100%;
        line-height: 43px;
        padding: 0 30px;
        font-size: 15px;
        color: #666;
        position: relative;
        cursor: pointer;

        &::after{
          position: absolute;
          left: 0;
          top: 100%;
          content: ' ';
          height: 1px;
          width: 100%;
          background-color: transparent;
        }

        &.active {
          color: #ec6941;
        }
        &.active::after{
          background-color: #ec6941;
        }
      }
    }
  }

  

  .content{
    height: calc(100% - 44px - 30px);
    overflow-y: auto;
  }

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
}
</style>
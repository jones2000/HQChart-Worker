import Promise from 'promise-polyfill'
import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
// import router from './router'

if (!window.Promise) {  
  window.Promise = Promise;  
}  

Vue.use(ElementUI)

new Vue({
  el: '#app',
  // router,
  render: h => h(App),
  beforeCreate() {
    Vue.prototype.$bus = this  //安装全局事件总线
  }
})

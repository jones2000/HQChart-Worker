import Vue from 'vue'
import VueRouter from 'vue-router'

import Home from './components/home.vue'
import Setting from './components/setting.vue'
import IndexEdit from './components/indexEdit.vue'
import StrategyEdit from './components/strategyEdit.vue'
import StrategyRun from './components/strategyRun.vue'
import CustomStockPool from './components/customStockPool.vue'

// const SysLog = () => import(/*webpackChunkName: "managerhq"*/ '@/secondPages/utshqsrv/sysLog.vue')
// const ApiUse = () => import(/*webpackChunkName: "managerhq"*/ '@/secondPages/apiUse/apiUse.vue')


Vue.use(VueRouter)

//解决编程式路由往同一地址跳转时会报错的情况
const originalPush = VueRouter.prototype.push
const originalReplace = VueRouter.prototype.replace
//push
VueRouter.prototype.push = function push(location, onResolve, onReject) {
    if (onResolve || onReject) return originalPush.call(this, location, onResolve, onReject)
    return originalPush.call(this, location).catch(err => err)
}
//replace
VueRouter.prototype.replace = function push(location, onResolve, onReject) {
    if (onResolve || onReject) return originalReplace.call(this, location, onResolve, onReject)
    return originalReplace.call(this, location).catch(err => err)
}

let routes = [
  {
    path:'/',
    redirect:'/home'
  },
  {
    path: '/home',
    component: Home
  },
  {
    path: '/setting',
    component: Setting,
    // children: [
    //   {
    //     path: 'sysCheck',
    //     component: SysCheck
    //   }
    // ]
  },
  {
    path: '/indexEdit',
    component: IndexEdit
  },
  {
    path: '/strategyEdit',
    component: StrategyEdit
  },
  {
    path: '/strategyRun',
    component: StrategyRun
  },{
    path: '/customStockPool',
    component: CustomStockPool
  }
]

let router = new VueRouter({
  routes
})

// router.beforeEach((to, from, next) => {
//   const isAuthenticated = Tools.getCookie('kword')
//   if (to.path !== '/' && !isAuthenticated) next({ name: 'login' })
//   else next()
// })

export default router

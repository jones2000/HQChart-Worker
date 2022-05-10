import urlObj from "../../../utils/urlObj"
import {find, findIndex} from 'lodash'


export default {
  addOneGroup(category, vueC){
    const data = {
      "name": vueC.text
    }
    urlObj.post(urlObj.apiGroupCreate, data, res => {
      if(res.code === 200){
        category.name = res.data.name
        category.categoryid = res.data.id
        category.creating = false

        vueC.sending = false
        vueC.text = ''
        vueC.createType = ''
        vueC.$message('创建成功')

        //新建分组成功，并且只包含一个分组，说明是首次创建，需要隐藏首次创建DOM
        if(vueC.categoryList.length === 1){
          vueC.isShowNoCategory = false
        }
      }else{
        vueC.$message('创建失败')
      }
    })
  },
  addOneStrategy(category, vueC, callback){ //创建一个指标
    const data = {
      "outArgs":[],
      "args": [], 
      "description": "", 
      "floatPrecision": "0", 
      "isMainIndex": false, 
      "groupId": category.groupId,
      "name": vueC.text, 
      "script": ""
    }
    urlObj.post(urlObj.apiStrategyCreate, data, res => {
      if(res.code === 200){
        category.name = res.data.name
        category.categoryid = res.data.id
        category.creating = false

        vueC.sending = false
        vueC.text = ''
        vueC.createType = ''

        callback([category.groupId, category.categoryid])
        vueC.$message('创建成功')
      }else{
        vueC.$message('创建失败')
      }
    })
  },
  addOneSelectStockStrategy(category, data, vueC, callback){ //创建一个选股策略
    urlObj.post(urlObj.apiAlgorithmCreate, data, res => {
      if(res.code === 200){
        category.name = res.data.name
        category.categoryid = res.data.id
        category.creating = false

        vueC.sending = false
        vueC.text = ''
        vueC.createType = ''

        callback([category.groupId, category.categoryid])
        vueC.$message('创建成功')
      }else{
        vueC.$message('创建失败')
      }
    })
  },
  updateOneGroup(category, vueC){
    const data = {
      "name": vueC.text
    }
    urlObj.post(`${urlObj.apiGroupOpr}${category.categoryid}`, data, res => {
      if(res.code === 200){
        category.name = res.data.name
        category.editing = false

        vueC.sending = false
        vueC.text = ''
        vueC.$message('修改成功')
      }else{
        vueC.$message('修改失败')
      }
    })
  },
  updateOneStrategy(category, newData, vueC, callback, explainArguments){ //explainArguments - 通达信语法解析出来的
    let needNOticeParent = false
    if(vueC && vueC.text && category.name !== vueC.text) needNOticeParent = true
    const data = {
      "outArgs": explainArguments || [],
      "args": newData ? (newData.args ? newData.args : category.args) : category.args,
      "description": "",
      "floatPrecision": "0",
      "id": category.categoryid,
      "isMainIndex": false,
      "name": vueC ? ( vueC.text ? vueC.text : category.name) : category.name,
      "script": newData ? (newData.script ? newData.script : category.script) : category.script,
    }
    urlObj.post(`${urlObj.apiStrategyOpr}${category.categoryid}`, data, res => {
      if(res.code === 200){
        category.name = res.data.name
        category.args = res.data.args
        category.script = res.data.script
        category.editing = false
        
        if(needNOticeParent && vueC.$el.className === 'category-wrap') { //必须是子组件
          vueC.$emit('changeStrategyName', category.categoryid, vueC.text)
        }
        
        if(vueC && vueC.sending) vueC.sending = false
        if(vueC && vueC.text) vueC.text = ''  //除了数组件，有可能其他组件也有text，注意不能取相似的名字
        //可能需要切换选中
        if(callback) callback([category.groupId, category.categoryid])
        vueC.$message('修改成功')
      }else{
        vueC.$message('修改失败')
      }
    })
  },
  queryOneStrategyDetail(category, callback){
    urlObj.get(`${urlObj.apiStrategyOpr}${category.categoryid}`, {}, res => {
      callback(category, res)
    })
  },
  deleteOneGroup(categoryList, category, vueC){
    urlObj.dele(`${urlObj.apiGroupOpr}${category.categoryid}`, res => {
      if(res.code === 200){
        //在总数据中查找这个分组，并删掉
        const index = findIndex(categoryList, {categoryid: category.categoryid})
        categoryList.splice(index, 1)
        if(categoryList.length === 0){
          vueC.isShowNoCategory = true
        }
        vueC.$message('删除成功')
      }else{
        vueC.$message('删除失败')
      }
    })
  },
  deleteOneStrategy(categoryList, category, vueC, callback){
    urlObj.dele(`${urlObj.apiStrategyOpr}${category.categoryid}`, res => {
      if(res.code === 200){
        //在总数据中查找这个分组下的策略，并删掉
        const group = find(categoryList, {categoryid: category.groupId})
        const index = findIndex(group.children, {categoryid: category.categoryid})
        const id = category.categoryid
        group.children.splice(index, 1)
        //删除操作通知父组件，更新tabs的显示
        vueC.$emit('deleteStrategy', id)

        //如果删掉的这个是选中的，则需要选中下一个，或者上一个策略
        if(vueC.currentSelectCategoryId.length === 2 && id === vueC.currentSelectCategoryId[1]){
          if(group.children.length > 0) {
            callback([group.categoryid, group.children[0].categoryid])
          }else{
            //选中第一个有策略的分组
            const gp = find(categoryList, item => item.children.length > 0)
            if(gp){
              callback([gp.categoryid, gp.children[0].categoryid])
              gp.opened = true
            }else{
              callback(null) //设置不选中
            }
          }
        }

        //如果删除后，分组内没有策略，需要重置分组的属性
        if(group.children.length === 0){
          group.ishaschildren = false
          group.isdelete = true
        }
        
        vueC.$message('删除成功')
      }else{
        vueC.$message('删除失败')
      }
    })
  },
  allGroup(){
  },
  allStrategy(){
  },
  oneGroupAllStrategy(){
  },
  getHqchartConfig(vueC){
    urlObj.get(urlObj.apiDataStatus, {}, res => {
      if(res.code === 200){
        vueC.form = res.data || []
        // vueC.$message('保存成功')
      }else{
        vueC.$message('获取设置失败')
      }
    })
  },
  saveHqchartConfig(formData, vueC){
    const pathAry = formData.map(item => {
      return {
        dataPath: item.dataPath,
        type: item.type
      }
    })
    const data =  {
      "data": pathAry
    }
    urlObj.post(urlObj.apiHqchartConfig, data, res => {
      if(res.code === 200){
        vueC.$message('保存成功')
      }else{
        vueC.$message('保存失败')
      }
    })
  },
  getBaseInfo(vueC){
    urlObj.get(urlObj.apiAboutInfo, {}, res => {
      vueC.baseInfo = res
    })
  },
  formatResData(data){ //对百分比进行格式化
    return data.map(item => {
      item.percent = item.percent !== null ? parseInt(item.percent) : item.percent
      return item
    })
  },
  firstQueryStatusApi(vueC, res){
    vueC.dataStatusAry = this.formatResData(res.data)

    // debugger

    //是否需要刷新状态数据
    let needTimer = false
    let status
    for (let i = 0; i < res.data.length; i++) {
      const item = res.data[i];
      status = item
      if(item.syncStatus === 1 || item.loadStatus === 1){
        needTimer = true
        //放到数组中，记录同步的是哪一个数据
        if(findIndex(vueC.syncAry, {type: item.type}) === -1){
          vueC.syncAry.push({type: item.type})
        }
        break 
      }
    }
    console.log('needTimer:', needTimer);
    if(needTimer) {
      this.addTimer(vueC, status)
    }
  },
  notFirstQueryStatusApi(vueC, res){
    //其他次，只更新状态码和进度条
    vueC.syncAry.forEach((syncItem, index) => {
      const statusObj = find(vueC.dataStatusAry, {type: syncItem.type})
      const resObj = find(res.data, {type: syncItem.type})
      // vueC.$set(statusObj, 'syncStatus', resObj.syncStatus)
      // vueC.$set(statusObj, 'loadStatus', resObj.loadStatus)
      vueC.$set(statusObj, 'percent', resObj.percent)
      vueC.$set(statusObj, 'taskname', resObj.taskname)
    })


    //清除定时器：syncStatus和loadStatus都没有等于1的
    let isEnd = false
    for (let i = 0; i < res.data.length; i++) {
      const item = res.data[i];
      if(item.syncStatus === 1 || item.loadStatus === 1){
        isEnd = false
        return
      }else{
        isEnd = true
      }
    }
    
    if(vueC.statusTimer && isEnd){
      clearInterval(vueC.statusTimer)
      vueC.statusTimer = null
    }
    //结束，更新所有数据
    if(isEnd){
      vueC.dataStatusAry = res.data
    }
  },
  getDataStatus(vueC){ //获取数据状态
    urlObj.get(urlObj.apiDataStatus, {}, res => {
      vueC.loading = false
      if(res.code === 200){
        try {
          //第一次拿到数据，全部更新数据
          if(!vueC.hasStatusData){
            this.firstQueryStatusApi(vueC, res)
            
          }else{
            this.notFirstQueryStatusApi(vueC, res)

          }
          
        } catch (error) {
          console.log(error.message);
          vueC.$message(error.message)
        }
        
        
        //设置已经获取数据
        vueC.hasStatusData = true
        
      }else{
        vueC.$message(res.msg)
      }
    }, res => {
      vueC.$message.error('获取数据状态失败')
      vueC.loading = false
    })
  },
  dataSync(data, vueC, status){
    urlObj.post(urlObj.apiDataSync, data, res => {
      if(res.code === 200){
        status.syncStatus = res.syncStatus
        const index = findIndex(vueC.dataStatusAry, {type: status.type})
        status.percent = 0
        vueC.dataStatusAry.splice(index, 1, status)
        
        vueC.$message(res.msg)

        //放到数组中，记录同步的是哪一个数据
        if(findIndex(vueC.syncAry, {type: status.type}) === -1){
          vueC.syncAry.push({type: status.type})
        }
        this.addTimer(vueC, status)
      }else{
        vueC.$message('同步失败')
      }
    })
  },
  addTimer(vueC, status){ //开启定时器，刷新同步结果
    //进度开始前，重置进度条信息
    if(status.taskname) status.taskname = ''
    if(status.percent) status.percent = 0

    if(vueC.statusTimer === null){
      vueC.statusTimer = setInterval(() => {
        this.getDataStatus(vueC)
      },
      2 * 1000)
    }else{
      clearInterval(vueC.statusTimer)
      vueC.statusTimer = null
    }

  },
  indexRun(data, vueC){
    urlObj.post(urlObj.apiRun, data, res => {
      res.code = 0
      if(res.code === 0){
        window.open('./klinshow.html', '_blank')
      }else{
        vueC.$message(res.msg)
      }
      
    })
  },
  apiDataLoad(data, vueC, status){
    urlObj.post(urlObj.apiDataLoad, data, res => {
      if(res.code === 200){
        status.loadStatus = res.loadStatus
        const index = findIndex(vueC.dataStatusAry, {type: status.type})
        vueC.dataStatusAry.splice(index, 1, status)
        
        vueC.$message(res.msg)

        //放到数组中，记录加载的是哪一个数据
        if(findIndex(vueC.syncAry, {type: status.type}) === -1){
          vueC.syncAry.push({type: status.type})
        }
        this.addTimer(vueC, status)
      }else{
        vueC.$message(res.msg)
      }
    })
  }

}
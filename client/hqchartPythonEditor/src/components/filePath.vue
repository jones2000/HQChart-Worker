<template>
  <div class="filePathWrap">
    <!-- webkitdirectory 限制属性 选择目录 -->
    <label :for="domId">选择</label>
    <input type="file" :id="domId" name="selectFile">
  </div>
</template>

<script>
export default {
  props: ['domId', 'index'],
  mounted() {
    const _this = this
    this.$nextTick(() => {
      const selectDataPath = document.getElementById(`${this.domId}`)
      selectDataPath.addEventListener('change', function(){
        // console.log('@@@', this.value, this.files);
        _this.getvl(this)
      }, false)
    })
    
  },
  methods: {
    //FX获取文件路径方法
    readFileFirefox(fileBrowser) {
      try {
        netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");
      } 
      catch (e) {
        alert('无法访问本地文件，由于浏览器安全设置。为了克服这一点，请按照下列步骤操作：(1)在地址栏输入"about:config";(2) 右键点击并选择 New->Boolean; (3) 输入"signed.applets.codebase_principal_support" （不含引号）作为一个新的首选项的名称;(4) 点击OK并试着重新加载文件');
        return;
      }
      var fileName=fileBrowser.value; //这一步就能得到客户端完整路径。下面的是否判断的太复杂，还有下面得到ie的也很复杂。
      var file = Components.classes["@mozilla.org/file/local;1"]
        .createInstance(Components.interfaces.nsILocalFile);
      try {
        // Back slashes for windows
        file.initWithPath( fileName.replace(/\//g, "\\\\") );
      }
      catch(e) {
        if (e.result!=Components.results.NS_ERROR_FILE_UNRECOGNIZED_PATH) throw e;
        alert("File '" + fileName + "' cannot be loaded: relative paths are not allowed. Please provide an absolute path to this file.");
        return;
      }
      if ( file.exists() == false ) {
        alert("File '" + fileName + "' not found.");
        return;
      }
    
    
      return file.path;
    },
    //根据不同浏览器获取路径
    getvl(obj){
      //判断浏览器
      var Sys = {}; 
      var ua = navigator.userAgent.toLowerCase(); 
      // console.log('###', ua);
      var s; 
      ua.indexOf('trident') > -1 || ua.indexOf('msie') > -1 ? Sys.ie = 11 :  //只能检查是ie内核，不能确定ie几
      (s = ua.match(/firefox\/([\d.]+)/)) ? Sys.firefox = s[1] : 
      (s = ua.match(/chrome\/([\d.]+)/)) ? Sys.chrome = s[1] : 
      (s = ua.match(/opera.([\d.]+)/)) ? Sys.opera = s[1] : 
      (s = ua.match(/version\/([\d.]+).*safari/)) ? Sys.safari = s[1] : 0;
      var file_url="";
      // console.log('###', Sys.ie);
      if(Sys.ie<="6.0"){
        //ie5.5,ie6.0
        file_url = obj.value;
      }else if(Sys.ie>="7.0"){
        //ie7,ie8
        file_url = obj.value;
        // obj.select();
        // file_url = document.selection.createRange().text;
      }else if(Sys.firefox){
        //fx
        file_url = this.readFileFirefox(obj);
      }else if(Sys.chrome){
        file_url = obj.value;
      }
      // console.log('@@',file_url);
      this.$emit('getpath', file_url, index)
      // alert(file_url);
      // document.getElementById("text").innerHTML="获取文件域完整路径为："+file_url;
    },
  }
}
</script>

<style lang="less">
.filePathWrap{
  display: inline;
  height: 33px;

  label{
    display: inline-block;
    line-height: 1;
    white-space: nowrap;
    cursor: pointer;
    background: #FFF;
    border: 1px solid #DCDFE6;
    color: #606266;
    text-align: center;
    box-sizing: border-box;
    outline: 0;
    margin: 0;
    transition: .1s;
    font-weight: 500;
    padding: 9px 15px;
    font-size: 12px;
    border-radius: 3px;
    cursor: pointer;

    &:hover{
      color: #409EFF;
      border-color: #c6e2ff;
      background-color: #ecf5ff;
    }

    &:active{
      color: #3a8ee6;
      border-color: #3a8ee6;
      outline: 0;
    }
  }

  input[type="file"] {
    opacity: 0;
  }
}

</style>
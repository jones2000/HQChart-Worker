//设置cookie
export function setCookie(cname, cvalue, exdays) {
  var exp = new Date();
  exp.setTime(exp.getTime() + exdays * 24 * 60 * 60 * 1000);
  document.cookie =
    cname + "=" + escape(cvalue) + ";expires=" + exp.toGMTString();
}

//获取cookie
export function getCookie(sName) {
  var aCookie = document.cookie.split("; ");
  for (var i = 0; i < aCookie.length; i++) {
    var aCrumb = aCookie[i].split("=");
    if (sName == aCrumb[0]) return unescape(aCrumb[1]);
  }
  return null;
}

//清除cookie
export function clearCookie(name) {
  setCookie(name, "", -1);
}

//通过url获取参数
export function getURLParams(name) {
  var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
  var r = window.location.search.substr(1).match(reg);
  if (r != null) return decodeURI(r[2]);
  return null;
}

export function formatUrl(url, query){
  let arr = [];
  for (let k in query) {
    if(query[k] !== '' && query[k] !== undefined){
      arr.push(`${k}=${query[k]}`);
    }
  }
  var str = '';
  if (url.indexOf('?') === -1) {
    str += '?';
  } else {
    str += '&';
  }
  if(arr.length > 0){
    return url += str + arr.join('&');
  }else{
    return url;
  }
}

export function getDateForApi(year){ //几年前-20210405
  let StartDate = 0
  let dateTime = new Date().getFullYear(); /* 获取现在的年份 */
  let date = new Date(new Date().setFullYear(dateTime-year))
  StartDate = date.getFullYear() * 10000
              + (date.getMonth() + 1) * 100
              + (date.getDate() > 9 ? date.getDate() : `0${date.getDate()}`) ; //xx年前
  StartDate = parseInt(StartDate)
  return StartDate
}

//通过url获取参数
export function openJump(url, target) {
  if(/^http:/.test(url)) {
    window.open(url, target)
  }else {
    var k = url.split('?')
    if(k.length > 1) {
      k.unshift();
    }
    k = k.join('');
    console.log(k)
    var reg = new RegExp("(^|&)" + 'version' + "=([^&]*)(&|$)", "i");
    var r = k.match(reg);
    r = r != null ? decodeURI(r[2]) : r;

    var version = getURLParams('version');

    if(version && !r) {
      url = formatUrl(url, {version: version});
    }
    window.open(url, target)
  }
}

export function getSuffix(url) {
  if(!url) return url;
  var urlsplit = url.split("/");
  var name = urlsplit[urlsplit.length-1];
  var suffix = name.split('.').pop().toLowerCase();
  return suffix;
}
export function getFileName(url) {
  if(!url) return url;
  var urlsplit = url.split("/");
  var name = urlsplit[urlsplit.length-1];
  return decodeURIComponent(name);
}
export function getFilePureName(url) {
  if(!url) return url;
  var urlsplit = url.split("/");
  var name = urlsplit[urlsplit.length-1];
  var _name = name.split(".");
  _name.pop()
  name = _name.join('.');
  return decodeURIComponent(name);
}
export function formatFilesList(filesList) {
  var list = [];
  filesList && filesList.forEach(item => {
    list.push({
      url: item,
      ext: getSuffix(item),
      name: getFileName(item),
      pureName: getFilePureName(item)
    })
  })
  return list;
}

const timeNumberToString=function(value)
{
    if (value<10) return '0'+value.toString();
    return value.toString();
}

export function formatDateString(value) //将20210914171732转换成时间格式,需要引入timeNumberToString 方法
{
  const valueStr = value.toString()
  if(valueStr.length === 14){
    const date = valueStr.substr(0,8)
    const time = valueStr.substr(8,14)
    var year=parseInt(date/10000);
    var month=parseInt(date/100)%100;
    var day=date%100;

    var h = parseInt(time/10000);
    var m = parseInt(time/100)%100;
    var s = time%100;
    return year + '-' + timeNumberToString(month) + '-' + timeNumberToString(day) + ' ' 
            + timeNumberToString(h) + ':'+ timeNumberToString(m) + ':'+ timeNumberToString(s);
  }else{
    return false
  }
}

export function formatValueThousandsString (value,floatPrecision)
{
    if (value==null || isNaN(value))
    {
        if (floatPrecision>0)
        {
            var nullText='-.';
            for(var i=0;i<floatPrecision;++i)
                nullText+='-';
            return nullText;
        }

        return '--';
    }

    var result='';
    var num=value.toFixed(floatPrecision);
    if(floatPrecision>0){
        var numFloat = num.split('.')[1];
        var numM = num.split('.')[0];
        var numMa = Number(numM);
        var isLowZero = null;
        if(numMa < 0){
            numMa = Math.abs(numMa);
            isLowZero = true;
        }
        numMa = numMa.toString();
        while (numMa.length > 3)
        {
            result = ',' + numMa.slice(-3) + result;
            numMa = numMa.slice(0, numMa.length - 3);
        }
        if (numMa) { result = isLowZero != null ? ('-' + numMa + result + '.' + numFloat) : (numMa + result + '.' + numFloat); }
    }else{
        var numNF = Number(num);
        var isLowZero = null;
        if(numNF < 0){
            numNF = Math.abs(numNF);
            isLowZero = true;
        }
        numNF = numNF.toString();
        while (numNF.length > 3)
        {
            result = ',' + numNF.slice(-3) + result;
            numNF = numNF.slice(0, numNF.length - 3);
        }
        if (numNF) { result = isLowZero != null ? ('-' + numNF + result) : (numNF + result); }
    }
    
    return result;
}

//数据输出格式化 floatPrecision=小数位数
export function formatValueString (value, floatPrecision)
{
    if (value==null || isNaN(value))
    {
        if (floatPrecision>0)
        {
            var nullText='-.';
            for(var i=0;i<floatPrecision;++i)
                nullText+='-';
            return nullText;
        }

        return '--';
    }

    if (value<0.00000000001 && value>-0.00000000001)
    {
        return "0";
    }

    var absValue = Math.abs(value);
    if (absValue < 10000)
    {
        return value.toFixed(floatPrecision);
    }
    else if (absValue < 100000000)
    {
        return (value/10000).toFixed(floatPrecision)+"万";
    }
    else if (absValue < 1000000000000)
    {
        return (value/100000000).toFixed(floatPrecision)+"亿";
    }
    else
    {
        return (value/1000000000000).toFixed(floatPrecision)+"万亿";
    }
}

export function formatTimeString (value)
{
    if (value<10000)
    {
        var hour=parseInt(value/100);
        var minute=value%100;
        return timeNumberToString(hour)+':'+ timeNumberToString(minute);
    }
    else
    {
        var hour=parseInt(value/10000);
        var minute=parseInt((value%10000)/100);
        var second=value%100;
        return timeNumberToString(hour)+':'+ timeNumberToString(minute) + ':' + timeNumberToString(second);
    }
}

export function formatMillisecondTimeString (value)
{
    if(value === 0){
      return '00:00:00.000'
    }else{
      return '--'
    }
}

export function showSuccessMessage(obj, msg){
  obj.$message({
    type: 'success',
    message: msg
  });
}

export function showInfoMessage(obj, msg){
  obj.$message({
    type: 'info',
    message: msg
  });
}

export function strByBytes(str, charset){
  var total = 0,
      charCode,
      i,
      len;
  charset = charset ? charset.toLowerCase() : '';
  if(charset === 'utf-16' || charset === 'utf16'){
      for(i = 0, len = str.length; i < len; i++){
          charCode = str.charCodeAt(i);
          if(charCode <= 0xffff){
              total += 2;
          }else{
              total += 4;
          }
      }
  }else{
      for(i = 0, len = str.length; i < len; i++){
          charCode = str.charCodeAt(i);
          // console.log('编码：：', charCode);
          if(charCode <= 0x007f) {
              total += 1;
          }else if(charCode <= 0x07ff){
              total += 2;
          }else if(charCode <= 0xffff){
              total += 3;
          }else{
              total += 4;
          }
      }
  }
  return total;
}
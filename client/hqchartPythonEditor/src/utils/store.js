var store = {
  debug: true,
  UTSHQSRV: 'utshqsrv',
  UTSCALC: 'utscalc',
  state: {
    sysType: '',
    kword: '',
    account: '',
    // loginApiData: null
  },
  // setLoginApiData (newValue) {
  //   if (this.debug) console.log('setLoginApiData triggered with', newValue)
  //   this.state.loginApiData = newValue
  // },
  setSysType(newValue){
    if (this.debug) console.log('setsysType triggered with', newValue)
    this.state.sysType = newValue
  },
  setKWordAction(newValue){
    if (this.debug) console.log('setKWordAction triggered with', newValue)
    this.state.kword = newValue
  },
  clearkwordAction(){
    if (this.debug) console.log('clearkwordAction triggered')
    this.state.kword = ''
  },
  setAccountAction(newValue){
    if (this.debug) console.log('setAccountAction triggered with', newValue)
    this.state.account = newValue
  },
  clearaccountAction(){
    if (this.debug) console.log('clearaccountAction triggered')
    this.state.account = ''
  }
}

export default store
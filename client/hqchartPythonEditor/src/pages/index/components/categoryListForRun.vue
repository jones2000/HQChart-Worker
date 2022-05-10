<template>
    <div class='category-wrap'
        id="categoryWrap"
        @click="hideRightMenu"
        @mouseleave="hideRightMenu"
        v-loading='loading'
    >
        <ul class="category-list">
            <li
                onselectstart="return false"
                :class="{'isSelected':item.isSelected}"
                v-for="item in categoryList"
                :key="item.categoryid"
                @contextmenu.stop="rightMenu($event, [item.categoryid])"
                >
                <template v-if="item.editing || item.creating">
                    <input @keyup.enter="submit" id="J-edit-input" type="text" v-model="text" placeholder="">
                </template>
                <template v-else>
                    <p class="catagory-lv1" @click="toggleShow(item)">
                        <i v-if="!item.opened" class="iconfont icon-m"></i>
                        <i v-else class="iconfont icon-p"></i>
                        {{item.name}}
                    </p>
                </template>
                <ul v-if="item.opened">
                    <li
                        onselectstart="return false"
                        :class="{'isSelected':itemSub.isSelected}"
                        v-for="itemSub in item.children"
                        :key="itemSub.children"
                        @contextmenu.stop="rightMenu($event, [item.categoryid, itemSub.categoryid])"
                        >
                        <template v-if="itemSub.editing || itemSub.creating">
                            <input @keyup.enter="submit" id="J-edit-input" type="text" v-model="text" placeholder="">
                        </template>
                        <template v-else>
                            <p @click="checkCategory([item.categoryid, itemSub.categoryid])" class="catagory-lv2">{{itemSub.name}}</p>
                        </template>
                    </li>
                </ul>
            </li>
        </ul>
        <div class="noCategory" v-if='isShowNoCategory'>
            <el-input v-model="text" placeholder="输入分组名称" size="small"></el-input>
            <el-button type="primary" size="small" @click='addFirstGroup'>新增分组</el-button>
        </div>
        <ul
            v-if="showRightMenu"
            class="right-menu"
            :style="{left: currentMousePosition.x+'px',top: currentMousePosition.y+'px'}"
            >
            <li v-show="showGroupCategory" @click="addCategory('brother')">
                <i class="iconfont icon-xinjianjiedian"></i> {{sameLevelChildOprTitle}}
            </li>
            <li v-show="showSubCategory" @click="addCategory('child')">
                <i style="visibility:hidden" class="iconfont icon-xinjianjiedian"></i> {{nextLevelChildOprTitle}}
            </li>
            <li v-show="showGroupCategory" @click="editCategory">
                <i class="iconfont icon-bianjibiaoti"></i> 编辑
            </li>
            <li v-if="showDelateButton" @click="confirm">
                <i class="iconfont icon-shanchujiedian"></i> 删除
            </li>
        </ul>
    </div>

</template>
<script>
import {find,findIndex} from 'lodash'
import urlObj from '../../../utils/urlObj'
import Service from './categoryService'


function defaultData(){}
defaultData.getListParentItem = () => ({
    opened: false,
    children: [], //指标数组 或 策略数组
    ishaschildren: false, //是否有子节点
    isSelected: false,
    categoryid: '',
    name: '',
    isdelete: false,
    editing: false,
    creating: false //新增
})
defaultData.getListSubItem = () => {
    return {
        isSelected: false,
        editing: false,
        creating: false, //新增
        isdelete: true,

        categoryid: '',
        name: '',
        groupId: ''
    }
}
defaultData.getGrandFatherId = () => {
    return 10000
}

export default {
    name: 'CategoryList',
    props: ['parentCompName'], //parentCompName=strategyEdit 是策略编辑
    data() {
        return {
            userid: '',
            permission: false,
            pageType: '',

            categoryList: [],
            currentOperateCategoryId: [], // 当前正在操作的节点id
            currentSelectCategoryId: [], // 当前选中的节点id
            showRightMenu: false,
            showDelateButton: false,
            sending: false,
            showSubCategory: false,
            showGroupCategory: false,
            sameLevelChildOprTitle: '新建同级节点',
            nextLevelChildOprTitle: '新建下级节点',
            createType: '',
            text: '',
            currentMousePosition:{
                x: 0,
                y: 0
            },
            loading: false,
            isShowNoCategory: false,

            isStrategyComp: false
        }
    },
    created() {
        // this.loading = true
        this.queryGroupList()
        // this.updataCategroy();
    },
    mounted() {
        // console.log('mounted');
        const categoryWrap = document.getElementById('categoryWrap')
        categoryWrap.addEventListener('click', (e) => { //其他需要点击隐藏input和右键菜单
            if(e.target == document.getElementById('J-edit-input')){
                return;
            }
            this.submit();
        }, true)
    },
    methods: {
        addFirstGroup(){
            const group = defaultData.getListParentItem()
            this.categoryList.push(group)
            const newCategory = this.categoryList[this.categoryList.length - 1]
            // this.addOneGroup(newCategory, this.text)
            Service.addOneGroup(newCategory, this)
        },
        changeCategory(category, categoryid, from){ //展示当前选中子节点的信息,from=elTab表示通过切换tab来选中子节点
            // console.log(category, categoryid);
            if(from != 'elTab'){
                if(category != null){
                    this.$emit('changeCategory', category, categoryid)
                }
            }else{
                this.$emit('refreshtablesize')
            }
            
        },
        toggleShow(item) {
            const opened = item.opened;
            this.$set(item, 'opened', !opened);
        },
        getCategoryId(type) {  //获取操作类型下当前节点id
            var cateGoryId;
            if(type == 'operate'){
                cateGoryId = this.currentOperateCategoryId;
            }else if(type == 'select'){
                cateGoryId = this.currentSelectCategoryId;
            }else{
                return false;
            }
            // console.log('???', type, cateGoryId);
            return cateGoryId[cateGoryId.length-1];
        },
        getCategory(type) {  //获取操作类型下当前节点对象
            var category = {};
            var first = false;
            var cateGoryId;
            if(type == 'operate'){
                cateGoryId = this.currentOperateCategoryId;
            }else if(type == 'select'){
                cateGoryId = this.currentSelectCategoryId;
            }else{
                return false;
            }
            cateGoryId.forEach((id) => {
                let parent;
                if(!first){
                    parent = this.categoryList;
                    first = true;
                }else{
                    parent = category.children;
                }
                category = find(parent, {categoryid: id})
            })
            return category;
        },
        getCurrentCategoryParent() { //查找当前操作的节点，所有的父节点
            if(this.currentOperateCategoryId.length == 1){
                return this.categoryList;
            }else if(this.currentOperateCategoryId.length == 2){
                return find(this.categoryList, {categoryid: this.currentOperateCategoryId[0]});
            }
        },
        checkCategory(id, from) { //选中子节点
            const oldCategoryid = this.getCategoryId('select');
            const oldCategory = this.getCategory('select');
            // console.log('checkCategory 111', !id, oldCategoryid, oldCategory);
            if(!id) {
                if(oldCategory) this.$set(oldCategory, 'isSelected', false);
                this.changeCategory(null);
                return;
            }
            this.currentSelectCategoryId = id;
            // console.log('checkCategory', this.currentSelectCategoryId);
            const categoryid = this.getCategoryId('select');
            const category = this.getCategory('select');
            if(categoryid){
                if(category.isSelected) return;
                if(oldCategoryid && oldCategory){
                    this.$set(oldCategory, 'isSelected', false);
                }
                this.$set(category, 'isSelected', true);
            }
            this.changeCategory(category, categoryid, from);
        },
        addCategory(type) {
            const category = this.getCategory('operate');
            // console.log('category::', category);
            let parent = this.getCurrentCategoryParent();
            this.createType = type;
            if(type == 'brother'){
                let item = null
                if(this.currentOperateCategoryId.length === 2){
                    item = defaultData.getListSubItem()
                    child.groupId = this.currentOperateCategoryId[0]
                    parent = parent.children;
                }else if(this.currentOperateCategoryId.length === 1){
                    item = defaultData.getListParentItem()
                }
                item.creating = true
                parent.push(item)
            }else if(type == 'child'){
                category.opened = true;
                const child = defaultData.getListSubItem()
                child.groupId = category.categoryid
                child.creating = true
                category.children.push(child)
                
            }else{
                console.error('添加节点错误');
                return;
            }
            this.$forceUpdate();
            this.hideRightMenu();
            this.inputFocus();
        },
        editCategory() {
            const category = this.getCategory('operate');
            this.text = category.name;
            this.$set(category, 'editing', true);
            this.hideRightMenu();
            this.inputFocus();
        },
        confirm() {
            this.$confirm('确定删除该节点吗？', {
                cancelButtonClass: 'btn-cancel',
                cancelButtonText: '取消',
                confirmButtonText: '确定'
            }).then(() => {
                this.deleteCategory();
            }).catch(err => {})
        },
        deleteCategory() {
            const category = this.getCategory('operate')
            if(this.currentOperateCategoryId.length === 2){
                setTimeout(() => { //模拟后台请求
                    let parent = this.getCurrentCategoryParent()
                    let index = findIndex(parent.children, {categoryid: this.currentOperateCategoryId[1]})
                    parent.children.splice(index, 1)   
                    
                    if(parent.children.length > 0){
                        this.checkCategory([parent.categoryid, parent.children[0].categoryid])
                    }
                }, 1000);
                
            }else{
            }
            
            this.hideRightMenu();
        },
        rightMenu(event, id) {
            event.preventDefault();
            if(!this.permission) return false;
            if(document.getElementById('J-edit-input')) return false;
            var __xx = event.clientX + document.body.scrollLeft;
            var topBanner = 43
            var __yy = event.clientY + document.body.scrollTop - topBanner;

            this.showSubCategory = id.length == 1;
            this.showGroupCategory = id.length == 2
            
            let rightMenuHeight;
            if(this.showSubCategory){
                rightMenuHeight = 100;
            }else{
                rightMenuHeight = 68;
            }
            if(window.innerHeight < rightMenuHeight + __yy) {
                __yy = __yy - rightMenuHeight;
            }

            this.currentMousePosition = {
                x: __xx,
                y: __yy
            }
            if(id.length === 1){
                this.sameLevelChildOprTitle = '新建同级节点'
                this.nextLevelChildOprTitle = '新建策略'
            }else{
                this.sameLevelChildOprTitle = '新建策略'
                // this.nextLevelChildOprTitle = ''
            }
            this.currentOperateCategoryId = id;
            const category = this.getCategory('operate');
            this.showDelateButton = category.isdelete;
            // this.showRightMenu = id.length == 2; 
            this.showRightMenu = true; 
        },
        //查询所有的分类
        queryGroupList(){
            const data = {
                params: {
                    status: 1
                }
            }
            // console.log('cccc');
            urlObj.get(urlObj.apiAlgorithmGroupList, data, res => {
                this.updataCategroyLocal(res)
            }, res => {
                this.$message.error(res.message || res.msg)
            })
        },
        updataCategroyLocal(res){
            if(res.code === 200) {
                this.categoryList = res.data.map(item => {
                    // debugger
                    let group = defaultData.getListParentItem()
                    group.categoryid = item.id
                    group.name = item.name
                    let children = []
                    children = item.algorithms.map(stra => { //子节点字段：algorithms
                        let sub = defaultData.getListSubItem()
                        sub.categoryid = stra.id
                        sub.name = stra.name
                        sub.groupId = item.id
                        return sub
                    })
                    // debugger
                    group.children = [...children]
                    if(group.children.length > 0){
                        group.ishaschildren = true
                        group.isdelete = false //有策略的分组不能删除
                    }
                    return group
                })
                // console.log('树结构：', this.categoryList);
                // debugger
                if(this.categoryList.length === 0){
                    this.isShowNoCategory = true
                    return
                }
                // console.log('***',this.categoryList);
                //选中特定的节点,并且展开
                if(this.currentOperateCategoryId.length > 1){
                    const categoryidlv1 =  this.currentSelectCategoryId[0];
                    const categoryidlv2 =  this.currentSelectCategoryId[1];
                    const indexP = findIndex(this.categoryList, item => item.categoryid === categoryidlv1)
                    const indexS = findIndex(this.categoryList[indexP].children, item => item.categoryid === categoryidlv2)
                    if(indexP > -1 && indexS  > -1){
                        this.checkCategory([categoryidlv1, categoryidlv2]);
                    }
                    this.categoryList[indexP].opened = true
                }else{
                    const parent = find(this.categoryList, item => item.ishaschildren)
                    // console.log(parent);
                    if(!parent) return
                    const parentId = parent.categoryid
                    const subId = parent.children[0].categoryid
                    this.checkCategory([parentId, subId]);
                    parent.opened = true
                }
            }else{
                this.$message('获取列表异常')
            }
            
        },
        hideRightMenu() {
            this.showRightMenu = false;
        },
        inputFocus() {
            this.$nextTick(() => {
                document.getElementById('J-edit-input').focus();
            })
        },
        submit() {
            const category = this.getCategory('operate');
            const categoryid = this.getCategoryId('operate');
            if(category && categoryid && !this.sending){
                if(this.text === ''){
                    this.cancel();
                    return;
                }else if(category.editing && this.text === category.name){
                    this.cancel();
                    return;
                }
                this.send();
            }
        },
        cancel() {
            const category = this.getCategory('operate');
            if(category.editing){
                category.editing = false;
            }else if(this.createType){
                if(this.createType == 'brother'){
                    let parent = this.getCurrentCategoryParent();
                    if(this.currentOperateCategoryId.length == 2){
                        parent = parent.children;
                    }
                    const len = parent.length;
                    parent.splice(len-1, 1);
                }else if(this.createType == 'child'){
                    const len = category.children.length;
                    category.children.splice(len-1, 1);
                }
                this.createType = '';
            }
        },
        send() {
            const category = this.getCategory('operate');
            if(category.editing){
                this.sending = true;
                if(this.currentOperateCategoryId.length === 2){
                    urlObj.post(`${urlObj.apiStockGroup}${this.currentOperateCategoryId[1]}`, {name: this.text}, res => {
                        if(res.code === 200){
                            category.name = res.data.name
                            category.editing = false
                            this.sending = false

                            let parent = this.getCurrentCategoryParent();
                            this.checkCategory([parent.categoryid, category.categoryid])
                            // this.$message('编辑成功')
                        }else{
                            this.$message('编辑失败')
                        }
                    })
                    
                }else{
                    // Service.updateOneGroup(category, this)
                }
            }else if(this.createType){
                this.sending = true;
                var api, newCategory;
                var text = this.text;
                if(this.createType == 'brother'){
                    let parent = this.getCurrentCategoryParent();
                    if(this.currentOperateCategoryId.length === 1){
                        // const len = parent.length;
                        // newCategory = parent[len-1];
                        // Service.addOneGroup(newCategory, this)
                    }else if(this.currentOperateCategoryId.length === 2){
                        const len = parent.children.length;
                        newCategory = parent.children[len-1];
                        this.poolCreate(newCategory, parent)
                    }
                }else if(this.createType == 'child'){
                    const len = category.children.length;
                    newCategory = category.children[len-1];
                    this.poolCreate(newCategory, category)
                }
            
            }
        },
        poolCreate(newCategory, parent){ //新建股票池
            urlObj.post(urlObj.apiStockGroupCreate, {name: this.text}, res => {
                if(res.code === 200){
                    newCategory.categoryid = res.data.id
                    newCategory.name = res.data.name
                    newCategory.creating = false
                    this.sending = false

                    this.checkCategory([parent.categoryid, newCategory.categoryid])
                    // this.$message('新建成功')
                }else{
                    this.$message('新建失败')
                }
            })
        }
    },
    
}
</script>

<style lang="less">
.category-wrap{
    .category-list{
        padding-top: 10px;
    }

    .noCategory{
        height: 100px;
        padding: 100px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-around;

        .el-input{
            width: 80%;
        }
    }
    .category-list > li{
        line-height: 32px;
        padding-left: 10px;
        .iconfont{
            position: relative;
            display: inline-block;
            z-index: 1;
            margin-left: 1px;
            margin-right: 5px;
            font-weight: normal;
            color: #333;
            width: 11px;
            height: 11px;
            vertical-align: middle;
            margin-top: -3px;
            &.icon-m{
                background-image: url('../assets/images/m.png');
            }
            &.icon-p{
                background-image: url('../assets/images/p.png');
            }
        }
        .catagory-lv1 {
            cursor: pointer;
            font-weight: bold;
            &:before{
                content: '';
                position: absolute;
                width: 16px;
                height: 16px;
                top: 4px;
                left: 7px;
                // border-bottom: 1px dashed #858585;
                background-image: url('../assets/images/x.png');
                background-repeat: repeat-x;
            }
            i{
                color: #a1a1a1;
                font-size: 12px;
            }
        }
        .catagory-lv1, ul{
            position: relative;
            &:after{
                content: '';
                position: absolute;
                width: 10px;
                top: 0;
                bottom: 0;
                left: -1px;
                // border-left: 1px dashed #858585;
                background-image: url('../assets/images/y.png');
                background-repeat: repeat-y;
            }
        }
    }
    .category-list > li:first-child .catagory-lv1:after{
        top: 10px;
    }
    .category-list > li:last-child{
        > p:last-child{
            &:after{
                bottom: 16px;
            }
        }
        > ul:last-child{
            &:after{
                bottom: 12px;
            }
        }
    }
    .category-list li ul > li{
        position: relative;
        &:before{
            content: '';
            position: absolute;
            width: 24px;
            height: 13px;
            top: 2px;
            left: 7px;
            // border-bottom: 1px dashed #858585;
            background-image: url('../assets/images/x.png');
            background-repeat: repeat-x;
        }
        .catagory-lv2 {
            cursor: pointer;
        }
        padding-left: 32px;
        line-height: 26px;
    }
    .category-list .isSelected > p{
        color: #ff7f00;
    }
    .right-menu{
        position: absolute;
        transform: translate(-5px, -5px);
        width: 128px;
        border: 1px solid #a2a2a2;
        border-radius: 3px;
        z-index: 1;
        li{
            background: rgba(255,255,255, .9);
            padding-left: 12px;
            line-height: 34px;
            cursor: pointer;
            &:hover{
                background: rgba(230,230,230, .9);
            }
        }
    }
}
</style>
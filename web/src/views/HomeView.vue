<template>
  <div class="common-layout">
    <el-container style="width: auto;">
      <el-header class="header">
        <h1>NUAA · CS · 停车场管理系统</h1> <img src="../assets/1.png" alt="NUAA Logo" class = "logo-img" />
      </el-header>
      <el-container style="width: 100%;">
      <div>
        <el-aside width="200px" class="aside">
          <el-col >
      <h5 class="mb-2">主要功能</h5>
      <el-menu
        default-active="2"
        class="el-menu-vertical-demo"
      >
        <el-sub-menu index="2">
          <template #title>
            <el-icon><location /></el-icon>
            <span>管理模块</span>
          </template>
          <el-menu-item-group title="车辆识别模块">
            <el-menu-item index="2-1" @click="currentTab = 'entry'" >进入</el-menu-item>
            <el-menu-item index="2-2" @click="currentTab = 'settlement'">结算</el-menu-item>
          </el-menu-item-group>
        </el-sub-menu>
        <el-menu-item index="3" @click="currentTab = 'find'"><el-icon><Compass /></el-icon><span>自动寻路</span></el-menu-item>
        <el-menu-item index="/stats"  @click="currentTab = 'stats'">
          <el-icon><document /></el-icon>
          <span>统计模块</span>
        </el-menu-item>
        <el-menu-item index="4">
          <el-icon><Promotion /></el-icon>
          <span>联系我们</span>
        </el-menu-item>
      </el-menu>
    </el-col>
        </el-aside>
      </div>
      <div style="flex:1;">
        <el-main class="main">
          <StatsModule v-if="currentTab === 'stats'" />
          <EntryModule v-if="currentTab === 'entry'" />
          <SettlementModule v-if="currentTab === 'settlement'" />
          <FindEnmpty v-if="currentTab === 'find'"/>
        </el-main>
      </div>
      </el-container>
    </el-container>
  </div>


</template>


<script>

import StatsModule from '../components/StatsModule.vue';
import EntryModule from '../components/EntryModule.vue';
import SettlementModule from '../components/SettlementModule.vue';
import FindEnmpty from '@/components/FindEnmpty.vue';

export default {
  data() {
    return {
      currentTab: 'find',
    };
  },
  components:{
    StatsModule,
    EntryModule,
    SettlementModule,
    FindEnmpty,
  }
};
</script>

<style>

.logo-img {
  float: right;
  width: 80px;
  height: auto;
  margin-top: 5px;
}

.el-menu {
  border-right: none !important;
}

.header {
  text-align: left; 
  background-color:#ffffff;
  height: 20%;
  width: 100%;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #ccc;
}

.el-menu-item-group__title {
  text-align: center;    /* 将文本居中 */
  margin-left: -50px;
}

h1 {
  display: inline-block;  /* 设置为行内块元素 */
  margin-right: 40px;    /* 设置右侧间距为 20px */
}

.header h1{
  white-space: nowrap; 
}

.header h1:hover{
  color: #7F3CFF
}

.aside {
  background-color: #ffffff;
  height: 100vh;

  border-right: 1px solid #ccc;
}

.main {
  background-color: #ffffff;
  display: flex;
  justify-content: flex-start;
  /* width: 100%;
  height: 100vh; */
}
</style>

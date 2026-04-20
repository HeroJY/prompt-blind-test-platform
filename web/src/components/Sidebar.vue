<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark">AB</div>
      <div>
        <h2>Prompt 盲测系统</h2>
        <p>本地联调版本</p>
      </div>
    </div>

    <div class="user-box">
      <div class="role" id="currentRoleLabel">{{ currentUser.role === 'tester' ? '测试用户' : '管理员' }}</div>
      <div class="name" id="currentUserName">{{ currentUser.username }}</div>
      <div class="sub" id="currentUserDesc">{{ currentUser.role === 'tester' ? '可参与已发布任务、逐题选择并实时保存。' : '可创建任务、配置题目、发布任务并查看统计。' }}</div>
    </div>

    <div class="nav-group" id="testerNavGroup" v-if="currentUser.role === 'tester'">
      <div class="nav-title">测试用户</div>
      <button class="nav-item" :class="{ active: currentView === 'tester-tasks' || currentView === 'tester-import' }" @click="$emit('change-view', 'tester-tasks')">Prompt盲选测试</button>
    </div>

    <div class="nav-group" id="adminNavGroup" v-if="currentUser.role === 'admin'">
      <div class="nav-title">管理员</div>
      <button class="nav-item" :class="{ active: currentView === 'admin-generate' }" @click="$emit('change-view', 'admin-generate')">Prompt一键生成</button>
      <button class="nav-item" :class="{ active: currentView === 'admin-test' || currentView === 'admin-import' }" @click="$emit('change-view', 'admin-test')">Prompt盲选测试</button>
      <button class="nav-item" :class="{ active: ['admin-tasks', 'admin-editor', 'admin-stats'].includes(currentView) }" @click="$emit('change-view', 'admin-tasks')">广场任务管理</button>
    </div>

    <div class="nav-group">
      <div class="nav-title">通用操作</div>
      <button class="nav-item" id="switchRoleBtn" @click="$emit('switch-role')">切换角色</button>
      <button class="nav-item" id="logoutBtn" @click="$emit('logout')">退出登录</button>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'Sidebar',
  props: {
    currentUser: {
      type: Object,
      required: true
    },
    currentView: {
      type: String,
      required: true
    }
  }
}
</script>

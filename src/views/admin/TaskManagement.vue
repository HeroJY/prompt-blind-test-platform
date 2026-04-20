<template>
  <section id="admin-tasks" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title">广场任务管理</h1>
        <p class="section-subtitle">这里展示当前后端中的任务列表。你可以创建任务、进入配置、发布任务，并查看统计结果。</p>
      </div>
      <div class="btn-row">
        <button class="btn primary" id="createDemoTaskBtn" @click="$emit('create-demo-task')">创建任务</button>
      </div>
    </div>
    <div class="grid-4" id="adminKpis">
      <div class="card pad kpi-card">
        <div class="kpi-label">总任务数</div>
        <div class="kpi-value">{{ tasks.length }}</div>
      </div>
      <div class="card pad kpi-card">
        <div class="kpi-label">已发布</div>
        <div class="kpi-value">{{ publishedTasksCount }}</div>
      </div>
      <div class="card pad kpi-card">
        <div class="kpi-label">总题目数</div>
        <div class="kpi-value">{{ totalItemsCount }}</div>
        <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: var(--muted);">
          <span>已发布: {{ publishedItemsCount }}</span>
          <span>草稿: {{ draftItemsCount }}</span>
        </div>
      </div>
      <div class="card pad kpi-card">
        <div class="kpi-label">总参与数</div>
        <div class="kpi-value">{{ totalSessionsCount }}</div>
      </div>
    </div>
    <div class="task-list" id="adminTaskList">
      <div v-for="task in tasks" :key="task.id" class="card task-card">
        <div>
          <div class="task-title-row">
            <div class="task-title">{{ task.name }}</div>
            <div class="pill">{{ task.status === 'published' ? '已发布' : '草稿' }}</div>
          </div>
          <div class="task-desc">{{ task.description }}</div>
          <div class="meta-row">
            <span class="meta-chip">题目数: {{ task.items.length }}</span>
            <span class="meta-chip">参与: {{ task.sessions.length }} 人</span>
          </div>
        </div>
        <div class="right-actions">
          <button class="btn secondary" @click="$emit('edit-task', task.id)">配置</button>
          <button v-if="task.status === 'published'" class="btn primary" @click="$emit('view-stats', task.id)">统计</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'TaskManagement',
  props: {
    tasks: {
      type: Array,
      required: true
    }
  },
  computed: {
    publishedTasksCount() {
      return this.tasks.filter(task => task.status === 'published').length
    },
    totalItemsCount() {
      return this.tasks.reduce((total, task) => {
        return total + task.items.length
      }, 0)
    },
    publishedItemsCount() {
      return this.tasks.filter(task => task.status === 'published').reduce((total, task) => {
        return total + task.items.length
      }, 0)
    },
    draftItemsCount() {
      return this.tasks.filter(task => task.status !== 'published').reduce((total, task) => {
        return total + task.items.length
      }, 0)
    },
    totalSessionsCount() {
      return this.tasks.reduce((total, task) => total + task.sessions.length, 0)
    }
  }
}
</script>

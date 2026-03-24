<template>
  <section id="tester-task-detail" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title" id="detailTaskTitle">{{ selectedTask ? selectedTask.name : '任务详情' }}</h1>
        <p class="section-subtitle" id="detailTaskDesc">{{ selectedTask ? selectedTask.description : '' }}</p>
      </div>
      <div class="btn-row">
        <button class="btn secondary" id="backToTasksBtn" @click="$emit('back')">返回任务列表</button>
      </div>
    </div>
    <div class="task-detail" style="display: flex; justify-content: center; align-items: center; min-height: 600px;">
      <div class="panel-grid" style="width: 80%; max-width: 800px;">
        <div class="card pad" style="padding: 32px; min-height: 400px; display: flex; flex-direction: column;">
          <div class="key-value">
            <div class="key-line">
              <div class="key">任务名称</div>
              <div id="detailName">{{ selectedTask ? selectedTask.name : '' }}</div>
            </div>
            <div class="key-line">
              <div class="key">任务说明</div>
              <div class="notice">本任务固定对比一组 Prompt A / Prompt B。用户端只显示候选回答 A / B，前端与后端都不应把选项文案直接绑定到 Prompt 来源，必须依赖映射关系进行归因统计。</div>
            </div>
            <div class="key-line">
              <div class="key">测试规则</div>
              <div>随机抽取最多 10 题；逐题保存；可随时退出；已作答内容计入统计。</div>
            </div>
            <div class="key-line">
              <div class="key">模式</div>
              <div>{{ selectedTask ? (selectedTask.mode === 'single' ? '单题模式' : '自定义模式') : '' }}</div>
            </div>
          </div>
          <div style="margin-top: auto; display: flex; justify-content: center; padding-top: 24px;">
            <button class="btn success" id="startTaskBtn" style="width: 200px; font-size: 16px; padding: 12px 24px;" @click="$emit('start-task', selectedTask.id)">开始测试</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'TaskDetail',
  props: {
    selectedTask: {
      type: Object,
      default: null
    }
  }
}
</script>

<template>
  <section id="tester-tasks" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title">Prompt盲选测试</h1>
        <p class="section-subtitle">选择一个任务开始盲测。你可以随时退出，已选择内容会立即保存并计入统计。</p>
      </div>
      <div style="display: flex; align-items: center; gap: 10px;">
        <button class="btn primary" @click="$emit('create-import-task')">导入任务</button>
        <div class="status-pill"><span class="status-dot"></span> 模拟在线 · 无后端接口</div>
      </div>
    </div>
    <div class="task-list" id="testerTaskList">
      <div v-for="task in tasks" :key="task.id" class="card task-card">
        <div>
          <div class="task-title-row">
            <div class="task-title">{{ task.name }}</div>
            <div class="pill">{{ task.status === 'published' ? '已发布' : '草稿' }}</div>
          </div>
          <div class="task-desc">{{ task.description }}</div>
          <div class="meta-row">
            <span class="meta-chip">单轮数量: {{ task.questionLimit || task.items.length }}</span>
            <span class="meta-chip">测试次数: {{ taskTestCounts[task.id] || 0 }}</span>
          </div>
        </div>
        <div class="right-actions" style="flex-direction: row; min-width: 480px; justify-content: flex-end;">
          <button class="btn primary" @click="$emit('view-task-detail', task.id)">查看详情</button>
          <button class="btn secondary" @click="$emit('view-history', task.id)">历史操作</button>
          <button class="btn success" @click="showTaskStats(task)">统计</button>
          <button class="btn danger" @click="$emit('delete-task', task.id)">删除</button>
        </div>
      </div>
    </div>

    <!-- 统计结果弹窗 -->
    <div v-if="showStatsModal" class="modal-overlay" @click="closeStatsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ currentTaskStats?.taskName }} - 统计结果</h2>
          <button class="close-btn" @click="closeStatsModal">×</button>
        </div>
        <div class="modal-body">
          <div class="stats-grid">
            <div class="stats-left">
              <h3>当前结论</h3>
              <div class="conclusion-card">
                <h4>{{ currentTaskStats?.conclusion }}</h4>
                <p>{{ currentTaskStats?.conclusionText }}</p>
              </div>
            </div>
            <div class="stats-right">
              <h3>PROMPT 选择占比</h3>
              <div class="stats-bar">
                <div class="stats-item">
                  <div class="stats-label">
                    <span>Prompt A</span>
                    <span>{{ currentTaskStats?.promptASelections }}次</span>
                  </div>
                  <div class="stats-progress">
                    <div class="stats-fill stats-fill-a" :style="{ width: currentTaskStats?.promptAPercentage + '%' }"></div>
                  </div>
                </div>
                <div class="stats-item">
                  <div class="stats-label">
                    <span>Prompt B</span>
                    <span>{{ currentTaskStats?.promptBSelections }}次</span>
                  </div>
                  <div class="stats-progress">
                    <div class="stats-fill stats-fill-b" :style="{ width: currentTaskStats?.promptBPercentage + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Prompt 内容展示 -->
          <div class="prompt-content-grid" style="margin-top: 24px;">
            <h3 style="grid-column: 1 / -1; margin-bottom: 16px;">Prompt 内容</h3>
            <div class="prompt-card prompt-card-a">
              <h4 style="margin-top: 0; margin-bottom: 12px; color: #2563eb;">Prompt A</h4>
              <pre style="white-space: pre-wrap; word-wrap: break-word; line-height: 1.6; padding: 16px; background-color: #f0f9ff; border-radius: 8px; font-family: monospace; margin: 0;">{{ currentTaskStats?.promptA }}</pre>
            </div>
            <div class="prompt-card prompt-card-b">
              <h4 style="margin-top: 0; margin-bottom: 12px; color: #db2777;">Prompt B</h4>
              <pre style="white-space: pre-wrap; word-wrap: break-word; line-height: 1.6; padding: 16px; background-color: #fef2f2; border-radius: 8px; font-family: monospace; margin: 0;">{{ currentTaskStats?.promptB }}</pre>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn primary" @click="closeStatsModal">关闭</button>
        </div>
      </div>
    </div>


  </section>
</template>

<script>
export default {
  name: 'TaskList',
  props: {
    tasks: {
      type: Array,
      required: true
    },
    currentUser: {
      type: Object,
      required: true
    },
    historyOperations: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      showStatsModal: false,
      currentTaskStats: null
    }
  },
  computed: {
    userStats() {
      if (!this.currentUser) return { completedSessions: 0, totalAnswers: 0, participatedTasks: 0, averageAccuracy: 0 }
      
      let completedSessions = 0
      let totalAnswers = 0
      let participatedTasks = new Set()
      
      this.tasks.forEach(task => {
        task.sessions.forEach(session => {
          if (session.userId === this.currentUser.username) {
            completedSessions++
            totalAnswers += session.answeredCount
            participatedTasks.add(task.id)
          }
        })
      })
      
      return {
        completedSessions,
        totalAnswers,
        participatedTasks: participatedTasks.size,
        averageAccuracy: 85 // 模拟数据
      }
    },
    taskTestCounts() {
      const counts = {};
      this.tasks.forEach(task => {
        counts[task.id] = this.historyOperations.filter(op => op.taskId === task.id).length;
      });
      return counts;
    },

  },
  methods: {
    showTaskStats(task) {
      // 计算任务的统计数据
      let promptASelections = 0
      let promptBSelections = 0
      
      // 从历史操作中统计选择结果，只统计当前用户的操作
      this.historyOperations.forEach(op => {
        if (op.taskId === task.id && op.type === 'session_completed' && op.userId === this.currentUser.username) {
          op.details.questions.forEach(q => {
            if (q.selectedPrompt === 'prompt_a') {
              promptASelections++
            } else if (q.selectedPrompt === 'prompt_b') {
              promptBSelections++
            }
          })
        }
      })
      
      // 计算总选择次数和百分比
      const totalSelections = promptASelections + promptBSelections
      const promptAPercentage = totalSelections > 0 ? Math.round((promptASelections / totalSelections) * 100) : 0
      const promptBPercentage = totalSelections > 0 ? Math.round((promptBSelections / totalSelections) * 100) : 0
      
      // 确定当前更优的 Prompt
      let conclusion = '暂无足够数据'
      let conclusionText = ''
      
      if (totalSelections > 0) {
        if (promptASelections > promptBSelections) {
          conclusion = 'Prompt A 当前更优'
          conclusionText = `当前 Prompt A 被选择 ${promptASelections} 次，高于 Prompt B 的 ${promptBSelections} 次，可作为下一轮优化的基线版本。`
        } else if (promptBSelections > promptASelections) {
          conclusion = 'Prompt B 当前更优'
          conclusionText = `当前 Prompt B 被选择 ${promptBSelections} 次，高于 Prompt A 的 ${promptASelections} 次，可作为下一轮优化的基线版本。`
        } else {
          conclusion = 'Prompt A 和 B 不分伯仲'
          conclusionText = `当前 Prompt A 和 B 各被选择 ${promptASelections} 次，建议增加测试次数以获得更明确的结果。`
        }
      }
      
      // 保存统计数据
      this.currentTaskStats = {
        taskName: task.name,
        promptA: task.promptA,
        promptB: task.promptB,
        promptASelections,
        promptBSelections,
        totalSelections,
        promptAPercentage,
        promptBPercentage,
        conclusion,
        conclusionText
      }
      
      // 显示弹窗
      this.showStatsModal = true
    },
    closeStatsModal() {
      this.showStatsModal = false
      this.currentTaskStats = null
    },

  }
}
</script>

<style scoped>
/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #64748b;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f1f5f9;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
}

/* 统计结果样式 */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.stats-left h3,
.stats-right h3 {
  margin-top: 0;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.conclusion-card {
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
}

.conclusion-card h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2563eb;
}

.conclusion-card p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
  color: #64748b;
}

.stats-bar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stats-label {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 500;
}

.stats-progress {
  height: 8px;
  background-color: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.stats-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.stats-fill-a {
  background-color: #2563eb;
}

.stats-fill-b {
  background-color: #db2777;
}

/* Prompt 内容网格布局 */
.prompt-content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.prompt-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
}

.prompt-card-a {
  border-left: 4px solid #2563eb;
}

.prompt-card-b {
  border-left: 4px solid #db2777;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .prompt-content-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
  }
  
  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .topbar > div:last-child {
    width: 100%;
    justify-content: space-between;
  }
}
</style>

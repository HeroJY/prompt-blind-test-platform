<template>
  <section id="admin-stats" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title">广场任务统计结果</h1>
        <p class="section-subtitle">统计口径：至少答过 1 道题的去重用户数，和所有已作答题目中真实映射到 Prompt A / Prompt B 的选择次数。</p>
      </div>
    </div>

    <div v-if="!selectedTask" id="statsEmpty" class="empty">请先在任务管理页选择一个任务后查看统计。</div>

    <div v-else-if="loading" class="empty">正在加载统计数据...</div>

    <div v-else-if="errorMessage" class="empty">{{ errorMessage }}</div>

    <div v-else id="statsContent" class="panel-grid">
      <div class="grid-4" id="statsKpis">
        <div class="card pad kpi-card">
          <div class="kpi-label">参与用户</div>
          <div class="kpi-value">{{ overview.participantCount }}</div>
        </div>
        <div class="card pad kpi-card">
          <div class="kpi-label">总作答数</div>
          <div class="kpi-value">{{ overview.totalSelections }}</div>
        </div>
        <div class="card pad kpi-card">
          <div class="kpi-label">Prompt A 选择</div>
          <div class="kpi-value">{{ overview.promptASelections }}</div>
        </div>
        <div class="card pad kpi-card">
          <div class="kpi-label">Prompt B 选择</div>
          <div class="kpi-value">{{ overview.promptBSelections }}</div>
        </div>
      </div>
      <div class="stat-banner">
        <div class="winner-box">
          <div class="eyebrow">当前结论</div>
          <div class="winner" id="winnerText">{{ winnerText }}</div>
          <div style="margin-top:10px;color:#475569;line-height:1.8;" id="winnerDesc">{{ winnerDesc }}</div>
        </div>
        <div class="card pad">
          <div class="eyebrow">Prompt 选择占比</div>
          <div class="bar-chart" id="barChart">
            <div class="bar-row">
              <div class="bar-head">
                <div>Prompt A</div>
                <div>{{ overview.promptAPercentage }}%</div>
              </div>
              <div class="bar-bg">
                <div class="bar-fill" :style="{ width: overview.promptAPercentage + '%' }"></div>
              </div>
            </div>
            <div class="bar-row">
              <div class="bar-head">
                <div>Prompt B</div>
                <div>{{ overview.promptBPercentage }}%</div>
              </div>
              <div class="bar-bg">
                <div class="bar-fill" :style="{ width: overview.promptBPercentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="card pad">
        <div class="eyebrow">分题概览</div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>题号</th>
                <th>原始问题摘要</th>
                <th>Prompt A</th>
                <th>Prompt B</th>
                <th>当前更优</th>
              </tr>
            </thead>
            <tbody id="statsItemBody">
              <tr v-for="item in statsItems" :key="item.id">
                <td>{{ item.code }}</td>
                <td>{{ item.sourceText }}</td>
                <td>{{ item.promptASelections || 0 }}</td>
                <td>{{ item.promptBSelections || 0 }}</td>
                <td>{{ item.promptASelections > (item.promptBSelections || 0) ? 'A' : item.promptBSelections > (item.promptASelections || 0) ? 'B' : '平局' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { postJSON } from '../../api'

export default {
  name: 'Stats',
  props: {
    selectedTask: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      loading: false,
      errorMessage: '',
      overview: {
        participantCount: 0,
        totalSelections: 0,
        promptASelections: 0,
        promptBSelections: 0,
        promptAPercentage: 0,
        promptBPercentage: 0
      },
      statsItems: []
    }
  },
  computed: {
    winnerText() {
      if (!this.selectedTask) return ''
      const a = this.overview.promptASelections || 0
      const b = this.overview.promptBSelections || 0
      if (a > b) return 'Prompt A 当前更优'
      if (b > a) return 'Prompt B 当前更优'
      return 'Prompt A 与 B 平局'
    },
    winnerDesc() {
      if (!this.selectedTask) return ''
      const a = this.overview.promptASelections || 0
      const b = this.overview.promptBSelections || 0
      const total = a + b
      if (total === 0) return '暂无数据'
      return `Prompt A: ${Math.round((a / total) * 100)}% vs Prompt B: ${Math.round((b / total) * 100)}%`
    }
  },
  watch: {
    selectedTask: {
      immediate: true,
      handler(newTask) {
        if (newTask && newTask.id) {
          this.fetchStats(newTask.id)
        } else {
          this.overview = {
            participantCount: 0,
            totalSelections: 0,
            promptASelections: 0,
            promptBSelections: 0,
            promptAPercentage: 0,
            promptBPercentage: 0
          }
          this.statsItems = []
          this.errorMessage = ''
        }
      }
    }
  },
  methods: {
    async fetchStats(taskId) {
      this.loading = true
      this.errorMessage = ''
      try {
        const overview = await postJSON('/stats/task_overview', { taskId })
        const items = await postJSON('/stats/task_items', { taskId })
        this.overview = {
          participantCount: overview.participantCount || 0,
          totalSelections: overview.totalSelections || 0,
          promptASelections: overview.promptASelections || 0,
          promptBSelections: overview.promptBSelections || 0,
          promptAPercentage: overview.promptAPercentage || 0,
          promptBPercentage: overview.promptBPercentage || 0
        }
        this.statsItems = items.items || []
      } catch (error) {
        this.errorMessage = error.message || '统计数据加载失败'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

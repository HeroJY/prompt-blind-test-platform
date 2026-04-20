<template>
  <div id="app">
    <!-- 登录页面 -->
    <Login v-if="!isLoggedIn" @login="login" />

    <!-- 应用页面 -->
    <div v-else id="appPage" class="page app-shell">
      <Sidebar 
        :current-user="currentUser" 
        :current-view="currentView"
        @change-view="currentView = $event"
        @switch-role="switchRole"
        @logout="logout"
      />

      <main class="main">
        <!-- 测试用户视图 -->
        <TaskList v-if="currentUser.role === 'tester' && currentView === 'tester-tasks' " 
          :tasks="testerTasks"
          :current-user="currentUser"
          :history-operations="historyOperations"
          @view-task-detail="viewTaskDetail"
          @start-task="startTask"
          @view-history="viewHistory"
          @create-import-task="createImportTask"
          @delete-task="deleteTask"
        />
        
        <ImportTaskEditor v-if="(currentUser.role === 'tester' && currentView === 'tester-import') || (currentUser.role === 'admin' && currentView === 'admin-import')" 
          :selected-task="selectedTask"
          @add-item="addItem"
          @delete-item="deleteItem"
          @back="backFromImport"
          @save="saveImportTask"
        />
        
        <TaskDetail v-if="currentUser.role === 'tester' && currentView === 'tester-task-detail'" 
          :selected-task="selectedTask"
          @back="currentView = 'tester-tasks'"
          @start-task="startTask"
        />
        
        <TestSession v-if="currentUser.role === 'tester' && currentView === 'tester-session' " 
          ref="testSession"
          :current-session="currentSession"
          :current-question-index="currentQuestionIndex"
          :selected-answer="selectedAnswer"
          :save-hint-text="saveHintText"
          :task-name="currentTaskName"
          :task="currentTaskData"
          :current-user="currentUser"
          @select-answer="selectAnswer"
          @prev-question="prevQuestion"
          @next-question="nextQuestion"
          @quit-session="quitSession"
          @finish-session="finishSession"
          @user-input-change="handleUserInputChange"
          @back="handleTestSessionBack"
        />
        
        <History v-if="currentUser.role === 'tester' && currentView === 'tester-history' " 
          :selected-task="selectedTask"
          @back="currentView = 'tester-tasks'"
          @delete-question="deleteQuestion"
        />

        <!-- 管理员视图 -->
        <TaskManagement v-if="currentUser.role === 'admin' && currentView === 'admin-tasks' " 
          :tasks="adminManagementTasks"
          @create-demo-task="createDemoTask"
          @edit-task="editTask"
          @view-stats="viewStats"
        />
        
        <TaskEditor v-if="currentUser.role === 'admin' && currentView === 'admin-editor'" 
          :selected-task="selectedTask"
          @delete-task="deleteTask"
          @publish-task="publishTask"
          @save-draft="saveDraft"
          @add-item="addItem"
          @delete-item="deleteItem"
          @back-to-task-management="backToTaskManagement"
        />
        
        <Stats v-if="currentUser.role === 'admin' && currentView === 'admin-stats'" 
          :selected-task="selectedTask"
        />
        
        <!-- 管理员Prompt一键生成视图 -->
        <PromptGenerate v-if="currentUser.role === 'admin' && currentView === 'admin-generate' " />
        
        <!-- 管理员Prompt盲选测试视图 -->
        <TaskList v-if="currentUser.role === 'admin' && currentView === 'admin-test' " 
          :tasks="adminTasks"
          :current-user="currentUser"
          :history-operations="historyOperations"
          @view-task-detail="viewTaskDetail"
          @start-task="startTask"
          @view-history="viewHistory"
          @create-import-task="createImportTask"
          @delete-task="deleteTask"
        />
        

        
        <TaskDetail v-if="currentUser.role === 'admin' && currentView === 'admin-task-detail'" 
          :selected-task="selectedTask"
          @back="currentView = 'admin-test'"
          @start-task="startTask"
        />
        
        <TestSession v-if="currentUser.role === 'admin' && currentView === 'admin-session' " 
          ref="testSession"
          :current-session="currentSession"
          :current-question-index="currentQuestionIndex"
          :selected-answer="selectedAnswer"
          :save-hint-text="saveHintText"
          :task-name="currentTaskName"
          :task="currentTaskData"
          :current-user="currentUser"
          @select-answer="selectAnswer"
          @prev-question="prevQuestion"
          @next-question="nextQuestion"
          @quit-session="quitAdminSession"
          @finish-session="finishSession"
          @user-input-change="handleUserInputChange"
          @back="handleAdminTestSessionBack"
        />
        
        <History v-if="currentUser.role === 'admin' && currentView === 'admin-history' " 
          :selected-task="selectedTask"
          @back="currentView = 'admin-test'"
          @delete-question="deleteQuestion"
        />
      </main>
    </div>

    <div id="toast" class="toast" :class="{ show: toast.show }">{{ toast.message }}</div>
  </div>
</template>

<script>
import Login from './views/auth/Login.vue'
import Sidebar from './components/Sidebar.vue'
import TaskList from './views/tester/TaskList.vue'
import TaskDetail from './views/tester/TaskDetail.vue'
import TestSession from './views/tester/TestSession.vue'
import History from './views/tester/History.vue'
import TaskManagement from './views/admin/TaskManagement.vue'
import TaskEditor from './views/admin/TaskEditor.vue'
import Stats from './views/admin/Stats.vue'
import PromptGenerate from './views/admin/PromptGenerate.vue'
import ImportTaskEditor from './views/tester/ImportTaskEditor.vue'
import { buildOperator, postJSON } from './api'

export default {
  name: 'App',
  components: {
    Login,
    Sidebar,
    TaskList,
    TaskDetail,
    TestSession,
    History,
    TaskManagement,
    TaskEditor,
    Stats,
    PromptGenerate,
    ImportTaskEditor
  },
  data() {
    return {
      isLoggedIn: false,
      currentUser: null,
      currentView: 'tester-tasks',
      selectedTaskId: null,
      currentSession: null,
      currentQuestionIndex: 0,
      selectedAnswer: null,
      saveHintText: '请选择 A 或 B，系统会立即保存。',
      userInputs: {},
      historyOperations: [],
      toast: {
        show: false,
        message: ''
      },
      tempTask: null,
      adminManagementTasks: [],
      adminTasks: [],
      testerTasks: []
    }
  },
  computed: {
    selectedTask() {
      if (this.selectedTaskId === 'temp') {
        return this.tempTask
      }
      
      let taskArray
      if (this.currentUser && this.currentUser.role === 'admin') {
        // 管理员在任务管理、配置、统计视图时使用adminManagementTasks
        if (['admin-tasks', 'admin-editor', 'admin-stats'].includes(this.currentView)) {
          taskArray = this.adminManagementTasks
        } else {
          // 管理员在测试相关视图时使用adminTasks
          taskArray = this.adminTasks
        }
      } else {
        // 测试员使用testerTasks
        taskArray = this.testerTasks
      }
      return taskArray.find(task => task.id === this.selectedTaskId)
    },
    currentTaskData() {
      if (!this.currentSession || !this.currentSession.taskId) {
        return null
      }
      const taskList = this.currentUser && this.currentUser.role === 'admin'
        ? this.adminTasks
        : this.testerTasks
      return taskList.find(task => task.id === this.currentSession.taskId) || null
    },
    currentTaskName() {
      return this.currentTaskData ? this.currentTaskData.name : ''
    }
  },
  methods: {
    operator() {
      return buildOperator(this.currentUser)
    },
    cloneDeep(value) {
      return JSON.parse(JSON.stringify(value))
    },
    async apiPost(path, body) {
      try {
        return await postJSON(path, body || {})
      } catch (error) {
        this.showToast(error.message || '请求失败')
        return null
      }
    },
    normalizeTask(task) {
      const result = this.cloneDeep(task || {})
      result.items = result.items || []
      result.sessions = result.sessions || []
      result.promptAImages = result.promptAImages || []
      result.promptBImages = result.promptBImages || []
      result.questionLimit = result.questionLimit || 49
      result.promptASelections = result.promptASelections || 0
      result.promptBSelections = result.promptBSelections || 0
      result.totalSelections = result.totalSelections || 0
      result.promptAPercentage = result.promptAPercentage || 0
      result.promptBPercentage = result.promptBPercentage || 0
      result.items.forEach(item => {
        item.promptASelections = item.promptASelections || 0
        item.promptBSelections = item.promptBSelections || 0
      })
      return result
    },
    setTasks(tasks) {
      const normalizedTasks = (tasks || []).map(task => this.normalizeTask(task))
      if (this.currentUser && this.currentUser.role === 'admin') {
        this.adminTasks = this.cloneDeep(normalizedTasks)
        this.adminManagementTasks = this.cloneDeep(normalizedTasks)
      } else {
        this.testerTasks = this.cloneDeep(normalizedTasks)
      }
      this.rebuildHistoryOperations(normalizedTasks)
    },
    rebuildHistoryOperations(tasks) {
      const operations = []
      ;(tasks || []).forEach(task => {
        ;(task.sessions || []).forEach(session => {
          operations.push({
            id: `h-${session.id}`,
            type: 'session_completed',
            userId: session.userId,
            taskId: task.id,
            taskName: task.name,
            sessionId: session.id,
            timestamp: session.endTime || session.startTime || new Date().toISOString(),
            details: {
              answeredCount: session.answeredCount || (session.answers || []).length,
              questions: (session.questions || []).map(question => {
                const answer = (session.answers || []).find(item => item.itemId === question.id)
                const questionId = String(question.id)
                return {
                  id: question.id,
                  originalQuestion: (session.userInputs || {})[question.id] || (session.userInputs || {})[questionId] || '',
                  answerA: question.answerA,
                  answerB: question.answerB,
                  selectedAnswer: answer ? answer.selectedOption : null,
                  selectedPrompt: answer ? answer.selectedPrompt : null,
                  modelJudge: question.modelJudge || null
                }
              })
            }
          })
        })
      })
      this.historyOperations = operations
    },
    async loadTasks() {
      const data = await this.apiPost('/task/list', {
        operator: this.operator()
      })
      if (!data) return
      this.setTasks(data.tasks || [])
    },
    async refreshTask(taskId) {
      const data = await this.apiPost('/task/detail', {
        operator: this.operator(),
        taskId
      })
      if (!data || !data.task) return null
      const normalizedTask = this.normalizeTask(data.task)
      ;['adminTasks', 'adminManagementTasks', 'testerTasks'].forEach(key => {
        const index = this[key].findIndex(item => item.id === normalizedTask.id)
        if (index >= 0) {
          this.$set(this[key], index, this.cloneDeep(normalizedTask))
        }
      })
      this.rebuildHistoryOperations(
        this.currentUser && this.currentUser.role === 'admin'
          ? this.adminTasks
          : this.testerTasks
      )
      return normalizedTask
    },
    async login(user) {
      this.currentUser = user
      this.isLoggedIn = true
      this.currentView = user.role === 'tester' ? 'tester-tasks' : 'admin-generate'
      await this.loadTasks()
      this.showToast('登录成功')
    },
    logout() {
      this.isLoggedIn = false
      this.currentUser = null
      this.currentView = 'tester-tasks'
      this.selectedTaskId = null
      this.currentSession = null
      this.testerTasks = []
      this.adminTasks = []
      this.adminManagementTasks = []
      this.historyOperations = []
      this.showToast('已退出登录')
    },
    switchRole() {
      const newRole = this.currentUser.role === 'tester' ? 'admin' : 'tester'
      return this.login({
        username: newRole === 'tester' ? 'tester01' : 'admin01',
        role: newRole
      })
    },
    viewTaskDetail(taskId) {
      this.selectedTaskId = taskId
      this.currentView = this.currentUser.role === 'admin' ? 'admin-task-detail' : 'tester-task-detail'
    },
    async viewHistory(taskId) {
      await this.refreshTask(taskId)
      this.selectedTaskId = taskId
      this.currentView = this.currentUser.role === 'admin' ? 'admin-history' : 'tester-history'
    },
    handleTestSessionBack() {
      this.currentSession = null
      this.currentView = this.currentUser.role === 'admin' ? 'admin-test' : 'tester-tasks'
      this.showToast('已返回任务列表')
    },
    handleAdminTestSessionBack() {
      this.currentSession = null
      this.currentView = 'admin-test'
      this.showToast('已返回任务列表')
    },
    async deleteQuestion(sessionId, questionId) {
      const data = await this.apiPost('/history/question/delete', {
        operator: this.operator(),
        sessionId,
        questionId
      })
      if (!data) return
      if (this.selectedTaskId && this.selectedTaskId !== 'temp') {
        await this.refreshTask(this.selectedTaskId)
      }
      this.showToast('测试任务记录已删除')
    },
    async startTask(taskId) {
      const data = await this.apiPost('/session/start', {
        operator: this.operator(),
        taskId,
        questionLimit: 49
      })
      if (!data) return
      this.currentSession = data.session
      this.currentQuestionIndex = 0
      this.selectedAnswer = null
      this.userInputs = {}
      this.currentView = this.currentUser.role === 'admin' ? 'admin-session' : 'tester-session'
    },
    handleUserInputChange(questionId, value) {
      if (this.currentSession) {
        this.currentSession.userInputs = this.currentSession.userInputs || {}
        this.currentSession.userInputs[questionId] = value
      }
    },
    async selectAnswer(answer) {
      if (!this.currentSession) return
      const currentQuestion = this.currentSession.questions[this.currentQuestionIndex]
      if (!currentQuestion || !currentQuestion.questionRecordId) {
        alert('请先生成候选回答')
        return
      }
      const data = await this.apiPost('/session/vote', {
        operator: this.operator(),
        sessionId: this.currentSession.id,
        questionRecordId: currentQuestion.questionRecordId,
        selectedOption: answer
      })
      if (!data) return
      this.selectedAnswer = answer
      this.saveHintText = '已保存选择，可继续下一题。'
      const currentAnswer = {
        itemId: currentQuestion.id,
        selectedOption: answer,
        selectedPrompt: data.selectedPrompt
      }
      const existingAnswerIndex = this.currentSession.answers.findIndex(a => a.itemId === currentAnswer.itemId)
      if (existingAnswerIndex >= 0) {
        this.currentSession.answers[existingAnswerIndex] = currentAnswer
      } else {
        this.currentSession.answers.push(currentAnswer)
      }
    },
    prevQuestion() {
      if (this.currentQuestionIndex > 0) {
        this.currentQuestionIndex--
        this.selectedAnswer = this.getAnswerForCurrentQuestion()
        this.saveHintText = this.selectedAnswer ? '已保存选择，可继续下一题。' : '请选择 A 或 B，系统会立即保存。'
      }
    },
    nextQuestion() {
      if (this.selectedAnswer && this.currentQuestionIndex < this.currentSession.questions.length - 1) {
        this.currentQuestionIndex++
        this.selectedAnswer = this.getAnswerForCurrentQuestion()
        this.saveHintText = this.selectedAnswer ? '已保存选择，可继续下一题。' : '请选择 A 或 B，系统会立即保存。'
      }
    },
    getAnswerForCurrentQuestion() {
      const answer = this.currentSession.answers.find(a => a.itemId === this.currentSession.questions[this.currentQuestionIndex].id)
      return answer ? answer.selectedOption || null : null
    },
    async quitSession(status = 'quit') {
      if (!this.currentSession) return
      const endpoint = status === 'finished' ? '/session/finish' : '/session/quit'
      const data = await this.apiPost(endpoint, {
        operator: this.operator(),
        sessionId: this.currentSession.id
      })
      if (!data) return
      await this.loadTasks()
      this.currentSession = null
      this.currentView = this.currentUser.role === 'admin' ? 'admin-test' : 'tester-tasks'
      this.showToast('已保存并退出测试')
    },
    quitAdminSession() {
      this.quitSession('quit')
    },
    finishSession() {
      this.quitSession('finished')
    },
    createDemoTask() {
      this.tempTask = {
        id: 'temp',
        name: `新任务 ${this.adminManagementTasks.length + 1}`,
        description: '请补充任务目标、Prompt 与测试题目。',
        promptA: '',
        promptB: '',
        promptAImages: [],
        promptBImages: [],
        status: 'draft',
        testCount: 5,
        questionLimit: 49,
        createdBy: this.currentUser.username,
        items: [],
        sessions: []
      }
      this.selectedTaskId = 'temp'
      this.currentView = 'admin-editor'
      this.showToast('已创建任务，请保存草稿或发布任务')
    },
    async editTask(taskId) {
      const task = await this.refreshTask(taskId)
      if (!task) return
      if (task && task.status === 'published') {
        this.tempTask = this.cloneDeep(task)
        this.tempTask.status = 'draft'
        this.selectedTaskId = 'temp'
      } else {
        this.selectedTaskId = taskId
      }
      this.currentView = 'admin-editor'
    },
    async viewStats(taskId) {
      await this.refreshTask(taskId)
      this.selectedTaskId = taskId
      this.currentView = 'admin-stats'
    },
    async addItem(itemForm) {
      if (!this.selectedTask) return
      if (this.selectedTaskId === 'temp') {
        this.tempTask.items.push({
          id: Date.now(),
          code: itemForm.code,
          sourceType: 'text',
          sortOrder: itemForm.sortOrder,
          sourceText: itemForm.sourceText,
          images: []
        })
      } else {
        const data = await this.apiPost('/task/item/create', {
          operator: this.operator(),
          taskId: this.selectedTask.id,
          item: {
            code: itemForm.code,
            sourceType: 'text',
            sortOrder: itemForm.sortOrder,
            sourceText: itemForm.sourceText,
            images: []
          }
        })
        if (!data) return
        await this.refreshTask(this.selectedTask.id)
      }
      this.showToast('已添加题目')
    },
    async deleteItem(itemId) {
      if (!this.selectedTask) return
      if (this.selectedTaskId === 'temp') {
        const itemIndex = this.selectedTask.items.findIndex(item => item.id === itemId)
        if (itemIndex >= 0) {
          this.selectedTask.items.splice(itemIndex, 1)
          this.showToast('题目已删除')
        }
        return
      }
      const data = await this.apiPost('/task/item/delete', {
        operator: this.operator(),
        taskId: this.selectedTask.id,
        itemId
      })
      if (!data) return
      await this.refreshTask(this.selectedTask.id)
      this.showToast('题目已删除')
    },
    async deleteTask(taskId) {
      if (taskId) {
        const data = await this.apiPost('/task/delete', {
          operator: this.operator(),
          taskId
        })
        if (!data) return
        await this.loadTasks()
        this.showToast('任务已删除')
        return
      }
      if (!this.selectedTask) {
        return
      }
      if (this.selectedTaskId === 'temp') {
        this.tempTask = null
        this.selectedTaskId = null
        this.currentView = 'admin-tasks'
        this.showToast('任务已删除')
        return
      }
      const data = await this.apiPost('/task/delete', {
        operator: this.operator(),
        taskId: this.selectedTaskId
      })
      if (!data) return
      await this.loadTasks()
      this.selectedTaskId = null
      this.currentView = 'admin-tasks'
      this.showToast('任务已删除')
    },
    async saveDraft() {
      if (!this.selectedTask) return
      const task = await this.persistTask('draft')
      if (!task) return
      this.tempTask = null
      this.showToast('任务已保存为草稿')
      this.selectedTaskId = null
      this.currentView = 'admin-tasks'
    },
    createImportTask() {
      // 创建一个新的临时任务用于导入
      this.tempTask = {
        id: 'temp-import',
        name: '新导入任务',
        description: '',
        promptA: '',
        promptB: '',
        promptAImages: [],
        promptBImages: [],
        status: 'draft',
        questionLimit: 49,
        createdBy: this.currentUser.username,
        items: [],
        sessions: []
      }
      this.selectedTaskId = 'temp'
      this.currentView = this.currentUser.role === 'admin' ? 'admin-import' : 'tester-import'
    },
    async saveImportTask() {
      if (!this.selectedTask) return
      const hasPromptA = !!(this.selectedTask.promptA || (this.selectedTask.promptAImages || []).length)
      const hasPromptB = !!(this.selectedTask.promptB || (this.selectedTask.promptBImages || []).length)
      if (!this.selectedTask.name || !this.selectedTask.description || !hasPromptA || !hasPromptB) {
        alert('请填写任务名称、描述，并为 Prompt A / B 至少提供文本或图片')
        return
      }
      const task = await this.persistTask('draft')
      if (!task) return
      this.tempTask = null
      this.selectedTaskId = null
      this.showToast('任务导入成功')
      this.currentView = this.currentUser.role === 'admin' ? 'admin-test' : 'tester-tasks'
    },
    backToTaskManagement() {
      this.selectedTaskId = null
      this.currentView = 'admin-tasks'
    },
    backFromImport() {
      this.tempTask = null
      this.selectedTaskId = null
      this.currentView = this.currentUser.role === 'admin' ? 'admin-test' : 'tester-tasks'
    },
    async publishTask() {
      if (!this.selectedTask) return
      const taskEditor = this.$children.find(child => child.$options.name === 'TaskEditor')
      if (taskEditor && taskEditor.publishCheckText !== '校验通过，可以发布。') {
        alert(`发布失败：${taskEditor.publishCheckText}`)
        return
      }
      const savedTask = await this.persistTask('draft')
      if (!savedTask) return
      const published = await this.apiPost('/task/publish', {
        operator: this.operator(),
        taskId: savedTask.id
      })
      if (!published) return
      await this.loadTasks()
      this.tempTask = null
      this.showToast('任务已重新发布')
      this.selectedTaskId = null
      this.currentView = 'admin-tasks'
    },
    async persistTask(status) {
      const payloadTask = this.cloneDeep(this.selectedTaskId === 'temp' ? this.tempTask : this.selectedTask)
      payloadTask.status = status
      if (this.selectedTaskId === 'temp') {
        const created = await this.apiPost('/task/create', {
          operator: this.operator(),
          task: payloadTask
        })
        if (!created) return null
        await this.loadTasks()
        return created.task
      }
      const updated = await this.apiPost('/task/update', {
        operator: this.operator(),
        taskId: payloadTask.id,
        task: payloadTask
      })
      if (!updated) return null
      await this.loadTasks()
      return updated.task
    },
    showToast(message) {
      this.toast.message = message
      this.toast.show = true
      setTimeout(() => {
        this.toast.show = false
      }, 3000)
    }
  }
}
</script>

<style>
:root {
  --bg: #f3f6fb;
  --surface: #ffffff;
  --surface-2: #f8fafc;
  --line: #e2e8f0;
  --line-2: #cbd5e1;
  --text: #0f172a;
  --muted: #64748b;
  --primary: #2563eb;
  --primary-2: #1d4ed8;
  --primary-soft: #dbeafe;
  --success: #16a34a;
  --warning: #d97706;
  --danger: #dc2626;
  --danger-soft: #fef2f2;
  --shadow: 0 10px 30px rgba(15, 23, 42, .08);
  --radius: 16px;
  --sidebar: 248px;
}

* {
  box-sizing: border-box;
}

html,
body {
  height: 100%;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  color: var(--text);
  background: linear-gradient(180deg, #f8fbff 0%, var(--bg) 100%);
}

.hidden {
  display: none !important;
}

.page {
  min-height: 100vh;
}

.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at 10% 10%, rgba(37, 99, 235, .10), transparent 26%),
    radial-gradient(circle at 90% 12%, rgba(124, 58, 237, .08), transparent 24%),
    linear-gradient(180deg, #f9fbff 0%, #f3f6fb 100%);
}

.auth-shell {
  width: 100%;
  max-width: 1120px;
  display: grid;
  grid-template-columns: 1.08fr .92fr;
  background: rgba(255, 255, 255, .78);
  border: 1px solid rgba(226, 232, 240, .95);
  border-radius: 28px;
  overflow: hidden;
  box-shadow: 0 30px 60px rgba(15, 23, 42, .12);
  backdrop-filter: blur(12px);
}

.auth-hero {
  padding: 42px;
  background: linear-gradient(140deg, #eff6ff 0%, #eef2ff 52%, #ffffff 100%);
  border-right: 1px solid rgba(226, 232, 240, .95);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 700px;
}

.auth-hero h1 {
  margin: 0;
  font-size: 36px;
  line-height: 1.2;
  white-space: pre-line;
}

.auth-hero p {
  margin: 14px 0 0;
  color: var(--muted);
  line-height: 1.8;
  font-size: 15px;
  max-width: 520px;
}

.hero-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 26px;
}

.hero-card {
  background: rgba(255, 255, 255, .85);
  border: 1px solid rgba(191, 219, 254, .8);
  border-radius: 18px;
  padding: 18px;
  box-shadow: var(--shadow);
}

.hero-card .eyebrow {
  color: var(--primary-2);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .06em;
  text-transform: uppercase;
}

.hero-card .big {
  font-size: 26px;
  font-weight: 800;
  margin-top: 8px;
}

.hero-strip {
  margin-top: 22px;
  display: grid;
  gap: 14px;
}

.mini-flow {
  background: rgba(255, 255, 255, .82);
  border: 1px solid rgba(226, 232, 240, .95);
  border-radius: 18px;
  padding: 18px;
  box-shadow: var(--shadow);
}

.steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.step {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 12px;
}

.step-num {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: 800;
  background: var(--primary-soft);
  color: var(--primary-2);
  margin-bottom: 8px;
}

.auth-panel {
  padding: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 700px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
}

.brand-mark {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  box-shadow: 0 12px 24px rgba(37, 99, 235, .25);
}

.brand h2 {
  margin: 0;
  font-size: 18px;
}

.brand p {
  margin: 4px 0 0;
  color: var(--muted);
  font-size: 13px;
}

.tabs {
  display: inline-flex;
  background: #eef2f7;
  padding: 4px;
  border-radius: 14px;
  margin-bottom: 18px;
}

.tab {
  border: 0;
  background: transparent;
  padding: 10px 16px;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  color: var(--muted);
}

.tab.active {
  background: #fff;
  color: var(--text);
  box-shadow: 0 2px 8px rgba(15, 23, 42, .08);
}

.card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}

.card.pad {
  padding: 22px;
}

.card.pad-lg {
  padding: 24px;
}

h1,
h2,
h3,
h4,
p {
  margin: 0;
}

.section-title {
  font-size: 28px;
  font-weight: 800;
  line-height: 1.2;
}

.section-subtitle {
  margin-top: 10px;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.8;
}

.field-grid {
  display: grid;
  gap: 14px;
  margin-top: 18px;
}

.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #475569;
  font-size: 13px;
  font-weight: 700;
}

input,
textarea,
select {
  width: 100%;
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 12px;
  font: inherit;
  color: var(--text);
  padding: 12px 14px;
  outline: none;
  transition: .18s ease;
}

input:focus,
textarea:focus,
select:focus {
  border-color: #93c5fd;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, .12);
}

textarea {
  min-height: 110px;
  resize: vertical;
}

.btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.btn {
  appearance: none;
  border: 0;
  cursor: pointer;
  padding: 11px 16px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  transition: .18s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn.primary {
  background: var(--primary);
  color: #fff;
}

.btn.primary:hover {
  background: var(--primary-2);
}

.btn.secondary {
  background: #fff;
  color: var(--text);
  border: 1px solid var(--line);
}

.btn.soft {
  background: var(--primary-soft);
  color: var(--primary-2);
}

.btn.success {
  background: var(--success);
  color: #fff;
}

.btn.danger {
  background: var(--danger-soft);
  color: var(--danger);
  border: 1px solid #fecaca;
}

.btn.block {
  width: 100%;
}

.auth-tip {
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 14px;
  background: #f8fafc;
  border: 1px solid var(--line);
  color: var(--muted);
  font-size: 13px;
  line-height: 1.7;
}

.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar) 1fr;
  min-height: 100vh;
}

.sidebar {
  background: rgba(255, 255, 255, .84);
  border-right: 1px solid rgba(226, 232, 240, .95);
  backdrop-filter: blur(10px);
  padding: 22px 18px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.nav-group {
  margin-top: 24px;
}

.nav-title {
  color: #94a3b8;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .08em;
  font-weight: 800;
  margin-bottom: 10px;
  padding: 0 10px;
}

.nav-item {
  width: 100%;
  text-align: left;
  border: 0;
  cursor: pointer;
  padding: 12px 14px;
  border-radius: 14px;
  background: transparent;
  color: #334155;
  font-weight: 700;
  margin-bottom: 6px;
}

.nav-item:hover {
  background: #eef4ff;
  color: var(--primary-2);
}

.nav-item.active {
  background: #e7f0ff;
  color: var(--primary-2);
}

.user-box {
  margin-top: 22px;
  padding: 16px;
  border-radius: 18px;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
  border: 1px solid #dbeafe;
}

.user-box .role {
  font-size: 12px;
  color: var(--primary-2);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .06em;
}

.user-box .name {
  font-size: 18px;
  font-weight: 800;
  margin-top: 6px;
}

.user-box .sub {
  color: var(--muted);
  font-size: 13px;
  margin-top: 6px;
  line-height: 1.7;
}

.main {
  padding: 24px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 18px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--muted);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--success);
}

.panel-grid {
  display: grid;
  gap: 18px;
}

.task-list {
  display: grid;
  gap: 16px;
}

.task-card {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  align-items: center;
  padding: 20px 22px;
}

.task-title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
}

.task-title {
  font-size: 20px;
  font-weight: 800;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  border: 1px solid var(--line);
  background: var(--surface-2);
  color: #475569;
}

.task-desc {
  color: var(--muted);
  line-height: 1.8;
  font-size: 14px;
  max-width: 760px;
}

.meta-row {
  margin-top: 14px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.meta-chip {
  padding: 7px 10px;
  border-radius: 999px;
  background: #f8fafc;
  border: 1px solid var(--line);
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.right-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 180px;
}

.kpi-card {
  padding: 18px;
}

.kpi-label {
  color: var(--muted);
  font-size: 13px;
}

.kpi-value {
  font-size: 30px;
  font-weight: 800;
  margin-top: 8px;
}

.task-detail {
  display: grid;
  grid-template-columns: 1.15fr .85fr;
  gap: 18px;
}

.key-value {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.key-line {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 12px;
  font-size: 14px;
  line-height: 1.8;
  padding-bottom: 12px;
  border-bottom: 1px solid #eff4f8;
}

.key-line .key {
  color: var(--muted);
  font-weight: 700;
}

.prompt-box {
  border: 1px solid var(--line);
  border-radius: 16px;
  background: #f8fbff;
  padding: 16px;
  min-height: 180px;
  white-space: pre-wrap;
  font-size: 14px;
  line-height: 1.8;
  color: #334155;
}

.notice {
  padding: 16px 18px;
  border-radius: 16px;
  background: linear-gradient(135deg, #eff6ff, #ffffff);
  border: 1px solid #dbeafe;
  color: #1e3a8a;
  font-size: 14px;
  line-height: 1.8;
}

.progress-panel {
  display: flex;
  align-items: center;
  gap: 16px;
}

.progress-bar {
  height: 10px;
  flex: 1;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.progress-bar>span {
  display: block;
  height: 100%;
  width: 0;
  border-radius: 999px;
  background: linear-gradient(90deg, #2563eb, #7c3aed);
  transition: width .2s ease;
}

.qa-layout {
  display: grid;
  gap: 18px;
}

.source-wrap {
  padding: 18px;
  border-radius: 18px;
  border: 1px dashed #bfd4f9;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}

.eyebrow {
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.source-text {
  color: #334155;
  line-height: 1.9;
  font-size: 15px;
  white-space: pre-wrap;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.mock-image {
  height: 176px;
  border-radius: 16px;
  border: 1px solid var(--line-2);
  background: linear-gradient(135deg, #dbeafe, #ede9fe);
  display: grid;
  place-items: center;
  color: #475569;
  font-weight: 800;
  position: relative;
  overflow: hidden;
}

.mock-image::after {
  content: "示意图";
  position: absolute;
  right: 10px;
  bottom: 10px;
  background: rgba(255, 255, 255, .86);
  border: 1px solid rgba(255, 255, 255, .95);
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 12px;
  color: #475569;
}

.answer-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.answer-card {
  border: 1px solid var(--line);
  background: #fff;
  border-radius: 20px;
  display: grid;
  gap: 14px;
  padding: 20px;
  min-height: 200px;
  transition: .18s ease;
  position: relative;
}

.answer-card:hover {
  border-color: #bfdbfe;
  box-shadow: 0 14px 28px rgba(37, 99, 235, .08);
}

.answer-card.selected {
  border-color: #60a5fa;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, .10);
}

.answer-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.answer-tag {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, #0f172a, #334155);
  flex-shrink: 0;
}

.answer-title {
  font-size: 18px;
  font-weight: 800;
}

.answer-sub {
  margin-top: 4px;
  color: var(--muted);
  font-size: 13px;
}

.answer-body {
  color: #334155;
  font-size: 14px;
  line-height: 1.9;
  white-space: pre-wrap;
}

.sticky-actions {
  position: sticky;
  bottom: 0;
  padding-top: 8px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, .92);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(226, 232, 240, .95);
  box-shadow: 0 8px 24px rgba(15, 23, 42, .08);
}

.save-hint {
  color: var(--muted);
  font-size: 13px;
}

.split {
  display: grid;
  grid-template-columns: 1.15fr .85fr;
  gap: 18px;
}

.upload-box {
  padding: 24px;
  border-radius: 18px;
  border: 2px dashed #bfd4f9;
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
  text-align: center;
}

.file-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.file-chip {
  padding: 8px 12px;
  border-radius: 999px;
  background: #eef4ff;
  border: 1px solid #bfdbfe;
  color: var(--primary-2);
  font-size: 12px;
  font-weight: 700;
}

.table-wrap {
  overflow: auto;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: #fff;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th,
td {
  text-align: left;
  padding: 14px 16px;
  border-bottom: 1px solid #eef2f7;
  vertical-align: top;
}

th {
  color: #64748b;
  font-size: 12px;
  letter-spacing: .06em;
  text-transform: uppercase;
  background: #f8fafc;
}

.stat-banner {
  display: grid;
  grid-template-columns: 1.08fr .92fr;
  gap: 18px;
}

.winner-box {
  padding: 22px;
  border-radius: 18px;
  background: linear-gradient(135deg, #eff6ff, #f5f3ff);
  border: 1px solid #dbeafe;
  min-height: 180px;
}

.winner-box .winner {
  font-size: 32px;
  font-weight: 900;
  color: var(--primary-2);
  margin-top: 8px;
}

.bar-chart {
  display: grid;
  gap: 16px;
  margin-top: 14px;
}

.bar-row {
  display: grid;
  gap: 8px;
}

.bar-head {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.bar-bg {
  height: 14px;
  border-radius: 999px;
  overflow: hidden;
  background: #e2e8f0;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #2563eb, #7c3aed);
}

.empty {
  padding: 50px 20px;
  text-align: center;
  color: var(--muted);
  border: 1px dashed var(--line-2);
  border-radius: 18px;
  background: #fff;
}

.toast {
  position: fixed;
  top: 50%;
  left: 50%;
  background: rgba(15, 23, 42, .92);
  color: #fff;
  padding: 20px 24px;
  border-radius: 16px;
  font-size: 16px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, .3);
  opacity: 0;
  transform: translate(-50%, -50%) translateY(20px);
  pointer-events: none;
  transition: .2s ease;
  z-index: 50;
  min-width: 300px;
  text-align: center;
}

.toast.show {
  opacity: 1;
  transform: translate(-50%, -50%) translateY(0);
}

.test-panel {
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 14px;
  background: #0f172a;
  color: #fff;
  font-size: 12px;
  line-height: 1.7;
  white-space: pre-wrap;
  display: none;
}

@media (max-width: 1180px) {

  .auth-shell,
  .task-detail,
  .split,
  .stat-banner {
    grid-template-columns: 1fr;
  }

  .grid-4 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: relative;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .answer-grid,
  .grid-2,
  .grid-3,
  .image-grid,
  .steps,
  .task-card,
  .grid-4 {
    grid-template-columns: 1fr;
  }

  .topbar,
  .action-bar,
  .progress-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .right-actions {
    min-width: 0;
  }

  .auth-panel,
  .auth-hero {
    min-height: auto;
  }
}
</style>

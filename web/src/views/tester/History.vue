<template>
  <div>
    <section id="tester-history" class="view">
      <div class="topbar">
        <div>
          <h1 class="section-title">历史操作</h1>
          <p class="section-subtitle">查看任务的历史测试记录，包括每一轮的原始问题、候选回答和选择结果。</p>
        </div>
        <div class="btn-row">
          <button class="btn secondary" @click="$emit('back')">返回任务列表</button>
        </div>
      </div>

      <div v-if="!selectedTask" class="empty">请选择一个任务查看历史操作。</div>

      <div v-else>
        <div class="card pad">
          <h2 style="margin-bottom: 16px;">{{ selectedTask.name }}</h2>
          <p style="color: var(--muted); margin-bottom: 24px;">{{ selectedTask.description }}</p>

          <div v-if="selectedTask.sessions.length === 0 || !hasValidSessions" class="empty">暂无测试记录。</div>

          <div v-else class="session-list">
            <div v-for="(session, index) in validSessions" :key="session.id" class="session-item card pad" style="margin-bottom: 24px;">
              <div v-for="(question, qIndex) in getSessionQuestions(session)" :key="question.id" class="question-item" style="margin-bottom: 24px; padding-bottom: 24px; border-bottom: 1px solid var(--line);">
                <div class="question-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                  <h3 style="margin: 0; font-size: 18px; font-weight: 800;">测试 #{{ index + 1 }} - 第 {{ qIndex + 1 }} 题</h3>
                  <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="color: var(--muted); font-size: 13px;">{{ formatTime(session.endTime || new Date()) }}</span>
                    <button class="btn danger" style="padding: 6px 12px; font-size: 12px;" @click="deleteQuestion(session.id, question.id)">删除</button>
                  </div>
                </div>

                <div class="original-question" style="margin: 16px 0; padding: 12px; background: #f8fafc; border-radius: 12px;">
                  <div style="font-weight: 700; margin-bottom: 8px;">问题：{{ question.originalQuestion || '无输入' }}</div>
                </div>
                
                <div v-if="question.testData" class="test-data" style="margin: 16px 0; padding: 12px; background: #f0f9ff; border-radius: 12px;">
                  <div style="font-weight: 700; margin-bottom: 8px;">测试数据：</div>
                  <div style="line-height: 1.6; color: #334155;">{{ question.testData }}</div>
                </div>

                <div class="answers" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                  <div class="answer-card" :class="{ 'selected': question.selectedAnswer === 'A' }" style="padding: 16px; border: 2px solid var(--line); border-radius: 12px; max-height: 150px; display: flex; flex-direction: column; transition: all 0.3s ease;">
                    <div style="font-weight: 700; margin-bottom: 8px;">候选回答 A：</div>
                    <div style="line-height: 1.6; color: #334155; max-height: 100px; overflow-y: auto; flex: 1;">{{ question.answerA }}</div>
                    <div v-if="question.promptMapping" style="margin-top: 8px; font-size: 12px; color: #64748b;">
                      实际使用：<button class="btn soft" style="padding: 2px 8px; font-size: 12px; margin-left: 4px;" @click="showPromptDetail(question.promptMapping.a === 'prompt_a' ? 'A' : 'B', question)">Prompt {{ question.promptMapping.a === 'prompt_a' ? 'A' : 'B' }}</button>
                    </div>
                  </div>
                  <div class="answer-card" :class="{ 'selected': question.selectedAnswer === 'B' }" style="padding: 16px; border: 2px solid var(--line); border-radius: 12px; max-height: 150px; display: flex; flex-direction: column; transition: all 0.3s ease;">
                    <div style="font-weight: 700; margin-bottom: 8px;">候选回答 B：</div>
                    <div style="line-height: 1.6; color: #334155; max-height: 100px; overflow-y: auto; flex: 1;">{{ question.answerB }}</div>
                    <div v-if="question.promptMapping" style="margin-top: 8px; font-size: 12px; color: #64748b;">
                      实际使用：<button class="btn soft" style="padding: 2px 8px; font-size: 12px; margin-left: 4px;" @click="showPromptDetail(question.promptMapping.b === 'prompt_a' ? 'A' : 'B', question)">Prompt {{ question.promptMapping.b === 'prompt_a' ? 'A' : 'B' }}</button>
                    </div>
                  </div>
                </div>

                <div v-if="question.selectedAnswer" class="selected-answer" style="margin-top: 16px; padding: 12px; background: #dcfce7; border-radius: 12px;">
                  <div style="font-weight: 700;">您的选择：候选回答 {{ question.selectedAnswer }}</div>
                </div>
                
                <div v-if="question.modelJudge" class="model-judge" style="margin-top: 16px; padding: 12px; background: #dbeafe; border-radius: 12px;">
                  <div style="font-weight: 700; margin-bottom: 8px;">大模型裁判推荐：{{ question.modelJudge.recommended }}</div>
                  <div style="line-height: 1.6; color: #334155;">{{ question.modelJudge.reason }}</div>
                </div>
                
                <div v-else class="model-judge" style="margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 12px;">
                  <div style="font-weight: 700; color: var(--muted);">未使用大模型裁判</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Prompt详情弹窗 -->
    <div v-if="showPromptModal" class="modal-overlay" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 1000;">
      <div class="modal-content" style="background-color: white; padding: 24px; border-radius: 12px; width: 80%; max-width: 600px; max-height: 80vh; overflow-y: auto;">
        <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
          <h3 style="margin: 0; font-size: 18px; font-weight: 800;">Prompt {{ currentPromptType }} 详情</h3>
        </div>
        <div class="modal-body" style="margin-bottom: 24px;">
          <pre style="white-space: pre-wrap; word-wrap: break-word; line-height: 1.6; padding: 16px; background-color: #f8fafc; border-radius: 8px; font-family: monospace;">{{ currentPromptContent }}</pre>
          <div v-if="currentPromptImages.length" class="prompt-image-grid">
            <img v-for="(image, index) in currentPromptImages" :key="`history-prompt-${index}`" :src="image.dataUrl" :alt="image.name || `Prompt ${currentPromptType} ${index + 1}`" class="prompt-image-preview" />
          </div>
        </div>
        <div class="modal-footer" style="display: flex; justify-content: flex-end;">
          <button class="btn primary" style="padding: 8px 16px;" @click="showPromptModal = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'History',
  props: {
    selectedTask: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      showPromptModal: false,
      currentPromptType: '',
      currentPromptContent: '',
      currentPromptImages: []
    }
  },
  computed: {
    hasValidSessions() {
      if (!this.selectedTask || !this.selectedTask.sessions) return false
      return this.selectedTask.sessions.some(session => this.getSessionQuestions(session).length > 0)
    },
    validSessions() {
      if (!this.selectedTask || !this.selectedTask.sessions) return []
      return this.selectedTask.sessions.filter(session => this.getSessionQuestions(session).length > 0)
    }
  },
  methods: {
    formatTime(time) {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    getSessionQuestions(session) {
      if (!session.questions) return []
      return session.questions.map(q => {
        const answer = session.answers.find(a => a.itemId === q.id)
        return {
          id: q.id,
          originalQuestion: session.userInputs ? session.userInputs[q.id] : '',
          testData: q.testData || (session.testDataByQuestion ? session.testDataByQuestion[q.id] : ''),
          answerA: q.answerA,
          answerB: q.answerB,
          selectedAnswer: answer ? (answer.selectedPrompt === 'prompt_a' ? 'A' : 'B') : null,
          modelJudge: q.modelJudge || null,
          promptMapping: q.promptMapping || null
        }
      })
    },
    deleteQuestion(sessionId, questionId) {
      if (confirm('确定要删除这条测试任务记录吗？')) {
        this.$emit('delete-question', sessionId, questionId)
      }
    },
    showPromptDetail(promptType, question) {
      this.currentPromptType = promptType
      this.currentPromptImages = []
      // 从selectedTask中获取对应的prompt内容
      if (this.selectedTask) {
        const promptImages = promptType === 'A'
          ? (this.selectedTask.promptAImages || [])
          : (this.selectedTask.promptBImages || [])
        if (promptType === 'A' && this.selectedTask.promptA) {
          this.currentPromptContent = this.selectedTask.promptA
        } else if (promptType === 'B' && this.selectedTask.promptB) {
          this.currentPromptContent = this.selectedTask.promptB
        } else if (promptImages.length) {
          this.currentPromptContent = '当前 Prompt 未填写文字，已上传图片内容。'
        } else {
          this.currentPromptContent = '未找到对应的Prompt内容'
        }
        if (promptType === 'A') {
          this.currentPromptImages = this.selectedTask.promptAImages || []
        } else if (promptType === 'B') {
          this.currentPromptImages = this.selectedTask.promptBImages || []
        }
      } else {
        this.currentPromptContent = '未找到对应的Prompt内容'
      }
      this.showPromptModal = true
    }
  }
}
</script>

<style scoped>
.answer-card.selected {
  border-color: #10b981 !important;
  background-color: #f0fdf4 !important;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
}

.answer-card.selected .answer-title {
  color: #059669 !important;
  font-weight: 800 !important;
}

.prompt-image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.prompt-image-preview {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #fff;
}
</style>

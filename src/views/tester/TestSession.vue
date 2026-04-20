<template>
  <section id="tester-session" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title" id="sessionTaskTitle">{{ currentSession ? `进行中的测试 - ${taskName}` : '测试会话' }}</h1>
        <p class="section-subtitle">每选择一次都会立刻写入后端。你可以随时退出，再回来查看历史记录和统计累计结果。</p>
      </div>
      <div class="btn-row">
        <button class="btn secondary" @click="$emit('back')">返回任务列表</button>
        <button class="btn soft" id="finishSessionBtn" @click="$emit('finish-session')">保存并结束本次任务</button>
      </div>
    </div>

    <div v-if="!currentSession" id="sessionEmpty" class="empty">当前还没有开始任何测试任务。请先去任务列表页选择一个任务并开始测试。</div>

    <div v-else id="sessionContent" class="qa-layout">
      <div class="card pad progress-panel">
        <div style="font-weight:800;min-width:140px;" id="sessionProgressText">第 {{ currentQuestionIndex + 1 }} / {{ currentSession.questions.length }} 题</div>
        <div class="progress-bar"><span id="sessionProgressBar" :style="{ width: progressPercentage + '%' }"></span></div>
        <div class="status-pill" id="sessionAutoSave">自动保存已开启</div>
      </div>

      <div class="card pad">
        <div class="source-wrap">
          <div class="eyebrow">测试数据</div>
          <textarea v-model="currentTestData" @input="handelTestDataChange" placeholder="输入测试数据..." :disabled="inputDisabled" style="width: 100%; min-height: 80px; padding: 12px; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 14px; resize: vertical;"></textarea>
        </div>
      </div>

      <div class="card pad">
        <div class="source-wrap">
          <div class="eyebrow">原始问题</div>
          <textarea v-model="userInput" placeholder="请输入您的问题..." :disabled="inputDisabled" style="width: 100%; min-height: 100px; padding: 12px; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 14px; resize: vertical;"></textarea>
          <div style="margin-top: 12px; display: flex; justify-content: center;">
            <button class="btn primary" @click="generateAnswers" :disabled="generateButtonDisabled">
              开始生成
            </button>
          </div>
        </div>
      </div>

      <div v-if="showAnswers || isGenerating" class="answer-grid" id="answerGrid">
        <div class="answer-card" :class="{ selected: selectedAnswer === 'A' }">
          <div class="answer-top">
            <div class="answer-tag answer-tag-a">A</div>
            <div style="flex: 1;">
              <div class="answer-title" style="text-align: left;">候选回答 A</div>
              <div class="answer-sub">用户侧不显示 Prompt 来源</div>
            </div>
          </div>
          <div class="answer-body" v-if="!isGenerating">
            {{ currentQuestion ? currentQuestion.answerA : '正在生成回答 A...' }}
          </div>
          <div class="answer-body" v-else style="display: flex; align-items: center; justify-content: center; min-height: 200px;">
            <div style="text-align: center; color: #64748b;">
              <div style="font-size: 16px; margin-bottom: 10px;">正在生成，请稍后。。。</div>
              <div style="width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top: 4px solid #2563eb; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
            </div>
          </div>
          <div style="margin-top: 20px;">
            <button class="btn primary block" @click="selectAnswer('A')" :class="{ 'selected': selectedAnswer === 'A' }" :disabled="isGenerating">选择 A</button>
          </div>
        </div>
        <div class="answer-card" :class="{ selected: selectedAnswer === 'B' }">
          <div class="answer-top">
            <div class="answer-tag answer-tag-b">B</div>
            <div style="flex: 1;">
              <div class="answer-title" style="text-align: left;">候选回答 B</div>
              <div class="answer-sub">用户侧不显示 Prompt 来源</div>
            </div>
          </div>
          <div class="answer-body" v-if="!isGenerating">
            {{ currentQuestion ? currentQuestion.answerB : '正在生成回答 B...' }}
          </div>
          <div class="answer-body" v-else style="display: flex; align-items: center; justify-content: center; min-height: 200px;">
            <div style="text-align: center; color: #64748b;">
              <div style="font-size: 16px; margin-bottom: 10px;">正在生成，请稍后。。。</div>
              <div style="width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top: 4px solid #9333ea; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
            </div>
          </div>
          <div style="margin-top: 20px;">
            <button class="btn primary block" @click="selectAnswer('B')" :class="{ 'selected': selectedAnswer === 'B' }" :disabled="isGenerating">选择 B</button>
          </div>
        </div>
      </div>

      <!-- 大模型裁判部分 -->
      <div v-if="showAnswers && !isGenerating" class="card pad" style="margin-top: 18px;">
        <div class="eyebrow">大模型裁判</div>
        <div v-if="currentJudgeAnswer" class="judge-result" style="margin-top: 16px; padding: 16px; border: 1px solid #e2e8f0; border-radius: 12px; background: #f8fafc;">
          <div style="font-weight: 800; margin-bottom: 8px;">大模型推荐：{{ currentJudgeAnswer.recommended }}</div>
          <div style="line-height: 1.6; color: #334155;">{{ currentJudgeAnswer.reason }}</div>
        </div>
        <div style="margin-top: 16px; display: flex; justify-content: center;">
          <button class="btn soft" @click="generateJudgeAnswer" :disabled="!canJudge || isJudging">
            <span v-if="!isJudging">大模型裁判</span>
            <span v-else style="display: flex; align-items: center;">
              <div style="width: 16px; height: 16px; border: 2px solid #2563eb; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px;"></div>
              正在分析...
            </span>
          </button>
        </div>
      </div>

      <div class="sticky-actions">
        <div class="action-bar">
          <div class="save-hint" id="saveHint">{{ saveHintText }}</div>
          <div class="btn-row">
            <button class="btn secondary" id="prevQuestionBtn" @click="prevQuestion" :disabled="currentQuestionIndex === 0">上一题</button>
            <button class="btn primary" id="nextQuestionBtn" @click="nextQuestion">下一题</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { buildOperator, postJSON } from '../../api'

export default {
  name: 'TestSession',
  props: {
    currentSession: {
      type: Object,
      default: null
    },
    currentQuestionIndex: {
      type: Number,
      default: 0
    },
    selectedAnswer: {
      type: String,
      default: null
    },
    saveHintText: {
      type: String,
      default: '请选择 A 或 B，系统会立即保存。'
    },
    taskName: {
      type: String,
      default: ''
    },
    task: {
      type: Object,
      default: null
    },
    currentUser: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      userInputs: {},
      testDataByQuestion: {},
      currentTestData: '',
      showAnswers: false,
      generateButtonDisabled: false,
      inputDisabled: false,
      isGenerating: false,
      modelJudgeAnswers: {},
      isJudging: false,
      testDataInitialized: false,
      promptMappings: {} // 存储每个问题的prompt映射关系
    }
  },
  computed: {
    currentQuestion() {
      if (!this.currentSession || !this.currentSession.questions[this.currentQuestionIndex]) {
        return null
      }
      return this.currentSession.questions[this.currentQuestionIndex]
    },
    progressPercentage() {
      if (!this.currentSession) return 0
      return ((this.currentQuestionIndex + 1) / this.currentSession.questions.length) * 100
    },
    userInput: {
      get() {
        if (!this.currentQuestion) return ''
        // 如果已经有保存的用户输入，返回保存的值
        if (this.userInputs[this.currentQuestion.id] !== undefined) {
          return this.userInputs[this.currentQuestion.id]
        }
        // 如果是导入的问题，显示导入的内容
        if (this.currentQuestion.isImported && this.currentQuestion.sourceText) {
          return this.currentQuestion.sourceText
        }
        // 否则返回空字符串
        return ''
      },
      set(value) {
        if (this.currentQuestion) {
          this.$set(this.userInputs, this.currentQuestion.id, value)
          console.log('User input saved for question', this.currentQuestion.id, ':', value)
          // 传递用户输入变化给父组件
          this.$emit('user-input-change', this.currentQuestion.id, value)
        }
      }
    },
    canJudge() {
      return this.showAnswers && !this.isGenerating && this.currentQuestion
    },
    currentJudgeAnswer() {
      if (!this.currentQuestion) return null
      return this.modelJudgeAnswers[this.currentQuestion.id]
    },
  },
  watch: {
    currentQuestionIndex(newIndex) {
      // 保存当前题目索引，用于调试
      console.log('currentQuestionIndex changed to:', newIndex)
      console.log('Current question:', this.currentQuestion)
      console.log('User inputs:', this.userInputs)
      console.log('Model judge answers:', this.modelJudgeAnswers)
      
      // 保存当前问题的测试数据
      // if (this.currentQuestion) {
      //   this.testDataByQuestion[this.currentQuestion.id] = this.currentTestData
      // }
      
      // 更新 currentTestData 为新问题的测试数据
      if (this.currentQuestion) {
        this.currentTestData = this.testDataByQuestion[this.currentQuestion.id] || ''
      } else {
        this.currentTestData = ''
      }
      
      // 检查当前题目是否已经有答案
      if (this.selectedAnswer) {
        this.showAnswers = true
        this.generateButtonDisabled = true
        this.inputDisabled = true
      } else {
        // 检查当前题目是否有用户输入
        const hasUserInput = this.currentQuestion && this.userInputs[this.currentQuestion.id]
        if (hasUserInput) {
          this.showAnswers = true
          this.generateButtonDisabled = true
          this.inputDisabled = true
        } else {
          this.showAnswers = false
          this.generateButtonDisabled = false
          this.inputDisabled = false
        }
      }
    },
    task: {
      handler(newTask) {
        // console.log('真是你个老6: ', newTask);
        // console.log('真是你个老6: ', this.testDataByQuestion);
        if (newTask && !this.testDataInitialized) {
          this.testDataInitialized = true
          if (this.currentSession && this.currentSession.questions) {
            this.currentSession.questions.forEach(question => {
              if (!this.testDataByQuestion.hasOwnProperty(question.id)) {
                this.testDataByQuestion[question.id] = newTask.testData || ''
              }
            })
          }
          // 更新 currentTestData 为当前问题的测试数据
          if (this.currentQuestion) {
            this.currentTestData = this.testDataByQuestion[this.currentQuestion.id] || ''
          }
        } else if (!newTask) {
          this.testDataByQuestion = {}
          this.currentTestData = ''
          this.testDataInitialized = false
        }
      },
      immediate: true,
      deep: false
    }
  },
  methods: {
    handelTestDataChange() {
      if (this.currentQuestion) {
        this.$set(this.testDataByQuestion, this.currentQuestion.id, this.currentTestData)
      }
      // console.log('变了数据: ', this.testDataByQuestion);
    },
    selectAnswer(answer) {
      this.$emit('select-answer', answer)
    },
    prevQuestion() {
      this.$emit('prev-question')
    },
    nextQuestion() {
      if (!this.selectedAnswer) {
        alert('请至少选择一个答案');
        return;
      }
      
      // 检查是否是最后一题
      const isLastQuestion = this.currentQuestionIndex === this.currentSession.questions.length - 1;
      
      // 检查是否有用户输入、候选回答和用户选择
      const hasUserInput = this.userInput.trim() !== '';
      const hasAnswers = this.currentQuestion && this.currentQuestion.answerA && this.currentQuestion.answerB;
      const hasSelection = this.selectedAnswer !== null;
      
      if (isLastQuestion && hasUserInput && hasAnswers && hasSelection) {
        // 弹窗询问用户是否要保存并结束本次任务
        if (confirm('是否要保存并结束本次任务？')) {
          this.$emit('finish-session');
        } else {
          // 用户取消，停留在当前页面
          return;
        }
      } else {
        this.$emit('next-question');
      }
    },
    async generateAnswers() {
      if (!this.userInput.trim()) {
        alert('请输入原始问题');
        return
      }

      if (this.currentQuestion) {
        const inputValue = this.userInput
        this.$set(this.userInputs, this.currentQuestion.id, inputValue)
        this.$emit('user-input-change', this.currentQuestion.id, inputValue)
      }

      this.isGenerating = true
      this.generateButtonDisabled = true
      this.inputDisabled = true

      try {
        const data = await postJSON('/session/generate', {
          operator: buildOperator(this.currentUser),
          sessionId: this.currentSession.id,
          slotIndex: this.currentQuestionIndex,
          originalQuestion: this.userInput,
          testData: this.currentTestData
        })

        if (this.currentQuestion) {
          this.currentQuestion.answerA = data.candidateA || ''
          this.currentQuestion.answerB = data.candidateB || ''
          this.currentQuestion.questionRecordId = data.questionRecordId || ''
        }

        this.showAnswers = true
      } catch (error) {
        alert(error.message || '生成失败')
        this.generateButtonDisabled = false
        this.inputDisabled = false
      } finally {
        this.isGenerating = false
      }
    },
    async generateJudgeAnswer() {
      if (!this.currentQuestion) return
      if (!this.currentQuestion.questionRecordId) {
        alert('请先生成候选回答')
        return
      }

      this.isJudging = true

      try {
        const judgeResult = await postJSON('/session/judge', {
          operator: buildOperator(this.currentUser),
          sessionId: this.currentSession.id,
          questionRecordId: this.currentQuestion.questionRecordId
        })
        this.$set(this.modelJudgeAnswers, this.currentQuestion.id, judgeResult)
      } catch (error) {
        alert(error.message || '裁判失败')
      } finally {
        this.isJudging = false
      }
    },
    getUserInputs() {
      return this.userInputs
    },
    getModelJudgeAnswers() {
      return this.modelJudgeAnswers
    }
  }
}
</script>

<style scoped>
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.answer-tag-a {
  background: #000;
  color: #fff;
}

.answer-tag-b {
  background: #9333ea;
  color: #fff;
}

.answer-card {
  display: flex;
  flex-direction: column;
  min-height: 200px;
}

.answer-body {
  flex: 1;
  margin: 16px 0;
}

.btn.primary.block {
  width: 100%;
  justify-content: center;
  display: flex;
  align-items: center;
}

#nextQuestionBtn {
  opacity: 1 !important;
  cursor: pointer !important;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

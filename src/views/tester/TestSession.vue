<template>
  <section id="tester-session" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title" id="sessionTaskTitle">{{ currentSession ? `进行中的测试 - ${taskName}` : '测试会话' }}</h1>
        <p class="section-subtitle">每选择一次都会立刻保存到模拟数据中。你可以体验“选一题就退出”的流程，看统计是否正确累计。</p>
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
    }
  },
  data() {
    return {
      userInputs: {},
      showAnswers: false,
      generateButtonDisabled: false,
      inputDisabled: false,
      isGenerating: false,
      modelJudgeAnswers: {},
      isJudging: false
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
    }
  },
  watch: {
    currentQuestionIndex(newIndex) {
      // 保存当前题目索引，用于调试
      console.log('currentQuestionIndex changed to:', newIndex)
      console.log('Current question:', this.currentQuestion)
      console.log('User inputs:', this.userInputs)
      console.log('Model judge answers:', this.modelJudgeAnswers)
      
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
    }
  },
  methods: {
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
    generateAnswers() {
      console.log('generateAnswers called, userInput:', this.userInput)
      console.log('currentQuestion:', this.currentQuestion)
      
      // 检查用户是否输入内容
      if (!this.userInput.trim()) {
        alert('请输入原始问题');
        return;
      }
      
      // 确保当前题目存在
      if (this.currentQuestion) {
        // 保存当前用户输入到userInputs对象
        const inputValue = this.userInput
        console.log('User input saved before generating answers:', this.userInputs)
        this.$set(this.userInputs, this.currentQuestion.id, inputValue)
        // 传递用户输入变化给父组件
        this.$emit('user-input-change', this.currentQuestion.id, inputValue)
      }
      
      // 显示加载状态
      this.isGenerating = true
      this.generateButtonDisabled = true
      this.inputDisabled = true
      
      // 模拟生成过程（实际项目中这里会调用API）
      setTimeout(() => {
        // 模拟生成回答
        if (this.currentQuestion) {
          // 生成模拟回答A和B
          const mockAnswerA = `这是针对问题"${this.userInput}"的回答A，使用了Prompt A的指令。`
          const mockAnswerB = `这是针对问题"${this.userInput}"的回答B，使用了Prompt B的指令。`
          
          // 保存生成的回答到当前问题对象
          this.currentQuestion.answerA = mockAnswerA
          this.currentQuestion.answerB = mockAnswerB
          
          console.log('Generated answers saved to currentQuestion:', this.currentQuestion)
        }
        
        // 显示答案
        this.showAnswers = true
        this.isGenerating = false
      }, 1500)
    },
    generateJudgeAnswer() {
      if (!this.currentQuestion) return
      
      // 显示加载状态
      this.isJudging = true
      
      // 模拟大模型分析过程（实际项目中这里会调用API）
      setTimeout(() => {
        // 生成裁判结果
        const judgeResult = {
          recommended: Math.random() > 0.5 ? 'A' : 'B',
          reason: '基于以下因素：1. 回答的完整性和准确性；2. 语言表达的清晰度和专业性；3. 对用户需求的理解程度；4. 解决方案的可行性。经过综合评估，推荐选择 ' + (Math.random() > 0.5 ? 'A' : 'B') + '。'
        }
        
        // 保存裁判结果
        this.$set(this.modelJudgeAnswers, this.currentQuestion.id, judgeResult)
        console.log('Model judge answer generated:', judgeResult)
        
        // 结束加载状态
        this.isJudging = false
      }, 2000)
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

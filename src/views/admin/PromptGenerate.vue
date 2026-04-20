<template>
  <section id="admin-generate" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title">Prompt一键生成</h1>
        <p class="section-subtitle">找不到思路？别慌，让我来帮助你生成提示词！</p>
      </div>
    </div>
    <div class="generate-container">
      <div class="card pad generate-card">
        <div class="field-grid">
          <div>
            <label for="questionInput">你的任务</label>
            <textarea 
              id="questionInput"
              v-model="question" 
              placeholder="请输入您的任务..."
              rows="3"
            ></textarea>
          </div>
          <div class="btn-row" style="justify-content: center;">
            <button 
              class="btn generate-btn" 
              @click="generatePrompt" 
              :disabled="isGenerating"
            >
              <span class="btn-icon">✨</span>
              {{ isGenerating ? '生成中...' : '生成' }}
            </button>
          </div>
        </div>
      </div>
      <div v-if="isGenerating" class="card pad result-card">
        <div class="loading-state">
          <div class="loading-spinner"></div>
          <p>正在生成回答，请稍候...</p>
        </div>
      </div>
      <div v-else-if="result" class="card pad result-card">
        <div class="eyebrow">生成结果</div>
        <div class="result-content">{{ result }}</div>
      </div>
    </div>
  </section>
</template>

<script>
import { postJSON } from '../../api'

export default {
  name: 'PromptGenerate',
  data() {
    return {
      question: '',
      isGenerating: false,
      result: ''
    }
  },
  methods: {
    async generatePrompt() {
      if (!this.question.trim()) {
        alert('请输入问题')
        return
      }

      this.isGenerating = true
      this.result = ''

      try {
        const data = await postJSON('/ai/prompt_generate', {
          requirement: this.question
        })
        this.result = data.prompt_text || ''
      } catch (error) {
        alert(error.message || '生成失败')
      } finally {
        this.isGenerating = false
      }
    }
  }
}
</script>

<style scoped>
.generate-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  max-width: 900px;
  margin: 0 auto;
}

.generate-card {
  width: 100%;
  max-width: 750px;
}

.result-card {
  width: 100%;
  max-width: 750px;
}

.generate-btn {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  color: white;
  padding: 10px 24px;
  border-radius: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.generate-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-icon {
  font-size: 16px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result-content {
  margin-top: 12px;
  padding: 16px;
  background-color: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>

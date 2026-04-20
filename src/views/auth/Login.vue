<template>
  <div id="loginPage" class="page login-page">
    <div class="auth-shell">
      <div class="auth-hero">
        <div>
          <div class="brand">
            <div class="brand-mark">AB</div>
            <div>
              <h2>Prompt 盲测系统</h2>
              <p>我要验牌 · 本地可运行版本 · JSON 存储</p>
            </div>
          </div>
          <h1>像最终系统一样操作，
            直接预览真实页面节奏</h1>
          <p>当前页面已经接入本地后端，可完成登录后的任务浏览、Prompt 盲测、结果保存、任务发布、提前退出、统计归因和 Excel 导入等核心流程。</p>
          <div class="hero-grid">
            <div class="hero-card">
              <div class="eyebrow">用户端</div>
              <div class="middle">任务列表 → 开始测试 → 选择记录 → 查看统计</div>
            </div>
            <div class="hero-card">
              <div class="eyebrow">管理端</div>
              <div class="middle">创建任务 → 导入题目 → 发布 → 看统计</div>
            </div>
          </div>
          <div class="hero-strip">
            <div class="mini-flow">
              <div style="font-weight:800;">用户操作路径</div>
              <div class="steps">
                <div class="step">
                  <div class="step-num">1</div>
                  <div style="font-weight:700;">登录系统</div>
                  <div style="font-size:13px;color:var(--muted);margin-top:6px;">内部账号进入</div>
                </div>
                <div class="step">
                  <div class="step-num">2</div>
                  <div style="font-weight:700;">选择任务</div>
                  <div style="font-size:13px;color:var(--muted);margin-top:6px;">查看任务说明</div>
                </div>
                <div class="step">
                  <div class="step-num">3</div>
                  <div style="font-weight:700;">开始盲测</div>
                  <div style="font-size:13px;color:var(--muted);margin-top:6px;">每题实时保存</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div>
          <div class="notice">建议你先分别体验“测试用户”和“管理员”两个角色。测试用户可以直接走完整答题流程；管理员可以体验新建任务、添加题目、Excel 导入、发布任务和查看统计。</div>
          <pre id="testOutput" class="test-panel"></pre>
        </div>
      </div>
      <div class="auth-panel">
        <div class="auth-card">
          <div class="tabs" id="roleTabs">
            <button class="tab" :class="{ active: authRole === 'tester' }" @click="authRole = 'tester'">测试用户</button>
            <button class="tab" :class="{ active: authRole === 'admin' }" @click="authRole = 'admin'">管理员</button>
          </div>
          <div class="card pad-lg">
            <div class="section-title" id="authTitle">{{ authRole === 'tester' ? '测试用户登录' : '管理员登录' }}</div>
            <div class="section-subtitle" id="authSubtitle">{{ authRole === 'tester' ? '进入任务列表，查看已发布任务并开始盲测。' : '进入管理后台，创建任务、配置题目并查看统计。' }}</div>
            <div class="field-grid">
              <div>
                <label>用户名</label>
                <input v-model="loginForm.username" id="loginUsername" />
              </div>
              <div>
                <label>密码</label>
                <input v-model="loginForm.password" type="password" id="loginPassword" value="123456" />
              </div>
            </div>
            <div class="btn-row" style="margin-top:18px;">
              <button class="btn primary block" id="loginBtn" @click="login">进入系统</button>
            </div>
            <div class="auth-tip" id="authTip">{{ authRole === 'tester' ? '建议账号：tester01 / 123456。进入后可直接开始题目盲测，答案选择将按真实 Prompt 映射统计。' : '建议账号：admin01 / 123456。进入后可创建任务、配置题目、发布任务并查看统计。' }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      authRole: 'tester',
      loginForm: {
        username: '',
        password: ''
      }
    }
  },
  mounted() {
    this.loginForm.username = this.authRole === 'tester' ? 'tester01' : 'admin01'
  },
  watch: {
    authRole(newRole) {
      this.loginForm.username = newRole === 'tester' ? 'tester01' : 'admin01'
    }
  },
  methods: {
    login() {
      this.$emit('login', {
        username: this.loginForm.username || (this.authRole === 'tester' ? 'tester01' : 'admin01'),
        role: this.authRole
      })
    }
  }
}
</script>

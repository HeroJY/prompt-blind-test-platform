<template>
  <section id="admin-editor" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title">广场任务配置</h1>
        <p class="section-subtitle">此页模拟最终后台的配置流程：填写任务基本信息、编辑 Prompt、添加题目、批量导入、发布任务。这里不会调用后端，只修改内存中的模拟数据。</p>
      </div>
      <div class="btn-row">
        <button class="btn secondary" @click="$emit('back-to-task-management')">返回广场任务列表</button>
      </div>
    </div>

    <div v-if="!selectedTask" id="editorEmpty" class="empty">请先在任务管理页选择一个任务，或点击“创建模拟任务”。</div>

    <div v-else id="editorContent">
      <!-- 任务状态与校验模块 -->
      <div class="card pad">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div style="font-weight: 600;">任务状态与校验</div>
          <div class="btn-row" style="gap: 8px;">
            <button class="btn secondary" id="saveDraftBtn" @click="$emit('save-draft')" v-if="selectedTask && selectedTask.status !== 'published'">保存草稿</button>
            <button class="btn danger" id="deleteTaskBtn" @click="$emit('delete-task')" v-if="selectedTask">删除任务</button>
            <button class="btn success" id="publishTaskBtn" @click="$emit('publish-task')" v-if="selectedTask">{{ selectedTask.status === 'published' ? '重新发布' : '发布任务' }}</button>
          </div>
        </div>
        <div class="grid-2" style="gap: 20px;">
          <div style="padding-right: 20px; border-right: 1px solid #e5e7eb;">
            <div class="key-value" id="editorStatusBox">
              <div class="key-line">
                <div class="key">任务状态</div>
                <div>{{ selectedTask.status === 'published' ? '已发布' : '草稿' }}</div>
              </div>
              <div class="key-line">
                <div class="key">题目数量</div>
                <div>{{ selectedTask.items.length }}</div>
              </div>
              <div class="key-line">
                <div class="key">创建时间</div>
                <div>{{ selectedTask.createdAt || '模拟数据' }}</div>
              </div>
            </div>
          </div>
          <div style="padding-left: 20px;">
            <div style="margin-bottom: 12px; font-size: 14px; line-height: 1.8; color: var(--muted); font-weight: 700;">发布前校验</div>
            <div :class="['notice', { 'error': isError }]" id="publishCheckText">{{ publishCheckText }}</div>
          </div>
        </div>
      </div>

      <!-- 任务基本信息模块独占一行 -->
      <div class="card pad" style="margin-top: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div style="font-weight: 600;">任务基本信息</div>
        </div>
        <div class="field-grid">
          <div>
            <label>任务名称</label>
            <input v-model="editorForm.name" id="editorName" />
          </div>
          <div>
            <label>任务说明</label>
            <textarea v-model="editorForm.description" id="editorDescription"></textarea>
          </div>
          <div class="grid-2">
            <div>
              <label>Prompt A</label>
              <textarea v-model="editorForm.promptA" id="editorPromptA"></textarea>
            </div>
            <div>
              <label>Prompt B</label>
              <textarea v-model="editorForm.promptB" id="editorPromptB"></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- 任务测试案例模块 -->
      <div class="card pad" style="margin-top: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div style="font-weight: 600;">任务测试案例</div>
        </div>
        
        <!-- 新增题目和批量导入模拟 -->
        <div class="panel-grid">
          <div class="card pad">
            <div class="eyebrow">新增题目</div>
            <div class="field-grid">
              <div class="grid-2">
                <div>
                  <label>题目标识码</label>
                  <input v-model="newItemForm.code" id="newItemCode" placeholder="例如 Q101" />
                </div>
                <div>
                  <label>排序号</label>
                  <input v-model.number="newItemForm.sortOrder" type="number" id="newItemOrder" value="99" />
                </div>
              </div>
              <div>
                <label>原始问题文本</label>
                <textarea v-model="newItemForm.sourceText" id="newItemSourceText" placeholder="输入原始问题文字"></textarea>
              </div>
            </div>
            <div class="btn-row" style="margin-top:18px;">
              <button class="btn primary" id="addItemBtn" @click="addItem">新增本题</button>
              <button class="btn secondary" id="fillSampleItemBtn" @click="fillSampleItem">填充示例</button>
            </div>
          </div>

          <div class="card pad">
            <div class="eyebrow">批量导入模拟</div>
            <div class="upload-box">
              <div style="font-size:20px;font-weight:800;">ZIP 导入包</div>
              <div style="margin-top:8px;color:var(--muted);font-size:14px;line-height:1.8;">模拟 manifest.csv + images/ 目录结构。点击按钮后会一次性向当前任务加入几条演示数据。</div>
              <div class="btn-row" style="justify-content:center;margin-top:18px;">
                <button class="btn primary" id="mockImportBtn" @click="$emit('mock-import')">模拟批量导入</button>
              </div>
              <div class="file-chip-row">
                <span class="file-chip">manifest.csv</span>
                <span class="file-chip">images/q301_1.jpg</span>
                <span class="file-chip">images/q301_2.jpg</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 题目列表 -->
        <div style="margin-top:18px;">
          <div class="topbar" style="margin-bottom:12px;">
            <div>
              <div class="eyebrow">题目列表</div>
              <div style="color:var(--muted);font-size:14px;line-height:1.8;">
                发布后不可编辑，所以这里用于发布前校对题目内容。当前原型只演示新增和查看，不做逐条编辑。</div>
            </div>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>题号</th>
                  <th>原始问题摘要</th>
                  <th>排序</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody id="itemTableBody">
                <tr v-for="item in selectedTask.items" :key="item.id">
                  <td>{{ item.code }}</td>
                  <td>{{ item.sourceText || item.images.join(', ') }}</td>
                  <td>{{ item.sortOrder }}</td>
                  <td>已添加</td>
                  <td><button class="btn danger small" @click="$emit('delete-item', item.id)">删除</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'TaskEditor',
  props: {
    selectedTask: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      editorForm: {
        name: '',
        description: '',
        promptA: '',
        promptB: ''
      },
      newItemForm: {
        code: '',
        sortOrder: 99,
        sourceText: ''
      }
    }
  },
  watch: {
    selectedTask: {
      handler(newTask) {
        if (newTask) {
          this.editorForm = {
            name: newTask.name,
            description: newTask.description,
            promptA: newTask.promptA,
            promptB: newTask.promptB
          }
        }
      },
      immediate: true
    },
    editorForm: {
      handler(newForm) {
        if (this.selectedTask) {
          this.selectedTask.name = newForm.name
          this.selectedTask.description = newForm.description
          this.selectedTask.promptA = newForm.promptA
          this.selectedTask.promptB = newForm.promptB
        }
      },
      deep: true
    }
  },
  computed: {
    publishCheckText() {
      if (!this.selectedTask) return '当前未选择任务。'
      if (!this.selectedTask.name) return '请填写任务名称。'
      if (!this.selectedTask.promptA) return '请填写 Prompt A。'
      if (!this.selectedTask.promptB) return '请填写 Prompt B。'
      return '校验通过，可以发布。'
    },
    isError() {
      return this.publishCheckText !== '校验通过，可以发布。'
    }
  },
  methods: {
    fillSampleItem() {
      this.newItemForm = {
        code: `Q${Date.now().toString().slice(-4)}`,
        sortOrder: this.selectedTask ? this.selectedTask.items.length + 1 : 1,
        sourceText: '用户询问如何使用产品的某个功能，请生成客服回复。'
      }
    },
    addItem() {
      // 表单验证
      if (!this.newItemForm.code) {
        alert('请填写题目标识码');
        return;
      }
      if (!this.newItemForm.sourceText) {
        alert('请填写原始问题文本');
        return;
      }
      // 验证通过，添加题目
      this.$emit('add-item', this.newItemForm);
      // 清空表单
      this.newItemForm = {
        code: '',
        sortOrder: this.selectedTask ? this.selectedTask.items.length + 1 : 1,
        sourceText: ''
      };
    }
  }
}
</script>

<style scoped>
.error {
  color: red;
}

/* 确保新增题目和批量导入模拟模块的布局与导入任务页面一致 */
.panel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .panel-grid {
    grid-template-columns: 1fr;
  }
}
</style>

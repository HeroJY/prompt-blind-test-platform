<template>
  <section id="admin-editor" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title">广场任务配置</h1>
        <p class="section-subtitle">此页模拟最终后台的配置流程：填写任务基本信息、编辑 Prompt、添加题目、批量导入、发布任务。这里不会调用后端，只修改内存中的模拟数据。</p>
      </div>
    </div>

    <div v-if="!selectedTask" id="editorEmpty" class="empty">请先在任务管理页选择一个任务，或点击“创建模拟任务”。</div>

    <div v-else id="editorContent" class="panel-grid">
      <!-- 合并后的任务状态与校验模块 -->
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
            <div style="font-weight: 600; margin-bottom: 12px;">任务状态</div>
            <div class="key-value" id="editorStatusBox">
              <div class="key-line">
                <div class="key">任务状态</div>
                <div>{{ selectedTask.status === 'published' ? '已发布' : '草稿' }}</div>
              </div>
              <div class="key-line">
                <div class="key">题目数量</div>
                <div>{{ editorForm.mode === 'custom' ? (editorForm.testCount || 0) : selectedTask.items.length }}</div>
              </div>
              <div class="key-line">
                <div class="key">创建时间</div>
                <div>{{ selectedTask.createdAt || '模拟数据' }}</div>
              </div>
            </div>
          </div>
          <div style="padding-left: 20px;">
            <div style="font-weight: 600; margin-bottom: 12px;">发布前校验</div>
            <div class="notice" id="publishCheckText">{{ publishCheckText }}</div>
          </div>
        </div>
      </div>

      <!-- 任务基本信息模块独占一行 -->
      <div class="card pad">
        <div class="eyebrow">任务基本信息</div>
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
          <div>
            <label>模式选择</label>
            <select v-model="editorForm.mode" id="editorMode" style="padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 8px; width: 100%; font-size: 14px; background-color: #ffffff; transition: all 0.2s ease-in-out;">
              <option value="single">单题模式</option>
              <option value="custom">自定义模式</option>
            </select>
          </div>
          <div v-if="editorForm.mode === 'custom'">
            <label>单轮测试数量</label>
            <input v-model.number="editorForm.testCount" type="number" id="editorTestCount" min="1" value="5" />
          </div>
        </div>
      </div>

      <!-- 单题模式相关模块 -->
      <div v-if="editorForm.mode === 'single'" class="panel-grid">
        <div class="card pad">
          <div class="eyebrow">新增单题</div>
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

      <div v-if="editorForm.mode === 'single'" class="card pad">
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
        mode: 'single',
        testCount: 5,
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
            mode: newTask.mode || 'single',
            testCount: newTask.testCount || 5,
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
          this.selectedTask.mode = newForm.mode
          this.selectedTask.testCount = newForm.testCount
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
      if (!this.selectedTask.promptA || !this.selectedTask.promptB) return '请填写 Prompt A 和 Prompt B。'
      if (this.editorForm.mode === 'single' && this.selectedTask.items.length === 0) return '请至少添加一道题目。'
      if (this.editorForm.mode === 'custom' && (!this.editorForm.testCount || this.editorForm.testCount < 1)) return '请填写有效的单轮测试数量。'
      return '校验通过，可以发布。'
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

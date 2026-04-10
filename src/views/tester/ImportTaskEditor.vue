<template>
  <section id="import-task-editor" class="view">
    <div class="topbar">
      <div>
        <h1 class="section-title">导入任务</h1>
        <p class="section-subtitle">填写任务基本信息、编辑 Prompt、添加题目、批量导入。</p>
      </div>
      <div class="btn-row">
        <button class="btn secondary" @click="$emit('back')">返回任务列表</button>
      </div>
    </div>

    <div v-if="!selectedTask" id="editorEmpty" class="empty">请先在任务管理页选择一个任务，或点击“创建模拟任务”。</div>

    <div v-else id="editorContent">
      <!-- 任务基本信息模块 -->
      <div class="card pad">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div class="eyebrow">任务基本信息</div>
          <div class="btn-row" style="gap: 8px;">
            <button class="btn secondary" @click="$emit('back')">取消</button>
            <button class="btn primary" @click="$emit('save')">保存</button>
          </div>
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
        </div>
      </div>

      <!-- 提示词导入模块 -->
      <div class="card pad" style="margin-top: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div class="eyebrow">提示词导入</div>
          <div class="btn-row">
            <button class="btn primary" @click="triggerFileUpload">上传提示词</button>
            <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" />
          </div>
        </div>
        <div class="field-grid">
          <div class="grid-2">
            <div>
              <label>Prompt A <span style="color: #94a3b8; font-size: 12px; font-weight: normal;">（只读，请上传文件解析）</span></label>
              <textarea v-model="editorForm.promptA" id="editorPromptA" disabled class="disabled-textarea"></textarea>
            </div>
            <div>
              <label>Prompt B <span style="color: #94a3b8; font-size: 12px; font-weight: normal;">（只读，请上传文件解析）</span></label>
              <textarea v-model="editorForm.promptB" id="editorPromptB" disabled class="disabled-textarea"></textarea>
            </div>
          </div>
        </div>
        <div style="margin-top: 12px; color: #000; font-size: 14px; line-height: 1.8; background-color: #fff3cd; padding: 8px 12px; border-radius: 4px; border-left: 3px solid #ffc107; font-weight: 500;">
          提示：在开始盲选测试之后，两份提示词会随机出现，不一定prompt a对应的答案出现在左侧
        </div>
      </div>

      <!-- 测试数据导入模块 -->
      <div class="card pad" style="margin-top: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div class="eyebrow">测试数据导入</div>
          <div class="btn-row">
            <button class="btn primary" @click="triggerDataUpload">上传数据</button>
            <input type="file" ref="dataInput" style="display: none" @change="handleDataUpload" />
          </div>
        </div>
        <div class="field-grid">
          <div>
            <label>测试数据</label>
            <textarea v-model="testData" id="testData" placeholder="输入测试数据，或点击上方按钮上传数据文件"></textarea>
          </div>
        </div>
      </div>

      <!-- 任务测试案例模块 -->
      <div class="card pad" style="margin-top: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div class="eyebrow">任务测试案例</div>
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
              <button class="btn primary" id="addItemBtn" @click="addItem">添加题目</button>
              <button class="btn secondary" id="fillSampleItemBtn" @click="fillSampleItem">填充示例</button>
            </div>
          </div>

          <div class="card pad">
            <div class="eyebrow">批量导入模拟</div>
            <div class="upload-box">
              <div style="font-size:20px;font-weight:800;">ZIP 导入包</div>
              <div style="margin-top:8px;color:var(--muted);font-size:14px;line-height:1.8;">模拟 manifest.csv + images/ 目录结构。点击按钮后会一次性向当前任务加入几条演示数据。</div>
              <div class="btn-row" style="justify-content:center;margin-top:18px;">
                <button class="btn primary" id="mockImportBtn" @click="$emit('mock-import', mockImportText)">批量导入</button>
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
                <tr v-for="(item, index) in selectedTask.items" :key="index">
                  <td>{{ item.code }}</td>
                  <td>{{ item.sourceText }}</td>
                  <td>{{ item.sortOrder || 99 }}</td>
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
  name: 'ImportTaskEditor',
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
      },
      mockImportText: '',
      testData: ''
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
          // 同步测试数据
          this.testData = newTask.testData || ''
          // 确保 items 数组存在
          if (!newTask.items) {
            this.$set(newTask, 'items', [])
          }
        }
      },
      immediate: true,
      deep: true
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
    },
    testData: {
      handler(newData) {
        if (this.selectedTask) {
          this.selectedTask.testData = newData
        }
      }
    }
  },
  methods: {
    fillSampleItem() {
      this.newItemForm = {
        code: `Q${Date.now().toString().slice(-4)}`,
        sortOrder: this.selectedTask ? this.selectedTask.items.length + 1 : 1,
        sourceText: '请对以下内容进行分析和回答。'
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
    },
    triggerFileUpload() {
      this.$refs.fileInput.click();
    },
    handleFileUpload() {
      // 模拟文件上传功能，不做实际解析
      alert('提示词文件已上传并自动解析');
      // 填充示例内容到 prompt a 和 prompt b
      this.editorForm.promptA = '这是 Prompt A 的示例内容，用于测试盲选功能。请根据用户的问题生成合适的回答。';
      this.editorForm.promptB = '这是 Prompt B 的示例内容，用于测试盲选功能。请根据用户的问题生成详细、准确的回答。';
      // 清空文件输入
      this.$refs.fileInput.value = '';
    },
    triggerDataUpload() {
      this.$refs.dataInput.click();
    },
    handleDataUpload() {
      // 模拟文件上传功能，不做实际解析
      alert('测试数据文件已上传并自动解析');
      // 填充示例内容到测试数据
      this.testData = '这是测试数据的示例内容，包含了多个测试用例。上传数据后，内容会显示在这里。';
      // 清空文件输入
      this.$refs.dataInput.value = '';
    }
  }
}
</script>

<style scoped>
/* 确保panel-grid内部的卡片间距一致 */
.panel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
}

/* 不可编辑文本框样式 */
.disabled-textarea {
  background-color: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #64748b;
  cursor: not-allowed;
}

.disabled-textarea::placeholder {
  color: #94a3b8;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .panel-grid {
    grid-template-columns: 1fr;
  }
}
</style>
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

    <div v-if="!selectedTask" id="editorEmpty" class="empty">请先选择一个任务，或先创建一个新任务。</div>

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
          <div class="eyebrow">提示词配置</div>
        </div>
        <div class="field-grid">
          <div class="grid-2">
            <div>
              <label>Prompt A <span style="color: #94a3b8; font-size: 12px; font-weight: normal;">（可直接输入文本）</span></label>
              <textarea v-model="editorForm.promptA" id="editorPromptA" placeholder="可直接输入 Prompt A 文本"></textarea>
              <div class="btn-row" style="margin-top: 12px;">
                <button class="btn secondary" @click="triggerPromptImageUpload('A')">上传图片</button>
                <input type="file" ref="promptAImageInput" accept="image/*" multiple style="display: none" @change="handlePromptImageUpload('A', $event)" />
              </div>
              <div v-if="editorForm.promptAImages.length" class="prompt-image-grid">
                <div v-for="(image, index) in editorForm.promptAImages" :key="`promptA-${index}`" class="prompt-image-card">
                  <img :src="imageSrc(image)" :alt="image.name || `Prompt A ${index + 1}`" class="prompt-image-preview" />
                  <div class="prompt-image-name">{{ image.name || `图片 ${index + 1}` }}</div>
                  <button class="btn danger small" @click="removePromptImage('A', index)">删除</button>
                </div>
              </div>
            </div>
            <div>
              <label>Prompt B <span style="color: #94a3b8; font-size: 12px; font-weight: normal;">（可直接输入文本）</span></label>
              <textarea v-model="editorForm.promptB" id="editorPromptB" placeholder="可直接输入 Prompt B 文本"></textarea>
              <div class="btn-row" style="margin-top: 12px;">
                <button class="btn secondary" @click="triggerPromptImageUpload('B')">上传图片</button>
                <input type="file" ref="promptBImageInput" accept="image/*" multiple style="display: none" @change="handlePromptImageUpload('B', $event)" />
              </div>
              <div v-if="editorForm.promptBImages.length" class="prompt-image-grid">
                <div v-for="(image, index) in editorForm.promptBImages" :key="`promptB-${index}`" class="prompt-image-card">
                  <img :src="imageSrc(image)" :alt="image.name || `Prompt B ${index + 1}`" class="prompt-image-preview" />
                  <div class="prompt-image-name">{{ image.name || `图片 ${index + 1}` }}</div>
                  <button class="btn danger small" @click="removePromptImage('B', index)">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div style="margin-top: 12px; color: #000; font-size: 14px; line-height: 1.8; background-color: #fff3cd; padding: 8px 12px; border-radius: 4px; border-left: 3px solid #ffc107; font-weight: 500;">
          提示：Prompt 可以直接输入文字，也可以上传图片做存档展示。批量导入题目仍只支持 `.xlsx`。
        </div>
      </div>

      <!-- 测试数据导入模块 -->
      <div class="card pad" style="margin-top: 18px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div class="eyebrow">测试数据导入</div>
          <div class="btn-row">
            <button class="btn primary" @click="triggerDataUpload">上传数据</button>
            <input type="file" ref="dataInput" accept=".xlsx" style="display: none" @change="handleDataUpload" />
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
        
        <!-- 新增题目和批量导入 -->
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
            <div class="eyebrow">批量导入</div>
            <div class="upload-box">
              <div style="font-size:20px;font-weight:800;">Excel 题目导入</div>
              <div style="margin-top:8px;color:var(--muted);font-size:14px;line-height:1.8;">当前仅支持 `.xlsx`。ZIP 功能预留但未开放。</div>
              <div class="btn-row" style="justify-content:center;margin-top:18px;">
                <button class="btn primary" id="itemImportBtn" @click="triggerItemUpload">上传并导入</button>
                <input type="file" ref="itemInput" accept=".xlsx" style="display: none" @change="handleItemUpload" />
              </div>
              <div class="file-chip-row">
                <span class="file-chip">code</span>
                <span class="file-chip">sort_order</span>
                <span class="file-chip">source_text</span>
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
import { postFile, resolveAssetUrl } from '../../api'

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
        promptB: '',
        promptAImages: [],
        promptBImages: []
      },
      newItemForm: {
        code: '',
        sortOrder: 99,
        sourceText: ''
      },
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
            promptB: newTask.promptB,
            promptAImages: newTask.promptAImages || [],
            promptBImages: newTask.promptBImages || []
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
          this.selectedTask.promptAImages = newForm.promptAImages || []
          this.selectedTask.promptBImages = newForm.promptBImages || []
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
    triggerPromptImageUpload(slot) {
      const refName = slot === 'A' ? 'promptAImageInput' : 'promptBImageInput'
      this.$refs[refName].click()
    },
    handlePromptImageUpload(slot, event) {
      const files = event.target.files ? Array.from(event.target.files) : []
      if (!files.length) return
      const targetKey = slot === 'A' ? 'promptAImages' : 'promptBImages'
      const readTasks = files.map(file => new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => {
          resolve({
            name: file.name,
            type: file.type,
            dataUrl: reader.result
          })
        }
        reader.onerror = () => reject(new Error('图片读取失败'))
        reader.readAsDataURL(file)
      }))

      Promise.all(readTasks).then(images => {
        this.editorForm[targetKey] = (this.editorForm[targetKey] || []).concat(images)
      }).catch(error => {
        alert(error.message || '图片上传失败')
      }).finally(() => {
        event.target.value = ''
      })
    },
    removePromptImage(slot, index) {
      const targetKey = slot === 'A' ? 'promptAImages' : 'promptBImages'
      this.editorForm[targetKey].splice(index, 1)
    },
    imageSrc(image) {
      if (!image) return ''
      return resolveAssetUrl(image.dataUrl || image.url || '')
    },
    triggerDataUpload() {
      this.$refs.dataInput.click()
    },
    async handleDataUpload(event) {
      const file = event.target.files && event.target.files[0]
      if (!file) return
      try {
        const data = await postFile('/upload/test_data_excel', file)
        this.testData = data.preview_text || ''
        alert('测试数据文件已上传并解析完成')
      } catch (error) {
        alert(error.message || '测试数据上传失败')
      } finally {
        this.$refs.dataInput.value = ''
      }
    },
    triggerItemUpload() {
      this.$refs.itemInput.click()
    },
    async handleItemUpload(event) {
      const file = event.target.files && event.target.files[0]
      if (!file) return
      try {
        const data = await postFile('/upload/item_excel', file)
        ;(data.items || []).forEach(item => {
          this.$emit('add-item', {
            code: item.code,
            sortOrder: item.sort_order,
            sourceText: item.source_text
          })
        })
        alert('题目 Excel 已导入')
      } catch (error) {
        alert(error.message || '题目导入失败')
      } finally {
        this.$refs.itemInput.value = ''
      }
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

.prompt-image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.prompt-image-card {
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 10px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prompt-image-preview {
  width: 100%;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: #fff;
}

.prompt-image-name {
  font-size: 12px;
  color: var(--muted);
  word-break: break-all;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .panel-grid {
    grid-template-columns: 1fr;
  }
}
</style>

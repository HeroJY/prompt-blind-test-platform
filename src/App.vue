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
          :task-name="currentSession ? testerTasks.find(t => t.id === currentSession.taskId).name : '' "
          :task-mode="currentSession ? currentSession.taskMode : 'custom' "
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
          @mock-import="mockImport"
          @delete-item="deleteItem"
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
          :task-name="currentSession ? adminTasks.find(t => t.id === currentSession.taskId).name : '' "
          :task-mode="currentSession ? currentSession.taskMode : 'custom' "
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
    PromptGenerate
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
      adminManagementTasks: [
        {
          id: 1,
          name: '这是第一个需要发布的任务对比',
          description: '比较两组提示词的效果1。',
          promptA: '这里是假的提示词1。',
          promptB: '请使用假的提示词2，用高情商生成回复：先共情，再给回答。',
          status: 'published',
          mode: 'single',
          questionLimit: 3,
          createdBy: 'admin01',
          items: [
            { id: 101, code: 'Q001', sourceType: 'text', sortOrder: 1, sourceText: '用户投诉：我昨天购买的商品今天就降价了，而且客服回复非常慢。请生成一段安抚用户情绪、解释规则并给出合理补偿建议的话术。', images: [], answerA: '您好，非常抱歉给您带来了不好的购物体验，也理解您看到商品短时间内出现价格变化后会产生落差感。平台活动价格会随时间动态调整，但我们非常重视您的感受。为了表达歉意，建议为您申请一张优惠券或积分补偿；如果您的订单符合价保条件，我也可以继续协助您核实处理。', answerB: '真的非常抱歉让您遇到这样的情况，换作是我也会感到失落。商品价格会因为活动时间不同而产生调整，这边无法直接保证下单后价格始终不变，但我会尽力帮您争取更好的处理方案，并优先为您申请补偿福利。' },
            { id: 102, code: 'Q002', sourceType: 'text', sortOrder: 2, sourceText: '用户反馈：快递已经延迟两天还没到，客服之前答应今天送达但目前没有更新。请生成一段安抚和补偿建议回复。', images: [], answerA: '您好，很抱歉让您久等了，也理解您在已经被承诺送达后却仍未收到包裹时的失望。我们会立即帮您再次催促物流并同步最新节点；如果最终仍超出承诺时效，我们也会为您申请补偿方案，尽量减少这次延迟带来的影响。', answerB: '非常抱歉这次配送没有达到预期，也感谢您耐心反馈。当前我们会先帮您核实物流异常原因，并持续跟进配送结果；同时这边会为您备注异常情况，若超时确认成立，会优先协助申请补偿。' },
            { id: 103, code: 'Q003', sourceType: 'text', sortOrder: 3, sourceText: '用户反馈商品表面存在明显划痕和边角磨损，外观完整性受影响。请生成客服回复。', images: [], answerA: '从图片来看，商品表面存在明显划痕和边角磨损，外观完整性受影响。建议在回复中先确认用户上传的证据清晰有效，再表达歉意，并提供换货、退货或补偿三种可执行方案。', answerB: '结合多张图片信息，问题主要集中在外观瑕疵与局部破损，用户主观感受通常会偏负面。更合适的回复方式是先认可图片证据，再说明售后流程，最后给出优先处理承诺。' },
            { id: 104, code: 'Q004', sourceType: 'text', sortOrder: 4, sourceText: '请针对“订单已经申请退款，但退款到账时间比预期慢，用户比较焦虑”的场景生成客服回复。', images: [], answerA: '您好，理解您现在着急想尽快收到退款的心情，也非常抱歉让您等待。退款在审核通过后通常会按原支付路径返还，具体到账时间会受支付渠道处理进度影响。我们会继续帮您跟进状态，如有异常会第一时间协助处理。', answerB: '非常抱歉退款进度没有达到您的预期，我们完全理解这会让人感到不安。当前退款申请已经在流程中，不同支付方式到账时效会有所差异；这边会继续为您关注进度，并在需要时优先协助您升级处理。' },
            { id: 105, code: 'Q005', sourceType: 'text', sortOrder: 5, sourceText: '用户表示安装服务预约多次改期，希望客服进行解释和安抚。', images: [], answerA: '您好，非常抱歉安装预约多次调整，确实给您添麻烦了。我们会立即帮您重新核实最近可安排时间，并优先为您争取更稳定的上门时段；如果因此影响了您的使用体验，也会为您同步补偿方案。', answerB: '很抱歉让您在安装安排上反复等待，这样的体验确实不好。我们会先尽快确认改期原因，再为您协调新的安装时间，并尽量减少再次变动；后续如果需要，我们也会协助您申请对应补偿。' },
            { id: 106, code: 'Q006', sourceType: 'text', sortOrder: 6, sourceText: '用户收到商品后发现配件缺失，希望客服回复。', images: [], answerA: '您好，给您带来不便真的很抱歉。针对您反馈的配件缺失问题，我们会先帮您核实订单与商品清单，如确认属实，可为您补发缺失配件，或根据情况协助申请相应补偿。', answerB: '非常抱歉让您收到的商品不完整，也理解这会影响正常使用。我们会马上为您核对包装与发货信息，如果确认缺件，会优先为您安排补发或提供其他处理方案。' },
            { id: 107, code: 'Q007', sourceType: 'text', sortOrder: 7, sourceText: '用户质疑客服之前承诺过可以特殊处理，现在却说不能办。请生成客服回复。', images: [], answerA: '您好，非常抱歉前后信息不一致给您造成了困扰。我们会先重新核查之前的沟通记录，尽量给您一个清晰、统一的处理说明；如果确实存在服务表达不准确的情况，我们也会积极协助补救。', answerB: '很抱歉这次沟通让您感到被反复说明，您的不满我们完全理解。我们会尽快核实此前承诺内容，并基于实际规则给出明确答复，同时尽力为您争取更合理的处理方案。' },
            { id: 108, code: 'Q008', sourceType: 'text', sortOrder: 8, sourceText: '用户说包装破损，但商品本身暂时还能使用，希望得到客服回复。', images: [], answerA: '您好，非常抱歉包裹送达时包装出现破损。即便商品暂时还能使用，这样的体验也不应该发生。我们会记录这次异常配送情况，并可根据实际影响帮您申请适当补偿。', answerB: '抱歉让您收到的包裹包装状态不佳，感谢您第一时间反馈。我们会先帮您登记物流异常，并根据包装受损程度及对商品使用的影响，进一步协助申请补偿或售后支持。' },
            { id: 109, code: 'Q009', sourceType: 'text', sortOrder: 9, sourceText: '请处理“用户想取消订单，但已经进入仓库打包流程”的客服话术。', images: [], answerA: '您好，理解您现在希望尽快取消订单的需求。由于订单已进入仓库打包流程，系统暂时可能无法直接拦截，但我们会立即帮您尝试联系仓库核实处理；若无法及时取消，您也可以在签收前后按规则申请退货。', answerB: '很抱歉当前订单状态给您的取消操作带来了不便。由于商品已经进入打包流程，系统拦截成功与否需要以仓库处理结果为准；我们会先帮您尽快提交取消申请，同时同步后续可执行的退货路径。' },
            { id: 110, code: 'Q010', sourceType: 'text', sortOrder: 10, sourceText: '用户称发票一直没有开具成功，影响报销，希望客服解释并安抚。', images: [], answerA: '您好，非常抱歉发票开具进度影响了您的报销安排。我们会立即帮您核查当前开票状态，并尽快推动处理；如果存在信息缺失或系统异常，也会第一时间联系您补充，尽量缩短等待时间。', answerB: '很抱歉发票问题影响到了您的使用和报销节奏，我们理解这会带来实际不便。我们将马上为您确认失败原因，并优先协助推进开票处理，后续也会持续同步结果。' },
            { id: 111, code: 'Q011', sourceType: 'text', sortOrder: 11, sourceText: '用户反馈外箱有压痕和破裂，希望客服回复。', images: [], answerA: '根据图片可见外箱有压痕和破裂，建议在客服回复中先确认照片已收到，再结合物流环节说明处理进度，最后给出退换或补偿路径。', answerB: '从图片看主要问题是运输造成的外包装受损，适合采用“认可证据—表达歉意—提供处理方案”的回复结构，以提升用户接受度。' },
            { id: 112, code: 'Q012', sourceType: 'text', sortOrder: 12, sourceText: '用户抱怨活动规则太复杂，希望客服解释但不要显得推卸责任。', images: [], answerA: '您好，很抱歉活动说明没有让您第一时间看明白，也感谢您指出这个问题。当前活动的参与条件和优惠生效方式会因页面配置有所不同，我们会尽量用更清楚的方式为您说明，并协助核实您当前订单是否满足相关条件。', answerB: '非常抱歉给您带来理解成本，我们也理解规则复杂会影响体验。我们会先把与您当前订单相关的关键条件简化说明给您，并继续协助确认是否有可以补救或优化的空间。' }
          ],
          sessions: [
            { id: 's-old-1', userId: 'tester01', answeredCount: 5, answers: [{ itemId: 101, selectedPrompt: 'prompt_a' }, { itemId: 102, selectedPrompt: 'prompt_b' }, { itemId: 103, selectedPrompt: 'prompt_a' }, { itemId: 104, selectedPrompt: 'prompt_a' }, { itemId: 105, selectedPrompt: 'prompt_b' }] },
            { id: 's-old-2', userId: 'tester02', answeredCount: 4, answers: [{ itemId: 101, selectedPrompt: 'prompt_b' }, { itemId: 102, selectedPrompt: 'prompt_a' }, { itemId: 103, selectedPrompt: 'prompt_a' }, { itemId: 104, selectedPrompt: 'prompt_b' }] },
            { id: 's-old-3', userId: 'tester03', answeredCount: 6, answers: [{ itemId: 101, selectedPrompt: 'prompt_a' }, { itemId: 102, selectedPrompt: 'prompt_a' }, { itemId: 103, selectedPrompt: 'prompt_b' }, { itemId: 104, selectedPrompt: 'prompt_a' }, { itemId: 105, selectedPrompt: 'prompt_a' }, { itemId: 106, selectedPrompt: 'prompt_b' }] }
          ]
        },
        {
          id: 2,
          name: '尽调报告生成对比',
          description: '比较两组提示词在尽调报告生成方面的差异。',
          promptA: '请对输入的客户信息进行综合风险分析，再按用户提问生成结构化回答。',
          promptB: '请把输入的客户信息整合成要点，用更口语化的表达回答用户，并尽可能减少遗漏。',
          status: 'published',
          mode: 'custom',
          questionLimit: 2,
          createdBy: 'admin01',
          items: [
            { id: 201, code: 'Q201', sourceType: 'text', sortOrder: 1, sourceText: '分析仪表盘数据，主要波动集中在转化率与客单价，需要先确认渠道结构变化。', images: [], answerA: '从多图可以看出指标主要波动集中在转化率与客单价，需要先确认渠道结构变化。', answerB: '这些图片最关键的信息是转化率下滑和销售额波动，回答时需要把原因和建议一起给出。' },
            { id: 202, code: 'Q202', sourceType: 'text', sortOrder: 2, sourceText: '分析设计图，总结整体风格问题，并分别点评排版、配色和重点信息层级。', images: [], answerA: '适合先做视觉问题归纳，再提出三条可执行修改建议。', answerB: '更合适的方式是先总结整体风格问题，再分别点评排版、配色和重点信息层级。' }
          ],
          sessions: []
        }
      ],
      adminTasks: [
        {
          id: 1,
          name: '客服回复质量对比',
          description: '比较两组提示词在客服安抚回复中的可读性、同理心表达、规则解释与补偿建议完整度。',
          promptA: '你是一名资深客服专家，请输出安抚式回复，先表达理解，再说明平台规则，最后给出可执行的补偿建议，整体语气温和、稳定、清晰。',
          promptB: '请作为高情商客服生成回复：先共情，再说明价格变动或流程机制，最后给出一到两种明确处理路径，并强调继续协助。',
          status: 'unpublished',
          mode: 'custom',
          questionLimit: 3,
          createdBy: 'admin01',
          items: [
            { id: 101, code: 'Q001', sourceType: 'text', sortOrder: 1, sourceText: '用户投诉：我昨天购买的商品今天就降价了，而且客服回复非常慢。请生成一段安抚用户情绪、解释规则并给出合理补偿建议的话术。', images: [], answerA: '您好，非常抱歉给您带来了不好的购物体验，也理解您看到商品短时间内出现价格变化后会产生落差感。平台活动价格会随时间动态调整，但我们非常重视您的感受。为了表达歉意，建议为您申请一张优惠券或积分补偿；如果您的订单符合价保条件，我也可以继续协助您核实处理。', answerB: '真的非常抱歉让您遇到这样的情况，换作是我也会感到失落。商品价格会因为活动时间不同而产生调整，这边无法直接保证下单后价格始终不变，但我会尽力帮您争取更好的处理方案，并优先为您申请补偿福利。' },
            { id: 102, code: 'Q002', sourceType: 'text', sortOrder: 2, sourceText: '用户反馈：快递已经延迟两天还没到，客服之前答应今天送达但目前没有更新。请生成一段安抚和补偿建议回复。', images: [], answerA: '您好，很抱歉让您久等了，也理解您在已经被承诺送达后却仍未收到包裹时的失望。我们会立即帮您再次催促物流并同步最新节点；如果最终仍超出承诺时效，我们也会为您申请补偿方案，尽量减少这次延迟带来的影响。', answerB: '非常抱歉这次配送没有达到预期，也感谢您耐心反馈。当前我们会先帮您核实物流异常原因，并持续跟进配送结果；同时这边会为您备注异常情况，若超时确认成立，会优先协助申请补偿。' },
            { id: 103, code: 'Q003', sourceType: 'images', sortOrder: 3, sourceText: '', images: ['sku_damage_1.jpg', 'sku_damage_2.jpg', 'sku_damage_3.jpg'], answerA: '从图片来看，商品表面存在明显划痕和边角磨损，外观完整性受影响。建议在回复中先确认用户上传的证据清晰有效，再表达歉意，并提供换货、退货或补偿三种可执行方案。', answerB: '结合多张图片信息，问题主要集中在外观瑕疵与局部破损，用户主观感受通常会偏负面。更合适的回复方式是先认可图片证据，再说明售后流程，最后给出优先处理承诺。' },
            { id: 104, code: 'Q004', sourceType: 'text', sortOrder: 4, sourceText: '请针对“订单已经申请退款，但退款到账时间比预期慢，用户比较焦虑”的场景生成客服回复。', images: [], answerA: '您好，理解您现在着急想尽快收到退款的心情，也非常抱歉让您等待。退款在审核通过后通常会按原支付路径返还，具体到账时间会受支付渠道处理进度影响。我们会继续帮您跟进状态，如有异常会第一时间协助处理。', answerB: '非常抱歉退款进度没有达到您的预期，我们完全理解这会让人感到不安。当前退款申请已经在流程中，不同支付方式到账时效会有所差异；这边会继续为您关注进度，并在需要时优先协助您升级处理。' },
            { id: 105, code: 'Q005', sourceType: 'text', sortOrder: 5, sourceText: '用户表示安装服务预约多次改期，希望客服进行解释和安抚。', images: [], answerA: '您好，非常抱歉安装预约多次调整，确实给您添麻烦了。我们会立即帮您重新核实最近可安排时间，并优先为您争取更稳定的上门时段；如果因此影响了您的使用体验，也会为您同步补偿方案。', answerB: '很抱歉让您在安装安排上反复等待，这样的体验确实不好。我们会先尽快确认改期原因，再为您协调新的安装时间，并尽量减少再次变动；后续如果需要，我们也会协助您申请对应补偿。' },
            { id: 106, code: 'Q006', sourceType: 'text', sortOrder: 6, sourceText: '用户收到商品后发现配件缺失，希望客服回复。', images: [], answerA: '您好，给您带来不便真的很抱歉。针对您反馈的配件缺失问题，我们会先帮您核实订单与商品清单，如确认属实，可为您补发缺失配件，或根据情况协助申请相应补偿。', answerB: '非常抱歉让您收到的商品不完整，也理解这会影响正常使用。我们会马上为您核对包装与发货信息，如果确认缺件，会优先为您安排补发或提供其他处理方案。' },
            { id: 107, code: 'Q007', sourceType: 'text', sortOrder: 7, sourceText: '用户质疑客服之前承诺过可以特殊处理，现在却说不能办。请生成客服回复。', images: [], answerA: '您好，非常抱歉前后信息不一致给您造成了困扰。我们会先重新核查之前的沟通记录，尽量给您一个清晰、统一的处理说明；如果确实存在服务表达不准确的情况，我们也会积极协助补救。', answerB: '很抱歉这次沟通让您感到被反复说明，您的不满我们完全理解。我们会尽快核实此前承诺内容，并基于实际规则给出明确答复，同时尽力为您争取更合理的处理方案。' },
            { id: 108, code: 'Q008', sourceType: 'text', sortOrder: 8, sourceText: '用户说包装破损，但商品本身暂时还能使用，希望得到客服回复。', images: [], answerA: '您好，非常抱歉包裹送达时包装出现破损。即便商品暂时还能使用，这样的体验也不应该发生。我们会记录这次异常配送情况，并可根据实际影响帮您申请适当补偿。', answerB: '抱歉让您收到的包裹包装状态不佳，感谢您第一时间反馈。我们会先帮您登记物流异常，并根据包装受损程度及对商品使用的影响，进一步协助申请补偿或售后支持。' },
            { id: 109, code: 'Q009', sourceType: 'text', sortOrder: 9, sourceText: '请处理“用户想取消订单，但已经进入仓库打包流程”的客服话术。', images: [], answerA: '您好，理解您现在希望尽快取消订单的需求。由于订单已进入仓库打包流程，系统暂时可能无法直接拦截，但我们会立即帮您尝试联系仓库核实处理；若无法及时取消，您也可以在签收前后按规则申请退货。', answerB: '很抱歉当前订单状态给您的取消操作带来了不便。由于商品已经进入打包流程，系统拦截成功与否需要以仓库处理结果为准；我们会先帮您尽快提交取消申请，同时同步后续可执行的退货路径。' },
            { id: 110, code: 'Q010', sourceType: 'text', sortOrder: 10, sourceText: '用户称发票一直没有开具成功，影响报销，希望客服解释并安抚。', images: [], answerA: '您好，非常抱歉发票开具进度影响了您的报销安排。我们会立即帮您核查当前开票状态，并尽快推动处理；如果存在信息缺失或系统异常，也会第一时间联系您补充，尽量缩短等待时间。', answerB: '很抱歉发票问题影响到了您的使用和报销节奏，我们理解这会带来实际不便。我们将马上为您确认失败原因，并优先协助推进开票处理，后续也会持续同步结果。' },
            { id: 111, code: 'Q011', sourceType: 'images', sortOrder: 11, sourceText: '', images: ['return_box_1.jpg', 'return_box_2.jpg'], answerA: '根据图片可见外箱有压痕和破裂，建议在客服回复中先确认照片已收到，再结合物流环节说明处理进度，最后给出退换或补偿路径。', answerB: '从图片看主要问题是运输造成的外包装受损，适合采用“认可证据—表达歉意—提供处理方案”的回复结构，以提升用户接受度。' },
            { id: 112, code: 'Q012', sourceType: 'text', sortOrder: 12, sourceText: '用户抱怨活动规则太复杂，希望客服解释但不要显得推卸责任。', images: [], answerA: '您好，很抱歉活动说明没有让您第一时间看明白，也感谢您指出这个问题。当前活动的参与条件和优惠生效方式会因页面配置有所不同，我们会尽量用更清楚的方式为您说明，并协助核实您当前订单是否满足相关条件。', answerB: '非常抱歉给您带来理解成本，我们也理解规则复杂会影响体验。我们会先把与您当前订单相关的关键条件简化说明给您，并继续协助确认是否有可以补救或优化的空间。' }
          ],
          sessions: [
            { id: 's-old-1', userId: 'tester01', answeredCount: 5, answers: [{ itemId: 101, selectedPrompt: 'prompt_a' }, { itemId: 102, selectedPrompt: 'prompt_b' }, { itemId: 103, selectedPrompt: 'prompt_a' }, { itemId: 104, selectedPrompt: 'prompt_a' }, { itemId: 105, selectedPrompt: 'prompt_b' }] },
            { id: 's-old-2', userId: 'tester02', answeredCount: 4, answers: [{ itemId: 101, selectedPrompt: 'prompt_b' }, { itemId: 102, selectedPrompt: 'prompt_a' }, { itemId: 103, selectedPrompt: 'prompt_a' }, { itemId: 104, selectedPrompt: 'prompt_b' }] },
            { id: 's-old-3', userId: 'tester03', answeredCount: 6, answers: [{ itemId: 101, selectedPrompt: 'prompt_a' }, { itemId: 102, selectedPrompt: 'prompt_a' }, { itemId: 103, selectedPrompt: 'prompt_b' }, { itemId: 104, selectedPrompt: 'prompt_a' }, { itemId: 105, selectedPrompt: 'prompt_a' }, { itemId: 106, selectedPrompt: 'prompt_b' }] }
          ]
        },
        {
          id: 2,
          name: '多图理解与问答完整性对比',
          description: '比较两组提示词在多图理解、问题归纳和答复完整性方面的差异。',
          promptA: '请对多张图片进行综合理解，先总结关键信息，再按用户提问生成结构化回答。',
          promptB: '请把多图信息整合成要点，用更口语化的表达回答用户，并尽可能减少遗漏。',
          status: 'unpublished',
          mode: 'custom',
          questionLimit: 2,
          createdBy: 'admin01',
          items: [
            { id: 201, code: 'Q201', sourceType: 'text', sortOrder: 1, sourceText: '分析仪表盘数据，主要波动集中在转化率与客单价，需要先确认渠道结构变化。', images: [], answerA: '从多图可以看出指标主要波动集中在转化率与客单价，需要先确认渠道结构变化。', answerB: '这些图片最关键的信息是转化率下滑和销售额波动，回答时需要把原因和建议一起给出。' },
            { id: 202, code: 'Q202', sourceType: 'text', sortOrder: 2, sourceText: '分析设计图，总结整体风格问题，并分别点评排版、配色和重点信息层级。', images: [], answerA: '适合先做视觉问题归纳，再提出三条可执行修改建议。', answerB: '更合适的方式是先总结整体风格问题，再分别点评排版、配色和重点信息层级。' }
          ],
          sessions: []
        }
      ],
      testerTasks: [
        {
          id: 1,
          name: '客服回复质量对比（V3 vs V4）',
          description: '比较两组提示词在客服安抚回复中的可读性、同理心表达、规则解释与补偿建议完整度。',
          promptA: '你是一名资深客服专家，请输出安抚式回复，先表达理解，再说明平台规则，最后给出可执行的补偿建议，整体语气温和、稳定、清晰。',
          promptB: '请作为高情商客服生成回复：先共情，再说明价格变动或流程机制，最后给出一到两种明确处理路径，并强调继续协助。',
          status: 'unpublished',
          mode: 'custom',
          questionLimit: 3,
          createdBy: 'admin01',
          items: [
            { id: 101, code: 'Q001', sourceType: 'text', sortOrder: 1, sourceText: '用户投诉：我昨天购买的商品今天就降价了，而且客服回复非常慢。请生成一段安抚用户情绪、解释规则并给出合理补偿建议的话术。', images: [], answerA: '您好，非常抱歉给您带来了不好的购物体验，也理解您看到商品短时间内出现价格变化后会产生落差感。平台活动价格会随时间动态调整，但我们非常重视您的感受。为了表达歉意，建议为您申请一张优惠券或积分补偿；如果您的订单符合价保条件，我也可以继续协助您核实处理。', answerB: '真的非常抱歉让您遇到这样的情况，换作是我也会感到失落。商品价格会因为活动时间不同而产生调整，这边无法直接保证下单后价格始终不变，但我会尽力帮您争取更好的处理方案，并优先为您申请补偿福利。' },
            { id: 102, code: 'Q002', sourceType: 'text', sortOrder: 2, sourceText: '用户反馈：快递已经延迟两天还没到，客服之前答应今天送达但目前没有更新。请生成一段安抚和补偿建议回复。', images: [], answerA: '您好，很抱歉让您久等了，也理解您在已经被承诺送达后却仍未收到包裹时的失望。我们会立即帮您再次催促物流并同步最新节点；如果最终仍超出承诺时效，我们也会为您申请补偿方案，尽量减少这次延迟带来的影响。', answerB: '非常抱歉这次配送没有达到预期，也感谢您耐心反馈。当前我们会先帮您核实物流异常原因，并持续跟进配送结果；同时这边会为您备注异常情况，若超时确认成立，会优先协助申请补偿。' },
            { id: 103, code: 'Q003', sourceType: 'text', sortOrder: 3, sourceText: '用户收到商品后发现配件缺失，希望客服回复。', images: [], answerA: '您好，给您带来不便真的很抱歉。针对您反馈的配件缺失问题，我们会先帮您核实订单与商品清单，如确认属实，可为您补发缺失配件，或根据情况协助申请相应补偿。', answerB: '非常抱歉让您收到的商品不完整，也理解这会影响正常使用。我们会马上为您核对包装与发货信息，如果确认缺件，会优先为您安排补发或提供其他处理方案。' },
          ],
          sessions: [
            { id: 's-old-1', userId: 'tester01', answeredCount: 5, answers: [{ itemId: 101, selectedPrompt: 'prompt_a' }, { itemId: 102, selectedPrompt: 'prompt_b' }, { itemId: 103, selectedPrompt: 'prompt_a' }, { itemId: 104, selectedPrompt: 'prompt_a' }, { itemId: 105, selectedPrompt: 'prompt_b' }] },
            { id: 's-old-2', userId: 'tester02', answeredCount: 4, answers: [{ itemId: 101, selectedPrompt: 'prompt_b' }, { itemId: 102, selectedPrompt: 'prompt_a' }, { itemId: 103, selectedPrompt: 'prompt_a' }, { itemId: 104, selectedPrompt: 'prompt_b' }] },
            { id: 's-old-3', userId: 'tester03', answeredCount: 6, answers: [{ itemId: 101, selectedPrompt: 'prompt_a' }, { itemId: 102, selectedPrompt: 'prompt_a' }, { itemId: 103, selectedPrompt: 'prompt_b' }, { itemId: 104, selectedPrompt: 'prompt_a' }, { itemId: 105, selectedPrompt: 'prompt_a' }, { itemId: 106, selectedPrompt: 'prompt_b' }] }
          ]
        },
        {
          id: 2,
          name: 'AI质检结果比对',
          description: '比较两组提示词在质检结果方面的差异。',
          promptA: '请对多张图片进行综合理解，先总结关键信息，再按用户提问生成结构化回答。',
          promptB: '请把多图信息整合成要点，用更口语化的表达回答用户，并尽可能减少遗漏。',
          status: 'unpublished',
          mode: 'single',
          questionLimit: 2,
          createdBy: 'admin01',
          items: [
            { id: 201, code: 'Q201', sourceType: 'text', sortOrder: 1, sourceText: '分析仪表盘数据，主要波动集中在转化率与客单价，需要先确认渠道结构变化。', images: [], answerA: '从多图可以看出指标主要波动集中在转化率与客单价，需要先确认渠道结构变化。', answerB: '这些图片最关键的信息是转化率下滑和销售额波动，回答时需要把原因和建议一起给出。' },
            { id: 202, code: 'Q202', sourceType: 'text', sortOrder: 2, sourceText: '分析设计图，总结整体风格问题，并分别点评排版、配色和重点信息层级。', images: [], answerA: '适合先做视觉问题归纳，再提出三条可执行修改建议。', answerB: '更合适的方式是先总结整体风格问题，再分别点评排版、配色和重点信息层级。' }
          ],
          sessions: []
        }
      ]
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
    }
  },
  mounted() {
    // 初始化任务统计数据
    this.adminTasks.forEach(task => {
      this.calculateTaskStats(task)
    })
    this.adminManagementTasks.forEach(task => {
      this.calculateTaskStats(task)
    })
    this.testerTasks.forEach(task => {
      this.calculateTaskStats(task)
    })
  },
  methods: {
    login(user) {
      this.currentUser = user
      this.isLoggedIn = true
      this.currentView = user.role === 'tester' ? 'tester-tasks' : 'admin-generate'
      this.showToast('登录成功')
    },
    logout() {
      this.isLoggedIn = false
      this.currentUser = null;
      this.currentView = 'tester-tasks'
      this.selectedTaskId = null
      this.currentSession = null
      this.showToast('已退出登录')
    },
    switchRole() {
      const newRole = this.currentUser.role === 'tester' ? 'admin' : 'tester'
      this.login({
        username: newRole === 'tester' ? 'tester01' : 'admin01',
        role: newRole
      })
    },
    viewTaskDetail(taskId) {
      this.selectedTaskId = taskId
      this.currentView = this.currentUser.role === 'admin' ? 'admin-task-detail' : 'tester-task-detail'
    },
    viewHistory(taskId) {
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
    deleteQuestion(sessionId, questionId) {
      if (this.selectedTask) {
        const session = this.selectedTask.sessions.find(session => session.id === sessionId)
        if (session) {
          // 从questions数组中删除对应的问题
          const questionIndex = session.questions.findIndex(q => q.id === questionId)
          if (questionIndex >= 0) {
            session.questions.splice(questionIndex, 1)
          }
          
          // 从answers数组中删除对应的答案
          const answerIndex = session.answers.findIndex(a => a.itemId === questionId)
          if (answerIndex >= 0) {
            session.answers.splice(answerIndex, 1)
          }
          
          // 从userInputs中删除对应的输入
          if (session.userInputs && session.userInputs[questionId]) {
            delete session.userInputs[questionId]
          }
          
          // 更新answeredCount
          session.answeredCount = session.answers.length
          
          // 如果会话中没有问题了，删除整个会话
          if (session.questions.length === 0) {
            const sessionIndex = this.selectedTask.sessions.findIndex(s => s.id === sessionId)
            if (sessionIndex >= 0) {
              this.selectedTask.sessions.splice(sessionIndex, 1)
            }
          }
          
          this.calculateTaskStats(this.selectedTask)
          this.showToast('测试任务记录已删除')
        }
      }
    },
    startTask(taskId) {
      const taskArray = this.currentUser.role === 'admin' ? this.adminTasks : this.testerTasks
      const task = taskArray.find(t => t.id === taskId)
      if (!task) return
      
      // 使用任务中指定数量的题目
      const selectedItems = task.items.slice(0, task.questionLimit || task.items.length)
      
      this.currentSession = {
        id: `s-${Date.now()}`,
        taskId: task.id,
        taskMode: task.mode || 'custom',
        questions: selectedItems,
        answers: [],
        userInputs: {},
        startTime: new Date()
      }
      
      this.currentQuestionIndex = 0
      this.selectedAnswer = null
      this.userInputs = {}
      this.currentView = this.currentUser.role === 'admin' ? 'admin-session' : 'tester-session'
    },
    handleUserInputChange(questionId, value) {
      if (this.currentSession) {
        this.currentSession.userInputs = this.currentSession.userInputs || {}
        this.currentSession.userInputs[questionId] = value
        console.log('User input changed:', questionId, value)
      }
    },
    selectAnswer(answer) {
      this.selectedAnswer = answer
      this.saveHintText = '已保存选择，可继续下一题。'
      
      // 保存答案
      const currentAnswer = {
        itemId: this.currentSession.questions[this.currentQuestionIndex].id,
        selectedPrompt: answer === 'A' ? 'prompt_a' : 'prompt_b'
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
      return answer ? (answer.selectedPrompt === 'prompt_a' ? 'A' : 'B') : null
    },
    quitSession() {
      if (this.currentSession) {
        // 保存会话到任务
        const taskArray = this.currentUser.role === 'admin' ? this.adminTasks : this.testerTasks
        const task = taskArray.find(t => t.id === this.currentSession.taskId)
        if (task) {
          // 过滤出有用户输入且有选择的问题
          const validQuestions = this.currentSession.questions.filter(q => {
            const hasUserInput = this.currentSession.userInputs && this.currentSession.userInputs[q.id] && this.currentSession.userInputs[q.id].trim()
            const hasAnswer = this.currentSession.answers.some(a => a.itemId === q.id)
            return hasUserInput && hasAnswer
          })
          
          // 过滤出对应的答案
          const validAnswers = this.currentSession.answers.filter(a => 
            validQuestions.some(q => q.id === a.itemId)
          )
          
          // 过滤出对应的用户输入
          const validUserInputs = {}
          validQuestions.forEach(q => {
            if (this.currentSession.userInputs && this.currentSession.userInputs[q.id]) {
              validUserInputs[q.id] = this.currentSession.userInputs[q.id]
            }
          })
          
          // 只有当有有效问题时才保存会话
          if (validQuestions.length > 0) {
            // 获取大模型裁判结果
            let modelJudgeAnswers = {}
            if (this.$refs.testSession) {
              modelJudgeAnswers = this.$refs.testSession.getModelJudgeAnswers()
              console.log('Model judge answers:', modelJudgeAnswers)
            }
            
            // 构建完整的会话信息，包括用户输入、候选回答、选择结果和大模型裁判结果
            const sessionWithDetails = {
              id: this.currentSession.id,
              userId: this.currentUser.username,
              answeredCount: validAnswers.length,
              answers: validAnswers,
              userInputs: validUserInputs,
              questions: validQuestions.map(q => ({
                ...q,
                modelJudge: modelJudgeAnswers[q.id] || null
              })),
              endTime: new Date()
            }
            
            console.log('Session with details:', sessionWithDetails)
            
            task.sessions.push(sessionWithDetails)
            this.calculateTaskStats(task)
            
            // 记录到历史操作
            this.historyOperations.push({
              id: `h-${Date.now()}`,
              type: 'session_completed',
              userId: this.currentUser.username,
              taskId: task.id,
              taskName: task.name,
              sessionId: this.currentSession.id,
              timestamp: new Date(),
              details: {
                answeredCount: validAnswers.length,
                questions: validQuestions.map(q => ({
                  id: q.id,
                  originalQuestion: validUserInputs[q.id] || '',
                  answerA: q.answerA,
                  answerB: q.answerB,
                  selectedAnswer: validAnswers.find(a => a.itemId === q.id) ? (validAnswers.find(a => a.itemId === q.id).selectedPrompt === 'prompt_a' ? 'A' : 'B') : null,
                  modelJudge: modelJudgeAnswers[q.id] || null
                }))
              }
            })
            
            console.log('Session completed and added to history:', this.historyOperations[this.historyOperations.length - 1])
          }
        }
        this.currentSession = null
        this.currentView = this.currentUser.role === 'admin' ? 'admin-test' : 'tester-tasks'
        this.showToast('已保存并退出测试')
      }
    },
    quitAdminSession() {
      this.quitSession()
    },
    finishSession() {
      this.quitSession()
    },
    createDemoTask() {
      this.tempTask = {
        id: this.adminManagementTasks.length + 1,
        name: `新任务 ${this.adminManagementTasks.length + 1}`,
        description: '这是一个新创建的模拟任务。',
        promptA: '请生成专业、详细的回答。',
        promptB: '请生成简洁、易懂的回答。',
        status: 'draft',
        mode: 'custom',
        testCount: 5,
        questionLimit: 10,
        createdBy: this.currentUser.username,
        items: [],
        sessions: []
      }
      this.selectedTaskId = 'temp'
      this.currentView = 'admin-editor'
      this.showToast('已创建模拟任务，请保存草稿或发布任务')
    },
    editTask(taskId) {
      const task = this.adminManagementTasks.find(task => task.id === taskId)
      if (task && task.status === 'published') {
        // 为已发布任务创建临时副本
        this.tempTask = JSON.parse(JSON.stringify(task))
        this.tempTask.status = 'draft'
        this.selectedTaskId = 'temp'
      } else {
        // 未发布任务直接编辑
        this.selectedTaskId = taskId
      }
      this.currentView = 'admin-editor'
    },
    viewStats(taskId) {
      this.selectedTaskId = taskId
      this.currentView = 'admin-stats'
    },
    addItem(itemForm) {
      if (!this.selectedTask) return
      
      const newItem = {
        id: Date.now(),
        code: itemForm.code,
        sortOrder: itemForm.sortOrder,
        sourceText: itemForm.sourceText
      }
      
      this.selectedTask.items.push(newItem)
      this.showToast('已添加题目')
    },
    mockImport() {
      if (!this.selectedTask) return
      
      // 模拟批量导入
      const sampleItems = [
        {
          id: Date.now() + 1,
          code: `Q${Date.now().toString().slice(-4)}`,
          sortOrder: this.selectedTask.items.length + 1,
          sourceText: '模拟导入题目 1：用户反馈产品问题'
        },
        {
          id: Date.now() + 2,
          code: `Q${(Date.now() + 1).toString().slice(-4)}`,
          sortOrder: this.selectedTask.items.length + 2,
          sourceText: '模拟导入题目 2：产品功能使用问题'
        }
      ]
      
      this.selectedTask.items.push(...sampleItems)
      this.showToast('模拟批量导入成功')
    },
    deleteItem(itemId) {
      if (!this.selectedTask) return
      
      const itemIndex = this.selectedTask.items.findIndex(item => item.id === itemId)
      if (itemIndex >= 0) {
        this.selectedTask.items.splice(itemIndex, 1)
        this.showToast('题目已删除')
      }
    },
    deleteTask() {
      if (!this.selectedTask) return
      
      // 如果是临时任务（修改已发布任务），删除原始任务
      if (this.selectedTaskId === 'temp' && this.tempTask) {
        const originalTaskIndex = this.adminManagementTasks.findIndex(task => task.id === this.tempTask.id)
        if (originalTaskIndex >= 0) {
          this.adminManagementTasks.splice(originalTaskIndex, 1)
        }
        this.tempTask = null
        this.selectedTaskId = null
        this.currentView = 'admin-tasks'
        this.showToast('任务已删除')
      } else if (this.selectedTaskId === 'temp') {
        // 新创建的临时任务，直接清除
        this.tempTask = null
        this.selectedTaskId = null
        this.currentView = 'admin-tasks'
        this.showToast('任务已删除')
      } else {
        // 删除现有任务
        const index = this.adminManagementTasks.findIndex(task => task.id === this.selectedTaskId)
        if (index >= 0) {
          this.adminManagementTasks.splice(index, 1)
          this.selectedTaskId = null
          this.currentView = 'admin-tasks'
          this.showToast('任务已删除')
        }
      }
    },
    saveDraft() {
      if (!this.selectedTask) return
      
      // 如果是临时任务
      if (this.selectedTaskId === 'temp' && this.tempTask) {
        const originalTaskIndex = this.adminManagementTasks.findIndex(task => task.id === this.tempTask.id)
        if (originalTaskIndex >= 0) {
          // 修改已发布任务的临时副本，更新原始任务
          this.tempTask.status = 'draft'
          this.adminManagementTasks[originalTaskIndex] = this.tempTask
          this.calculateTaskStats(this.tempTask)
        } else {
          // 新创建的临时任务，添加到任务列表
          this.tempTask.status = 'draft'
          this.adminManagementTasks.push(this.tempTask)
          this.calculateTaskStats(this.tempTask)
        }
        this.tempTask = null
      } else {
        // 直接编辑的任务，更新状态
        this.selectedTask.status = 'draft'
        const taskIndex = this.adminManagementTasks.findIndex(task => task.id === this.selectedTaskId)
        if (taskIndex >= 0) {
          this.adminManagementTasks[taskIndex] = this.selectedTask
          this.calculateTaskStats(this.selectedTask)
        }
      }
      
      this.showToast('任务已保存为草稿')
      this.selectedTaskId = null
      this.currentView = 'admin-tasks'
    },
    publishTask() {
      if (!this.selectedTask) return
      
      // 检查发布前校验
      const taskEditor = this.$children.find(child => child.$options.name === 'TaskEditor')
      if (taskEditor && taskEditor.publishCheckText !== '校验通过，可以发布。') {
        alert(`发布失败：${taskEditor.publishCheckText}`)
        return
      }
      
      // 如果是临时任务
      if (this.selectedTaskId === 'temp' && this.tempTask) {
        const originalTaskIndex = this.adminManagementTasks.findIndex(task => task.id === this.tempTask.id)
        if (originalTaskIndex >= 0) {
          // 修改已发布任务的临时副本，更新原始任务
          this.tempTask.status = 'published'
          this.adminManagementTasks[originalTaskIndex] = this.tempTask
          this.calculateTaskStats(this.tempTask)
        } else {
          // 新创建的临时任务，添加到任务列表
          this.tempTask.status = 'published'
          this.adminManagementTasks.push(this.tempTask)
          this.calculateTaskStats(this.tempTask)
        }
        this.tempTask = null
      } else {
        // 直接编辑的任务，更新状态
        this.selectedTask.status = 'published'
        const taskIndex = this.adminManagementTasks.findIndex(task => task.id === this.selectedTaskId)
        if (taskIndex >= 0) {
          this.adminManagementTasks[taskIndex] = this.selectedTask
          this.calculateTaskStats(this.selectedTask)
        }
      }
      
      this.showToast('任务已重新发布')
      this.selectedTaskId = null
      this.currentView = 'admin-tasks'
    },
    calculateTaskStats(task) {
      // 计算总选择数
      let totalSelections = 0
      let promptASelections = 0
      let promptBSelections = 0
      
      task.sessions.forEach(session => {
        session.answers.forEach(answer => {
          totalSelections++
          if (answer.selectedPrompt === 'prompt_a') {
            promptASelections++
          } else {
            promptBSelections++
          }
        })
      })
      
      task.totalSelections = totalSelections
      task.promptASelections = promptASelections
      task.promptBSelections = promptBSelections
      task.promptAPercentage = totalSelections > 0 ? Math.round((promptASelections / totalSelections) * 100) : 0
      task.promptBPercentage = totalSelections > 0 ? Math.round((promptBSelections / totalSelections) * 100) : 0
      
      // 计算每题的选择数
      task.items.forEach(item => {
        let itemPromptASelections = 0
        let itemPromptBSelections = 0
        
        task.sessions.forEach(session => {
          const answer = session.answers.find(a => a.itemId === item.id)
          if (answer) {
            if (answer.selectedPrompt === 'prompt_a') {
              itemPromptASelections++
            } else {
              itemPromptBSelections++
            }
          }
        })
        
        item.promptASelections = itemPromptASelections
        item.promptBSelections = itemPromptBSelections
      })
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

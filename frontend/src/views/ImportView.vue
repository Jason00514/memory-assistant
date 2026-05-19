<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-xl font-bold mb-6">导入内容</h1>

    <!-- ファイルアップロードゾーン -->
    <div
      class="border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-colors"
      :class="dragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
      @click="fileInput?.click()"
    >
      <div class="text-4xl mb-3">📂</div>
      <p class="text-gray-600 font-medium">拖拽文件到此处，或点击选择</p>
      <p class="text-sm text-gray-400 mt-1">支持 .xlsx / .xls / .txt 格式</p>
      <input ref="fileInput" type="file" accept=".xlsx,.xls,.txt" class="hidden" @change="onFileChange" />
    </div>

    <!-- 選択ファイル表示 -->
    <div v-if="file" class="mt-3 flex items-center gap-3 bg-white border rounded-xl px-4 py-3">
      <span class="text-xl">{{ file.name.endsWith('.txt') ? '📝' : '📄' }}</span>
      <span class="flex-1 text-sm text-gray-700 truncate">{{ file.name }}</span>
      <span class="text-xs text-gray-400">{{ fileTypeLabel }}</span>
      <button @click="file = null" class="text-gray-400 hover:text-red-500 text-xl leading-none">×</button>
    </div>

    <!-- インポートボタン -->
    <button
      :disabled="!file || importing"
      @click="doImport"
      class="mt-4 w-full py-3 rounded-xl font-semibold text-white transition-colors"
      :class="file && !importing ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-gray-300 cursor-not-allowed'"
    >
      {{ importing ? '导入中…' : '开始导入' }}
    </button>

    <!-- インポート結果 -->
    <div v-if="importResult" class="mt-6 bg-white rounded-2xl border p-5">
      <div class="flex items-center gap-3 mb-4">
        <span class="text-2xl">{{ importResult.failed === 0 ? '✅' : '⚠️' }}</span>
        <div>
          <p class="font-semibold">导入完成：{{ importResult.total_imported }} 条成功，{{ importResult.failed }} 条失败</p>
          <p class="text-sm text-gray-400">点击下方按钮解析为复习卡片</p>
        </div>
      </div>

      <!-- カーブ選択 -->
      <div class="flex gap-3 items-center mb-3">
        <label class="text-sm text-gray-600 whitespace-nowrap">使用曲线：</label>
        <select v-model="selectedCurveId"
          class="border rounded-lg px-2 py-1.5 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-indigo-400">
          <option value="">默认曲线</option>
          <option v-for="c in curves" :key="c.curve_id" :value="c.curve_id">
            {{ c.curve_name }}（{{ fmtIntervals(c.intervals) }}）
          </option>
        </select>
        <!-- カーブプレビュー -->
        <button v-if="selectedCurveId" @click="togglePreview"
          class="text-xs text-indigo-500 underline whitespace-nowrap">
          {{ showPreview ? '收起预览' : '预览时间表' }}
        </button>
      </div>

      <!-- カーブプレビュー表示 -->
      <div v-if="showPreview && curvePreview" class="mb-4 bg-indigo-50 rounded-xl p-4 text-sm">
        <p class="font-semibold text-indigo-700 mb-2">
          📅 {{ curvePreview.curve_name }} — 全部答对共需 {{ curvePreview.total_days }} 天 / {{ curvePreview.total_reviews }} 次复习
        </p>
        <div class="grid grid-cols-7 gap-1">
          <div v-for="entry in curvePreview.schedule" :key="entry.level"
            class="text-center bg-white rounded-lg p-2 border border-indigo-100">
            <div class="text-xs text-gray-400">Lv{{ entry.level }}</div>
            <div class="text-xs font-semibold text-indigo-600 mt-1">{{ entry.review_date_label }}</div>
          </div>
        </div>
      </div>

      <button @click="doProcess" :disabled="processing"
        class="w-full py-2.5 rounded-xl font-semibold transition-colors"
        :class="processing ? 'bg-gray-200 text-gray-400' : 'bg-green-600 text-white hover:bg-green-700'">
        {{ processing ? '解析中…' : '🔄 解析为复习卡片' }}
      </button>
    </div>

    <!-- 解析結果 -->
    <div v-if="processResult" class="mt-4 bg-green-50 border border-green-200 rounded-2xl p-5">
      <p class="font-semibold text-green-700 mb-2">
        ✅ 解析完成：{{ processResult.total_processed }} 张卡片已就绪
      </p>
      <div class="space-y-1.5 max-h-52 overflow-y-auto">
        <div v-for="item in processResult.items" :key="item.PC_ID"
          class="flex items-center gap-2 text-sm bg-white rounded-lg px-3 py-2 border">
          <span class="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{{ item.content_type }}</span>
          <span class="flex-1 truncate text-gray-700">{{ item.question }}</span>
          <span class="text-indigo-500 font-medium text-xs">{{ item.category }}</span>
        </div>
      </div>
      <RouterLink to="/review" class="mt-3 inline-block text-sm text-indigo-600 underline">→ 去复习</RouterLink>
    </div>

    <!-- フォーマットガイド -->
    <div class="mt-8 bg-white rounded-2xl border p-5">
      <h3 class="font-semibold text-gray-700 mb-3">支持的格式（Excel 和 TXT 通用）</h3>
      <div class="space-y-3 text-sm text-gray-600">
        <div v-for="ex in formatExamples" :key="ex.title" class="bg-gray-50 rounded-lg p-3">
          <p class="text-xs font-semibold text-gray-500 mb-1">{{ ex.title }}</p>
          <pre class="font-mono text-xs leading-6 whitespace-pre-wrap">{{ ex.code }}</pre>
        </div>
        <p class="text-xs text-gray-400">TXT 文件：用空行或 "---" 分隔每张卡片</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { importExcel, importText, processRaw, getCurves, getCurvePreview } from '../api'
import type { ImportResult, ProcessResult, MemoryCurve, CurvePreview } from '../types'

const file = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const dragging = ref(false)
const importing = ref(false)
const processing = ref(false)
const importResult = ref<ImportResult | null>(null)
const processResult = ref<ProcessResult | null>(null)
const curves = ref<MemoryCurve[]>([])
const selectedCurveId = ref('')
const showPreview = ref(false)
const curvePreview = ref<CurvePreview | null>(null)

const fileTypeLabel = computed(() => {
  if (!file.value) return ''
  if (file.value.name.endsWith('.txt')) return 'TXT文本'
  return 'Excel'
})

function fmtIntervals(intervals: number[]) {
  return intervals.map(h => h < 24 ? `${h}h` : `${Math.round(h/24)}d`).join('-')
}

function onDrop(e: DragEvent) {
  dragging.value = false
  const f = e.dataTransfer?.files[0]
  if (f) file.value = f
}
function onFileChange(e: Event) {
  const f = (e.target as HTMLInputElement).files?.[0]
  if (f) file.value = f
}

async function doImport() {
  if (!file.value) return
  importing.value = true
  importResult.value = null
  processResult.value = null
  try {
    if (file.value.name.endsWith('.txt')) {
      importResult.value = await importText(file.value)
    } else {
      importResult.value = await importExcel(file.value)
    }
  } finally {
    importing.value = false
  }
}

async function doProcess() {
  processing.value = true
  try {
    processResult.value = await processRaw(selectedCurveId.value || undefined)
  } finally {
    processing.value = false
  }
}

async function togglePreview() {
  showPreview.value = !showPreview.value
  if (showPreview.value && selectedCurveId.value) {
    curvePreview.value = await getCurvePreview(selectedCurveId.value)
  }
}

watch(selectedCurveId, async (id) => {
  if (id && showPreview.value) {
    curvePreview.value = await getCurvePreview(id)
  }
})

const formatExamples = [
  { title: '记忆模式（无答案）', code: '# Category: 常忘知识点\n\nTCP三次握手：SYN → SYN-ACK → ACK，确保双方能发送和接收。' },
  { title: '单词/解释模式', code: '# Category: 英语词汇\n\nabandon\nvt.\n\nanswer: 放弃，遗弃' },
  { title: '单选题', code: '下列哪项不属于OSI模型的层？\nA. 表示层\nB. 会话层\nC. 传输层\nD. 控制层\n\nanswer option: D\nexplain: OSI共7层，没有控制层。' },
  { title: '多选题', code: '以下哪些是Python内置数据类型？\nA. list  B. array  C. tuple  D. dict\n\nanswer check: A,C,D\nexplain: array不是内置类型。' },
]

onMounted(async () => {
  curves.value = await getCurves()
})
</script>

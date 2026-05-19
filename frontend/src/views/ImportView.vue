<template>
  <div class="max-w-2xl mx-auto">
    <h1 class="text-xl font-bold mb-6">导入 Excel</h1>

    <!-- Upload zone -->
    <div
      class="border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-colors"
      :class="dragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
      @click="fileInput?.click()"
    >
      <div class="text-4xl mb-3">📂</div>
      <p class="text-gray-600 font-medium">拖拽 Excel 文件到此处，或点击选择</p>
      <p class="text-sm text-gray-400 mt-1">支持 .xlsx / .xls，单列格式</p>
      <input ref="fileInput" type="file" accept=".xlsx,.xls" class="hidden" @change="onFileChange" />
    </div>

    <!-- Selected file -->
    <div v-if="file" class="mt-3 flex items-center gap-3 bg-white border rounded-xl px-4 py-3">
      <span class="text-green-500 text-xl">📄</span>
      <span class="flex-1 text-sm text-gray-700 truncate">{{ file.name }}</span>
      <button @click="file = null" class="text-gray-400 hover:text-red-500 text-lg leading-none">×</button>
    </div>

    <!-- Import button -->
    <button
      :disabled="!file || importing"
      @click="doImport"
      class="mt-4 w-full py-3 rounded-xl font-semibold text-white transition-colors"
      :class="file && !importing ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-gray-300 cursor-not-allowed'"
    >
      {{ importing ? '导入中…' : '开始导入' }}
    </button>

    <!-- Import result -->
    <div v-if="importResult" class="mt-6 bg-white rounded-2xl border p-5">
      <div class="flex items-center gap-3 mb-4">
        <span class="text-2xl">{{ importResult.failed === 0 ? '✅' : '⚠️' }}</span>
        <div>
          <p class="font-semibold">导入完成：{{ importResult.total_imported }} 条成功，{{ importResult.failed }} 条失败</p>
          <p class="text-sm text-gray-400">状态：未解析 (unprocessed)，点击下方按钮解析为复习卡片</p>
        </div>
      </div>

      <!-- Curve selector -->
      <div class="flex gap-3 items-center mb-3">
        <label class="text-sm text-gray-600 whitespace-nowrap">使用曲线：</label>
        <select v-model="selectedCurveId" class="border rounded-lg px-2 py-1.5 text-sm flex-1 focus:outline-none focus:ring-2 focus:ring-indigo-400">
          <option value="">默认（标准单词曲线）</option>
          <option v-for="c in curves" :key="c.curve_id" :value="c.curve_id">
            {{ c.curve_name }} — [{{ c.intervals.join(', ') }}]h
          </option>
        </select>
      </div>

      <button @click="doProcess" :disabled="processing"
        class="w-full py-2.5 rounded-xl font-semibold transition-colors"
        :class="processing ? 'bg-gray-200 text-gray-400' : 'bg-green-600 text-white hover:bg-green-700'">
        {{ processing ? '解析中…' : '🔄 解析为复习卡片' }}
      </button>
    </div>

    <!-- Process result -->
    <div v-if="processResult" class="mt-4 bg-green-50 border border-green-200 rounded-2xl p-5">
      <p class="font-semibold text-green-700 mb-2">
        ✅ 解析完成：{{ processResult.total_processed }} 条卡片已就绪
      </p>
      <div class="space-y-2 max-h-60 overflow-y-auto">
        <div v-for="item in processResult.items" :key="item.PC_ID"
          class="flex items-center gap-2 text-sm bg-white rounded-lg px-3 py-2 border">
          <span class="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-500">{{ item.content_type }}</span>
          <span class="flex-1 truncate text-gray-700">{{ item.question }}</span>
          <span class="text-indigo-500 font-medium text-xs">{{ item.category }}</span>
        </div>
      </div>
      <RouterLink to="/review" class="mt-3 inline-block text-sm text-indigo-600 underline">→ 去复习</RouterLink>
    </div>

    <!-- Format guide -->
    <div class="mt-8 bg-white rounded-2xl border p-5">
      <h3 class="font-semibold text-gray-700 mb-3">Excel 格式说明</h3>
      <div class="space-y-3 text-sm text-gray-600">
        <div class="bg-gray-50 rounded-lg p-3 font-mono text-xs leading-6">
          <div class="text-indigo-600 font-semibold"># Category: 英语核心词汇</div>
          <div class="mt-2">abandon<br/>vt.<br/><br/>answer: 放弃，遗弃</div>
          <div class="mt-2 text-gray-400">（单词/答案模式）</div>
        </div>
        <div class="bg-gray-50 rounded-lg p-3 font-mono text-xs leading-6">
          <div>TCP三次握手：SYN → SYN-ACK → ACK</div>
          <div class="text-gray-400">（纯记忆模式，无需 answer:）</div>
        </div>
        <div class="bg-gray-50 rounded-lg p-3 font-mono text-xs leading-6">
          <div>下列哪项不属于OSI模型的层？<br/>A. 表示层  B. 会话层<br/>C. 传输层  D. 控制层<br/><br/>answer option: D<br/>explain: OSI共7层，没有控制层。</div>
          <div class="text-gray-400">（单选题模式）</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { importExcel, processRaw, getCurves } from '../api'
import type { ImportResult, ProcessResult, MemoryCurve } from '../types'

const file = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const dragging = ref(false)
const importing = ref(false)
const processing = ref(false)
const importResult = ref<ImportResult | null>(null)
const processResult = ref<ProcessResult | null>(null)
const curves = ref<MemoryCurve[]>([])
const selectedCurveId = ref('')

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
    importResult.value = await importExcel(file.value)
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

onMounted(async () => {
  curves.value = await getCurves()
})
</script>

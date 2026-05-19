<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold">记忆曲线</h1>
      <button @click="openCreate" class="btn-primary">+ 新建曲线</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-7 h-7 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Curve cards -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="c in curves" :key="c.curve_id"
        class="bg-white rounded-2xl border p-5 hover:shadow-md transition-shadow">
        <div class="flex items-start justify-between mb-2">
          <div>
            <h3 class="font-semibold text-gray-800">{{ c.curve_name }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ c.curve_id }}</p>
          </div>
          <div class="flex gap-2">
            <button @click="openEdit(c)" class="text-xs text-indigo-500 hover:underline">编辑</button>
            <button @click="doDelete(c)" class="text-xs text-red-400 hover:underline">删除</button>
          </div>
        </div>

        <p v-if="c.description" class="text-sm text-gray-500 mb-3">{{ c.description }}</p>

        <!-- Interval visualizer -->
        <div class="mb-3">
          <div class="text-xs text-gray-400 mb-1.5">复习间隔（小时）</div>
          <div class="flex gap-1.5 items-end h-12">
            <div v-for="(h, i) in c.intervals" :key="i"
              class="flex-1 bg-indigo-200 rounded-t text-center relative group"
              :style="{ height: barHeight(h, c.intervals) + '%' }">
              <span class="absolute -top-5 left-0 right-0 text-center text-xs text-indigo-600 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                {{ fmtH(h) }}
              </span>
            </div>
          </div>
          <div class="flex gap-1.5 mt-0.5">
            <div v-for="i in 7" :key="i" class="flex-1 text-center text-xs text-gray-300">L{{ i }}</div>
          </div>
        </div>

        <div class="text-xs text-gray-400">
          严重过期倍数：<span class="text-gray-600 font-medium">{{ c.overdue_multiplier }}×</span>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md shadow-xl">
        <h3 class="font-bold text-lg mb-4">{{ editing ? '编辑曲线' : '新建曲线' }}</h3>

        <div class="space-y-3">
          <div>
            <label class="text-sm text-gray-600">曲线名称</label>
            <input v-model="form.curve_name" class="input mt-1 w-full" placeholder="如：标准单词曲线" />
          </div>
          <div>
            <label class="text-sm text-gray-600">描述（可选）</label>
            <input v-model="form.description" class="input mt-1 w-full" placeholder="适用场景说明" />
          </div>
          <div>
            <label class="text-sm text-gray-600 block mb-1">
              7级复习间隔（小时）
              <span class="text-gray-400 text-xs ml-1">— 对应 Level 1 到 Level 7</span>
            </label>
            <div class="grid grid-cols-7 gap-1.5">
              <div v-for="(_, i) in form.intervals" :key="i">
                <div class="text-center text-xs text-gray-400 mb-0.5">L{{ i + 1 }}</div>
                <input v-model.number="form.intervals[i]" type="number" min="1"
                  class="input text-center px-1 w-full text-sm" />
              </div>
            </div>
          </div>
          <div>
            <label class="text-sm text-gray-600">严重过期倍数</label>
            <input v-model.number="form.overdue_multiplier" type="number" min="1" class="input mt-1 w-full" />
          </div>
        </div>

        <div class="flex gap-3 mt-5">
          <button @click="showModal = false" class="flex-1 py-2 rounded-lg border text-sm hover:bg-gray-50">取消</button>
          <button @click="save" :disabled="saving"
            class="flex-1 py-2 rounded-lg bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50">
            {{ saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getCurves, createCurve, updateCurve, deleteCurve } from '../api'
import type { MemoryCurve } from '../types'

const curves = ref<MemoryCurve[]>([])
const loading = ref(true)
const showModal = ref(false)
const saving = ref(false)
const editing = ref<MemoryCurve | null>(null)

const blankForm = () => ({
  curve_name: '',
  description: '',
  intervals: [1, 4, 24, 48, 168, 360, 720],
  overdue_multiplier: 10,
})
const form = ref(blankForm())

function barHeight(h: number, intervals: number[]) {
  const max = Math.max(...intervals)
  return Math.max(15, (h / max) * 100)
}
function fmtH(h: number) {
  if (h < 24) return `${h}h`
  if (h < 24 * 7) return `${Math.round(h / 24)}d`
  return `${Math.round(h / 24 / 7)}w`
}

function openCreate() {
  editing.value = null
  form.value = blankForm()
  showModal.value = true
}
function openEdit(c: MemoryCurve) {
  editing.value = c
  form.value = { curve_name: c.curve_name, description: c.description ?? '', intervals: [...c.intervals], overdue_multiplier: c.overdue_multiplier }
  showModal.value = true
}

async function save() {
  saving.value = true
  try {
    if (editing.value) {
      await updateCurve(editing.value.curve_id, form.value)
    } else {
      await createCurve(form.value)
    }
    showModal.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function doDelete(c: MemoryCurve) {
  if (!confirm(`确定删除「${c.curve_name}」？`)) return
  await deleteCurve(c.curve_id)
  await load()
}

async function load() {
  loading.value = true
  curves.value = await getCurves()
  loading.value = false
}

onMounted(load)
</script>

<style scoped>
.input {
  @apply border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400;
}
.btn-primary {
  @apply bg-indigo-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors text-sm;
}
</style>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold">卡片库</h1>
      <div class="flex gap-2">
        <input v-model="categoryFilter" @keyup.enter="load" placeholder="按分类筛选"
          class="border rounded px-2 py-1 text-sm w-36 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
        <select v-model="typeFilter" @change="load"
          class="border rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400">
          <option value="">全部类型</option>
          <option value="word">单词</option>
          <option value="memory">记忆</option>
          <option value="single_choice">单选</option>
          <option value="multiple_choice">多选</option>
        </select>
        <button @click="load" class="border rounded px-3 py-1 text-sm hover:bg-gray-50">刷新</button>
      </div>
    </div>

    <!-- Stats bar -->
    <div class="grid grid-cols-4 gap-3 mb-5">
      <div v-for="s in stats" :key="s.label" class="bg-white rounded-xl border px-4 py-3 text-center">
        <div class="text-2xl font-bold" :class="s.color">{{ s.value }}</div>
        <div class="text-xs text-gray-400 mt-0.5">{{ s.label }}</div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-7 h-7 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Table -->
    <div v-else class="bg-white rounded-2xl border overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            <th class="text-left px-4 py-3">问题</th>
            <th class="text-left px-4 py-3 w-24">分类</th>
            <th class="text-left px-4 py-3 w-20">类型</th>
            <th class="text-center px-4 py-3 w-16">等级</th>
            <th class="text-left px-4 py-3 w-32">下次复习</th>
            <th class="text-center px-4 py-3 w-20">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="item in filtered" :key="item.PC_ID"
            class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 max-w-xs">
              <div class="truncate text-gray-800">{{ item.question }}</div>
              <div class="text-xs text-gray-400 truncate mt-0.5">{{ item.answer !== 'NONE' ? item.answer : '' }}</div>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ item.category }}</td>
            <td class="px-4 py-3">
              <span :class="typeClass(item.content_type)"
                class="px-2 py-0.5 rounded-full text-xs font-medium">
                {{ typeLabel(item.content_type) }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <LevelBadge :level="item.current_level" />
            </td>
            <td class="px-4 py-3 text-xs" :class="overdueClass(item)">
              {{ fmtNextReview(item) }}
            </td>
            <td class="px-4 py-3 text-center">
              <button @click="openReset(item)" class="text-gray-400 hover:text-indigo-600 text-xs underline">重置</button>
            </td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="6" class="text-center py-12 text-gray-400">暂无卡片</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Reset modal -->
    <div v-if="resetTarget" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-80 shadow-xl">
        <h3 class="font-bold text-lg mb-2">重置等级</h3>
        <p class="text-sm text-gray-500 mb-4 truncate">{{ resetTarget.question }}</p>
        <div class="flex gap-2 mb-4 flex-wrap">
          <button v-for="lv in [1,2,3,4,5,6,7]" :key="lv"
            @click="resetLevel = lv"
            :class="['w-10 h-10 rounded-lg font-bold text-sm transition-colors',
              resetLevel === lv ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']">
            {{ lv }}
          </button>
        </div>
        <div class="flex gap-3">
          <button @click="resetTarget = null" class="flex-1 py-2 rounded-lg border text-sm hover:bg-gray-50">取消</button>
          <button @click="doReset" class="flex-1 py-2 rounded-lg bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700">确认重置</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getAllItems, resetCard } from '../api'
import type { ReviewItem } from '../types'
import LevelBadge from '../components/LevelBadge.vue'

const items = ref<ReviewItem[]>([])
const loading = ref(true)
const categoryFilter = ref('')
const typeFilter = ref('')
const resetTarget = ref<ReviewItem | null>(null)
const resetLevel = ref(1)

const filtered = computed(() => items.value.filter(i => {
  if (categoryFilter.value && !i.category.includes(categoryFilter.value)) return false
  if (typeFilter.value && i.content_type !== typeFilter.value) return false
  return true
}))

const stats = computed(() => {
  const all = items.value
  const overdue = all.filter(i => i.is_overdue).length
  const mastered = all.filter(i => i.current_level === 7).length
  return [
    { label: '总卡片', value: all.length, color: 'text-gray-700' },
    { label: '待复习', value: all.filter(i => !i.next_review_time || i.is_overdue).length, color: 'text-indigo-600' },
    { label: '已过期', value: overdue, color: 'text-red-500' },
    { label: 'Lv7 掌握', value: mastered, color: 'text-green-600' },
  ]
})

function typeLabel(t: string) {
  return { memory: '记忆', word: '单词', single_choice: '单选', multiple_choice: '多选' }[t] ?? t
}
function typeClass(t: string) {
  return { memory: 'bg-purple-50 text-purple-600', word: 'bg-blue-50 text-blue-600', single_choice: 'bg-orange-50 text-orange-600', multiple_choice: 'bg-pink-50 text-pink-600' }[t] ?? 'bg-gray-100 text-gray-500'
}
function overdueClass(item: ReviewItem) {
  if (item.is_severely_overdue) return 'text-red-600 font-medium'
  if (item.is_overdue) return 'text-orange-500'
  return 'text-gray-400'
}
function fmtNextReview(item: ReviewItem) {
  if (!item.next_review_time) return '待首次复习'
  const h = item.hours_until_review ?? 0
  if (h < 0) return `过期 ${Math.abs(Math.round(h))}h`
  if (h < 1) return `${Math.round(h * 60)}分钟后`
  if (h < 24) return `${Math.round(h)}小时后`
  return `${Math.round(h / 24)}天后`
}

function openReset(item: ReviewItem) {
  resetTarget.value = item
  resetLevel.value = item.current_level
}
async function doReset() {
  if (!resetTarget.value) return
  await resetCard(resetTarget.value.PC_ID, resetLevel.value)
  resetTarget.value = null
  await load()
}

async function load() {
  loading.value = true
  items.value = await getAllItems()
  loading.value = false
}

onMounted(load)
</script>

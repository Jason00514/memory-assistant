<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold">卡片库</h1>
      <button @click="load" class="border rounded px-3 py-1 text-sm hover:bg-gray-50">刷新</button>
    </div>

    <!-- フィルターエリア -->
    <div class="bg-white rounded-2xl border p-4 mb-4 flex flex-wrap gap-3 items-center">
      <!-- カテゴリ -->
      <select v-model="catFilter" @change="applyFilter"
        class="border rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none">
        <option value="">全部分类</option>
        <option v-for="c in allCategories" :key="c" :value="c">{{ c }}</option>
      </select>

      <!-- タグ -->
      <select v-model="tagFilter" @change="applyFilter"
        class="border rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none">
        <option value="">全部标签</option>
        <option v-for="t in allTags" :key="t" :value="t">{{ t }}</option>
      </select>

      <!-- 状態フィルターボタン -->
      <div class="flex gap-2">
        <button v-for="btn in statusBtns" :key="btn.value"
          @click="statusFilter = btn.value; applyFilter()"
          :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition-colors border',
            statusFilter === btn.value ? btn.activeClass : 'bg-white text-gray-500 hover:bg-gray-50']">
          {{ btn.label }}
        </button>
      </div>
    </div>

    <!-- 統計バー -->
    <div class="grid grid-cols-4 gap-3 mb-5">
      <div v-for="s in stats" :key="s.label" class="bg-white rounded-xl border px-4 py-3 text-center shadow-sm">
        <div class="text-2xl font-bold" :class="s.color">{{ s.value }}</div>
        <div class="text-xs text-gray-400 mt-0.5">{{ s.label }}</div>
      </div>
    </div>

    <!-- ローディング -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-7 h-7 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- テーブル -->
    <div v-else class="bg-white rounded-2xl border overflow-hidden shadow-sm">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            <th class="text-left px-4 py-3">问题</th>
            <th class="text-left px-4 py-3 w-28">分类/标签</th>
            <th class="text-left px-4 py-3 w-16">类型</th>
            <th class="text-center px-4 py-3 w-14">等级</th>
            <th class="text-left px-4 py-3 w-28">下次复习</th>
            <th class="text-center px-4 py-3 w-24">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="item in filtered" :key="item.PC_ID"
            class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 max-w-xs">
              <div class="truncate text-gray-800">{{ item.question }}</div>
              <div v-if="item.answer !== 'NONE'" class="text-xs text-gray-400 truncate mt-0.5">{{ item.answer }}</div>
            </td>
            <td class="px-4 py-3">
              <div class="text-xs text-gray-500">{{ item.category }}</div>
              <!-- タグ表示 -->
              <div class="flex flex-wrap gap-1 mt-1">
                <span v-for="t in (item.tags ?? [])" :key="t"
                  class="text-xs bg-indigo-50 text-indigo-500 px-1.5 py-0.5 rounded-full">{{ t }}</span>
              </div>
            </td>
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
            <td class="px-4 py-3 text-center flex gap-2 justify-center">
              <button @click="openTagEdit(item)" class="text-xs text-indigo-400 hover:text-indigo-700 underline">标签</button>
              <button @click="openReset(item)" class="text-xs text-gray-400 hover:text-gray-700 underline">重置</button>
            </td>
          </tr>
          <tr v-if="filtered.length === 0">
            <td colspan="6" class="text-center py-12 text-gray-400">没有符合条件的卡片</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ========== タグ編集モーダル ========== -->
    <div v-if="tagTarget" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-96 shadow-xl">
        <h3 class="font-bold text-lg mb-1">编辑标签</h3>
        <p class="text-xs text-gray-400 mb-4 truncate">{{ tagTarget.question }}</p>

        <!-- 既存タグ -->
        <div class="flex flex-wrap gap-2 mb-3 min-h-8">
          <span v-for="t in editTags" :key="t"
            class="inline-flex items-center gap-1 bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full text-sm">
            {{ t }}
            <button @click="removeTag(t)" class="text-indigo-400 hover:text-red-500 font-bold leading-none">×</button>
          </span>
          <span v-if="editTags.length === 0" class="text-xs text-gray-400">还没有标签</span>
        </div>

        <!-- 既存タグから選択 -->
        <div v-if="allTags.length" class="flex flex-wrap gap-1.5 mb-3">
          <button v-for="t in allTags" :key="t"
            @click="addExistingTag(t)"
            :disabled="editTags.includes(t)"
            :class="['text-xs px-2 py-1 rounded-full border transition-colors',
              editTags.includes(t) ? 'bg-indigo-100 text-indigo-400 border-indigo-200 cursor-default' : 'border-gray-300 hover:bg-indigo-50 hover:text-indigo-600']">
            + {{ t }}
          </button>
        </div>

        <!-- 新規タグ入力 -->
        <div class="flex gap-2 mb-4">
          <input v-model="newTag" @keyup.enter="addNewTag" placeholder="输入新标签后回车"
            class="flex-1 border rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
          <button @click="addNewTag" class="px-3 py-1.5 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700">添加</button>
        </div>

        <div class="flex gap-3">
          <button @click="tagTarget = null" class="flex-1 py-2 rounded-lg border text-sm hover:bg-gray-50">取消</button>
          <button @click="saveTagEdit" class="flex-1 py-2 rounded-lg bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700">保存</button>
        </div>
      </div>
    </div>

    <!-- ========== レベルリセットモーダル ========== -->
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
import { getAllItems, resetCard, getAllTags, updateCardTags } from '../api'
import type { ReviewItem } from '../types'
import LevelBadge from '../components/LevelBadge.vue'

const allItems = ref<ReviewItem[]>([])
const filtered = ref<ReviewItem[]>([])
const loading = ref(true)
const catFilter = ref('')
const tagFilter = ref('')
const statusFilter = ref('')
const allTags = ref<string[]>([])
const allCategories = computed(() => [...new Set(allItems.value.map(i => i.category))].sort())

// リセットモーダル
const resetTarget = ref<ReviewItem | null>(null)
const resetLevel = ref(1)

// タグ編集モーダル
const tagTarget = ref<ReviewItem | null>(null)
const editTags = ref<string[]>([])
const newTag = ref('')

const statusBtns = [
  { label: '全部', value: '', activeClass: 'bg-gray-800 text-white border-gray-800' },
  { label: '待复习', value: 'due', activeClass: 'bg-indigo-600 text-white border-indigo-600' },
  { label: '已过期', value: 'overdue', activeClass: 'bg-red-500 text-white border-red-500' },
]

const stats = computed(() => {
  const now = new Date()
  const f = filtered.value
  return [
    { label: '显示中', value: f.length, color: 'text-gray-700' },
    { label: '待复习', value: f.filter(i => !i.next_review_time || i.is_overdue).length, color: 'text-indigo-600' },
    { label: '已过期', value: f.filter(i => i.is_overdue).length, color: 'text-red-500' },
    { label: 'Lv7掌握', value: f.filter(i => i.current_level === 7).length, color: 'text-green-600' },
  ]
})

function typeLabel(t: string) {
  return { memory:'记忆', word:'单词', single_choice:'单选', multiple_choice:'多选' }[t] ?? t
}
function typeClass(t: string) {
  return { memory:'bg-purple-50 text-purple-600', word:'bg-blue-50 text-blue-600', single_choice:'bg-orange-50 text-orange-600', multiple_choice:'bg-pink-50 text-pink-600' }[t] ?? 'bg-gray-100 text-gray-500'
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
  if (h < 1) return `${Math.round(h * 60)}分后`
  if (h < 24) return `${Math.round(h)}小时后`
  return `${Math.round(h / 24)}天后`
}

function applyFilter() {
  filtered.value = allItems.value.filter(item => {
    if (catFilter.value && item.category !== catFilter.value) return false
    if (tagFilter.value && !(item.tags ?? []).includes(tagFilter.value)) return false
    if (statusFilter.value === 'due' && item.next_review_time && !item.is_overdue) return false
    if (statusFilter.value === 'overdue' && !item.is_overdue) return false
    return true
  })
}

// ---- タグ編集 ----
function openTagEdit(item: ReviewItem) {
  tagTarget.value = item
  editTags.value = [...(item.tags ?? [])]
  newTag.value = ''
}
function addExistingTag(t: string) {
  if (!editTags.value.includes(t)) editTags.value.push(t)
}
function addNewTag() {
  const t = newTag.value.trim()
  if (t && !editTags.value.includes(t)) editTags.value.push(t)
  newTag.value = ''
}
function removeTag(t: string) {
  editTags.value = editTags.value.filter(x => x !== t)
}
async function saveTagEdit() {
  if (!tagTarget.value) return
  await updateCardTags(tagTarget.value.PC_ID, editTags.value)
  tagTarget.value = null
  await load()
}

// ---- リセット ----
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
  allItems.value = await getAllItems()
  allTags.value = await getAllTags()
  applyFilter()
  loading.value = false
}

onMounted(load)
</script>

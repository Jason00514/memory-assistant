<template>
  <div>
    <div class="flex items-center justify-between mb-5">
      <h1 class="text-xl font-bold">学习一览</h1>
      <button @click="load" class="text-sm border rounded px-3 py-1 hover:bg-gray-50">刷新</button>
    </div>

    <!-- 合計統計 -->
    <div class="grid grid-cols-4 gap-3 mb-6">
      <div v-for="s in totals" :key="s.label"
        class="bg-white rounded-2xl border px-4 py-4 text-center shadow-sm">
        <div class="text-3xl font-bold" :class="s.color">{{ s.value }}</div>
        <div class="text-xs text-gray-400 mt-1">{{ s.label }}</div>
      </div>
    </div>

    <!-- ローディング -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="w-7 h-7 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- カテゴリ別テーブル -->
    <div v-else class="bg-white rounded-2xl border overflow-hidden shadow-sm">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
          <tr>
            <th class="text-left px-5 py-3">分类</th>
            <th class="text-center px-4 py-3">总数</th>
            <th class="text-center px-4 py-3">
              <span class="text-indigo-600">待复习</span>
            </th>
            <th class="text-center px-4 py-3">
              <span class="text-red-500">已过期</span>
            </th>
            <th class="text-center px-4 py-3">
              <span class="text-green-600">Lv7掌握</span>
            </th>
            <th class="text-center px-4 py-3">进度</th>
            <th class="text-center px-4 py-3">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-if="stats.length === 0">
            <td colspan="7" class="text-center py-12 text-gray-400">
              暂无数据。请先<RouterLink to="/import" class="text-indigo-500 underline">导入内容</RouterLink>
            </td>
          </tr>
          <tr v-for="s in stats" :key="s.category"
            class="hover:bg-gray-50 transition-colors">
            <td class="px-5 py-3 font-medium text-gray-800">{{ s.category }}</td>
            <td class="px-4 py-3 text-center text-gray-600">{{ s.total }}</td>
            <td class="px-4 py-3 text-center">
              <span :class="s.due > 0 ? 'text-indigo-600 font-bold' : 'text-gray-400'">
                {{ s.due }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <span :class="s.overdue > 0 ? 'text-red-500 font-bold' : 'text-gray-400'">
                {{ s.overdue }}
              </span>
            </td>
            <td class="px-4 py-3 text-center">
              <span :class="s.mastered > 0 ? 'text-green-600 font-semibold' : 'text-gray-400'">
                {{ s.mastered }}
              </span>
            </td>
            <!-- 進捗バー -->
            <td class="px-4 py-3 w-32">
              <div class="flex items-center gap-2">
                <div class="flex-1 bg-gray-100 rounded-full h-2">
                  <div class="bg-green-500 h-2 rounded-full transition-all"
                    :style="{ width: s.total ? (s.mastered / s.total * 100) + '%' : '0%' }"></div>
                </div>
                <span class="text-xs text-gray-400 whitespace-nowrap">
                  {{ s.total ? Math.round(s.mastered / s.total * 100) : 0 }}%
                </span>
              </div>
            </td>
            <td class="px-4 py-3 text-center">
              <!-- このカテゴリの復習へジャンプ -->
              <RouterLink
                :to="`/review?category=${encodeURIComponent(s.category)}`"
                class="text-xs text-indigo-500 hover:underline font-medium">
                去复习 →
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getDashboardStats } from '../api'
import type { CategoryStat } from '../types'

const stats = ref<CategoryStat[]>([])
const loading = ref(true)

const totals = computed(() => {
  const all = stats.value
  return [
    { label: '总卡片',  value: all.reduce((s, c) => s + c.total, 0),    color: 'text-gray-700' },
    { label: '待复习',  value: all.reduce((s, c) => s + c.due, 0),      color: 'text-indigo-600' },
    { label: '已过期',  value: all.reduce((s, c) => s + c.overdue, 0),  color: 'text-red-500' },
    { label: 'Lv7掌握', value: all.reduce((s, c) => s + c.mastered, 0), color: 'text-green-600' },
  ]
})

async function load() {
  loading.value = true
  stats.value = await getDashboardStats()
  loading.value = false
}

onMounted(load)
</script>

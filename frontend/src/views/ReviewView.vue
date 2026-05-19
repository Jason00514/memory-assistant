<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-bold">今日复习</h1>
      <div class="flex gap-2 items-center">
        <input v-model="categoryFilter" @keyup.enter="load" placeholder="按分类筛选"
          class="border rounded px-2 py-1 text-sm w-36 focus:outline-none focus:ring-2 focus:ring-indigo-400" />
        <button @click="load" class="btn-secondary text-sm">刷新</button>
      </div>
    </div>

    <!-- Empty -->
    <div v-if="!loading && items.length === 0"
      class="flex flex-col items-center justify-center py-24 text-gray-400">
      <div class="text-5xl mb-4">🎉</div>
      <p class="text-lg font-medium">今天没有待复习的内容</p>
      <p class="text-sm mt-1">去<RouterLink to="/import" class="text-indigo-500 underline">导入</RouterLink>更多内容吧</p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="flex justify-center py-24">
      <div class="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- Card -->
    <div v-else>
      <!-- Progress -->
      <div class="flex items-center gap-3 mb-4 text-sm text-gray-500">
        <span>{{ doneCount }} / {{ totalCount }} 已完成</span>
        <div class="flex-1 bg-gray-200 rounded-full h-2">
          <div class="bg-indigo-500 h-2 rounded-full transition-all"
            :style="{ width: totalCount ? (doneCount / totalCount * 100) + '%' : '0%' }"></div>
        </div>
      </div>

      <!-- Flash card -->
      <div class="card-flip w-full" style="min-height:320px">
        <div class="card-inner rounded-2xl shadow-lg bg-white" :class="{ flipped: showAnswer }"
          style="min-height:320px">

          <!-- Front -->
          <div class="card-front p-8 flex flex-col justify-between" style="min-height:320px">
            <div class="flex items-start justify-between gap-2">
              <span class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">
                {{ current.category }} · {{ typeLabel(current.content_type) }}
              </span>
              <LevelBadge :level="current.current_level" />
            </div>

            <!-- Question -->
            <div class="flex-1 flex items-center justify-center py-6">
              <pre class="text-lg font-medium text-center whitespace-pre-wrap leading-relaxed">{{ current.question }}</pre>
            </div>

            <!-- Choice options (show on front for choice types) -->
            <div v-if="isChoice && current.extra?.options" class="grid grid-cols-1 gap-2 mb-4">
              <button v-for="opt in current.extra.options" :key="opt"
                :class="['text-left px-4 py-2 rounded-lg border text-sm transition-colors',
                  selectedOption === opt
                    ? (showAnswer ? (isCorrectOption(opt) ? 'bg-green-100 border-green-400 text-green-800' : 'bg-red-100 border-red-400 text-red-800') : 'bg-indigo-100 border-indigo-400')
                    : (showAnswer && isCorrectOption(opt) ? 'bg-green-50 border-green-300 text-green-700' : 'bg-gray-50 border-gray-200 hover:bg-gray-100')]"
                :disabled="showAnswer"
                @click="selectOption(opt)">
                {{ opt }}
              </button>
            </div>

            <div class="flex justify-center">
              <button v-if="!showAnswer" @click="showAnswer = true"
                class="btn-primary px-8">翻转查看答案</button>
            </div>
          </div>

          <!-- Back -->
          <div class="card-back p-8 flex flex-col justify-between bg-white rounded-2xl" style="min-height:320px">
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-indigo-600">答案</span>
              <LevelBadge :level="current.current_level" />
            </div>

            <div class="flex-1 flex flex-col items-center justify-center py-4 gap-3">
              <div class="text-2xl font-bold text-indigo-700 text-center whitespace-pre-wrap">{{ current.answer }}</div>
              <div v-if="current.extra?.explanation" class="text-sm text-gray-500 bg-gray-50 rounded-lg px-4 py-2 text-center">
                {{ current.extra.explanation }}
              </div>
            </div>

            <!-- Result buttons -->
            <div class="flex gap-4 justify-center">
              <button @click="submit(false)"
                class="flex-1 max-w-[160px] py-3 rounded-xl bg-red-100 text-red-700 font-semibold hover:bg-red-200 transition-colors">
                ✗ 答错了
              </button>
              <button @click="submit(true)"
                class="flex-1 max-w-[160px] py-3 rounded-xl bg-green-100 text-green-700 font-semibold hover:bg-green-200 transition-colors">
                ✓ 答对了
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Result toast -->
      <Transition name="fade">
        <div v-if="lastResult" :class="[
          'mt-4 rounded-xl px-4 py-3 text-sm font-medium text-center',
          lastResult.new_level > lastResult.old_level ? 'bg-green-50 text-green-700' :
          lastResult.new_level < lastResult.old_level ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700'
        ]">
          {{ resultMsg }}
        </div>
      </Transition>

      <!-- Skip / queue info -->
      <div class="mt-4 flex justify-between items-center text-sm text-gray-400">
        <span>剩余 {{ items.length }} 题</span>
        <button @click="skip" class="underline hover:text-gray-600">跳过</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getDueItems, submitAnswer } from '../api'
import type { ReviewItem, ReviewResult } from '../types'
import LevelBadge from '../components/LevelBadge.vue'

const items = ref<ReviewItem[]>([])
const loading = ref(true)
const showAnswer = ref(false)
const categoryFilter = ref('')
const lastResult = ref<ReviewResult | null>(null)
const selectedOption = ref<string | null>(null)
const doneCount = ref(0)
const totalCount = ref(0)

const current = computed(() => items.value[0])
const isChoice = computed(() =>
  current.value?.content_type === 'single_choice' || current.value?.content_type === 'multiple_choice'
)

function typeLabel(t: string) {
  return { memory: '记忆', word: '单词', single_choice: '单选', multiple_choice: '多选' }[t] ?? t
}

function isCorrectOption(opt: string): boolean {
  const letter = opt.match(/^([A-E])/)?.[1]
  return !!letter && !!current.value?.extra?.correct_answers?.includes(letter)
}

function selectOption(opt: string) {
  selectedOption.value = opt
  showAnswer.value = true
}

const resultMsg = computed(() => {
  if (!lastResult.value) return ''
  const r = lastResult.value
  if (r.new_level > r.old_level) return `⬆️ 升级！Lv${r.old_level} → Lv${r.new_level}，下次复习：${fmtTime(r.next_review_time)}`
  if (r.new_level < r.old_level) return `⬇️ 降级 Lv${r.old_level} → Lv${r.new_level}，加油！下次 ${fmtTime(r.next_review_time)}`
  return `➡️ 等级不变 Lv${r.new_level}，下次复习：${fmtTime(r.next_review_time)}`
})

function fmtTime(iso: string) {
  const d = new Date(iso)
  const now = new Date()
  const diff = (d.getTime() - now.getTime()) / 3600000
  if (diff < 1) return `${Math.round(diff * 60)} 分钟后`
  if (diff < 24) return `${Math.round(diff)} 小时后`
  return `${Math.round(diff / 24)} 天后`
}

async function load() {
  loading.value = true
  lastResult.value = null
  items.value = await getDueItems(categoryFilter.value || undefined)
  totalCount.value = items.value.length
  doneCount.value = 0
  loading.value = false
}

async function submit(correct: boolean) {
  if (!current.value) return
  const result = await submitAnswer(current.value.PC_ID, correct)
  lastResult.value = result
  doneCount.value++
  setTimeout(() => {
    items.value.shift()
    showAnswer.value = false
    selectedOption.value = null
    if (items.value.length === 0) lastResult.value = null
  }, 1200)
}

function skip() {
  const first = items.value.shift()
  if (first) items.value.push(first)
  showAnswer.value = false
  selectedOption.value = null
  lastResult.value = null
}

onMounted(load)
</script>

<style scoped>
.btn-primary {
  @apply bg-indigo-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors;
}
.btn-secondary {
  @apply bg-white border border-gray-300 text-gray-700 font-medium py-1 px-3 rounded-lg hover:bg-gray-50 transition-colors;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

<template>
  <div>
    <!-- フィルターバー -->
    <div class="flex flex-wrap items-center gap-2 mb-4">
      <h1 class="text-xl font-bold mr-2">复习</h1>

      <!-- カテゴリ絞り込み -->
      <select v-model="categoryFilter" @change="load"
        class="border rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-indigo-400 focus:outline-none">
        <option value="">全部分类</option>
        <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
      </select>

      <!-- 答え表示モード切替 -->
      <div class="ml-auto flex items-center gap-1 bg-gray-100 rounded-lg p-1">
        <button
          @click="answerMode = 'flip'"
          :class="['px-3 py-1 rounded-md text-xs font-medium transition-colors',
            answerMode === 'flip' ? 'bg-white shadow text-indigo-700' : 'text-gray-500 hover:text-gray-700']">
          🔄 翻转
        </button>
        <button
          @click="answerMode = 'below'"
          :class="['px-3 py-1 rounded-md text-xs font-medium transition-colors',
            answerMode === 'below' ? 'bg-white shadow text-indigo-700' : 'text-gray-500 hover:text-gray-700']">
          📋 下方显示
        </button>
      </div>

      <button @click="load" class="border rounded px-3 py-1.5 text-sm hover:bg-gray-50">刷新</button>
    </div>

    <!-- 空状態 -->
    <div v-if="!loading && items.length === 0"
      class="flex flex-col items-center justify-center py-24 text-gray-400">
      <div class="text-5xl mb-4">🎉</div>
      <p class="text-lg font-medium">没有待复习的内容</p>
      <p class="text-sm mt-1">
        <RouterLink to="/import" class="text-indigo-500 underline">导入内容</RouterLink>
        或换个分类试试
      </p>
    </div>

    <!-- ローディング -->
    <div v-else-if="loading" class="flex justify-center py-24">
      <div class="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else>
      <!-- 進捗バー -->
      <div class="flex items-center gap-3 mb-4 text-sm text-gray-500">
        <span>{{ doneCount }} / {{ totalCount }} 完成</span>
        <div class="flex-1 bg-gray-200 rounded-full h-2">
          <div class="bg-indigo-500 h-2 rounded-full transition-all"
            :style="{ width: totalCount ? (doneCount / totalCount * 100) + '%' : '0%' }"></div>
        </div>
        <span class="text-xs">剩余 {{ items.length }}</span>
      </div>

      <!-- ========== 翻転モード ========== -->
      <template v-if="answerMode === 'flip'">
        <div class="card-flip w-full" style="min-height:320px">
          <div class="card-inner rounded-2xl shadow-lg bg-white" :class="{ flipped: showAnswer }"
            style="min-height:320px">

            <!-- 表面（問題） -->
            <div class="card-front p-8 flex flex-col justify-between" style="min-height:320px">
              <CardHeader :item="current" />
              <QuestionBody :item="current" :show-answer="showAnswer" @select="selectOption" />
              <div class="flex justify-center mt-4">
                <button v-if="!showAnswer" @click="showAnswer = true"
                  class="btn-primary px-8">翻转查看答案</button>
              </div>
            </div>

            <!-- 裏面（答え） -->
            <div class="card-back p-8 flex flex-col justify-between bg-white rounded-2xl"
              style="min-height:320px">
              <div class="flex items-center justify-between">
                <span class="text-sm font-semibold text-indigo-600">答案</span>
                <LevelBadge :level="current.current_level" />
              </div>
              <AnswerBody :item="current" />
              <AnswerButtons @correct="submit(true)" @wrong="submit(false)" />
            </div>
          </div>
        </div>
      </template>

      <!-- ========== 下方表示モード ========== -->
      <template v-else>
        <div class="bg-white rounded-2xl shadow-lg p-8" style="min-height:200px">
          <CardHeader :item="current" />
          <QuestionBody :item="current" :show-answer="showAnswer" @select="selectOption" class="my-6" />
          <button v-if="!showAnswer" @click="showAnswer = true"
            class="btn-secondary w-full">显示答案</button>
          <div v-else>
            <hr class="my-4 border-dashed border-gray-200" />
            <AnswerBody :item="current" />
            <AnswerButtons class="mt-4" @correct="submit(true)" @wrong="submit(false)" />
          </div>
        </div>
      </template>

      <!-- 結果トースト -->
      <Transition name="fade">
        <div v-if="lastResult" :class="[
          'mt-4 rounded-xl px-4 py-3 text-sm font-medium text-center',
          lastResult.new_level > lastResult.old_level ? 'bg-green-50 text-green-700' :
          lastResult.new_level < lastResult.old_level ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700',
        ]">{{ resultMsg }}</div>
      </Transition>

      <div class="mt-4 text-right">
        <button @click="skip" class="text-sm text-gray-400 underline hover:text-gray-600">跳过</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getDueItems, submitAnswer, getAllTags } from '../api'
import type { ReviewItem, ReviewResult } from '../types'
import LevelBadge from '../components/LevelBadge.vue'

// ---- サブコンポーネント（インライン定義）----
import { defineComponent, h } from 'vue'

const CardHeader = defineComponent({
  props: { item: Object as () => ReviewItem },
  setup(props) {
    return () => h('div', { class: 'flex items-start justify-between gap-2 mb-2' }, [
      h('div', { class: 'flex flex-wrap gap-1' }, [
        h('span', { class: 'text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full' },
          `${props.item!.category} · ${{ memory:'记忆', word:'单词', single_choice:'单选', multiple_choice:'多选' }[props.item!.content_type] ?? props.item!.content_type}`
        ),
        ...(props.item!.tags ?? []).map((t: string) =>
          h('span', { class: 'text-xs bg-indigo-50 text-indigo-500 px-2 py-0.5 rounded-full' }, t)
        ),
      ]),
      h('span', { class: `inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${['','bg-red-100 text-red-700','bg-orange-100 text-orange-700','bg-yellow-100 text-yellow-700','bg-lime-100 text-lime-700','bg-green-100 text-green-700','bg-teal-100 text-teal-700','bg-indigo-100 text-indigo-700'][props.item!.current_level]}` },
        `Lv${props.item!.current_level}`
      ),
    ])
  },
})

const AnswerBody = defineComponent({
  props: { item: Object as () => ReviewItem },
  setup(props) {
    return () => h('div', { class: 'flex flex-col items-center gap-3 py-4' }, [
      h('div', { class: 'text-2xl font-bold text-indigo-700 text-center whitespace-pre-wrap' }, props.item!.answer),
      props.item!.extra?.explanation
        ? h('div', { class: 'text-sm text-gray-500 bg-gray-50 rounded-lg px-4 py-2 text-center' }, props.item!.extra!.explanation)
        : null,
    ])
  },
})

const AnswerButtons = defineComponent({
  emits: ['correct', 'wrong'],
  setup(_, { emit }) {
    return () => h('div', { class: 'flex gap-4 justify-center' }, [
      h('button', { onClick: () => emit('wrong'),   class: 'flex-1 max-w-[160px] py-3 rounded-xl bg-red-100 text-red-700 font-semibold hover:bg-red-200' }, '✗ 答错了'),
      h('button', { onClick: () => emit('correct'), class: 'flex-1 max-w-[160px] py-3 rounded-xl bg-green-100 text-green-700 font-semibold hover:bg-green-200' }, '✓ 答对了'),
    ])
  },
})

const QuestionBody = defineComponent({
  props: { item: Object as () => ReviewItem, showAnswer: Boolean },
  emits: ['select'],
  setup(props, { emit }) {
    return () => {
      const isChoice = ['single_choice', 'multiple_choice'].includes(props.item!.content_type)
      return h('div', { class: 'flex-1 flex flex-col items-center justify-center py-4 gap-4' }, [
        h('pre', { class: 'text-lg font-medium text-center whitespace-pre-wrap leading-relaxed' }, props.item!.question),
        isChoice && props.item!.extra?.options
          ? h('div', { class: 'grid grid-cols-1 gap-2 w-full' },
            props.item!.extra!.options!.map((opt: string) => {
              const letter = opt.match(/^([A-E])/)?.[1] ?? ''
              const isCorrect = props.item!.extra?.correct_answers?.includes(letter)
              return h('button', {
                class: ['text-left px-4 py-2 rounded-lg border text-sm transition-colors',
                  props.showAnswer
                    ? (isCorrect ? 'bg-green-50 border-green-400 text-green-800' : 'bg-gray-50 border-gray-200 text-gray-400')
                    : 'bg-gray-50 border-gray-200 hover:bg-indigo-50 hover:border-indigo-300'].join(' '),
                disabled: props.showAnswer,
                onClick: () => { if (!props.showAnswer) emit('select', opt) },
              }, opt)
            })
          )
          : null,
      ])
    }
  },
})
// ---- ここまでサブコンポーネント ----

const route = useRoute()
const items = ref<ReviewItem[]>([])
const loading = ref(true)
const showAnswer = ref(false)
const answerMode = ref<'flip' | 'below'>('flip')   // 答え表示モード
const categoryFilter = ref('')
const categories = ref<string[]>([])
const lastResult = ref<ReviewResult | null>(null)
const doneCount = ref(0)
const totalCount = ref(0)

const current = computed(() => items.value[0])

const resultMsg = computed(() => {
  if (!lastResult.value) return ''
  const r = lastResult.value
  const next = fmtTime(r.next_review_time)
  if (r.new_level > r.old_level) return `⬆️ 升级！Lv${r.old_level} → Lv${r.new_level}，下次：${next}`
  if (r.new_level < r.old_level) return `⬇️ 降级 Lv${r.old_level} → Lv${r.new_level}，加油！${next}`
  return `➡️ 等级不变 Lv${r.new_level}，下次：${next}`
})

function fmtTime(iso: string) {
  const h = (new Date(iso).getTime() - Date.now()) / 3600000
  if (Math.abs(h) < 1) return `${Math.round(Math.abs(h) * 60)}分钟后`
  if (Math.abs(h) < 24) return `${Math.round(Math.abs(h))}小时后`
  return `${Math.round(Math.abs(h) / 24)}天后`
}

function selectOption(_opt: string) {
  showAnswer.value = true
}

async function load() {
  loading.value = true
  lastResult.value = null
  items.value = await getDueItems({ category: categoryFilter.value || undefined })
  totalCount.value = items.value.length
  doneCount.value = 0
  loading.value = false

  // カテゴリ一覧をユニーク抽出（フィルター用）
  const all = await getDueItems()
  categories.value = [...new Set(all.map(i => i.category))].sort()
}

async function submit(correct: boolean) {
  if (!current.value) return
  const result = await submitAnswer(current.value.PC_ID, correct)
  lastResult.value = result
  doneCount.value++
  setTimeout(() => {
    items.value.shift()
    showAnswer.value = false
    if (items.value.length === 0) lastResult.value = null
  }, 1200)
}

function skip() {
  const first = items.value.shift()
  if (first) items.value.push(first)
  showAnswer.value = false
  lastResult.value = null
}

// URL クエリパラメータからカテゴリを初期設定（Dashboard からのジャンプ対応）
watch(() => route.query.category, (cat) => {
  if (cat && typeof cat === 'string') categoryFilter.value = cat
}, { immediate: true })

onMounted(load)
</script>

<style scoped>
.btn-primary  { @apply bg-indigo-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors; }
.btn-secondary { @apply w-full py-2.5 rounded-xl border border-indigo-300 text-indigo-600 font-semibold hover:bg-indigo-50 transition-colors; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

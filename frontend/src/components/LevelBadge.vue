<template>
  <span :class="cls" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold">
    Lv{{ level }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ level: number }>()
const cls = computed(() => {
  const map: Record<number, string> = {
    1: 'bg-red-100 text-red-700',
    2: 'bg-orange-100 text-orange-700',
    3: 'bg-yellow-100 text-yellow-700',
    4: 'bg-lime-100 text-lime-700',
    5: 'bg-green-100 text-green-700',
    6: 'bg-teal-100 text-teal-700',
    7: 'bg-indigo-100 text-indigo-700',
  }
  return map[props.level] ?? 'bg-gray-100 text-gray-600'
})
</script>

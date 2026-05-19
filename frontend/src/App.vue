<template>
  <div class="min-h-screen flex flex-col">
    <!-- ナビゲーションバー -->
    <nav class="bg-indigo-700 text-white shadow-md">
      <div class="max-w-5xl mx-auto px-4 flex items-center h-14 gap-1">
        <span class="font-bold text-lg mr-5 tracking-wide">🧠 记忆助手</span>
        <RouterLink
          v-for="link in links" :key="link.to"
          :to="link.to"
          class="px-3 py-1.5 rounded text-sm font-medium transition-colors hover:bg-indigo-600"
          active-class="bg-indigo-900"
        >{{ link.label }}</RouterLink>
      </div>
    </nav>

    <!-- ページコンテンツ -->
    <main class="flex-1 max-w-5xl mx-auto w-full px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
const links = [
  { to: '/dashboard', label: '📊 一览' },
  { to: '/review',    label: '📖 复习' },
  { to: '/import',    label: '📥 导入' },
  { to: '/cards',     label: '🗂️ 卡片库' },
  { to: '/curves',    label: '📈 记忆曲线' },
]
</script>

import { createRouter, createWebHistory } from 'vue-router'
import ReviewView from '../views/ReviewView.vue'
import ImportView from '../views/ImportView.vue'
import CardsView from '../views/CardsView.vue'
import CurvesView from '../views/CurvesView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/review' },
    { path: '/review', component: ReviewView, meta: { title: '复习' } },
    { path: '/import', component: ImportView, meta: { title: '导入' } },
    { path: '/cards', component: CardsView, meta: { title: '卡片库' } },
    { path: '/curves', component: CurvesView, meta: { title: '记忆曲线' } },
  ]
})

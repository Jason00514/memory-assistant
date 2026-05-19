import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import ReviewView from '../views/ReviewView.vue'
import ImportView from '../views/ImportView.vue'
import CardsView from '../views/CardsView.vue'
import CurvesView from '../views/CurvesView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', component: DashboardView, meta: { title: '一覧' } },
    { path: '/review',    component: ReviewView,    meta: { title: '復習' } },
    { path: '/import',    component: ImportView,    meta: { title: 'インポート' } },
    { path: '/cards',     component: CardsView,     meta: { title: 'カード库' } },
    { path: '/curves',    component: CurvesView,    meta: { title: '記憶カーブ' } },
  ],
})

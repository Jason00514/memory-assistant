/**
 * API 呼び出しを全て一元管理するファイル。
 * Vite の proxy 設定により /api/* → http://localhost:8001/* に転送される。
 */
import type {
  MemoryCurve, CurvePreview,
  RawContent, ImportResult, ProcessResult, ProcessedContent,
  ReviewItem, ReviewResult,
  CategoryStat,
} from '../types'

const BASE = '/api'

/** 共通 fetch ラッパー：エラー時は Error をスロー */
async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, options)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

// ===== 記憶カーブ =====

export const getCurves = () =>
  req<MemoryCurve[]>('/curves/')

export const createCurve = (data: Omit<MemoryCurve, 'curve_id' | 'created_at' | 'data_flag'>) =>
  req<MemoryCurve>('/curves/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

export const updateCurve = (id: string, data: Partial<MemoryCurve>) =>
  req<MemoryCurve>(`/curves/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

export const deleteCurve = (id: string) =>
  req<{ message: string }>(`/curves/${id}`, { method: 'DELETE' })

/** カーブのプレビュー（全正解時の復習スケジュール）を取得 */
export const getCurvePreview = (id: string) =>
  req<CurvePreview>(`/curves/${id}/preview`)

// ===== インポート =====

/** Excel ファイル（.xlsx）をアップロードして RawContent として保存 */
export const importExcel = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return req<ImportResult>('/import/excel', { method: 'POST', body: form })
}

/** テキストファイル（.txt）をアップロードして RawContent として保存 */
export const importText = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return req<ImportResult>('/import/text', { method: 'POST', body: form })
}

/** RawContent を解析して ProcessedContent（復習カード）を生成 */
export const processRaw = (curveId?: string) =>
  req<ProcessResult>('/import/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ curve_id: curveId ?? null }),
  })

export const getRawList = (category?: string) =>
  req<RawContent[]>('/import/raw' + (category ? `?category=${category}` : ''))

// ===== 復習 =====

/** 今日復習すべきカード（過期順）を取得 */
export const getDueItems = (params?: { category?: string; tag?: string }) => {
  const q = new URLSearchParams()
  if (params?.category) q.set('category', params.category)
  if (params?.tag) q.set('tag', params.tag)
  return req<ReviewItem[]>('/review/due' + (q.toString() ? '?' + q : ''))
}

/** 全カード一覧を取得（カード库画面用）*/
export const getAllItems = (params?: { category?: string; tag?: string; status?: string }) => {
  const q = new URLSearchParams()
  if (params?.category) q.set('category', params.category)
  if (params?.tag) q.set('tag', params.tag)
  if (params?.status) q.set('status', params.status)
  return req<ReviewItem[]>('/review/all' + (q.toString() ? '?' + q : ''))
}

/** 答え合わせ結果を送信し、レベル更新結果を受け取る */
export const submitAnswer = (pcId: string, isCorrect: boolean) =>
  req<ReviewResult>('/review/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ PC_ID: pcId, is_correct: isCorrect }),
  })

/** カードのレベルをリセットする */
export const resetCard = (pcId: string, level = 1) =>
  req<ProcessedContent>(`/review/reset/${pcId}?level=${level}`, { method: 'POST' })

// ===== カード管理 =====

/** DB に存在する全タグの一覧を取得 */
export const getAllTags = () =>
  req<string[]>('/cards/tags')

/** カードのタグを更新する */
export const updateCardTags = (pcId: string, tags: string[]) =>
  req<ProcessedContent>(`/cards/${pcId}/tags`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tags }),
  })

/** カードの記憶カーブを変更する */
export const updateCardCurve = (pcId: string, curveId: string) =>
  req<ProcessedContent>(`/cards/${pcId}/curve`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ curve_id: curveId }),
  })

// ===== Dashboard =====

/** カテゴリ別統計を取得 */
export const getDashboardStats = () =>
  req<CategoryStat[]>('/dashboard/stats')

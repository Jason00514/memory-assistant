import type { MemoryCurve, ReviewItem, ReviewResult, ImportResult, ProcessResult, ProcessedContent } from '../types'

const BASE = '/api'

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, options)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

// Curves
export const getCurves = () => req<MemoryCurve[]>('/curves/')
export const createCurve = (data: Omit<MemoryCurve, 'curve_id' | 'created_at' | 'data_flag'>) =>
  req<MemoryCurve>('/curves/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
export const updateCurve = (id: string, data: Partial<MemoryCurve>) =>
  req<MemoryCurve>(`/curves/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
export const deleteCurve = (id: string) =>
  req<{ message: string }>(`/curves/${id}`, { method: 'DELETE' })

// Import
export const importExcel = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return req<ImportResult>('/import/excel', { method: 'POST', body: form })
}
export const processRaw = (curveId?: string) =>
  req<ProcessResult>('/import/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ curve_id: curveId ?? null })
  })
export const getRawList = (category?: string) =>
  req<import('../types').RawContent[]>('/import/raw' + (category ? `?category=${category}` : ''))

// Review
export const getDueItems = (category?: string) =>
  req<ReviewItem[]>('/review/due' + (category ? `?category=${category}` : ''))
export const getAllItems = (category?: string) =>
  req<ReviewItem[]>('/review/all' + (category ? `?category=${category}` : ''))
export const submitAnswer = (pcId: string, isCorrect: boolean) =>
  req<ReviewResult>('/review/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ PC_ID: pcId, is_correct: isCorrect })
  })
export const resetCard = (pcId: string, level = 1) =>
  req<ProcessedContent>(`/review/reset/${pcId}?level=${level}`, { method: 'POST' })

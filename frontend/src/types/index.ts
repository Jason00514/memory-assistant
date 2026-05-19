export interface MemoryCurve {
  curve_id: string
  curve_name: string
  description: string | null
  intervals: number[]
  overdue_multiplier: number
  created_at: string
  data_flag: number
}

export interface RawContent {
  RC_ID: string
  category: string
  content_type: string
  raw_text: string
  source: string
  process_status: string
  data_flag: number
  imported_at: string
}

export interface ProcessedContent {
  PC_ID: string
  RC_ID: string
  content_type: string
  question: string
  answer: string
  extra: { options?: string[]; correct_answers?: string[]; explanation?: string } | null
  category: string
  usage_type: string | null
  curve_id: string | null
  current_level: number
  last_reviewed_at: string | null
  next_review_time: string | null
  process_version: number
  data_flag: number
  processed_at: string
}

export interface ReviewItem {
  PC_ID: string
  content_type: string
  question: string
  answer: string
  extra: { options?: string[]; correct_answers?: string[]; explanation?: string } | null
  category: string
  current_level: number
  next_review_time: string | null
  hours_until_review: number | null
  is_overdue: boolean
  is_severely_overdue: boolean
}

export interface ReviewResult {
  PC_ID: string
  old_level: number
  new_level: number
  next_review_time: string
  review_type: string
}

export interface ImportResult {
  total_imported: number
  failed: number
  items: RawContent[]
}

export interface ProcessResult {
  total_processed: number
  failed: number
  items: ProcessedContent[]
}

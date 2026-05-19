// ===== 記憶カーブ =====

export interface MemoryCurve {
  curve_id: string
  curve_name: string
  description: string | null
  intervals: number[]           // Level1-7 の復習間隔（時間単位）
  overdue_multiplier: number    // 深刻過期の判定倍率
  created_at: string
  data_flag: number
}

export interface CurvePreviewEntry {
  level: number
  hours_from_start: number
  review_date_label: string     // 例: "4時間後"
}

export interface CurvePreview {
  curve_id: string
  curve_name: string
  schedule: CurvePreviewEntry[]
  total_days: number
  total_reviews: number
}

// ===== インポート =====

export interface RawContent {
  RC_ID: string
  category: string
  content_type: string          // memory/word/single_choice/multiple_choice
  raw_text: string
  source: string
  process_status: string        // unprocessed/processing/processed/failed
  data_flag: number
  imported_at: string
}

export interface ImportResult {
  total_imported: number
  failed: number
  items: RawContent[]
}

// ===== カード（ProcessedContent）=====

export interface ExtraData {
  options?: string[]
  correct_answers?: string[]
  explanation?: string
}

export interface ProcessedContent {
  PC_ID: string
  RC_ID: string
  content_type: string
  question: string
  answer: string
  extra: ExtraData | null
  category: string
  tags: string[]                // 追加タグ一覧
  usage_type: string | null
  curve_id: string | null
  current_level: number         // 1-7
  last_reviewed_at: string | null
  next_review_time: string | null
  process_version: number
  data_flag: number
  processed_at: string
}

export interface ProcessResult {
  total_processed: number
  failed: number
  items: ProcessedContent[]
}

// ===== 復習 =====

export interface ReviewItem {
  PC_ID: string
  content_type: string
  question: string
  answer: string
  extra: ExtraData | null
  category: string
  tags: string[]
  current_level: number
  next_review_time: string | null
  hours_until_review: number | null   // 正=残り時間、負=過期時間
  is_overdue: boolean
  is_severely_overdue: boolean
}

export interface ReviewResult {
  PC_ID: string
  old_level: number
  new_level: number
  next_review_time: string
  review_type: string           // normal/early/severely_overdue
}

// ===== Dashboard =====

export interface CategoryStat {
  category: string
  total: number
  due: number                   // 今日復習すべき数
  overdue: number               // 過期済み数
  mastered: number              // Lv7 達成数
}

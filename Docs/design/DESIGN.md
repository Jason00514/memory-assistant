# 记忆助手 — 设计书 v1.0

> 作者：Jason00514 / Claude Sonnet 4.6
> 更新日：2026-05-20
> 对象读者：初级开发人员、AI辅助开发

---

## 目录

1. [要件定义（What to build）](#1-要件定义)
2. [基本设计（How to build）](#2-基本设计)
3. [详细设计（Code level）](#3-详细设计)
4. [命名规则](#4-命名规则)
5. [开发环境与启动方法](#5-开发环境与启动方法)

---

## 1. 要件定义

### 1.1 项目概要

| 项目 | 内容 |
|------|------|
| 系统名 | 记忆助手（Memory Assistant） |
| 目的 | 基于艾宾浩斯遗忘曲线，管理个人学习内容的复习计划 |
| 使用者 | 个人学习者（单人使用） |
| 第一阶段 | 后端 API + 基本 Web 前端 |
| 第二阶段（未来）| 手机端、用户系统、共享功能 |

### 1.2 功能要件

#### FR-01 内容导入

| ID | 功能 | 优先度 |
|----|------|--------|
| FR-01-1 | 从 Excel（.xlsx/.xls）导入内容 | 必须 |
| FR-01-2 | 从文本文件（.txt）导入内容 | 必须 |
| FR-01-3 | 自动识别内容类型（记忆/单词/选择题）| 必须 |
| FR-01-4 | 导入后可选择使用的记忆曲线 | 必须 |

#### FR-02 复习功能

| ID | 功能 | 优先度 |
|----|------|--------|
| FR-02-1 | 显示今日待复习内容 | 必须 |
| FR-02-2 | 按分类筛选复习内容 | 必须 |
| FR-02-3 | 按紧急度排序（过期最优先）| 必须 |
| FR-02-4 | 翻卡动画显示答案 | 必须 |
| FR-02-5 | 答案显示模式切换（翻卡/下方固定）| 推荐 |
| FR-02-6 | 答对/答错更新等级 | 必须 |

#### FR-03 卡片管理

| ID | 功能 | 优先度 |
|----|------|--------|
| FR-03-1 | 查看所有卡片列表 | 必须 |
| FR-03-2 | 多标签（Tags）分类管理 | 必须 |
| FR-03-3 | 按标签/状态筛选卡片 | 必须 |
| FR-03-4 | 重置卡片等级 | 推荐 |
| FR-03-5 | 修改卡片使用的记忆曲线 | 推荐 |

#### FR-04 记忆曲线

| ID | 功能 | 优先度 |
|----|------|--------|
| FR-04-1 | 查看/新建/编辑/删除记忆曲线 | 必须 |
| FR-04-2 | 预览选择曲线后的复习时间表 | 推荐 |
| FR-04-3 | 显示预计完成记忆所需时间 | 推荐 |

#### FR-05 一览 Dashboard

| ID | 功能 | 优先度 |
|----|------|--------|
| FR-05-1 | 按分类显示待复习数量 | 必须 |
| FR-05-2 | 显示今日/本周复习进度 | 推荐 |

### 1.3 非功能要件

| 项目 | 要求 |
|------|------|
| 响应速度 | 主要操作 < 1秒 |
| 数据库 | 开发阶段使用 SQLite，正式版切换 PostgreSQL |
| 浏览器 | Chrome/Edge 最新版 |
| 语言 | 界面支持中文显示 |

---

## 2. 基本设计

### 2.1 系统构成

```
┌─────────────────────────────────────────────┐
│                  浏览器                       │
│   Vue3 + TypeScript + Tailwind CSS          │
│   Port: 5173 (dev) / 80 (prod)              │
└──────────────────┬──────────────────────────┘
                   │ HTTP /api/* (Vite proxy)
┌──────────────────▼──────────────────────────┐
│              FastAPI 后端                    │
│   Python 3.12+ / Port: 8001                 │
└──────────────────┬──────────────────────────┘
                   │ SQLAlchemy ORM
┌──────────────────▼──────────────────────────┐
│   SQLite（开发）/ PostgreSQL（本番）          │
└─────────────────────────────────────────────┘
```

### 2.2 数据库 ER 图

```
RawContent           ProcessedContent        MemoryCurve
──────────           ────────────────        ──────────
RC_ID (PK)    1──N   PC_ID (PK)       N──1   curve_id (PK)
category             RC_ID (FK)              curve_name
content_type         content_type            intervals [JSON]
raw_text             question                overdue_multiplier
source               answer                  description
process_status       extra [JSON]            created_at
data_flag            category                data_flag
imported_at          tags [JSON] ←新增
                     usage_type
                     curve_id (FK)
                     current_level (1-7)
                     last_reviewed_at
                     next_review_time
                     data_flag
                     processed_at
```

### 2.3 画面遷移

```
/ → /dashboard    ← ホーム（一覧表）
     /review      ← 复习主界面
     /import      ← 导入页
     /cards       ← 卡片库
     /curves      ← 记忆曲线管理
```

### 2.4 API 一览

| Method | Path | 功能 |
|--------|------|------|
| GET | /dashboard/stats | 按分类统计 |
| POST | /import/excel | 导入 Excel |
| POST | /import/text | 导入文本文件 |
| POST | /import/process | 解析为卡片 |
| GET | /import/raw | 查看原始数据 |
| GET | /review/due | 今日待复习 |
| GET | /review/all | 全部卡片 |
| POST | /review/answer | 提交答题结果 |
| POST | /review/reset/{id} | 重置等级 |
| GET | /curves/ | 记忆曲线列表 |
| POST | /curves/ | 新建曲线 |
| PUT | /curves/{id} | 编辑曲线 |
| DELETE | /curves/{id} | 删除曲线 |
| GET | /curves/{id}/preview | 曲线预览 |
| GET | /tags/ | 标签列表 |
| PUT | /cards/{id}/tags | 更新卡片标签 |
| PUT | /cards/{id}/curve | 更新卡片曲线 |

### 2.5 记忆曲线算法

```
正常复习（当前时间 ≥ next_review_time）:
  答对 → level + 1（上限 7）
  答错 → level - 1（下限 1）

提前复习（当前时间 < next_review_time）:
  等级不变，仅更新下次复习时间

严重过期（过期时间 > 当前间隔 × overdue_multiplier）:
  答错 → level - 2（下限 1）

next_review_time = last_reviewed_at + intervals[current_level - 1] 小时
```

---

## 3. 详细设计

### 3.1 目录结构

```
memory-assistant/
├── app/                          # FastAPI 后端
│   ├── main.py                   # 入口：路由注册、启动初始化
│   ├── core/
│   │   ├── config.py             # 环境变量配置（DATABASE_URL等）
│   │   └── database.py           # SQLAlchemy engine、session、Base
│   ├── models/                   # 数据库表定义（SQLAlchemy ORM）
│   │   ├── raw_content.py        # RawContent 表
│   │   ├── processed_content.py  # ProcessedContent 表（含tags字段）
│   │   └── memory_curve.py       # MemoryCurve 表
│   ├── schemas/                  # API 请求/响应格式（Pydantic）
│   │   ├── raw_content.py
│   │   ├── processed_content.py  # ReviewItem、ReviewAnswer等
│   │   └── memory_curve.py       # CurvePreview等
│   ├── crud/                     # 数据库 CRUD 操作
│   │   ├── raw_content.py
│   │   ├── processed_content.py  # 含tag过滤、紧急度排序
│   │   └── memory_curve.py       # 含seed默认曲线
│   ├── routers/                  # API 路由（按功能分文件）
│   │   ├── import_excel.py       # /import/* 导入相关
│   │   ├── review.py             # /review/* 复习相关
│   │   ├── curves.py             # /curves/* 曲线相关
│   │   ├── cards.py              # /cards/* 卡片管理（新增）
│   │   └── dashboard.py          # /dashboard/* 统计（新增）
│   ├── services/                 # 业务逻辑
│   │   ├── excel_parser.py       # Excel → raw records
│   │   ├── text_parser.py        # TXT → raw records（新增）
│   │   ├── content_parser.py     # raw → structured card
│   │   └── review_scheduler.py   # 复习算法
│   └── utils/
│       └── id_generator.py       # RC_/PC_/MC_ ID生成
├── frontend/                     # Vue3 前端
│   ├── src/
│   │   ├── main.ts               # Vue 入口
│   │   ├── App.vue               # 布局 + 导航
│   │   ├── style.css             # Tailwind 全局样式
│   │   ├── router/index.ts       # 页面路由
│   │   ├── api/index.ts          # 所有 API 调用
│   │   ├── types/index.ts        # TypeScript 类型定义
│   │   ├── components/
│   │   │   └── LevelBadge.vue    # 等级标签组件
│   │   └── views/
│   │       ├── DashboardView.vue  # 一览表（新增）
│   │       ├── ReviewView.vue     # 复习主界面
│   │       ├── ImportView.vue     # 导入页
│   │       ├── CardsView.vue      # 卡片库
│   │       └── CurvesView.vue     # 记忆曲线管理
│   ├── package.json
│   ├── vite.config.ts            # Vite配置（含代理到 :8001）
│   ├── tailwind.config.js
│   └── tsconfig.json
├── Docs/
│   └── design/
│       ├── DESIGN.md             # 本设计书
│       └── AI_GUIDE.md           # AI交流指南
├── migrations/
│   └── init_db.py                # 手动初始化脚本
├── requirements.txt
├── .env.example                  # 环境变量模板
└── .gitignore
```

### 3.2 ID 命名规则

| 表 | ID 格式 | 例子 | 位数 |
|----|---------|------|------|
| RawContent | RC_XXXXXXX | RC_0000001 | RC_ + 7位数字 |
| ProcessedContent | PC_XXXXXXX | PC_0000001 | PC_ + 7位数字 |
| MemoryCurve | MC_XXXXXX | MC_000001 | MC_ + 6位数字 |

### 3.3 代码命名规则

| 对象 | 规则 | 例子 |
|------|------|------|
| Python 变量/函数 | snake_case | `get_due_items`, `current_level` |
| Python 类 | PascalCase | `ProcessedContent`, `ReviewScheduler` |
| Python 文件 | snake_case | `review_scheduler.py` |
| TypeScript 变量 | camelCase | `currentLevel`, `isDue` |
| TypeScript 型 | PascalCase | `ReviewItem`, `MemoryCurve` |
| Vue ファイル | PascalCase | `ReviewView.vue`, `LevelBadge.vue` |
| CSS クラス | kebab-case（Tailwind） | `bg-indigo-600` |
| API パス | kebab-case | `/review/due`, `/import/excel` |
| DB テーブル | snake_case 複数形 | `raw_contents`, `memory_curves` |
| DB カラム | snake_case | `process_status`, `data_flag` |

### 3.4 data_flag 値の意味

| 値 | 意味 |
|----|------|
| 0 | 正常使用中 |
| 1 | 削除済み（論理削除） |
| 2 | テストデータ |

### 3.5 content_type 一覧

| 值 | 意味 | 判定条件 |
|----|------|----------|
| `memory` | 純記憶 | answer: なし |
| `word` | 単語/普通答え | `answer:` あり |
| `single_choice` | 単選択題 | `answer option:` あり |
| `multiple_choice` | 複数選択 | `answer check:` あり |

### 3.6 process_status 一覧

| 值 | 意味 |
|----|------|
| `unprocessed` | 未処理（インポート直後） |
| `processing` | 処理中 |
| `processed` | 処理完了 |
| `failed` | 処理失敗 |

### 3.7 環境変数（.env）

```env
DATABASE_URL=sqlite:///./memory_assistant.db
# PostgreSQL の場合：
# DATABASE_URL=postgresql://user:pass@localhost:5432/memory_assistant
APP_ENV=development
```

---

## 4. 命名規則

### 4.1 ファイル命名

```
# バックエンド
app/routers/[機能名].py       例: review.py, curves.py
app/services/[機能名]_[動詞].py  例: excel_parser.py, review_scheduler.py
app/models/[テーブル名単数].py  例: raw_content.py

# フロントエンド
src/views/[ページ名]View.vue    例: ReviewView.vue
src/components/[機能名].vue     例: LevelBadge.vue
src/api/index.ts               （全API一元管理）
src/types/index.ts             （全型定義一元管理）
```

### 4.2 API レスポンス規約

成功：HTTP 200, JSON ボディ
エラー：HTTP 4xx/5xx + `{"detail": "エラーメッセージ"}`

### 4.3 コメント規約

```python
# ① 関数の先頭：目的だけ（何をするか、なぜそうするか）
# ② 複雑なロジックの前：なぜこの実装か
# ③ 定数：値の意味と単位

# 例：
INTERVALS = [1, 4, 24, 48, 168, 360, 720]  # Level1-7 の復習間隔（単位：時間）

def process_review(...):
    # 严重过期の判定：経過時間が現在間隔×倍率を超えた場合
    if elapsed_hours > current_interval * overdue_multiplier:
        ...
```

---

## 5. 開発環境と起動方法

### 5.1 必要なソフト

| ソフト | バージョン | 用途 |
|--------|-----------|------|
| Python | 3.10+ | バックエンド |
| Node.js | 18+ | フロントエンド |
| Git | 任意 | バージョン管理 |

### 5.2 初回セットアップ

```bash
# 1. 依存パッケージインストール
pip install -r requirements.txt
cd frontend && npm install

# 2. 環境変数設定
cp .env.example .env
# .env の DATABASE_URL を確認

# 3. データベース初期化（テーブル作成＋デフォルトカーブ）
python migrations/init_db.py
```

### 5.3 起動

```bash
# バックエンド（ルートディレクトリで）
python -c "import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8001, reload=True)"

# フロントエンド（frontend/ ディレクトリで）
npm run dev
```

### 5.4 アクセス先

| 内容 | URL |
|------|-----|
| フロントエンド | http://localhost:5173 |
| API ドキュメント | http://localhost:8001/docs |
| API（直接アクセス）| http://localhost:8001 |

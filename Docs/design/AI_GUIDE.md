# Claude Code との開発交流ガイド

> このプロジェクトで AI（Claude Code）と効果的に協力するための実践ガイドです。

---

## 1. 基本的な考え方

Claude Code は「今この会話の内容しか見えていない」と思ってください。
前回の会話は覚えていません。毎回、必要な文脈を伝えることが大切です。

---

## 2. 新しい会話を始めるときのテンプレート

```
## プロジェクト概要
記忆助手（Memory Assistant）
- バックエンド：Python + FastAPI（Port 8001）
- フロントエンド：Vue3 + TypeScript + Tailwind CSS（Port 5173）
- DB：SQLite（開発）/ PostgreSQL（本番）
- GitHub：https://github.com/Jason00514/memory-assistant

## 現在の作業
[今日やりたいことを1〜3行で書く]

## 関連ファイル
[修正予定のファイルパスを書く]

## 問題 / 要求
[具体的に何をしたいか書く]
```

---

## 3. バグ報告のテンプレート

```
## バグ報告

### 何が起きた？
[現象を具体的に書く]
例：/review/due にアクセスすると 500エラーが出る

### どうなるべき？
[期待する動作]
例：今日の復習リストがJSON形式で返ってくる

### エラーメッセージ
[コンソールやターミナルのエラーをそのまま貼る]
例：
  IntegrityError: UNIQUE constraint failed: processed_contents.PC_ID

### 再現手順
1. Excel をインポートする
2. /import/process を実行する
3. /review/due にアクセスする

### 関連ファイル
app/routers/review.py
app/crud/processed_content.py
```

---

## 4. 機能追加要求のテンプレート

```
## 機能追加要求

### 追加したい機能
[1〜2文で要約]
例：カードに複数のタグを付けられるようにしたい

### なぜ必要？
[理由・背景]
例：英単語が「英語四級」「AI語彙」「日常会話」など複数カテゴリに属するから

### 具体的な動作
- ユーザーがカードの編集画面でタグを追加/削除できる
- タグで絞り込んで複習できる
- 1枚のカードに最大10タグまで

### 影響するファイル（わかる範囲で）
- app/models/processed_content.py（tags カラム追加）
- frontend/src/views/CardsView.vue
```

---

## 5. コード説明を頼むときのコツ

**❌ あまり良くない例：**
```
このコードを説明して
```

**✅ 良い例：**
```
app/services/review_scheduler.py の process_review() 関数の、
"severely_overdue" の判定ロジックがわかりません。
特に elapsed_hours の計算方法を、初心者にもわかるように説明してください。
```

---

## 6. 実際の会話例

### 例①：新機能を追加してもらう

```
記忆助手プロジェクトの続きです。

プロジェクト：https://github.com/Jason00514/memory-assistant
バックエンド：FastAPI (Port 8001)、フロントエンド：Vue3 (Port 5173)

【やりたいこと】
カード（ProcessedContent）に複数タグを付けられる機能を追加したい。
現在は category（単一文字列）しかないが、
tags（文字列配列）を追加して、1枚のカードに複数の分類ができるようにしたい。

【必要な変更】
1. DB：processed_contents テーブルに tags JSON カラムを追加
2. API：タグ更新エンドポイント PUT /cards/{id}/tags
3. フロント：CardsView.vue でタグを表示・編集できる UI

全部実装してください。質問は不要です。
```

### 例②：バグを直してもらう

```
記忆助手プロジェクトでバグが出ています。

【現象】
Excel をインポートすると Internal Server Error になる

【エラーログ】
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed: raw_contents.RC_ID

【原因の仮説】
同じ RC_ID が2回発行されているみたい

【関連ファイル】
app/utils/id_generator.py
app/routers/import_excel.py

修正してください。
```

### 例③：デザインを変えてもらう

```
記忆助手のフロントエンド（Vue3）の改修をお願いします。

【対象ファイル】
frontend/src/views/ReviewView.vue

【変更内容】
現在：答えを見るにはカードを「翻転」しないといけない
変更後：画面下部に「答えを表示」ボタンを置いて、
        クリックすると同じ画面内に答えが表示されるオプションを追加したい。
        翻転モードと下部表示モードを切り替えるトグルボタンも追加。
```

---

## 7. よく使うフレーズ集

| 場面 | フレーズ |
|------|----------|
| 全部任せたい | 「全部実装してください。質問は不要です。」 |
| 確認しながら進めたい | 「方針を教えてから実装してください。」 |
| 説明だけ欲しい | 「コードは書かず、説明だけしてください。」 |
| 別の方法も聞きたい | 「他の実装方法も2〜3案挙げてください。」 |
| テストして欲しい | 「実装後、curl コマンドで動作確認もしてください。」 |

---

## 8. GitHub への反映手順

```bash
# 1. 変更を確認
git status
git diff

# 2. ステージング
git add app/ frontend/src/

# 3. コミット
git commit -m "feat: タグ機能追加"

# 4. プッシュ（トークンが必要）
git push origin main
```

> ⚠️ GitHub トークン（ghp_xxx）は使用後すぐに削除してください：
> https://github.com/settings/tokens

---

## 9. このプロジェクト特有のルール

1. **DB の ID は必ず flush() してから次の ID を生成する**
   → 同一バッチで複数レコードを作る場合、flush() しないと同じ ID になるバグが出る

2. **SQLite で起動、PostgreSQL 移行時は DATABASE_URL だけ変えればよい**
   → `app/core/config.py` の `DATABASE_URL` を変更

3. **フロントエンドの API 呼び出しは全て `src/api/index.ts` に集める**
   → 分散させると管理が難しくなる

4. **新しい画面を追加したら `src/router/index.ts` と `App.vue` の nav も更新する**

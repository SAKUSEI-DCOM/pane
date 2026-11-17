# パネルびらき — IRIAM公式イベント情報連携

このZIPを展開し、**中身の `index.html`、`scripts/`、`data/`、`.github/` をリポジトリのルート**へアップロードしてください。ZIPファイル自体をGitHub Pagesに置いても動作しません。

## 自動更新の設定

1. GitHubリポジトリの Settings → Pages で公開元を `Deploy from a branch`、ブランチを `main`、フォルダを `/ (root)` に設定。
2. Settings → Actions → General → Workflow permissions で **Read and write permissions** を選択（組織ポリシーで変更できない場合は管理者に確認）。
3. Actions → **Update IRIAM official notices** → **Run workflow** で初回実行。
4. `data/official_news.json` に `updated_at` と `items` が書き込まれたことを確認。以降は6時間おきの実行予定です（GitHubの都合で遅延する場合があります）。

## ギフトの抽出について

IRIAM公式の「イベント・キャンペーン等お知らせ」から記事を探し、関連記事（同じ `info.iriam.com` 内、最大3リンク）まで確認します。「対象ギフト」「指定ギフト」などの見出し直後にある**文字列のみ**を候補として抽出します。候補には根拠記事のURL・見出しを `evidence` として保存します。

**重要**：抽出結果は確定情報ではありません。イベント特典で配布されるギフトと、イベント集計対象のギフトは区別が必要です。画像中だけに書かれた名前やアプリ内のみの情報は読み取れません。公式記事を開いて確認してから使ってください。

イベント情報を読み込めないときは、前回のデータを消さずに維持します。ローカルの `file://` で開くとJSONの読み込みが失敗する場合があります。GitHub Pagesで確認してください。

## テスト

`python -m pip install requests beautifulsoup4`
`python scripts/update_events.py`

公式サイトへのアクセスが制限されている場合は取得が失敗します。サイト側の仕様変更にも対応が必要です。


## 2026-11-16: パネル作成画面のギフト対象設定
- 「適当に埋める」の直下にギフト対象（すべて / LOVE / イベント）を移動しました。
- 「適当に埋める」と「目標ptでギフトを自動設定」の両方に対象ギフトの制限を適用します。
- LOVEの11種は公開されている2024年時点の一覧を基準にしています。現行のIRIAMアプリの分類との一致は保証しません。
- イベントの対象ギフトは公式お知らせから抽出した候補を確認して設定してください。

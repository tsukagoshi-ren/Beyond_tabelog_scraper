# 食べログスクレイピングツール

食べログから店舗情報を取得し、Excelファイルとして保存するGUIアプリケーションです。

## 機能

- **地域選択**: 都道府県、中項目（地域）、小項目（詳細地域）での絞り込み
- **ニューオープンモード**: 新規オープン店舗のみを対象
- **オープン日フィルタ**: 年/月単位でのフィルタリング
- **進行状況表示**: リアルタイムログとプログレスバー
- **50ページ区切り**: 大量データの分割取得

## 取得する情報

- 店舗名
- ジャンル
- 住所
- オープン日
- 電話番号
- URL
- 営業時間/定休日
- 公式アカウント（Instagram）
- サービス

## 必要な環境

- Python 3.8以上
- Windows 10/11（他のOSでも動作可能ですが、一部パスの調整が必要）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/yourusername/tabelog-scraper.git
cd tabelog-scraper
```

### 2. 仮想環境の作成（推奨）

```bash
# Windowsの場合
python -m venv venv
venv\Scripts\activate

# macOS/Linuxの場合
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

## 使用方法

### 開発環境での実行

```bash
python main.py
```

### GUIの使い方

1. **検索条件タブ**で以下を設定：
   - 保存先フォルダ（デフォルト：ダウンロードフォルダ）
   - 都道府県（必須）
   - 地域（中項目）（オプション）
   - 地域（小項目）（オプション）
   - 開始ページ（デフォルト：1）
   - オプション設定

2. **「スクレイピング開始」**ボタンをクリック

3. 自動的に**進行状況タブ**に切り替わり、以下が表示されます：
   - 現在の処理状況
   - プログレスバー
   - 詳細なログ

4. 完了後、指定したフォルダにExcelファイルが保存されます

## ビルド手順

### 方法1: cx_Freezeを使用（推奨）

1. cx_Freezeをインストール：
   ```bash
   pip install cx_Freeze
   ```

2. ビルドを実行：
   ```bash
   python setup.py build
   ```

3. MSIインストーラーを作成（オプション）：
   ```bash
   python setup.py bdist_msi
   ```

4. 実行ファイルは `build/exe.win-amd64-3.x/` フォルダに生成されます

### 方法2: PyInstallerを使用

1. PyInstallerをインストール：
   ```bash
   pip install pyinstaller
   ```

2. ビルドを実行：
   ```bash
   # コンソールウィンドウなし
   pyinstaller --onefile --windowed --name="TabeLogScraper" main.py
   
   # アイコン付き（icon.icoファイルが必要）
   pyinstaller --onefile --windowed --icon=icon.ico --name="TabeLogScraper" main.py
   ```

3. 実行ファイルは `dist/` フォルダに生成されます

### VSCodeでのビルド

VSCodeを使用している場合、`Ctrl+Shift+B` でビルドタスクを実行できます。
（`.vscode/tasks.json` が設定されている場合）

## プロジェクト構成

```
tabelog-scraper/
├── src/                            # ソースコード
│   ├── main.py                     # メインエントリーポイント
│   ├── gui/                        # GUI関連
│   │   ├── __init__.py
│   │   ├── main_window.py          # メインウィンドウ
│   │   ├── search_tab.py           # 検索条件タブ
│   │   └── progress_tab.py         # 進行状況タブ
│   │
│   ├── scraping/                   # スクレイピング機能
│   │   ├── __init__.py
│   │   ├── scraper.py              # スクレイピングコア機能
│   │   ├── url_builder.py          # URL生成機能
│   │   └── parser.py               # HTMLパーサー
│   │
│   ├── data/                       # データ管理
│   │   ├── __init__.py
│   │   ├── prefectures.py          # 都道府県データ
│   │   ├── middle_categories.py    # 中項目データ
│   │   └── small_categories.py     # 小項目データ
│   │
│   ├── utils/                      # ユーティリティ
│   │   ├── __init__.py
│   │   ├── date_filter.py          # 日付フィルタリング
│   │   ├── file_handler.py         # ファイル保存処理
│   │   └── logger.py               # ログ管理
│   │
│   └── config/                     # 設定
│       ├── __init__.py
│       └── settings.py             # アプリケーション設定
│
├── build/                          # ビルド関連
│   ├── setup.py                    # cx_Freeze設定
│   └── icon.ico                    # アプリケーションアイコン（オプション）
│
├── docs/                           # ドキュメント
│   └── README.md                   # プロジェクト説明
│
├── requirements.txt                # 依存関係
├── .gitignore                      # Git除外設定
├── LICENSE                         # ライセンス
└── run.py                          # 開発用実行スクリプト
```

## トラブルシューティング

### エラー: モジュールが見つからない

ビルド後の実行ファイルでモジュールエラーが発生する場合：

1. `setup.py` の `packages` リストに不足しているモジュールを追加
2. データファイル（.py）が含まれているか確認

### エラー: requests関連のSSLエラー

```bash
pip install --upgrade certifi
```

### ビルドファイルのサイズが大きい

`setup.py` の `excludes` リストに不要なモジュールを追加してください。

## 注意事項

- スクレイピングは相手サーバーに負荷をかけないよう、適切な間隔を空けて実行されます
- 大量のデータを取得する場合は、50ページ区切りオプションの使用を推奨します
- robots.txtやサイトの利用規約を確認の上、適切に使用してください

## ライセンス

[MITライセンス](LICENSE)

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを作成して変更内容を議論してください。

## 作者

[Your Name]

## 更新履歴

- v2.0.0 (2024-XX-XX)
  - 地域（中項目・小項目）選択機能を追加
  - オープン日フィルタリング機能を追加
  - UIをタブ形式に変更
  - リアルタイムログ表示を追加
  - スクレイピング停止機能を追加

- v1.0.0 (2024-XX-XX)
  - 初回リリース
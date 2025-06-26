import sys
from cx_Freeze import setup, Executable

# 必要なパッケージをリストアップ
packages = [
    "tkinter", 
    "pandas", 
    "os", 
    "datetime", 
    "requests", 
    "bs4", 
    "requests_cache", 
    "time",
    "threading",
    "re",
    "openpyxl",  # Excel出力用
    "lxml",  # BeautifulSoupのパーサー
    "urllib3",  # requestsの依存関係
    "certifi",  # SSL証明書
    "idna",  # 国際化ドメイン名
    "charset_normalizer"  # 文字エンコーディング
]

# インクルードするファイル
include_files = [
    ("prefectures.py", "prefectures.py"),
    ("middle_categorys.py", "middle_categorys.py"),
    ("small_categorys.py", "small_categorys.py")
]

# 除外するモジュール（不要なものを削減）
excludes = [
    "matplotlib",
    "numpy",
    "scipy",
    "test",
    "unittest",
    "email",
    "html",
    "http",
    "xml",
    "pydoc_data"
]

# GUIアプリの場合はbase="Win32GUI"を指定
if sys.platform == "win32":
    base = "Win32GUI"
else:
    base = None

# ビルドオプション
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "include_msvcr": True,  # Visual C++ランタイムを含める
}

setup(
    name="TabeLogScraper",  # アプリケーション名
    version="2.0",
    description="食べログスクレイピングツール（地域選択・オープン日フィルタ対応版）",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="TabeLogScraper.exe",
            icon=None  # アイコンファイルがある場合は "icon.ico" を指定
        )
    ]
)
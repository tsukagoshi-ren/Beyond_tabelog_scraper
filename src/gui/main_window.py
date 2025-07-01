"""
メインウィンドウ管理
"""

import tkinter as tk
from tkinter import ttk

from .search_tab import SearchTab
from .progress_tab import ProgressTab
from scraping.scraper import Scraper


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("食べログスクレイピングツール")
        self.window.geometry("700x750")
        
        # スクレイパーインスタンス
        self.scraper = Scraper()
        
        # ノートブック（タブ）の作成
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 各タブの作成
        self._create_tabs()
        
    def _create_tabs(self):
        """タブを作成"""
        # 検索条件タブ
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="検索条件")
        self.search_tab = SearchTab(search_frame, self)
        
        # 進行状況タブ
        progress_frame = ttk.Frame(self.notebook)
        self.notebook.add(progress_frame, text="進行状況")
        self.progress_tab = ProgressTab(progress_frame, self)
        
    def start_scraping(self, search_params):
        """スクレイピングを開始"""
        # 進行状況タブに切り替え
        self.notebook.select(1)
        
        # 検索条件タブを無効化
        self.notebook.tab(0, state="disabled")
        
        # 進行状況タブの準備
        self.progress_tab.on_start()
        
        # スクレイピング実行
        self.scraper.start(
            search_params,
            progress_callback=self.progress_tab.update_progress,
            status_callback=self.progress_tab.update_status,
            log_callback=self.progress_tab.add_log,
            complete_callback=self.on_scraping_complete
        )
        
    def stop_scraping(self):
        """スクレイピングを停止"""
        self.scraper.stop()
        self.progress_tab.add_log("スクレイピング停止が要求されました...")
        
    def on_scraping_complete(self):
        """スクレイピング完了時の処理"""
        # 検索条件タブを有効化
        self.notebook.tab(0, state="normal")
        
        # ボタンの状態を更新
        self.search_tab.enable_controls()
        self.progress_tab.on_complete()
        
    def run(self):
        """アプリケーションを実行"""
        self.window.mainloop()
"""
進行状況タブの実装
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class ProgressTab:
    """進行状況タブクラス"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.create_widgets()
        
    def create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ステータスラベル
        self.status_label = ttk.Label(self.frame, text="準備完了", font=("Helvetica", 12))
        self.status_label.pack(pady=10)
        
        # 進捗バー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            orient=tk.HORIZONTAL, 
            length=100, 
            mode='determinate', 
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(self.frame, text="進捗: 0/0 ページ")
        self.progress_label.pack(pady=5)
        
        # 停止ボタン
        self.stop_button = ttk.Button(
            self.frame, 
            text="スクレイピング停止", 
            command=self.stop_scraping,
            state="disabled"
        )
        self.stop_button.pack(pady=10)
        
        # ログ表示エリア
        log_label = ttk.Label(self.frame, text="実行ログ:")
        log_label.pack(anchor=tk.W, pady=(10, 5))
        
        # ログテキストエリアとスクロールバー
        log_frame = ttk.Frame(self.frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame, 
            height=15, 
            wrap=tk.WORD, 
            yscrollcommand=log_scrollbar.set
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.config(command=self.log_text.yview)
        
        # ログテキストを読み取り専用に
        self.log_text.bind("<Key>", lambda e: "break")
        
    def update_progress(self, value, max_value):
        """進捗バーを更新する"""
        if max_value > 0:
            self.progress_var.set(value / max_value * 100)
            self.progress_label.config(text=f"進捗: {value}/{max_value} ページ")
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="進捗: 0/0 ページ")
            
    def update_status(self, text):
        """ステータスラベルを更新する"""
        self.status_label.config(text=text)
        
    def add_log(self, text):
        """ログテキストを追加する"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"{timestamp} - {text}\n")
        self.log_text.see(tk.END)
        
    def stop_scraping(self):
        """スクレイピングを停止"""
        self.main_window.stop_scraping()
        
    def on_start(self):
        """スクレイピング開始時の処理"""
        self.stop_button.configure(state="normal")
        self.progress_var.set(0)
        
    def on_complete(self):
        """スクレイピング完了時の処理"""
        self.stop_button.configure(state="disabled")
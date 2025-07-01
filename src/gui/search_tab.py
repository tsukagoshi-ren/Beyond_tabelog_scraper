"""
検索条件タブの実装
"""

import tkinter as tk
from tkinter import ttk, filedialog
import os
from datetime import datetime

from data import prefectures_values, prefectures_middle_category, prefectures_small_category
from config import Settings


class SearchTab:
    """検索条件タブクラス"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.create_widgets()
        
    def create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトルラベル
        title_label = ttk.Label(self.frame, text="食べログスクレイピングツール", font=("Helvetica", 16))
        title_label.pack(pady=10)
        
        # 保存先選択
        self._create_save_path_widgets()
        
        # 地域選択
        self._create_area_widgets()
        
        # オプション設定
        self._create_option_widgets()
        
        # スクレイピング実行ボタン
        self._create_action_buttons()
        
        # 説明テキスト
        self._create_help_text()
        
    def _create_save_path_widgets(self):
        """保存先選択ウィジェットを作成"""
        save_frame = ttk.Frame(self.frame)
        save_frame.pack(fill=tk.X, pady=5)
        
        save_label = ttk.Label(save_frame, text="保存先:", width=15)
        save_label.pack(side=tk.LEFT)
        
        self.save_path_var = tk.StringVar(value=Settings.DEFAULT_SAVE_PATH)
        save_path_entry = ttk.Entry(save_frame, textvariable=self.save_path_var, state="readonly")
        save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.save_path_button = ttk.Button(save_frame, text="選択", command=self.choose_save_path)
        self.save_path_button.pack(side=tk.LEFT)
        
    def _create_area_widgets(self):
        """地域選択ウィジェットを作成"""
        # 都道府県選択
        prefecture_frame = ttk.Frame(self.frame)
        prefecture_frame.pack(fill=tk.X, pady=5)
        
        prefecture_label = ttk.Label(prefecture_frame, text="都道府県:", width=15)
        prefecture_label.pack(side=tk.LEFT)
        
        prefecture_values = ["全国"] + list(prefectures_values.keys())
        self.prefecture_combo = ttk.Combobox(prefecture_frame, values=prefecture_values, state="readonly")
        self.prefecture_combo.set(prefecture_values[0])
        self.prefecture_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.prefecture_combo.bind("<<ComboboxSelected>>", self.on_prefecture_changed)
        
        # 地域（中項目）選択
        middle_frame = ttk.Frame(self.frame)
        middle_frame.pack(fill=tk.X, pady=5)
        
        middle_label = ttk.Label(middle_frame, text="地域（中項目）:", width=15)
        middle_label.pack(side=tk.LEFT)
        
        self.middle_combo = ttk.Combobox(middle_frame, values=[""], state="disabled")
        self.middle_combo.set("")
        self.middle_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.middle_combo.bind("<<ComboboxSelected>>", self.on_middle_changed)
        
        # 地域（小項目）選択
        small_frame = ttk.Frame(self.frame)
        small_frame.pack(fill=tk.X, pady=5)
        
        small_label = ttk.Label(small_frame, text="地域（小項目）:", width=15)
        small_label.pack(side=tk.LEFT)
        
        self.small_combo = ttk.Combobox(small_frame, values=[""], state="disabled")
        self.small_combo.set("")
        self.small_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def _create_option_widgets(self):
        """オプション設定ウィジェットを作成"""
        # 開始ページ指定
        page_frame = ttk.Frame(self.frame)
        page_frame.pack(fill=tk.X, pady=5)
        
        start_page_label = ttk.Label(page_frame, text="開始ページ:", width=15)
        start_page_label.pack(side=tk.LEFT)
        
        self.start_page_entry = ttk.Entry(page_frame)
        self.start_page_entry.insert(0, str(Settings.DEFAULT_START_PAGE))
        self.start_page_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # チェックボックスオプション
        options_frame = ttk.Frame(self.frame)
        options_frame.pack(fill=tk.X, pady=10)
        
        self.fifty_page_var = tk.BooleanVar(value=True)
        self.fifty_page_check = ttk.Checkbutton(options_frame, text="50ページ区切り", variable=self.fifty_page_var)
        self.fifty_page_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.new_open_var = tk.BooleanVar(value=False)
        self.new_open_check = ttk.Checkbutton(options_frame, text="ニューオープンモード", variable=self.new_open_var)
        self.new_open_check.pack(side=tk.LEFT)
        
        # オープン日フィルタ
        date_frame = ttk.Frame(self.frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        date_label = ttk.Label(date_frame, text="オープン日:", width=15)
        date_label.pack(side=tk.LEFT)
        
        # 年選択
        current_year = datetime.now().year
        year_values = ["指定なし"] + [str(year) for year in range(current_year, current_year - 10, -1)]
        self.year_combo = ttk.Combobox(date_frame, values=year_values, width=10, state="readonly")
        self.year_combo.set("指定なし")
        self.year_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        year_label = ttk.Label(date_frame, text="年")
        year_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 月選択
        month_values = ["指定なし"] + [str(month) for month in range(1, 13)]
        self.month_combo = ttk.Combobox(date_frame, values=month_values, width=10, state="readonly")
        self.month_combo.set("指定なし")
        self.month_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        month_label = ttk.Label(date_frame, text="月")
        month_label.pack(side=tk.LEFT)
        
    def _create_action_buttons(self):
        """アクションボタンを作成"""
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="スクレイピング開始", command=self.start_scraping)
        self.start_button.pack(ipadx=10, ipady=5)
        
    def _create_help_text(self):
        """ヘルプテキストを作成"""
        help_text = """
        使用方法：
        1. 保存先フォルダを選択（デフォルト：ダウンロードフォルダ）
        2. 対象の都道府県を選択（「全国」でも可）
        3. 必要に応じて地域（中項目・小項目）を選択
        4. 開始ページを指定（省略時は1）
        5. オプションを設定
          - 50ページ区切り：ONにすると最大50ページまでスクレイピング
          - ニューオープンモード：新規オープン店舗のみをスクレイピング
        6. オープン日でフィルタリング（年/月を指定可能）
        7. 「スクレイピング開始」ボタンをクリック
        
        結果は指定したフォルダに保存されます。
        """
        
        help_label = ttk.Label(self.frame, text=help_text, justify=tk.LEFT, wraplength=560)
        help_label.pack(pady=10)
        
    def choose_save_path(self):
        """保存先を選択"""
        folder_selected = filedialog.askdirectory(
            initialdir=self.save_path_var.get(),
            title="保存先フォルダを選択"
        )
        if folder_selected:
            self.save_path_var.set(folder_selected)
            
    def on_prefecture_changed(self, *args):
        """都道府県が変更されたときの処理"""
        prefecture = self.prefecture_combo.get()
        
        if prefecture == "全国":
            # 全国選択時は中項目・小項目を無効化
            self.middle_combo.set("")
            self.middle_combo.configure(values=[""])
            self.middle_combo.configure(state="disabled")
            self.small_combo.set("")
            self.small_combo.configure(values=[""])
            self.small_combo.configure(state="disabled")
        else:
            # 都道府県選択時は中項目を有効化
            middle_categories = prefectures_middle_category.get(prefecture, {})
            middle_names = [""] + list(middle_categories.keys())
            self.middle_combo.configure(values=middle_names)
            self.middle_combo.configure(state="readonly")
            self.middle_combo.set("")
            # 小項目をリセット
            self.small_combo.set("")
            self.small_combo.configure(values=[""])
            self.small_combo.configure(state="disabled")
            
    def on_middle_changed(self, *args):
        """中項目が変更されたときの処理"""
        middle = self.middle_combo.get()
        
        if middle == "":
            # 中項目未選択時は小項目を無効化
            self.small_combo.set("")
            self.small_combo.configure(values=[""])
            self.small_combo.configure(state="disabled")
        else:
            # 中項目選択時は小項目を有効化
            small_categories = prefectures_small_category.get(middle, {})
            small_names = [""] + list(small_categories.keys())
            self.small_combo.configure(values=small_names)
            self.small_combo.configure(state="readonly")
            self.small_combo.set("")
            
    def start_scraping(self):
        """スクレイピングを開始"""
        # 検索パラメータを収集
        search_params = {
            'save_path': self.save_path_var.get(),
            'prefecture': self.prefecture_combo.get(),
            'middle': self.middle_combo.get(),
            'small': self.small_combo.get(),
            'start_page': int(self.start_page_entry.get()) if self.start_page_entry.get() else 1,
            'fifty_page_mode': self.fifty_page_var.get(),
            'new_open_mode': self.new_open_var.get(),
            'filter_year': self.year_combo.get(),
            'filter_month': self.month_combo.get()
        }
        
        # コントロールを無効化
        self.disable_controls()
        
        # メインウィンドウのスクレイピング開始メソッドを呼び出し
        self.main_window.start_scraping(search_params)
        
    def disable_controls(self):
        """コントロールを無効化"""
        self.start_button.configure(state="disabled")
        self.save_path_button.configure(state="disabled")
        self.prefecture_combo.configure(state="disabled")
        self.middle_combo.configure(state="disabled")
        self.small_combo.configure(state="disabled")
        self.start_page_entry.configure(state="disabled")
        self.fifty_page_check.configure(state="disabled")
        self.new_open_check.configure(state="disabled")
        self.year_combo.configure(state="disabled")
        self.month_combo.configure(state="disabled")
        
    def enable_controls(self):
        """コントロールを有効化"""
        self.start_button.configure(state="normal")
        self.save_path_button.configure(state="normal")
        self.prefecture_combo.configure(state="readonly")
        self.middle_combo.configure(state="readonly")
        self.small_combo.configure(state="readonly")
        self.start_page_entry.configure(state="normal")
        self.fifty_page_check.configure(state="normal")
        self.new_open_check.configure(state="normal")
        self.year_combo.configure(state="readonly")
        self.month_combo.configure(state="readonly")
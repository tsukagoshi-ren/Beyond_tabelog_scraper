import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import os
from datetime import datetime
import requests_cache
import requests
from bs4 import BeautifulSoup
import requests.exceptions
import time
import threading
import re

# 環境変数設定
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# データインポート
from prefectures import prefectures_values
from middle_categorys import prefectures_middle_category
from small_categorys import prefectures_small_category

def generate_tabelog_url(prefecture_code, middle_code=None, small_code=None, start_page=1, new_open_mode=False):
    """
    食べログのURLを正確に生成する関数
    
    1ページ目: https://tabelog.com/tokyo/A1301/A130101/
    2ページ目以降: https://tabelog.com/tokyo/A1301/A130101/rstLst/2/
    ニューオープン: https://tabelog.com/tokyo/A1301/A130101/rstLst/cond16-00-00/
    
    Args:
        prefecture_code (str): 都道府県コード
        middle_code (str): 中項目コード
        small_code (str): 小項目コード
        start_page (int): 開始ページ
        new_open_mode (bool): ニューオープンモードかどうか
    
    Returns:
        str: 生成されたURL
    """
    base_url = "https://tabelog.com"
    
    # URLパスの構築
    path_parts = []
    
    # 都道府県コード
    if prefecture_code:
        path_parts.append(prefecture_code)
    
    # 中項目コード
    if middle_code:
        path_parts.append(middle_code)
    
    # 小項目コード
    if small_code:
        path_parts.append(small_code)
    
    # 基本パスの作成
    if path_parts:
        base_path = f"{base_url}/{'/'.join(path_parts)}"
    else:
        base_path = base_url
    
    # ページ番号とモードに応じてURLを構築
    if new_open_mode:
        # ニューオープンモード
        if start_page > 1:
            url = f"{base_path}/rstLst/cond16-00-00/{start_page}/"
        else:
            url = f"{base_path}/rstLst/cond16-00-00/"
    else:
        # 通常モード
        if start_page > 1:
            url = f"{base_path}/rstLst/{start_page}/"
        else:
            # 1ページ目はrstLstをつけない
            url = f"{base_path}/"
    
    # 全国の場合の特別処理
    if not path_parts:
        if new_open_mode:
            if start_page > 1:
                url = f"{base_url}/rstLst/cond16-00-00/{start_page}/"
            else:
                url = f"{base_url}/rstLst/cond16-00-00/"
        else:
            if start_page > 1:
                url = f"{base_url}/rstLst/{start_page}/"
            else:
                url = f"{base_url}/rstLst/"
    
    return url

def parse_opened_date(opened_date_text):
    """
    オープン日のテキストから年月を抽出する
    
    Args:
        opened_date_text (str): オープン日のテキスト
    
    Returns:
        tuple: (year, month) または None
    """
    if not opened_date_text or opened_date_text == '記載なし':
        return None
    
    # 年月を抽出する正規表現パターン
    pattern = r'(\d{4})年(\d{1,2})月'
    match = re.search(pattern, opened_date_text)
    
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return (year, month)
    
    return None

def filter_by_opened_date(opened_date_text, filter_year, filter_month):
    """
    オープン日でフィルタリングする
    
    Args:
        opened_date_text (str): オープン日のテキスト
        filter_year (int): フィルタリング用の年
        filter_month (int): フィルタリング用の月（0の場合は年のみでフィルタ）
    
    Returns:
        bool: フィルタリング条件に合致するかどうか
    """
    parsed_date = parse_opened_date(opened_date_text)
    
    if not parsed_date:
        return False
    
    year, month = parsed_date
    
    # 年のみでフィルタリング
    if filter_month == 0:
        return year == filter_year
    
    # 年月でフィルタリング
    return year == filter_year and month == filter_month

def scrape_shop_details(shop_url):
    """店舗詳細ページから情報を取得する"""
    retry_count = 0
    max_retries = 3
    wait_time = 5
    
    while retry_count < max_retries:
        try:
            shop_response = requests.get(shop_url, timeout=10)
            shop_response.raise_for_status()
            shop_soup = BeautifulSoup(shop_response.text, 'html.parser')
            
            # より柔軟なセレクタを使用
            name_element = shop_soup.find('h2', class_='display-name') or shop_soup.find('h2', class_='rstdtl-header__rst-name')
            name = name_element.text.strip() if name_element else '記載なし'
            
            address_element = shop_soup.find('p', class_='rstinfo-table__address') or shop_soup.find('p', class_='rstinfo-table__address-text')
            address = address_element.text.strip() if address_element else '記載なし'
            
            # より汎用的な方法で営業時間を取得
            opening_hours_element = None
            for heading in shop_soup.find_all(['th', 'dt']):
                if '営業時間' in heading.text:
                    opening_hours_element = heading.find_next(['td', 'dd'])
                    break
            opening_hours = opening_hours_element.text.strip() if opening_hours_element else '記載なし'
            
            phone_element = shop_soup.find('p', class_='rstdtl-side-yoyaku__tel-number') or shop_soup.find('strong', class_='rstinfo-table__tel-num')
            phone_number = phone_element.text.strip() if phone_element else '記載なし'
            
            opened_date_element = shop_soup.find('p', class_='rstinfo-opened-date')
            opened_dates = opened_date_element.text.strip() if opened_date_element else '記載なし'
            
            instagram_element = shop_soup.find('a', class_='rstinfo-sns-instagram')
            instagram = instagram_element['href'] if instagram_element and 'href' in instagram_element.attrs else '記載なし'
            
            # よりロバストな方法でサービスとジャンルを取得
            service = '記載なし'
            genre = '記載なし'
            
            for th in shop_soup.find_all('th'):
                if 'サービス' in th.text:
                    next_td = th.find_next('td')
                    if next_td:
                        service = next_td.get_text(strip=True)
                elif 'ジャンル' in th.text:
                    next_td = th.find_next('td')
                    if next_td:
                        genre = next_td.get_text(strip=True)
            
            return {
                '店舗名': name,
                'ジャンル': genre,
                '住所': address,
                'オープン日': opened_dates,
                '電話番号': phone_number,
                'URL': shop_url,
                '営業時間/定休日': opening_hours,
                '公式アカウント': instagram,
                'サービス': service
            }
        except requests.exceptions.RequestException as e:
            print(f'{shop_url}でエラーが発生しました: {e}')
            retry_count += 1
            time.sleep(wait_time)
            wait_time *= 2
        except AttributeError as e:
            print(f'{shop_url}で要素の取得に失敗しました: {e}')
            retry_count += 1
            time.sleep(wait_time)
        except Exception as e:
            print(f'{shop_url}で予期しないエラーが発生しました: {e}')
            return {}
    return {}

def update_progress(value, max_value):
    """進捗バーを更新する"""
    progress_var.set(value / max_value * 100)
    progress_label.config(text=f"進捗: {value}/{max_value} ページ")
    window.update()

def update_status(text):
    """ステータスラベルを更新する"""
    status_label.config(text=text)
    window.update()

def add_log(text):
    """ログテキストを追加する"""
    log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {text}\n")
    log_text.see(tk.END)
    window.update()

def disable_controls():
    """スクレイピング中のコントロールを無効化する"""
    area_scrape_button.configure(state="disabled")
    stop_button.configure(state="normal")
    # 検索条件タブを無効化
    notebook.tab(0, state="disabled")

def enable_controls():
    """スクレイピング終了後にコントロールを有効化する"""
    area_scrape_button.configure(state="normal")
    stop_button.configure(state="disabled")
    # 検索条件タブを有効化
    notebook.tab(0, state="normal")

def get_prefecture_code(prefecture):
    """都道府県名から都道府県コードを取得する"""
    if prefecture == "全国":
        return ""
    return prefectures_values.get(prefecture, "")

def on_prefecture_changed(*args):
    """都道府県が変更されたときの処理"""
    prefecture = prefecture_combo.get()
    
    if prefecture == "全国":
        # 全国選択時は中項目・小項目を無効化
        middle_combo.set("")
        middle_combo.configure(values=[""])
        middle_combo.configure(state="disabled")
        small_combo.set("")
        small_combo.configure(values=[""])
        small_combo.configure(state="disabled")
    else:
        # 都道府県選択時は中項目を有効化
        middle_categories = prefectures_middle_category.get(prefecture, {})
        middle_names = [""] + list(middle_categories.keys())
        middle_combo.configure(values=middle_names)
        middle_combo.configure(state="readonly")
        middle_combo.set("")
        # 小項目をリセット
        small_combo.set("")
        small_combo.configure(values=[""])
        small_combo.configure(state="disabled")

def on_middle_changed(*args):
    """中項目が変更されたときの処理"""
    middle = middle_combo.get()
    
    if middle == "":
        # 中項目未選択時は小項目を無効化
        small_combo.set("")
        small_combo.configure(values=[""])
        small_combo.configure(state="disabled")
    else:
        # 中項目選択時は小項目を有効化
        small_categories = prefectures_small_category.get(middle, {})
        small_names = [""] + list(small_categories.keys())
        small_combo.configure(values=small_names)
        small_combo.configure(state="readonly")
        small_combo.set("")

def choose_save_path():
    """保存先を選択する"""
    folder_selected = filedialog.askdirectory(
        initialdir=save_path_var.get(),
        title="保存先フォルダを選択"
    )
    if folder_selected:
        save_path_var.set(folder_selected)

# スクレイピング停止フラグ
stop_scraping = False

def stop_scraping_process():
    """スクレイピングを停止する"""
    global stop_scraping
    stop_scraping = True
    add_log("スクレイピング停止が要求されました...")

def scrape_data_thread():
    """別スレッドでスクレイピングを実行する（UIのフリーズを防ぐ）"""
    thread = threading.Thread(target=scrape_data)
    thread.daemon = True
    thread.start()

def scrape_data():
    """スクレイピングを実行する"""
    global stop_scraping
    stop_scraping = False
    
    disable_controls()
    update_status("スクレイピングの準備中...")
    add_log("スクレイピングを開始します")
    
    # 進行状況タブに切り替え
    notebook.select(1)
    
    # 設定値の取得
    prefecture = prefecture_combo.get()
    middle = middle_combo.get()
    small = small_combo.get()
    start_page = int(start_page_entry.get()) if start_page_entry.get() else 1
    fifty_page_mode = fifty_page_var.get()
    new_open_mode = new_open_var.get()
    max_pages = 50 if fifty_page_mode else 999
    
    # オープン日フィルタの設定
    filter_year = year_combo.get()
    filter_month = month_combo.get()
    filter_year_int = int(filter_year) if filter_year and filter_year != "指定なし" else 0
    filter_month_int = int(filter_month) if filter_month and filter_month != "指定なし" else 0
    
    # スクレイピングする最大ページ数を計算
    end_page = start_page + max_pages - 1
    
    # コードの取得
    prefecture_code = get_prefecture_code(prefecture)
    middle_code = None
    small_code = None
    
    if middle and prefecture != "全国":
        middle_categories = prefectures_middle_category.get(prefecture, {})
        middle_code = middle_categories.get(middle)
    
    if small:
        small_categories = prefectures_small_category.get(middle, {})
        small_code = small_categories.get(small)
    
    # URL生成
    current_url = generate_tabelog_url(prefecture_code, middle_code, small_code, start_page, new_open_mode)
    
    update_status(f"スクレイピング開始: {current_url}")
    add_log(f"URL: {current_url}")
    
    all_scraped_data = []
    page_count = start_page
    pages_scraped = 0
    
    # 進捗バーの初期化
    progress_var.set(0)
    
    while current_url and page_count <= end_page and not stop_scraping:
        update_status(f"スクレイピング中: ページ {page_count}/{end_page}")
        update_progress(pages_scraped + 1, max_pages)
        add_log(f"ページ {page_count} をスクレイピング中: {current_url}")
        
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            shop_list = soup.find_all('div', class_='list-rst')
            
            shop_count = len(shop_list)
            if shop_count == 0:
                add_log("このページには店舗がありません。")
                break
                
            add_log(f"ページ {page_count} で {shop_count} 件の店舗を発見")
            
            for i, shop in enumerate(shop_list):
                if stop_scraping:
                    break
                    
                update_status(f"ページ {page_count}/{end_page} - 店舗 {i+1}/{shop_count} スクレイピング中")
                detail_url_element = shop.find('a', class_='list-rst__rst-name-target') or shop.find('a', class_='list-rst__title-target')
                if detail_url_element and 'href' in detail_url_element.attrs:
                    shop_url = detail_url_element['href']
                    shop_data = scrape_shop_details(shop_url)
                    
                    # オープン日でフィルタリング
                    if filter_year_int > 0:
                        if filter_by_opened_date(shop_data.get('オープン日', ''), filter_year_int, filter_month_int):
                            all_scraped_data.append(shop_data)
                            add_log(f"  {shop_data.get('店舗名', '不明')} - 追加")
                    else:
                        all_scraped_data.append(shop_data)
                else:
                    add_log("  店舗詳細URLが見つかりませんでした。")
                
                # 負荷軽減のための待機
                time.sleep(0.5)
            
            if stop_scraping:
                add_log("スクレイピングが停止されました")
                break
            
            # このページのスクレイピングが完了
            pages_scraped += 1
            
            # 最大ページ数に達したかチェック
            if pages_scraped >= max_pages:
                add_log(f"最大ページ数({max_pages}ページ)に達しました。スクレイピングを終了します。")
                break
            
            # 次のページを探す
            next_link = soup.find('a', class_='c-pagination__arrow c-pagination__arrow--next')
            if next_link and 'href' in next_link.attrs:
                next_url = next_link['href']
                if not next_url.startswith("https://tabelog.com"):
                    next_url = "https://tabelog.com" + next_url
                current_url = next_url
                page_count += 1
                # ページ間の待機時間を長めに設定
                time.sleep(2)
            else:
                add_log("次のページはありません。")
                break
                
        except requests.exceptions.RequestException as e:
            add_log(f'エラーが発生しました: {e}')
            update_status(f"エラーが発生しました: {e}")
            time.sleep(5)
            break
        except Exception as e:
            add_log(f'予期しないエラーが発生しました: {e}')
            update_status(f"予期しないエラーが発生しました: {e}")
            break
    
    # 結果の保存
    if all_scraped_data:
        update_status("データをExcelに保存中...")
        add_log(f"合計 {len(all_scraped_data)} 件のデータを保存中...")
        
        df = pd.DataFrame(all_scraped_data)
        
        # 不要な空のデータを除外
        df = df[df['店舗名'] != '記載なし']
        
        # 保存先の設定
        save_dir = save_path_var.get()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # ファイル名の作成
        file_prefix_parts = []
        if prefecture != "全国":
            file_prefix_parts.append(prefecture)
        if middle:
            file_prefix_parts.append(middle)
        if small:
            file_prefix_parts.append(small)
        
        if not file_prefix_parts:
            file_prefix_parts.append("全国")
            
        if new_open_mode:
            file_prefix_parts.append("ニューオープン")
            
        if filter_year_int > 0:
            if filter_month_int > 0:
                file_prefix_parts.append(f"{filter_year_int}年{filter_month_int}月")
            else:
                file_prefix_parts.append(f"{filter_year_int}年")
        
        file_prefix = "_".join(file_prefix_parts)
        file_name = f"{file_prefix}_scraped_data_{timestamp}.xlsx"
        file_path = os.path.join(save_dir, file_name)
        
        df.to_excel(file_path, index=False)
        update_status(f"スクレイピングが完了しました。")
        add_log(f"スクレイピングが完了しました。\nファイル名: {file_name}\n保存先: {save_dir}")
    else:
        update_status("スクレイピングに失敗しました。データが取得できませんでした。")
        add_log("データが取得できませんでした。")
    
    enable_controls()
    stop_scraping = False

def create_gui():
    """GUIを作成する"""
    global prefecture_combo, middle_combo, small_combo, start_page_entry, fifty_page_var
    global area_scrape_button, new_open_var, window, year_combo, month_combo
    global progress_var, progress_label, status_label, fifty_page_check, new_open_check
    global save_path_var, save_path_button, log_text, notebook, stop_button
    
    window = tk.Tk()
    window.title("食べログスクレイピングツール")
    window.geometry("700x750")
    
    # ノートブック（タブ）の作成
    notebook = ttk.Notebook(window)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 検索条件タブ
    search_frame = ttk.Frame(notebook)
    notebook.add(search_frame, text="検索条件")
    
    # 進行状況タブ
    progress_frame = ttk.Frame(notebook)
    notebook.add(progress_frame, text="進行状況")
    
    # === 検索条件タブの内容 ===
    search_inner_frame = ttk.Frame(search_frame)
    search_inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # タイトルラベル
    title_label = ttk.Label(search_inner_frame, text="食べログスクレイピングツール", font=("Helvetica", 16))
    title_label.pack(pady=10)
    
    # 保存先選択
    save_frame = ttk.Frame(search_inner_frame)
    save_frame.pack(fill=tk.X, pady=5)
    
    save_label = ttk.Label(save_frame, text="保存先:", width=15)
    save_label.pack(side=tk.LEFT)
    
    save_path_var = tk.StringVar(value=os.path.expanduser("~\\Downloads"))
    save_path_entry = ttk.Entry(save_frame, textvariable=save_path_var, state="readonly")
    save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    save_path_button = ttk.Button(save_frame, text="選択", command=choose_save_path)
    save_path_button.pack(side=tk.LEFT)
    
    # 都道府県選択
    prefecture_frame = ttk.Frame(search_inner_frame)
    prefecture_frame.pack(fill=tk.X, pady=5)
    
    prefecture_label = ttk.Label(prefecture_frame, text="都道府県:", width=15)
    prefecture_label.pack(side=tk.LEFT)
    
    prefecture_values = ["全国"] + list(prefectures_values.keys())
    prefecture_combo = ttk.Combobox(prefecture_frame, values=prefecture_values, state="readonly")
    prefecture_combo.set(prefecture_values[0])
    prefecture_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    prefecture_combo.bind("<<ComboboxSelected>>", on_prefecture_changed)
    
    # 地域（中項目）選択
    middle_frame = ttk.Frame(search_inner_frame)
    middle_frame.pack(fill=tk.X, pady=5)
    
    middle_label = ttk.Label(middle_frame, text="地域（中項目）:", width=15)
    middle_label.pack(side=tk.LEFT)
    
    middle_combo = ttk.Combobox(middle_frame, values=[""], state="disabled")
    middle_combo.set("")
    middle_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    middle_combo.bind("<<ComboboxSelected>>", on_middle_changed)
    
    # 地域（小項目）選択
    small_frame = ttk.Frame(search_inner_frame)
    small_frame.pack(fill=tk.X, pady=5)
    
    small_label = ttk.Label(small_frame, text="地域（小項目）:", width=15)
    small_label.pack(side=tk.LEFT)
    
    small_combo = ttk.Combobox(small_frame, values=[""], state="disabled")
    small_combo.set("")
    small_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # 開始ページ指定
    page_frame = ttk.Frame(search_inner_frame)
    page_frame.pack(fill=tk.X, pady=5)
    
    start_page_label = ttk.Label(page_frame, text="開始ページ:", width=15)
    start_page_label.pack(side=tk.LEFT)
    
    start_page_entry = ttk.Entry(page_frame)
    start_page_entry.insert(0, "1")
    start_page_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    # オプションフレーム
    options_frame = ttk.Frame(search_inner_frame)
    options_frame.pack(fill=tk.X, pady=10)
    
    # 50ページ区切り
    fifty_page_var = tk.BooleanVar(value=True)
    fifty_page_check = ttk.Checkbutton(options_frame, text="50ページ区切り", variable=fifty_page_var)
    fifty_page_check.pack(side=tk.LEFT, padx=(0, 20))
    
    # ニューオープン
    new_open_var = tk.BooleanVar(value=False)
    new_open_check = ttk.Checkbutton(options_frame, text="ニューオープンモード", variable=new_open_var)
    new_open_check.pack(side=tk.LEFT)
    
    # オープン日フィルタ
    date_frame = ttk.Frame(search_inner_frame)
    date_frame.pack(fill=tk.X, pady=5)
    
    date_label = ttk.Label(date_frame, text="オープン日:", width=15)
    date_label.pack(side=tk.LEFT)
    
    # 年選択
    current_year = datetime.now().year
    year_values = ["指定なし"] + [str(year) for year in range(current_year, current_year - 10, -1)]
    year_combo = ttk.Combobox(date_frame, values=year_values, width=10, state="readonly")
    year_combo.set("指定なし")
    year_combo.pack(side=tk.LEFT, padx=(0, 5))
    
    year_label = ttk.Label(date_frame, text="年")
    year_label.pack(side=tk.LEFT, padx=(0, 10))
    
    # 月選択
    month_values = ["指定なし"] + [str(month) for month in range(1, 13)]
    month_combo = ttk.Combobox(date_frame, values=month_values, width=10, state="readonly")
    month_combo.set("指定なし")
    month_combo.pack(side=tk.LEFT, padx=(0, 5))
    
    month_label = ttk.Label(date_frame, text="月")
    month_label.pack(side=tk.LEFT)
    
    # スクレイピング実行ボタン
    button_frame = ttk.Frame(search_inner_frame)
    button_frame.pack(pady=20)
    
    area_scrape_button = ttk.Button(button_frame, text="スクレイピング開始", command=scrape_data_thread)
    area_scrape_button.pack(ipadx=10, ipady=5)
    
    # 説明テキスト
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
    
    help_label = ttk.Label(search_inner_frame, text=help_text, justify=tk.LEFT, wraplength=560)
    help_label.pack(pady=10)
    
    # === 進行状況タブの内容 ===
    progress_inner_frame = ttk.Frame(progress_frame)
    progress_inner_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    # ステータスラベル
    status_label = ttk.Label(progress_inner_frame, text="準備完了", font=("Helvetica", 12))
    status_label.pack(pady=10)
    
    # 進捗バー
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(progress_inner_frame, orient=tk.HORIZONTAL, length=100, mode='determinate', variable=progress_var)
    progress_bar.pack(fill=tk.X, pady=5)
    
    progress_label = ttk.Label(progress_inner_frame, text="進捗: 0/0 ページ")
    progress_label.pack(pady=5)
    
    # 停止ボタン
    stop_button = ttk.Button(progress_inner_frame, text="スクレイピング停止", command=stop_scraping_process, state="disabled")
    stop_button.pack(pady=10)
    
    # ログ表示エリア
    log_label = ttk.Label(progress_inner_frame, text="実行ログ:")
    log_label.pack(anchor=tk.W, pady=(10, 5))
    
    # ログテキストエリアとスクロールバー
    log_frame = ttk.Frame(progress_inner_frame)
    log_frame.pack(fill=tk.BOTH, expand=True)
    
    log_scrollbar = ttk.Scrollbar(log_frame)
    log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    log_text = tk.Text(log_frame, height=15, wrap=tk.WORD, yscrollcommand=log_scrollbar.set)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    log_scrollbar.config(command=log_text.yview)
    
    # ログテキストを読み取り専用に
    log_text.bind("<Key>", lambda e: "break")
    
    window.mainloop()

if __name__ == "__main__":
    requests_cache.install_cache('tabelog_cache', expire_after=3600)
    create_gui()
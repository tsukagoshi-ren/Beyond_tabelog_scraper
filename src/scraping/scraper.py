"""
スクレイピングコア機能
"""

import threading
import time
import requests
from bs4 import BeautifulSoup

from .url_builder import URLBuilder
from .parser import Parser
from utils import DateFilter, FileHandler
from data import prefectures_values, prefectures_middle_category, prefectures_small_category
from config import Settings


class Scraper:
    """スクレイパークラス"""
    
    def __init__(self):
        self.stop_flag = False
        self.thread = None
        
    def start(self, search_params, progress_callback=None, status_callback=None, 
              log_callback=None, complete_callback=None):
        """スクレイピングを開始"""
        self.stop_flag = False
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.log_callback = log_callback
        self.complete_callback = complete_callback
        
        # 別スレッドで実行
        self.thread = threading.Thread(target=self._scrape, args=(search_params,))
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """スクレイピングを停止"""
        self.stop_flag = True
        
    def _scrape(self, search_params):
        """スクレイピングの実行"""
        try:
            self._update_status("スクレイピングの準備中...")
            self._add_log("スクレイピングを開始します")
            
            # パラメータの解析
            params = self._parse_params(search_params)
            
            # URL生成
            current_url = URLBuilder.build(
                prefecture_code=params['prefecture_code'],
                middle_code=params['middle_code'],
                small_code=params['small_code'],
                start_page=params['start_page'],
                new_open_mode=params['new_open_mode']
            )
            
            self._update_status(f"スクレイピング開始: {current_url}")
            self._add_log(f"URL: {current_url}")
            
            # スクレイピング実行
            all_scraped_data = []
            page_count = params['start_page']
            pages_scraped = 0
            
            while current_url and page_count <= params['end_page'] and not self.stop_flag:
                self._update_status(f"スクレイピング中: ページ {page_count}/{params['end_page']}")
                self._update_progress(pages_scraped + 1, params['max_pages'])
                self._add_log(f"ページ {page_count} をスクレイピング中: {current_url}")
                
                # ページのスクレイピング
                page_data, next_url = self._scrape_page(current_url, params)
                
                if page_data:
                    all_scraped_data.extend(page_data)
                    pages_scraped += 1
                    
                    # 最大ページ数に達したかチェック
                    if pages_scraped >= params['max_pages']:
                        self._add_log(f"最大ページ数({params['max_pages']}ページ)に達しました。")
                        break
                        
                    # 次のページへ
                    if next_url:
                        current_url = next_url
                        page_count += 1
                        time.sleep(Settings.PAGE_WAIT_TIME)
                    else:
                        self._add_log("次のページはありません。")
                        break
                else:
                    break
                    
            # 結果の保存
            if all_scraped_data and not self.stop_flag:
                self._save_results(all_scraped_data, search_params)
            elif self.stop_flag:
                self._add_log("スクレイピングが停止されました")
                self._update_status("スクレイピングが停止されました")
            else:
                self._update_status("データが取得できませんでした。")
                self._add_log("データが取得できませんでした。")
                
        except Exception as e:
            self._add_log(f"エラーが発生しました: {e}")
            self._update_status(f"エラーが発生しました: {e}")
            
        finally:
            if self.complete_callback:
                self.complete_callback()
                
    def _parse_params(self, search_params):
        """検索パラメータを解析"""
        # 基本パラメータ
        start_page = search_params.get('start_page', 1)
        fifty_page_mode = search_params.get('fifty_page_mode', True)
        max_pages = 50 if fifty_page_mode else 999
        end_page = start_page + max_pages - 1
        
        # 地域コードの取得
        prefecture = search_params.get('prefecture', '')
        middle = search_params.get('middle', '')
        small = search_params.get('small', '')
        
        prefecture_code = self._get_prefecture_code(prefecture)
        middle_code = None
        small_code = None
        
        if middle and prefecture != "全国":
            middle_categories = prefectures_middle_category.get(prefecture, {})
            middle_code = middle_categories.get(middle)
            
        if small:
            small_categories = prefectures_small_category.get(middle, {})
            small_code = small_categories.get(small)
            
        # フィルタ設定
        filter_year = search_params.get('filter_year', '指定なし')
        filter_month = search_params.get('filter_month', '指定なし')
        filter_year_int = int(filter_year) if filter_year != '指定なし' else 0
        filter_month_int = int(filter_month) if filter_month != '指定なし' else 0
        
        return {
            'start_page': start_page,
            'end_page': end_page,
            'max_pages': max_pages,
            'new_open_mode': search_params.get('new_open_mode', False),
            'prefecture_code': prefecture_code,
            'middle_code': middle_code,
            'small_code': small_code,
            'filter_year': filter_year_int,
            'filter_month': filter_month_int
        }
        
    def _get_prefecture_code(self, prefecture):
        """都道府県名から都道府県コードを取得"""
        if prefecture == "全国":
            return ""
        return prefectures_values.get(prefecture, "")
        
    def _scrape_page(self, url, params):
        """1ページをスクレイピング"""
        try:
            response = requests.get(url, timeout=Settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 店舗リストを取得
            shop_list = soup.find_all('div', class_='list-rst')
            
            if not shop_list:
                self._add_log("このページには店舗がありません。")
                return None, None
                
            self._add_log(f"ページで {len(shop_list)} 件の店舗を発見")
            
            page_data = []
            parser = Parser()
            
            for i, shop in enumerate(shop_list):
                if self.stop_flag:
                    break
                    
                # 店舗URLを取得
                detail_url_element = shop.find('a', class_='list-rst__rst-name-target') or \
                                   shop.find('a', class_='list-rst__title-target')
                                   
                if detail_url_element and 'href' in detail_url_element.attrs:
                    shop_url = detail_url_element['href']
                    shop_data = parser.parse_shop_details(shop_url)
                    
                    # オープン日でフィルタリング
                    if params['filter_year'] > 0:
                        if DateFilter.filter_by_opened_date(
                            shop_data.get('オープン日', ''), 
                            params['filter_year'], 
                            params['filter_month']
                        ):
                            page_data.append(shop_data)
                            self._add_log(f"  {shop_data.get('店舗名', '不明')} - 追加")
                    else:
                        page_data.append(shop_data)
                        
                time.sleep(Settings.SHOP_WAIT_TIME)
                
            # 次のページURLを取得
            next_link = soup.find('a', class_='c-pagination__arrow c-pagination__arrow--next')
            next_url = None
            if next_link and 'href' in next_link.attrs:
                next_url = next_link['href']
                if not next_url.startswith("https://tabelog.com"):
                    next_url = "https://tabelog.com" + next_url
                    
            return page_data, next_url
            
        except requests.exceptions.RequestException as e:
            self._add_log(f'エラーが発生しました: {e}')
            return None, None
            
    def _save_results(self, data, search_params):
        """結果を保存"""
        self._update_status("データをExcelに保存中...")
        self._add_log(f"合計 {len(data)} 件のデータを保存中...")
        
        file_handler = FileHandler()
        file_path = file_handler.save_to_excel(data, search_params)
        
        if file_path:
            file_name = file_path.name
            save_dir = file_path.parent
            self._update_status("スクレイピングが完了しました。")
            self._add_log(f"スクレイピングが完了しました。\nファイル名: {file_name}\n保存先: {save_dir}")
        else:
            self._update_status("ファイルの保存に失敗しました。")
            self._add_log("ファイルの保存に失敗しました。")
            
    def _update_progress(self, current, total):
        """進捗を更新"""
        if self.progress_callback:
            self.progress_callback(current, total)
            
    def _update_status(self, text):
        """ステータスを更新"""
        if self.status_callback:
            self.status_callback(text)
            
    def _add_log(self, text):
        """ログを追加"""
        if self.log_callback:
            self.log_callback(text)
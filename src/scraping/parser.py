"""
HTML解析機能
"""

import time
import requests
from bs4 import BeautifulSoup

from config import Settings


class Parser:
    """HTMLパーサークラス"""
    
    def parse_shop_details(self, shop_url):
        """店舗詳細ページから情報を取得する"""
        retry_count = 0
        wait_time = Settings.RETRY_WAIT_TIME
        
        while retry_count < Settings.MAX_RETRIES:
            try:
                response = requests.get(shop_url, timeout=Settings.REQUEST_TIMEOUT)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 店舗情報を抽出
                shop_data = {
                    '店舗名': self._extract_name(soup),
                    'ジャンル': self._extract_genre(soup),
                    '住所': self._extract_address(soup),
                    'オープン日': self._extract_opened_date(soup),
                    '電話番号': self._extract_phone(soup),
                    'URL': shop_url,
                    '営業時間/定休日': self._extract_opening_hours(soup),
                    '公式アカウント': self._extract_instagram(soup),
                    'サービス': self._extract_service(soup)
                }
                
                return shop_data
                
            except requests.exceptions.RequestException as e:
                print(f'{shop_url}でエラーが発生しました: {e}')
                retry_count += 1
                time.sleep(wait_time)
                wait_time *= 2  # エクスポネンシャルバックオフ
            except AttributeError as e:
                print(f'{shop_url}で要素の取得に失敗しました: {e}')
                retry_count += 1
                time.sleep(wait_time)
            except Exception as e:
                print(f'{shop_url}で予期しないエラーが発生しました: {e}')
                return self._get_empty_data(shop_url)
                
        return self._get_empty_data(shop_url)
        
    def _extract_name(self, soup):
        """店舗名を抽出"""
        name_element = soup.find('h2', class_='display-name') or \
                      soup.find('h2', class_='rstdtl-header__rst-name')
        return name_element.text.strip() if name_element else Settings.NO_DATA_VALUE
        
    def _extract_address(self, soup):
        """住所を抽出"""
        address_element = soup.find('p', class_='rstinfo-table__address') or \
                         soup.find('p', class_='rstinfo-table__address-text')
        return address_element.text.strip() if address_element else Settings.NO_DATA_VALUE
        
    def _extract_opening_hours(self, soup):
        """営業時間を抽出"""
        opening_hours_element = None
        for heading in soup.find_all(['th', 'dt']):
            if '営業時間' in heading.text:
                opening_hours_element = heading.find_next(['td', 'dd'])
                break
        return opening_hours_element.text.strip() if opening_hours_element else Settings.NO_DATA_VALUE
        
    def _extract_phone(self, soup):
        """電話番号を抽出"""
        phone_element = soup.find('p', class_='rstdtl-side-yoyaku__tel-number') or \
                       soup.find('strong', class_='rstinfo-table__tel-num')
        return phone_element.text.strip() if phone_element else Settings.NO_DATA_VALUE
        
    def _extract_opened_date(self, soup):
        """オープン日を抽出"""
        opened_date_element = soup.find('p', class_='rstinfo-opened-date')
        return opened_date_element.text.strip() if opened_date_element else Settings.NO_DATA_VALUE
        
    def _extract_instagram(self, soup):
        """Instagramアカウントを抽出"""
        instagram_element = soup.find('a', class_='rstinfo-sns-instagram')
        return instagram_element['href'] if instagram_element and 'href' in instagram_element.attrs else Settings.NO_DATA_VALUE
        
    def _extract_service(self, soup):
        """サービス情報を抽出"""
        service = Settings.NO_DATA_VALUE
        for th in soup.find_all('th'):
            if 'サービス' in th.text:
                next_td = th.find_next('td')
                if next_td:
                    service = next_td.get_text(strip=True)
                break
        return service
        
    def _extract_genre(self, soup):
        """ジャンル情報を抽出"""
        genre = Settings.NO_DATA_VALUE
        for th in soup.find_all('th'):
            if 'ジャンル' in th.text:
                next_td = th.find_next('td')
                if next_td:
                    genre = next_td.get_text(strip=True)
                break
        return genre
        
    def _get_empty_data(self, shop_url):
        """空のデータを返す"""
        return {field: Settings.NO_DATA_VALUE for field in Settings.SHOP_FIELDS} | {'URL': shop_url}
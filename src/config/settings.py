"""
アプリケーション設定
"""

import os


class Settings:
    """アプリケーション設定クラス"""
    
    # アプリケーション情報
    APP_NAME = "食べログスクレイピングツール"
    APP_VERSION = "2.0.0"
    
    # ウィンドウ設定
    WINDOW_WIDTH = 700
    WINDOW_HEIGHT = 750
    
    # スクレイピング設定
    MAX_RETRIES = 3  # リトライ回数
    RETRY_WAIT_TIME = 5  # リトライ待機時間（秒）
    REQUEST_TIMEOUT = 10  # リクエストタイムアウト（秒）
    PAGE_WAIT_TIME = 2  # ページ間待機時間（秒）
    SHOP_WAIT_TIME = 0.5  # 店舗間待機時間（秒）
    
    # デフォルト値
    DEFAULT_MAX_PAGES = 50  # デフォルトの最大ページ数
    DEFAULT_START_PAGE = 1  # デフォルトの開始ページ
    DEFAULT_SAVE_PATH = os.path.expanduser("~\\Downloads")  # デフォルトの保存先
    
    # キャッシュ設定
    CACHE_NAME = 'tabelog_cache'
    CACHE_EXPIRE_AFTER = 3600  # キャッシュ有効期限（秒）
    
    # Excel出力設定
    EXCEL_ENGINE = 'openpyxl'
    EXCEL_INDEX = False
    
    # 店舗情報フィールド
    SHOP_FIELDS = [
        '店舗名',
        'ジャンル',
        '住所',
        'オープン日',
        '電話番号',
        'URL',
        '営業時間/定休日',
        '公式アカウント',
        'サービス'
    ]
    
    # デフォルト値（データがない場合）
    NO_DATA_VALUE = '記載なし'
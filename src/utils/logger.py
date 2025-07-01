"""
ログ管理機能
"""

import logging
from datetime import datetime
from pathlib import Path


class Logger:
    """ログ管理クラス"""
    
    def __init__(self, name='TabeLogScraper', log_dir='logs'):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # ログファイル名の生成
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"{name}_{timestamp}.log"
        
        # ロガーの設定
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # ファイルハンドラーの設定
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # コンソールハンドラーの設定
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # フォーマッターの設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # ハンドラーの追加
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
    def debug(self, message):
        """デバッグメッセージ"""
        self.logger.debug(message)
        
    def info(self, message):
        """情報メッセージ"""
        self.logger.info(message)
        
    def warning(self, message):
        """警告メッセージ"""
        self.logger.warning(message)
        
    def error(self, message):
        """エラーメッセージ"""
        self.logger.error(message)
        
    def critical(self, message):
        """重大なエラーメッセージ"""
        self.logger.critical(message)
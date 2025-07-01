"""
オープン日フィルタリング機能
"""

import re


class DateFilter:
    """日付フィルタリングクラス"""
    
    @staticmethod
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
    
    @staticmethod
    def filter_by_opened_date(opened_date_text, filter_year, filter_month=0):
        """
        オープン日でフィルタリングする
        
        Args:
            opened_date_text (str): オープン日のテキスト
            filter_year (int): フィルタリング用の年
            filter_month (int): フィルタリング用の月（0の場合は年のみでフィルタ）
        
        Returns:
            bool: フィルタリング条件に合致するかどうか
        """
        parsed_date = DateFilter.parse_opened_date(opened_date_text)
        
        if not parsed_date:
            return False
        
        year, month = parsed_date
        
        # 年のみでフィルタリング
        if filter_month == 0:
            return year == filter_year
        
        # 年月でフィルタリング
        return year == filter_year and month == filter_month
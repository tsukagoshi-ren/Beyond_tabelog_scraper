"""
ファイル保存処理
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path

from config import Settings


class FileHandler:
    """ファイルハンドラークラス"""
    
    def save_to_excel(self, data, search_params):
        """データをExcelファイルとして保存"""
        try:
            # DataFrameの作成
            df = pd.DataFrame(data)
            
            # 空のデータを除外
            df = df[df['店舗名'] != Settings.NO_DATA_VALUE]
            
            if df.empty:
                return None
                
            # ファイル名の生成
            file_name = self._generate_filename(search_params)
            
            # 保存先パスの生成
            save_dir = search_params.get('save_path', Settings.DEFAULT_SAVE_PATH)
            file_path = Path(save_dir) / file_name
            
            # Excelファイルとして保存
            df.to_excel(
                file_path, 
                index=Settings.EXCEL_INDEX,
                engine=Settings.EXCEL_ENGINE
            )
            
            return file_path
            
        except Exception as e:
            print(f"ファイル保存エラー: {e}")
            return None
            
    def _generate_filename(self, search_params):
        """ファイル名を生成"""
        # タイムスタンプ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # ファイル名の部品を作成
        parts = []
        
        # 地域情報
        prefecture = search_params.get('prefecture', '')
        middle = search_params.get('middle', '')
        small = search_params.get('small', '')
        
        if prefecture and prefecture != "全国":
            parts.append(prefecture)
        if middle:
            parts.append(middle)
        if small:
            parts.append(small)
            
        if not parts:
            parts.append("全国")
            
        # モード情報
        if search_params.get('new_open_mode'):
            parts.append("ニューオープン")
            
        # フィルタ情報
        filter_year = search_params.get('filter_year', '')
        filter_month = search_params.get('filter_month', '')
        
        if filter_year and filter_year != '指定なし':
            year_int = int(filter_year)
            if filter_month and filter_month != '指定なし':
                month_int = int(filter_month)
                parts.append(f"{year_int}年{month_int}月")
            else:
                parts.append(f"{year_int}年")
                
        # ファイル名の組み立て
        prefix = "_".join(parts)
        file_name = f"{prefix}_scraped_data_{timestamp}.xlsx"
        
        return file_name
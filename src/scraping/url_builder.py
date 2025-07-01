"""
食べログURL生成機能
"""


class URLBuilder:
    """URL生成クラス"""
    
    BASE_URL = "https://tabelog.com"
    
    @staticmethod
    def build(prefecture_code="", middle_code=None, small_code=None, 
              start_page=1, new_open_mode=False):
        """
        食べログのURLを生成する
        
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
            base_path = f"{URLBuilder.BASE_URL}/{'/'.join(path_parts)}"
        else:
            base_path = URLBuilder.BASE_URL
        
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
                    url = f"{URLBuilder.BASE_URL}/rstLst/cond16-00-00/{start_page}/"
                else:
                    url = f"{URLBuilder.BASE_URL}/rstLst/cond16-00-00/"
            else:
                if start_page > 1:
                    url = f"{URLBuilder.BASE_URL}/rstLst/{start_page}/"
                else:
                    url = f"{URLBuilder.BASE_URL}/rstLst/"
        
        return url
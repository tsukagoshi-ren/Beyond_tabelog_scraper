"""
データ管理モジュール
"""

# 互換性のため、既存のインポート方法もサポート
try:
    from .prefectures import prefectures_values
    from .middle_categories import prefectures_middle_category
    from .small_categories import prefectures_small_category
except ImportError:
    # ファイル名が変更されていない場合の対応
    try:
        from .middle_categorys import prefectures_middle_category
        from .small_categorys import prefectures_small_category
    except ImportError:
        prefectures_middle_category = {}
        prefectures_small_category = {}

__all__ = [
    'prefectures_values',
    'prefectures_middle_category',
    'prefectures_small_category'
]
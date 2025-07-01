#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
食べログスクレイピングツール - メインエントリーポイント
"""

import os
import sys
import requests_cache

# 環境変数設定
os.environ['TK_SILENCE_DEPRECATION'] = '1'

# モジュールのインポート
from gui.main_window import MainWindow


def main():
    """メイン関数"""
    # キャッシュの設定
    requests_cache.install_cache('tabelog_cache', expire_after=3600)
    
    # GUIアプリケーションの起動
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
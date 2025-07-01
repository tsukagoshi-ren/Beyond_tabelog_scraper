#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
食べログスクレイピングツール - 開発用実行スクリプト
開発環境でアプリケーションを起動する
"""

import sys
import os

# srcディレクトリをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from main import main
    main()
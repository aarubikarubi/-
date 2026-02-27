# TODO: UIレイアウト崩れの抜本的修正

- [x] 1. `src/setup_ui.py` のバックアップを取る
- [x] 2. 設定エリア全体を `QScrollArea` で囲むようにリファクタリング
    - [x] 背景を透明、枠線を消去するQSSの設定
- [x] 3. メインウィンドウに適切な `setMinimumSize(850, 600)` を設定
- [x] 4. 各種ラベル（説明文など）に `setWordWrap(True)` を設定
- [x] 5. レイアウトのマージン・スペーシングの調整
- [x] 6. 動作確認（ウィンドウサイズ変更時の挙動チェック）

# TODO: QSSボタンスタイルの修正

- [x] 1. `src/setup_ui.py` の `MODERN_QSS` に `QPushButton:disabled` スタイルを追加
- [x] 2. `QScrollArea` 内のボタンに正しくスタイルが当たるよう、セレクタまたはID指定を見直す
- [x] 3. 「日課を開始」「すべてのゲームをリセット」「自動検出」ボタンの `setObjectName` を再確認
- [x] 4. 動作確認（スタイルの復旧とグレーアウトの確認）

# TODO: ボタンの視認性向上とレイアウト調整

- [x] 1. `src/setup_ui.py` の `MODERN_QSS` を修正し、ボタンの文字色を黒に強制化
- [x] 2. `init_app_settings` でリセットボタンを左下に配置（QHBoxLayout + Stretch）
- [x] 3. 動作確認（色の視認性と配置の正常性チェック）

# TODO: ツールチップ真っ黒バグの完全修正

- [x] 1. `src/setup_ui.py` の `QToolTip` スタイルに `!important` を追加し、数値をユーザー指定に合わせる
- [x] 2. `GameSetupApp` で `setStyleSheet` が確実にアプリケーション全体に適用されるようにする
- [x] 3. 動作確認（ツールチップが白背景・黒文字で表示されるか）

# TODO: ツールチップ「真っ黒バグ」の絶対的解消（物理修正版）

- [ ] 1. `src/setup_ui.py` の `make_help_icon` をHTMLリッチテキスト形式のツールチップに修正
- [ ] 2. `src/setup_ui.py` 内の他の `setToolTip` 箇所をリッチテキスト化
- [ ] 3. `GameSetupApp` で `QPalette` を用い、ツールチップの色を強制上書き
- [ ] 4. 動作確認（物理的な色指定の強制力の確認）

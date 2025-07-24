# movie-generator

このプロジェクトは、Googleの生成AIモデル（Veo, Lyria）とFFmpegを組み合わせて、複数の短い動画クリップとBGMを生成し、それらを結合して一つの完成された動画を作成するツールです。

**使用しているMCPサーバーとサービス:**

*   **mcp-veo-go**: GoogleのVeoモデル（`veo_t2v`サービス）を呼び出し、テキストプロンプトから動画を生成します。
*   **mcp-lyria-go**: GoogleのLyriaモデル（`lyria_generate_music`サービス）を呼び出し、テキストプロンプトからBGMを生成します。
*   **FFmpeg**: 生成された動画クリップの連結や、動画とBGMの合成に使用します。

## 実行方法

このプロジェクトは、以下の3つの方法で実行できます。

### 1. Gemini CLI を使用して実行する

Gemini CLI を使用すると、対話形式で動画生成プロセスを制御できます。
<br>
※環境変数が.zshrcを読み込んでいる場合は、PROJECT_ID, LOCATION, GENMEDIA_BUCKETの記載が必要        

1.  **Gemini CLI を起動します。**

    ```bash
    # ログイン（確認 gcloud auth list）
    gcloud auth application-default login

    # Gemini CLI の起動コマンド（環境に合わせて調整してください）
    gemini-cli
    ```

2.  **対話形式で指示を出します。**
    例えば、以下のように指示を出すことで、動画生成プロセスを開始できます。

    ```
    python3 generate_video.py を実行して下さい
    ```
    Gemini CLI は、`generate_video.py` スクリプトの実行、エラーの修正、ファイルの移動など、一連のタスクを自動的に処理します。

### 2. Python コマンドを使用して実行する

`generate_video.py` スクリプトを直接Pythonコマンドで実行できます。

1.  **必要なライブラリをインストールします。**

    ```bash
    pip install -r requirements.txt
    ```

2.  **環境変数を設定します。**
    `.env` ファイルに `GENMEDIA_BUCKET` などの必要な環境変数を設定してください。

    ```
    # .env ファイルの例
    GENMEDIA_BUCKET=your-gcs-bucket-name
    ```

3.  **スクリプトを実行します。**

    ```bash
    python3 generate_video.py
    ```

    **例: 3つの動画プロンプトとBGMプロンプトを指定して実行する**

    ```bash
    python3 generate_video.py \
      --video_prompts "穏やかな夏の浜辺の夕暮れ、静かに打ち寄せる波の様子" \
                      "賑やかな夜の都市、タイムラプスで走る車のライト" \
                      "朝の森に差し込む朝日で木漏れ日が揺れる風景" \
      --music_prompt "Bright tropical instrumental BGM with percussion, synth pads, and marimba. No vocals, lyrics, or dialogue."
    ```

### 3. シェルスクリプトを使用して実行する

`generate_video.py` スクリプトの実行を自動化するシェルスクリプトを作成し、実行することも可能です。

1.  **`run_generator.sh` ファイルを作成します。**

    ```bash
    #!/bin/bash

    # 必要なライブラリをインストール
    pip install -r requirements.txt

    # Pythonスクリプトを実行
    python3 generate_video.py

    echo "動画生成プロセスが完了しました。"
    ```

2.  **実行権限を付与します。**

    ```bash
    chmod +x run_generator.sh
    ```

3.  **スクリプトを実行します。**

    ```bash
    ./run_generator.sh
    ```

## 出力ファイル

生成された動画クリップ、BGM、および最終的な動画は、`outputs/` ディレクトリ以下に保存されます。

```
└── outputs/                     # 生成メディアの出力先ディレクトリ
    ├── clips/                   # 各8秒クリップのアーカイブ
    │   └── YYYYMMDD_HHMMSS/     # 処理実行日時ごとのアーカイブ
    │       ├── video0.mp4
    │       ├── video1.mp4
    │       └── video2.mp4
    ├── music/                   # 生成された BGM／音声ファイル
    │   └── music0.mp3
    ├── combined/                # 連結前後の中間ファイル
    │   └── combined_video.mp4
    └── final/                   # 最終出力（24秒動画）
        └── final_video_YYYYMMDD_HHMMSS.mp4
```
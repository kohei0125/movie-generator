#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv
import json
from datetime import datetime
import shutil
import argparse

# 1. .env を読み込んで環境変数に反映
load_dotenv()

# ディレクトリ設定
BASE_DIR    = Path(__file__).parent
CLIPS_DIR   = BASE_DIR / "outputs" / "clips"
MUSIC_DIR   = BASE_DIR / "outputs" / "music"
FINAL_DIR   = BASE_DIR / "outputs" / "final"

# 2. 動画クリップ生成
def generate_clips(prompts):
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)
    for i, prompt in enumerate(prompts):
        params = {
            "prompt": prompt,
            "model": "Veo 2",
            "duration": 8,
            "bucket": f"gs://{os.getenv("GENMEDIA_BUCKET")}",
            "output_directory": str(CLIPS_DIR)
        }
        cmd = [
            "mcptools", "call", "veo_t2v",
            "--params", json.dumps(params),
            str(BASE_DIR / "mcp" / "mcp-veo-go")
        ]
        print()
        print(f">>> クリップ生成: {prompt}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("mcptools stdout:", result.stdout)
        print("mcptools stderr:", result.stderr)

        generated_file = CLIPS_DIR / "sample_0.mp4"
        new_clip_path = CLIPS_DIR / f"video{i}.mp4"
        if generated_file.exists():
            generated_file.rename(new_clip_path)
            print(f"リネーム: {generated_file.name} -> {new_clip_path.name}")
        else:
            print(f"警告: {generated_file.name} が見つかりませんでした。")

# 3. BGM生成
def generate_music(prompt):
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    out_file = MUSIC_DIR / "music0.mp3"
    params = {
        "prompt": prompt,
        "output_gcs_bucket": f"gs://{os.getenv("GENMEDIA_BUCKET")}",
        "local_path": str(MUSIC_DIR),
        "file_name": out_file.name
    }
    cmd = [
        "mcptools", "call", "lyria_generate_music",
        "--params", json.dumps(params),
        str(BASE_DIR / "mcp" / "mcp-lyria-go")
    ]
    print(">>> BGM生成")
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("mcptools stdout:", result.stdout)
    print("mcptools stderr:", result.stderr)
    return out_file

# 4. クリップ連結＆音声合成
def combine_media(clip_paths, music_path):
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_video = FINAL_DIR / f"final_video_{timestamp}.mp4"

    list_file = BASE_DIR / "outputs" / "videos.txt"
    with list_file.open("w") as f:
        for clip in clip_paths:
            f.write(f"file '{str(clip.resolve())}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-i", str(music_path),
        "-c:v", "copy", "-c:a", "aac", "-shortest",
        str(final_video)
    ]
    print(">>> 動画連結とBGM合成")
    subprocess.run(cmd, check=True)
    print(f"✅ 完成動画: {final_video}")

    list_file.unlink(missing_ok=True)
    print(f"一時ファイル {list_file.name} を削除しました。")

# 5. メイン
def main():
    parser = argparse.ArgumentParser(description="Generate video clips and combine them with background music.")
    parser.add_argument(
        "--video_prompts", 
        nargs='+', 
        default=[
            "穏やかな夏の浜辺の夕暮れ、静かに打ち寄せる波の様子",
            "賑やかな夜の都市、タイムラプスで走る車のライト",
            "朝の森に差し込む朝日で木漏れ日が揺れる風景"
        ],
        help="List of prompts for video clip generation. Each prompt will generate an 8-second clip."
    )
    parser.add_argument(
        "--music_prompt", 
        type=str, 
        default="Relaxing music.",
        help="Prompt for background music generation."
    )
    args = parser.parse_args()

    try:
        generate_clips(args.video_prompts)
        music_file = generate_music(args.music_prompt)
        clip_files = sorted(CLIPS_DIR.glob("video*.mp4"))
        combine_media(clip_files, music_file)

        # 処理完了後、clipsディレクトリの内容をタイムスタンプ付きのサブディレクトリに移動
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_target_dir = CLIPS_DIR / timestamp # outputs/clips/YYYYMMDD_HHMMSS
        
        archive_target_dir.mkdir(parents=True, exist_ok=True) 

        for clip_file in CLIPS_DIR.iterdir():
            if clip_file.is_file():
                shutil.move(clip_file, archive_target_dir / clip_file.name)
        shutil.rmtree(CLIPS_DIR)
        print(f"clipsディレクトリの内容を {archive_target_dir} に移動し、元のclipsディレクトリを削除しました。")

    except subprocess.CalledProcessError as e:
        print("⚠️ 処理中にエラーが発生しました:", e, file=sys.stderr)
        print("コマンド:", e.cmd, file=sys.stderr)
        print("標準出力:", e.stdout.decode() if e.stdout else "(なし)", file=sys.stderr)
        print("標準エラー出力:", e.stderr.decode() if e.stderr else "(なし)", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
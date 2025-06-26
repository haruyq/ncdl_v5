import subprocess
import argparse
import sys
import re
import os

def run_command(command):
    """コマンドを実行し、標準出力を返す"""
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.stdout.strip()
    except FileNotFoundError:
        print(f"エラー: 'git' コマンドが見つかりません。Gitがインストールされ、PATHが通っているか確認してください。")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"エラー: コマンド '{' '.join(command)}' の実行に失敗しました。")
        print(f"終了コード: {e.returncode}")
        print(f"標準出力:\n{e.stdout}")
        print(f"標準エラー:\n{e.stderr}")
        sys.exit(1)

def get_latest_tag():
    """
    最新のGitタグを取得する。
    タグが存在しない場合はNoneを返す。
    """
    try:
        latest_tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        ).strip()
        return latest_tag
    except subprocess.CalledProcessError as e:
        if "fatal: No names found" in e.stderr:
            return None
        else:
            print(f"エラー: 'git describe' の実行中に予期せぬエラーが発生しました。")
            print(f"Gitからのエラーメッセージ:\n{e.stderr}")
            sys.exit(1)

def get_version_from_file(filepath):
    """main.pyから__version__を読み取る"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", content, re.M)
            if match:
                return f"v{match.group(1)}"
        print(f"エラー: {filepath} 内に __version__ が見つかりませんでした。")
        sys.exit(1)
    except FileNotFoundError:
        print(f"エラー: {filepath} が見つかりません。")
        sys.exit(1)

def update_version_in_file(filepath, new_version):
    """main.pyの__version__を更新する"""
    version_number = new_version.lstrip('v')
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content, count = re.subn(
        r"^(__version__\s*=\s*['\"])([^'\"]*)(['\"])",
        f"\\g<1>{version_number}\\g<3>",
        content,
        count=1,
        flags=re.M
    )

    if count == 0:
        print(f"エラー: {filepath} 内で __version__ の行を置換できませんでした。")
        sys.exit(1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"{filepath} のバージョンを {version_number} に更新しました。")


def bump_version(version_str, part_to_bump):
    """指定されたパートのバージョンを1つ上げる"""
    if version_str.startswith('v'):
        version_str = version_str[1:]

    parts = list(map(int, version_str.split('.')))
    
    if part_to_bump == 'major':
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif part_to_bump == 'minor':
        parts[1] += 1
        parts[2] = 0
    elif part_to_bump == 'patch':
        parts[2] += 1

    return f"v{'.'.join(map(str, parts))}"

def main():
    parser = argparse.ArgumentParser(
        description="Gitのバージョンタグを自動で生成し、プッシュします。",
        usage="python %(prog)s {major|minor|patch|vX.Y.Z}"
    )
    parser.add_argument(
        "version_spec",
        help="上げるバージョンパート('major', 'minor', 'patch')、または特定のバージョン ('v1.2.3'など) を指定します。"
    )
    args = parser.parse_args()
    version_spec = args.version_spec

    # --- ここからが変更箇所 ---
    new_version = ""
    # 引数が major, minor, patch の場合
    if version_spec in ['major', 'minor', 'patch']:
        main_py_path = 'main.py'
        latest_tag = get_latest_tag()
        if latest_tag:
            current_version = latest_tag
            print(f"現在の最新タグ: {current_version}")
        else:
            print("Gitタグが見つかりません。")
            current_version = get_version_from_file(main_py_path)
            print(f"{main_py_path}からバージョンを取得しました: {current_version}")
        
        new_version = bump_version(current_version, version_spec)
        print(f"作成する新しいバージョン: {new_version}")

    # 引数が vX.Y.Z 形式の場合
    elif re.match(r"^v\d+\.\d+\.\d+$", version_spec):
        new_version = version_spec
        print(f"指定された新しいバージョン: {new_version}")

    # どちらでもない無効な引数の場合
    else:
        print(f"エラー: 引数 '{version_spec}' は無効です。")
        parser.print_help()
        sys.exit(1)
    # --- ここまでが変更箇所 ---

    # 確認
    confirm = input(f"バージョンを {new_version} に更新し、コミット・タグ作成・プッシュを実行しますか？ (y/n): ").lower()
    if confirm != 'y':
        print("処理を中断しました。")
        sys.exit(0)
        
    # main.py の __version__ を更新
    update_version_in_file('main.py', new_version)

    # すべての変更をコミット
    commit_message = f"chore: bump version to {new_version}"
    print(f"すべての変更をコミットしています... (メッセージ: '{commit_message}')")
    run_command(["git", "add", "."])
    run_command(["git", "commit", "-m", commit_message])
    
    # 新しいタグを作成
    print(f"ローカルにタグ '{new_version}' を作成しています...")
    run_command(["git", "tag", new_version])

    # コミットとタグをリモートリポジトリにプッシュ
    print(f"リモートリポジトリにコミットとタグをプッシュしています...")
    run_command(["git", "push", "origin"])
    run_command(["git", "push", "origin", new_version])

    print("\n完了しました！")

if __name__ == "__main__":
    main()
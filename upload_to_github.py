import os
import sys
import base64
import json
import urllib.request
import urllib.error

def upload_to_github(token, repo_owner, repo_name, branch="main", directory="."):
    """Uploads files to GitHub using the REST API."""
    api_base = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    
    # 1. Get the latest commit SHA
    try:
        req = urllib.request.Request(f"{api_base}/git/refs/heads/{branch}")
        req.add_header("Authorization", f"token {token}")
        with urllib.request.urlopen(req) as response:
            ref_data = json.loads(response.read().decode())
            latest_commit_sha = ref_data["object"]["sha"]
    except urllib.error.HTTPError as e:
        print(f"Error accessing repository {repo_owner}/{repo_name} branch {branch}: {e}")
        return

    # 2. Get the base tree SHA
    req = urllib.request.Request(f"{api_base}/git/commits/{latest_commit_sha}")
    req.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(req) as response:
        commit_data = json.loads(response.read().decode())
        base_tree_sha = commit_data["tree"]["sha"]

    tree_items = []
    
    # Files to ignore
    ignore_dirs = {".git", "__pycache__", "venv", "env", ".venv", ".pytest_cache"}
    ignore_files = {"upload_to_github.py", ".env", "ebs_math.db"}
    
    print("Preparing files for upload...")
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            if file in ignore_files or file.endswith(".pyc") or file.endswith(".sqlite3"):
                continue
            
            file_path = os.path.join(root, file)
            # Make path relative to the script directory and use forward slashes
            rel_path = os.path.relpath(file_path, directory).replace("\\", "/")
            
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                
                # Create blob
                req = urllib.request.Request(f"{api_base}/git/blobs", method="POST")
                req.add_header("Authorization", f"token {token}")
                req.add_header("Content-Type", "application/json")
                
                # Base64 encode content
                blob_data = {
                    "content": base64.b64encode(content).decode("utf-8"),
                    "encoding": "base64"
                }
                
                req.data = json.dumps(blob_data).encode("utf-8")
                
                with urllib.request.urlopen(req) as response:
                    blob_response = json.loads(response.read().decode())
                    blob_sha = blob_response["sha"]
                
                tree_items.append({
                    "path": rel_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha
                })
                print(f"Prepared blob: {rel_path}")
                
            except Exception as e:
                print(f"Failed to process {rel_path}: {e}")

    if not tree_items:
        print("No files to upload.")
        return

    print("Creating tree...")
    # 3. Create a new tree
    req = urllib.request.Request(f"{api_base}/git/trees", method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Content-Type", "application/json")
    
    tree_data = {
        "base_tree": base_tree_sha,
        "tree": tree_items
    }
    req.data = json.dumps(tree_data).encode("utf-8")
    with urllib.request.urlopen(req) as response:
        new_tree_data = json.loads(response.read().decode())
        new_tree_sha = new_tree_data["sha"]

    print("Creating commit...")
    # 4. Create a new commit
    req = urllib.request.Request(f"{api_base}/git/commits", method="POST")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Content-Type", "application/json")
    
    commit_data = {
        "message": "feat: Full rebuild of ProjectEbsMathVideo into an EdTech Platform",
        "tree": new_tree_sha,
        "parents": [latest_commit_sha]
    }
    req.data = json.dumps(commit_data).encode("utf-8")
    with urllib.request.urlopen(req) as response:
        new_commit_data = json.loads(response.read().decode())
        new_commit_sha = new_commit_data["sha"]

    print("Updating reference...")
    # 5. Update the reference (branch)
    req = urllib.request.Request(f"{api_base}/git/refs/heads/{branch}", method="PATCH")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Content-Type", "application/json")
    
    ref_data = {
        "sha": new_commit_sha
    }
    req.data = json.dumps(ref_data).encode("utf-8")
    with urllib.request.urlopen(req) as response:
        print("✅ Successfully uploaded to GitHub!")


if __name__ == "__main__":
    print("=" * 50)
    print("GitHub Uploader for ProjectEbsMathVideo")
    print("=" * 50)
    print("현재 PC에 Git이 설치되어 있지 않아 API를 통해 업로드합니다.")
    print("GitHub의 Personal Access Token (Classic)이 필요합니다.\n")
    
    # Repository details
    repo_owner = "inha20"
    repo_name = "ProjectEbsMathVideo"
    
    token = input("GitHub Token을 입력하세요 (ghp_...): ").strip()
    
    if token:
        upload_to_github(token, repo_owner, repo_name)
    else:
        print("토큰이 입력되지 않아 종료합니다.")

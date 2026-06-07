import httpx
import re
import time
from core.config import GITHUB_TOKEN

# Thread-safe in-memory cache to prevent GitHub API Rate Limit exhaustion
REPO_CACHE = {}
CACHE_TTL = 600  # 10 minutes

async def repo_agent(state):
    repo_url = state.get("repo_url", "")
    if not repo_url:
        state["outputs"].append({"agent": "Repo Agent", "status": "error", "output": "❌ CRITICAL: No repository URL provided. (Score: +0/20) -> Action Required: Provide a valid public GitHub repository link."})
        return state

    match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        state["outputs"].append({"agent": "Repo Agent", "status": "error", "output": "❌ INVALID: Improper GitHub URL structure format. (Score: +0/20) -> Action Required: Check your repository string format."})
        return state
        
    owner, repo = match.groups()
    repo = repo.replace(".git", "")
    cache_key = f"{owner}/{repo}".lower()

    # Serve from cache if available and fresh
    current_time = time.time()
    if cache_key in REPO_CACHE:
        cached_data, timestamp = REPO_CACHE[cache_key]
        if current_time - timestamp < CACHE_TTL:
            state["repo_files"] = cached_data
            state["outputs"].append({"agent": "Repo Agent", "status": "success", "output": f"✅ SUCCESS: Codebase pulled from production cache layer. (Score: +20/20) -> Mapped {len(cached_data)} structural files instantly."})
            state["score"] += 20
            return state

    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "AITeamBuilder-AutoGrader"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    
    # Force a hard drop if connection hangs or read streams block
    timeout_config = httpx.Timeout(10.0, connect=5.0, read=10.0)

    try:
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            response = await client.get(api_url, headers=headers)
            
            # Fallback to master branch if main is not found
            if response.status_code == 404:
                api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
                response = await client.get(api_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                file_paths = [item["path"] for item in data.get("tree", []) if item["type"] == "blob"]
                
                REPO_CACHE[cache_key] = (file_paths, current_time)
                state["repo_files"] = file_paths
                state["outputs"].append({"agent": "Repo Agent", "status": "success", "output": f"✅ SUCCESS: Codebase reached and cataloged. (Score: +20/20) -> Found {len(file_paths)} structural files."})
                state["score"] += 20 
            
            elif response.status_code in (403, 429):
                state["outputs"].append({"agent": "Repo Agent", "status": "error", "output": f"❌ BLOCKED: GitHub API Rate Limit triggered [Status {response.status_code}]. (Score: +0/20) -> Action Required: Add a personal access token to your .env file."})
                state["repo_files"] = []
                
            else:
                state["outputs"].append({"agent": "Repo Agent", "status": "error", "output": f"❌ FAILED: API connection rejected [Status Code {response.status_code}]. (Score: +0/20) -> Loss Reason: Access blocked or private repo."})
                state["repo_files"] = []
                
    except httpx.TimeoutException:
        state["outputs"].append({"agent": "Repo Agent", "status": "error", "output": "❌ NETWORK TIMEOUT: Failed to reach GitHub servers under heavy load conditions. (Score: +0/20)"})
        state["repo_files"] = []
    except httpx.RequestError as e:
        state["outputs"].append({"agent": "Repo Agent", "status": "error", "output": f"❌ CONNECTION ERROR: {str(e)} (Score: +0/20)"})
        state["repo_files"] = []

    return state
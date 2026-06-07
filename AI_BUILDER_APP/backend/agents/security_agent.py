def security_agent(state):
    files = state.get("repo_files", [])
    has_env = any(".env" in f for f in files)
    
    if has_env:
        state["outputs"].append({"agent": "Security Agent", "status": "warning", "output": "🚨 CRITICAL VULNERABILITY: Active environment profile '.env' secret maps checked directly into Git history! (Score: -10 Penalty) -> Loss Reason: Exposing live credential variables leaks server access infrastructure. Action Required: Immediately clean repo cache history and update your secrets profile maps."})
        state["score"] -= 10
    else:
        state["outputs"].append({"agent": "Security Agent", "status": "success", "output": "✅ SANITIZED: Excellent repository hygiene. Credentials and development environment files are hidden safely. (Score: +20/20)"})
        state["score"] += 20

    return state
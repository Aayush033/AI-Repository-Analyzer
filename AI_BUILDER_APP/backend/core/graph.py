import asyncio
import time

# Importing all your agents
from agents.planner import planner_agent
from agents.repo_agent import repo_agent
from agents.docker_agent import docker_agent
from agents.cicd_agent import cicd_agent
from agents.security_agent import security_agent
from agents.deploy_agent import deploy_agent
from agents.summary_agent import summary_agent

from core.metrics import timer_start, timer_end
from core.memory import remember

async def run_workflow(requirement, repo_url, ws):
    print("\n--- 🚀 [DEBUG] run_workflow STARTED ---")
    start = timer_start()

    state = {
        "requirement": requirement,
        "repo_url": repo_url,
        "tasks": [],
        "outputs": [],
        "score": 0,
        "repo_files": []
    }

    # Immediate feedback log to browser frontend
    try:
        await ws.send_json({"type": "log", "msg": "🚀 Orchestrator: Activating multi-agent workspace graph..."})
    except Exception as e:
        print(f"[DEBUG] Failed to send initial WS log: {e}")

    # --- 📋 STEP 1: PLANNER AGENT ---
    print("[DEBUG] Next step: Running planner_agent...")
    try:
        state = planner_agent(state)
        print(f"[DEBUG] planner_agent completed successfully. Tasks planned: {state.get('tasks')}")
    except Exception as e:
        print(f"💥 [DEBUG ERROR] planner_agent crashed: {str(e)}")
        state["tasks"] = ["repo", "docker", "cicd", "security", "deploy", "summary"]

    if not state.get("tasks"):
        state["tasks"] = ["repo", "docker", "cicd", "security", "deploy", "summary"]

    # --- 🔄 STEP 2: LOOP THROUGH PLANNED TASKS ---
    for task in state["tasks"]:
        print(f"\n👉 [DEBUG] Preparing to execute agent task: [{task.upper()}]")
        
        try:
            # Let the browser know which agent is spinning up
            await ws.send_json({"type": "log", "msg": f"🤖 Agent [{task.upper()}]: Commencing evaluation sequence..."})
            
            if task == "repo":
                print("[DEBUG] Entering async repo_agent...")
                state = await repo_agent(state)
                print("[DEBUG] Exited repo_agent successfully.")
                
            elif task == "docker":
                print("[DEBUG] Entering synchronous docker_agent...")
                state = docker_agent(state)
                print("[DEBUG] Exited docker_agent successfully.")
                
            elif task == "cicd":
                print("[DEBUG] Entering synchronous cicd_agent...")
                state = cicd_agent(state)
                print("[DEBUG] Exited cicd_agent successfully.")
                
            elif task == "security":
                print("[DEBUG] Entering synchronous security_agent...")
                state = security_agent(state)
                print("[DEBUG] Exited security_agent successfully.")
                
            elif task == "deploy":
                print("[DEBUG] Entering synchronous deploy_agent...")
                state = deploy_agent(state)
                print("[DEBUG] Exited deploy_agent successfully.")
                
            elif task == "summary":
                print("[DEBUG] Entering synchronous summary_agent...")
                state = summary_agent(state)
                print("[DEBUG] Exited summary_agent successfully.")

            await ws.send_json({"type": "log", "msg": f"✅ Agent [{task.upper()}]: Task processed successfully."})

        except Exception as e:
            print(f"💥 [DEBUG ERROR] Task [{task.upper()}] threw an exception: {str(e)}")
            await ws.send_json({"type": "log", "msg": f"💥 Fault inside [{task.upper()}]: {str(e)}"})
            state["outputs"].append({
                "agent": f"{task.capitalize()} Agent", 
                "status": "warning", 
                "output": f"Analysis interrupted due to script exception: {str(e)}"
            })
        
        await asyncio.sleep(0.1)

    print("\n--- 🏁 [DEBUG] ALL AGENT TASKS COMPLETED ---")
    
    try:
        runtime = timer_end(start)
        remember("last_run", repo_url)
    except Exception as e:
        print(f"[DEBUG] Timer/Memory exception: {e}")
        runtime = 0.0

    return {
        "tasks": state.get("tasks", []),
        "score": state.get("score", 0),
        "runtime": runtime,
        "results": state.get("outputs", [])
    }
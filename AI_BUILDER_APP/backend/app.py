import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from core.websocket import manager
from core.graph import run_workflow

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    return {"message": "AI Team Builder - Gemini AutoGrader Engine Active"}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    print("\n[WS INITIALIZED] A new recruiter frontend client connected successfully.")
    
    try:
        while True:
            # 1. Receive incoming socket transmission
            data = await ws.receive_json()
            print(f"[DATA RECEIVED FROM FRONTEND]: {data}")
            
            requirement = data.get("requirement", "")
            repo_url = data.get("repo_url", "") or data.get("repoUrl", "")
            
            if not repo_url:
                print("[WARNING] Received execution request but 'repo_url' was missing or blank.")
                await ws.send_json({"type": "log", "msg": "❌ Orchestrator Error: Received an empty repository string link."})
                continue

            print(f"[WORKFLOW STARTING]: Target -> {repo_url}")
            
            # 2. Execute protected graph loop with terminal logging
            try:
                result = await run_workflow(requirement, repo_url, ws)
                print(f"[WORKFLOW COMPLETED SUCCESSFULLY]: Sending results back.")
                await ws.send_json({"type": "result", "data": result})
                
            except Exception as graph_err:
                # 💡 This catches hidden internal graph exceptions and displays them in VS Code
                print("\n💥 [CRITICAL GRAPH CRASH DETECTED] 💥")
                traceback.print_exc() 
                
                # Report it cleanly back to the UI screen stream so it doesn't freeze
                await ws.send_json({
                    "type": "log", 
                    "msg": f"💥 Internal Server Execution Crash: {str(graph_err)}"
                })
                await ws.send_json({
                    "type": "result",
                    "data": {"tasks": [], "score": 0, "runtime": 0.0, "results": [{"agent": "System Orchestrator", "status": "error", "output": f"Backend failure loop: {str(graph_err)}"}]}
                })

    except WebSocketDisconnect:
        manager.disconnect(ws)
        print("[WS DISCONNECTED] Client closed connection tab.")
    except Exception as ws_err:
        print(f"[WS LOOP ERROR]: {str(ws_err)}")
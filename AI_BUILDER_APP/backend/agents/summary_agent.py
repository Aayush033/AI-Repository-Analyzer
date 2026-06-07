def summary_agent(state):
    state["outputs"].append({"agent": "Summary Agent", "status": "success", "output": f"🏁 Metrics evaluation loop completed. Final Calculated Score Matrix: {state['score']}/100"})
    return state
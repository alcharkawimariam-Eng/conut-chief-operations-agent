from fastapi import FastAPI
from agent import handle_request

app = FastAPI(title="Conut AI Agent")

@app.get("/call")
def call_agent(intent: str, branch_id: int = None):
    """
    Generic endpoint to call the agent.
    """
    return handle_request(intent, branch_id=branch_id)

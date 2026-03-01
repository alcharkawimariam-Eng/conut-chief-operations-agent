from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import time, uuid

app = FastAPI()

# ------------------- Models -------------------

class ForecastRequest(BaseModel):
    branch_id: str

class StaffingRequest(BaseModel):
    branch_id: str
    shift: str

class ComboRequest(BaseModel):
    branch_id: str

# ------------------- Routes -------------------

@app.get("/")
def root():
    return {"status": "Chief of Operations Agent running"}

@app.get("/v1/models")
def v1_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "dummy-model",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def v1_chat_completions(req: Request):
    payload = await req.json()
    messages = payload.get("messages", [])

    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = m.get("content", "")
            break

text = (last_user or "").strip()
low = text.lower()

def pick_last_token(s: str) -> str:
    parts = s.split()
    return parts[-1] if parts else ""

if "forecast" in low:
    # example: "forecast B001"
    branch = pick_last_token(text)
    result = forecast(ForecastRequest(branch_id=branch))
    dummy_text = str(result)

elif "staff" in low or "staffing" in low:
    # example: "staffing B001 morning"
    parts = text.split()
    branch = parts[1] if len(parts) >= 2 else ""
    shift  = parts[2] if len(parts) >= 3 else "morning"
    result = staffing(StaffingRequest(branch_id=branch, shift=shift))
    dummy_text = str(result)

elif "combo" in low:
    # example: "combo B001"
    branch = pick_last_token(text)
    result = combo(ComboRequest(branch_id=branch))
    dummy_text = str(result)

elif "expansion" in low:
    dummy_text = str(expansion())

elif "beverage" in low:
    dummy_text = str(beverage_strategy())

else:
    dummy_text = (
        "Say one of these:\n"
        "- forecast <branch_id>\n"
        "- staffing <branch_id> <shift>\n"
        "- combo <branch_id>\n"
        "- expansion\n"
        "- beverage"
    )
    return JSONResponse({
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": payload.get("model", "dummy-model"),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": dummy_text},
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    })

@app.post("/v1/responses")
async def v1_responses(req: Request):
    payload = await req.json()
    inp = payload.get("input", "")
    dummy_text = f"[DUMMY MODEL] You said: {inp}"

    return JSONResponse({
        "id": f"resp-{uuid.uuid4().hex}",
        "object": "response",
        "created": int(time.time()),
        "model": payload.get("model", "dummy-model"),
        "output": [{
            "type": "message",
            "role": "assistant",
            "content": [{"type": "output_text", "text": dummy_text}]
        }]
    })

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/forecast")
def forecast(req: ForecastRequest):
    return {
        "objective": "demand_forecasting",
        "branch": req.branch_id,
        "prediction": "dummy_prediction",
        "recommendation": "Increase inventory by 10%"
    }

@app.post("/staffing")
def staffing(req: StaffingRequest):
    return {
        "objective": "shift_staffing",
        "branch": req.branch_id,
        "shift": req.shift,
        "recommended_staff": 5
    }

@app.post("/combo")
def combo(req: ComboRequest):
    return {
        "objective": "combo_optimization",
        "branch": req.branch_id,
        "top_combos": [
            {"items": ["Donut A", "Iced Coffee"], "confidence": 0.78},
            {"items": ["Milkshake", "Chocolate Donut"], "confidence": 0.65}
        ]
    }

@app.get("/expansion")
def expansion():
    return {
        "objective": "expansion_feasibility",
        "recommended_location_type": "High beverage sales zone",
        "confidence_score": 0.82
    }

@app.get("/beverage-strategy")
def beverage_strategy():
    return {
        "objective": "coffee_milkshake_growth",
        "recommendations": [
            "Bundle coffee with breakfast items",
            "Introduce limited-time milkshake flavors",
            "Offer 5-7 PM beverage discount"
        ]
    }


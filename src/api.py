from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse, StreamingResponse
import time, uuid
import json
from src.ops_agent.router import route_intent
from src.ops_agent.runner import run_intent
from src.ops_agent.formatter import format_exec_answer

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
def _get_last_user_text(messages):
    # OpenAI/OpenClaw can send content as string OR list of parts
    for m in reversed(messages or []):
        if m.get("role") != "user":
            continue
        c = m.get("content")
        if isinstance(c, str):
            return c
        if isinstance(c, list):
            # parts like [{"type":"text","text":"..."}]
            texts = []
            for part in c:
                if isinstance(part, dict) and part.get("type") == "text":
                    texts.append(part.get("text", ""))
            return "".join(texts).strip()
    return ""


@app.get("/")
def root():
    return {"status": "Chief of Operations Agent running"}

def content_to_text(content):
    # OpenAI-style: content can be a string OR a list of parts like:
    # [{"type":"text","text":"hello"}]
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, str):
                texts.append(part)
            elif isinstance(part, dict):
                # common keys
                if "text" in part and isinstance(part["text"], str):
                    texts.append(part["text"])
                elif part.get("type") in ("input_text", "output_text", "text") and isinstance(part.get("text"), str):
                    texts.append(part["text"])
        return " ".join(texts)
    return ""

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
    stream = bool(payload.get("stream", False))
    include_usage = bool((payload.get("stream_options") or {}).get("include_usage", False))

    user_text = _get_last_user_text(messages)

    # TODO: replace this with your real model call
    intent = route_intent(user_text)
    result = run_intent(intent)
    reply_text = format_exec_answer(intent, result)

    chat_id = f"chatcmpl-{uuid.uuid4().hex}"
    model_name = payload.get("model", "dummy-model")
    created = int(time.time())

    if not stream:
        return JSONResponse({
    "id": chat_id,
    "object": "chat.completion",
    "created": created,
    "model": model_name,
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": reply_text
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }
})
    

    # ---- STREAMING (SSE) ----
    def sse(data: dict) -> str:
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    async def gen():
        # 1) initial chunk (role)
        yield sse({
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_name,
            "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
        })

        # 2) content chunks (split a bit so UI renders)
        chunk_size = 40
        for i in range(0, len(reply_text), chunk_size):
            yield sse({
                "id": chat_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model_name,
                "choices": [{"index": 0, "delta": {"content": reply_text[i:i+chunk_size]}, "finish_reason": None}],
            })

        # 3) final chunk (finish_reason + optional usage)
        final = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model_name,
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        if include_usage:
            final["usage"] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        yield sse(final)
        yield "data: [DONE]\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")




# --- OpenClaw/vLLM compatibility aliases ---

@app.get("/models")
def models_alias():
    return v1_models()

@app.post("/chat/completions")
async def chat_completions_alias(req: Request):
    payload = await req.json()
    print("=== /chat/completions payload ===")
    print(payload)
    print("=================================")
    # re-create the request handling by calling the same logic:
    # simplest: just call the same function again by reusing payload (we’ll fix next step)
    return await v1_chat_completions(req)

@app.post("/responses")
async def responses_alias(req: Request):
    return await v1_responses(req)

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
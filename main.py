from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ===== CONFIG =====
API_KEY = "amigo123"   # change this
state = {"value": 0}   # 0=Idle, 1=Shutdown, 2=Restart, 3=Sleep

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== API =====
@app.get("/state")
def get_state():
    return {"state": state["value"]}


@app.post("/state")
async def set_state(request: Request):
    key = request.headers.get("x-api-key")

    if key != API_KEY:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    data = await request.json()
    value = int(data.get("state", 0))

    if value not in (0, 1, 2, 3):
        return JSONResponse({"error": "state must be 0–3"}, status_code=400)

    state["value"] = value
    return {"state": state["value"]}


# ===== UI =====
@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Amigo Remote Control</title>
    <meta charset="UTF-8" />
    <style>
        body {
            background: #111;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: Arial;
        }
        h1 { margin-bottom: 20px; }
        .btn {
            font-size: 1.5rem;
            padding: 15px 25px;
            margin: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            width: 200px;
        }
        .shutdown { background: red; }
        .restart { background: orange; }
        .sleep { background: blue; }
        .idle { background: gray; }
        #status {
            margin-top: 20px;
            font-size: 1.2rem;
        }
    </style>
</head>
<body>

<h1>🖥️ Amigo Remote Control</h1>

<button class="btn shutdown" onclick="setState(1)">Shutdown</button>
<button class="btn restart" onclick="setState(2)">Restart</button>
<button class="btn sleep" onclick="setState(3)">Sleep</button>
<button class="btn idle" onclick="setState(0)">Idle</button>

<div id="status">Status: Loading...</div>

<script>
const API_KEY = "amigo123";

async function setState(value) {
    await fetch("/state", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        body: JSON.stringify({state: value})
    });
    fetchState();
}

function getText(value) {
    return ["Idle","Shutdown","Restart","Sleep"][value] || "Unknown";
}

async function fetchState() {
    const res = await fetch("/state");
    const data = await res.json();
    document.getElementById("status").innerText =
        "Status: " + getText(data.state);
}

// auto refresh every 2 sec
setInterval(fetchState, 2000);
fetchState();
</script>

</body>
</html>
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ===== CONFIG =====
API_KEY = "amigo123"
state = {"value": 0}  # 0=Idle, 1=Shutdown, 2=Restart, 3=Sleep, 4=Force Quit

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    if value not in (0, 1, 2, 3, 4):
        return JSONResponse({"error": "state must be 0–4"}, status_code=400)

    state["value"] = value
    return {"state": state["value"]}


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Amigo Remote Control</title>
<style>
body {
    background: #111;
    color: white;
    text-align: center;
    font-family: Arial;
    margin-top: 100px;
}
button {
    font-size: 1.2rem;
    padding: 15px 25px;
    margin: 10px;
    border: none;
    border-radius: 10px;
    cursor: pointer;
}
.shutdown { background: red; }
.restart { background: orange; }
.sleep { background: blue; }
.force { background: purple; }
.idle { background: gray; }
</style>
</head>
<body>

<h1>🖥️ Amigo Control Panel</h1>

<button class="shutdown" onclick="setState(1)">Shutdown</button>
<button class="restart" onclick="setState(2)">Restart</button>
<button class="sleep" onclick="setState(3)">Sleep</button>
<button class="force" onclick="setState(4)">Force Quit</button>
<button class="idle" onclick="setState(0)">Idle</button>

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
}
</script>

</body>
</html>
"""

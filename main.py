from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

API_KEY = "amigo123"

state = {"value": 0}
target_app = {"name": ""}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/state")
def get_state():
    return {
        "state": state["value"],
        "target": target_app["name"]
    }

@app.post("/state")
async def set_state(request: Request):
    key = request.headers.get("x-api-key")

    if key != API_KEY:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    data = await request.json()
    value = int(data.get("state", 0))
    app_name = data.get("target", "")

    if value not in (0, 1, 2, 3, 4, 5):
        return JSONResponse({"error": "state must be 0–5"}, status_code=400)

    state["value"] = value
    target_app["name"] = app_name

    return {
        "state": state["value"],
        "target": target_app["name"]
    }

@app.get("/", response_class=HTMLResponse)
def index():
    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Amigo Control</title>
<style>
body {{
    background:#111;
    color:white;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    height:100vh;
    font-family:Arial;
}}
.btn {{
    padding:15px;
    margin:10px;
    font-size:1.2rem;
    border:none;
    border-radius:10px;
    cursor:pointer;
    width:220px;
}}
.shutdown {{background:red;}}
.restart {{background:orange;}}
.sleep {{background:blue;}}
.idle {{background:gray;}}
.force {{background:purple;}}

input {{
    padding:10px;
    margin-top:10px;
    border-radius:8px;
    border:none;
    width:220px;
}}
</style>
</head>
<body>

<h2>🖥️ Amigo Remote</h2>

<button class="btn shutdown" onclick="setState(1)">Shutdown</button>
<button class="btn restart" onclick="setState(2)">Restart</button>
<button class="btn sleep" onclick="setState(3)">Sleep</button>
<button class="btn idle" onclick="setState(0)">Idle</button>
<button class="btn force" onclick="setState(4)">Force Quit Active</button>

<input id="appInput" placeholder="chrome.exe">
<button class="btn force" onclick="killApp()">Kill Specific App</button>

<script>
const API_KEY = "amigo123";

async function setState(val){{
    await fetch("/state", {{
        method:"POST",
        headers:{{"Content-Type":"application/json","x-api-key":API_KEY}},
        body:JSON.stringify({{state:val}})
    }});
}}

async function killApp(){{
    let app = document.getElementById("appInput").value;
    if(!app){{ alert("Enter app name"); return; }}

    await fetch("/state", {{
        method:"POST",
        headers:{{"Content-Type":"application/json","x-api-key":API_KEY}},
        body:JSON.stringify({{state:5,target:app}})
    }});
}}
</script>

</body>
</html>
"""

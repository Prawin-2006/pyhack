# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# in-memory state: 0 = OFF, 1 = ON
state = {"value": 0}

# allow your HTML page to call this API from browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to your domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/state")
def get_state():
    return {"state": state["value"]}


@app.post("/state")
async def set_state(request: Request):
    data = await request.json()
    value = int(data.get("state", 0))
    if value not in (0, 1):
        return JSONResponse({"error": "state must be 0 or 1"}, status_code=400)
    state["value"] = value
    return {"state": state["value"]}


# simple HTML with single ON/OFF button
@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Remote Switch</title>
    <meta charset="UTF-8" />
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            height: 100vh;
            align-items: center;
            justify-content: center;
            background: #111;
            color: #fff;
        }
        #toggleBtn {
            font-size: 2rem;
            padding: 20px 40px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <button id="toggleBtn">OFF</button>

    <script>
        const btn = document.getElementById("toggleBtn");

        async function fetchState() {
            const res = await fetch("/state");
            const data = await res.json();
            const value = data.state;
            updateButton(value);
        }

        function updateButton(value) {
            if (value === 1) {
                btn.textContent = "ON";
                btn.style.background = "lime";
            } else {
                btn.textContent = "OFF";
                btn.style.background = "red";
            }
        }

        btn.addEventListener("click", async () => {
            const newState = btn.textContent === "OFF" ? 1 : 0;
            await fetch("/state", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ state: newState })
            });
            updateButton(newState);
        });

        // load initial state on page open
        fetchState();
    </script>
</body>
</html>
    """

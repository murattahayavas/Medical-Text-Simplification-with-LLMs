$ErrorActionPreference = "Stop"

if (-not (Test-Path "node_modules")) {
    npm ci
}

& ".\node_modules\.bin\vite.cmd" "--host" "127.0.0.1" "--port" "5173"

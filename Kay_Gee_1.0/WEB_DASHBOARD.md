# KayGee 1.0 - Web Dashboard

**React + Vite + FastAPI**

Beautiful, real-time web dashboard with voice controls.

## Quick Start

### Backend (FastAPI)

```powershell
# Install dependencies
cd backend
pip install -r requirements.txt

# Run API server
python main.py
# or
uvicorn main:app --reload --port 8000
```

API will run at: **http://localhost:8000**
Docs at: **http://localhost:8000/docs**

### Frontend (React + Vite)

```powershell
# Install dependencies
cd frontend
npm install

# Run dev server
npm run dev
```

Dashboard will run at: **http://localhost:5173**

## Architecture

```
frontend/          ← React + Vite + TypeScript
  ├── src/
  │   ├── App.tsx           ← Main dashboard component
  │   ├── main.tsx          ← Entry point
  │   └── index.css         ← Tailwind styles
  ├── vite.config.ts        ← Vite configuration
  ├── tailwind.config.js    ← Tailwind config
  └── package.json

backend/           ← FastAPI + WebSocket
  ├── main.py               ← API server + WebSocket
  └── requirements.txt      ← Python dependencies
```

## Features

✅ **Real-time Updates** - WebSocket streaming  
✅ **Live Metrics** - Merkle root, confidence, interactions  
✅ **Beautiful UI** - Dark cyber theme with gradients  
✅ **Type-safe** - TypeScript + Pydantic  
✅ **Voice Ready** - Add browser speech APIs later  

## API Endpoints

- `GET /status` - Current system status
- `POST /speak` - Process user message
- `WS /ws` - WebSocket for live updates
- `GET /health` - Health check
- `GET /docs` - Swagger documentation

## Development

### Build Frontend

```powershell
cd frontend
npm run build
```

### Production

```powershell
# Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend (serve dist/)
npm run preview
```

## What's Next

- [ ] Add voice recording in browser
- [ ] Philosophical quotes carousel
- [ ] Merkle proof viewer
- [ ] Session history
- [ ] Dark/light theme toggle
- [ ] Mobile responsive

---

**Built by:** Claude + Kimi + Grok  
**Christmas 2025** 🎄

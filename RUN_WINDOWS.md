# Run Migration Pulse AI on Windows

1. Put your TinyFish key in `backend\.env`:

```env
TINYFISH_API_KEY=your_real_key_here
DEMO_MODE=false
```

2. Backend:

```powershell
cd C:\Users\gopal\Downloads\migrationpulse\backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

3. Check:

`http://127.0.0.1:8001/api/health`

4. Frontend, in a second terminal:

```powershell
cd C:\Users\gopal\Downloads\migrationpulse\frontend
npm install
npm run dev
```

5. Open the Vite URL printed by the frontend terminal.

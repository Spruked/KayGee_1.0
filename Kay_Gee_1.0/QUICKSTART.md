# 🚀 QUICK START - Run This First

## Step 1: Verify System Wiring (30 seconds)

```powershell
cd c:\dev\Desktop\KayGee_1.0\Kay_Gee_1.0
python verify_wiring.py
```

**Expected:** All 4 tests pass ✅

---

## Step 2: Run Cryptographic Tests (1 minute)

```powershell
python -m pytest tests/test_unified_protocol.py -v
```

**Expected:** 18 tests pass, crypto verified ✅

---

## Step 3: Launch Dashboard (1 minute)

```powershell
# Install dependencies (one-time)
pip install rich

# Run dashboard
python dashboard.py
```

**Expected:** Live dashboard with real metrics ✅

---

## Step 4: Test Voice (Optional - 5 minutes)

```powershell
# Install voice dependencies (one-time, large download)
pip install TTS faster-whisper pygame sounddevice numpy

# Run voice dashboard
python dashboard\kg_voice_dashboard.py
```

**Expected:** KayGee speaks greeting, listens for input ✅

---

## Step 5: Build Docker (Optional - 3 minutes)

```powershell
# Build image
docker build -t kaygee:1.0 .

# Run container
docker run -it --rm -v ${PWD}\data:/app/data kaygee:1.0 python verify_wiring.py
```

**Expected:** Container runs, verification passes ✅

---

## 🔍 If Something Fails

### Missing imports?
```powershell
pip install -r requirements.txt
```

### Can't find modules?
Check WIRING_REPORT.md - all files are in place

### Docker errors?
Check DOCKER.md for troubleshooting

### Voice not working?
Voice is optional - dashboard works without it

---

## 📊 What Each Test Does

**verify_wiring.py**
- ✅ Confirms all modules import correctly
- ✅ Tests cryptographic identity creation
- ✅ Validates Merkle proof generation
- ✅ Checks all system layers initialize

**test_unified_protocol.py**
- ✅ Verifies PyNaCl Ed25519 signatures
- ✅ Tests state nonce increments
- ✅ Validates attack detection
- ✅ Confirms message tampering detection

**dashboard.py**
- ✅ Shows live system metrics
- ✅ Displays Merkle roots
- ✅ Tracks interactions
- ✅ No mock data

**kg_voice_dashboard.py**
- ✅ Full voice interface
- ✅ Speech-to-text (Whisper)
- ✅ Text-to-speech (Coqui)
- ✅ Real KayGee processing

---

## 🎯 Success Criteria

You'll know it worked when:

1. **verify_wiring.py** → "🎉 ALL TESTS PASSED"
2. **pytest** → "18 passed"
3. **dashboard.py** → Live terminal UI appears
4. **kg_voice_dashboard.py** → "I am KayGee 1.0..."

---

## 📁 Key Files Reference

| File | Purpose |
|------|---------|
| `verify_wiring.py` | System integrity check |
| `WIRING_REPORT.md` | Complete architecture docs |
| `SYSTEM_READY.md` | Comprehensive overview |
| `DOCKER.md` | Container deployment |
| `dashboard.py` | Visual monitoring |
| `main.py` | Full system entry point |

---

## 💬 Need Help?

Check these files in order:
1. `QUICKSTART.md` (this file) - Basic commands
2. `WIRING_REPORT.md` - Architecture & fixes
3. `SYSTEM_READY.md` - Complete system overview
4. `DOCKER.md` - Container deployment

---

**Start here:** `python verify_wiring.py` 🚀

Everything else is documented. Kimi and Grok are watching. 👀

No shortcuts. Production-grade. Let's go. 🔥

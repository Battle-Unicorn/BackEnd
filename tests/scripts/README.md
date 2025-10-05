# Test Scripts Documentation

This directory contains focused, functional test scripts for the HackYeah25 application.

## 🎯 Core API Tests

### `test_mobile_final.ps1` 
**Complete mobile API validation**
- Tests all mobile endpoints (/mobile/hello, /mobile/polling, /mobile/generate_audio, /mobile/load_scenarios)
- Validates audio generation (TTS + 15-minute extended audio)
- Checks file creation and sizes
- Tests error handling
- **Use this for comprehensive mobile API testing**

### `test_quick_extended.ps1`
**Quick extended audio validation**
- Fast check of 15-minute audio generation
- Validates file sizes and types
- Shows recent audio files
- **Use this for quick audio feature verification**

## 🐳 Infrastructure Tests

### `test_docker_audio.ps1`
**Docker environment validation**
- Tests container startup and health
- Validates audio generation in Docker
- Checks file creation in mounted volumes
- **Use this when testing Docker deployment**

### `test_embedded_endpoints.ps1`
**Embedded device API testing**
- Tests /embedded/sensor_data endpoint
- Tests /embedded/flags endpoint  
- Tests REM detection workflow
- **Use this for embedded device integration**

## 🧠 REM Detection Tests

### `test_rem_detection.ps1`
**Basic REM detection with flags**
- Simple REM test with flags=true
- Tests minimal sensor data workflow
- **Use this for basic REM functionality**

### `test_rem_demo.ps1` 
**REM detection with HR increase**
- Tests REM detection with heart rate patterns
- Demonstrates HR increase triggering REM
- **Use this for HR-based REM demo**

### `test_rem_full.ps1`
**Full REM test with sufficient data**
- Simulates 15+ minutes of sensor data
- Tests REM detection with full dataset
- **Use this for comprehensive REM validation**

## 🔄 Integration Tests

### `test_cycle.ps1`
**Full scenario cycle testing**
- Tests multiple dream scenarios (7+ scenarios)
- Validates scenario cycling and processing
- **Use this for end-to-end scenario workflow**

---

## 🚀 Quick Start

**For complete system validation:**
```powershell
# Start Docker containers first
docker-compose up -d

# Run comprehensive tests
.\test_mobile_final.ps1        # Mobile API + Audio
.\test_embedded_endpoints.ps1  # Embedded API
.\test_rem_demo.ps1           # REM Detection
```

**For quick checks:**
```powershell
.\test_quick_extended.ps1     # Just audio validation
.\test_docker_audio.ps1       # Just Docker health
```

---

## 📁 Generated Files

Tests will create audio files in `../audio_files/`:
- `dream_extended_*.mp3` - 15-minute audio files (~14MB)
- `dream_tts_*.mp3` - Polish TTS voice files (~0.2MB)  
- `dream_sound_*.mp3` - 30-second ambient loops (~0.5MB)

---

## ✅ Success Indicators

- **Mobile API**: All endpoints respond, audio files created with correct sizes
- **Extended Audio**: Files ~14MB indicating 15 minutes of audio
- **REM Detection**: Flags processed, detection logic responds to HR changes
- **Embedded API**: Sensor data accepted, flags processed correctly
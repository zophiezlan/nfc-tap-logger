# Quick Start Guide

## NFC Tap Logger - Get Running in 15 Minutes

---

## 📦 What You Need

- ✅ Raspberry Pi Zero 2 W
- ✅ PN532 NFC module
- ✅ 100× NTAG215 cards
- ✅ Power bank (10,000mAh)
- ✅ MicroSD card (8GB+) with Raspberry Pi OS

---

## ⚡ 15-Minute Setup

### Step 1: Wire Hardware (5 min)

```
PN532 → Pi
VCC   → Pin 1 (3.3V)  [RED]
GND   → Pin 6 (GND)   [BLACK]
SDA   → Pin 3 (GPIO2) [BLUE]
SCL   → Pin 5 (GPIO3) [YELLOW]
```

**⚠️ IMPORTANT:** Use 3.3V, NOT 5V!

### Step 2: Install Software (5 min)

```bash
# On your Pi
git clone <your-repo-url>
cd nfc-tap-logger
bash scripts/install.sh

# Reboot
sudo reboot
```

### Step 3: Configure Station (2 min)

Edit `config.yaml`:

```yaml
station:
  device_id: "station1" # station1 or station2
  stage: "QUEUE_JOIN" # QUEUE_JOIN or EXIT
  session_id: "festival-2025"
```

### Step 4: Verify Hardware (2 min)

```bash
source venv/bin/activate
python scripts/verify_hardware.py
```

All checks should pass ✓

### Step 5: Start Service (1 min)

```bash
sudo systemctl start tap-station
tail -f logs/tap-station.log
```

Look for: `Station ready - waiting for cards...`

---

## 🎴 Initialize Cards (One Time)

```bash
source venv/bin/activate
python scripts/init_cards.py
```

Tap each card when prompted. Takes ~10 minutes for 100 cards.

---

## 🎉 You're Ready

**Test:** Tap a card → should beep

**Deploy:** Place stations at queue entrance and exit

**After event:** `python scripts/export_data.py`

---

## 🆘 Quick Troubleshooting

| Problem             | Fix                                       |
| ------------------- | ----------------------------------------- |
| No beep on tap      | Check `i2cdetect -y 1` shows `24`         |
| Service won't start | Check `sudo systemctl status tap-station` |
| Card won't read     | Hold flat on reader for 2 seconds         |
| Battery low         | Check `vcgencmd get_throttled` = `0x0`    |

---

## 📞 Get Help

1. Check logs: `tail -f logs/tap-station.log`
2. See `README.md` for detailed troubleshooting
3. See `docs/HARDWARE.md` for wiring diagrams

---

**That's it! Simple as tap-beep-done.** 🎊

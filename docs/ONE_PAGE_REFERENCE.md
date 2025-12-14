# NFC Tap Logger - One Page Reference

## 🔌 Hardware Setup
```
PN532 → Pi          Buzzer → Pi
VCC → Pin 1 (3.3V)  + → Pin 11 (GPIO17)
GND → Pin 6         - → GND
SDA → Pin 3
SCL → Pin 5
```

## ⚙️ Initial Setup
```bash
bash scripts/install.sh
sudo reboot
python scripts/verify_hardware.py
python scripts/init_cards.py
```

## 🚀 Start/Stop
```bash
sudo systemctl start tap-station   # Start
sudo systemctl stop tap-station    # Stop
sudo systemctl status tap-station  # Check status
tail -f logs/tap-station.log       # View logs
```

## 📊 Operations
```bash
python -m tap_station.main --stats    # Show statistics
python scripts/export_data.py         # Export to CSV
sudo i2cdetect -y 1                   # Check PN532 (should show 24)
vcgencmd get_throttled                # Check power (should be 0x0)
```

## 🔧 Quick Fixes
| Problem | Solution |
|---------|----------|
| No beep | `sudo i2cdetect -y 1`, check wiring |
| Won't start | `sudo systemctl status tap-station` |
| Slow | Check power: `vcgencmd get_throttled` |
| Database locked | `sudo systemctl restart tap-station` |

## 📱 Beep Codes
- **1 beep** = Success ✓
- **2 beeps** = Already logged (duplicate)
- **Long beep** = Error, try again

## 📁 Important Files
- `config.yaml` - Station configuration
- `data/events.db` - Event database
- `logs/tap-station.log` - Service logs
- `data/card_mapping.csv` - Card UIDs to token IDs

## 🎯 Peer Workflow
1. Hand card → 2. Tap → 3. Hear beep → 4. Done!

## 📈 Data Analysis (R)
```r
library(tidyverse)
events <- read_csv("export.csv")
flow <- events %>%
  pivot_wider(names_from = stage, values_from = timestamp) %>%
  mutate(wait_time = difftime(EXIT, QUEUE_JOIN, units = "mins"))
median(flow$wait_time, na.rm = TRUE)  # Median wait
```

## 🆘 Emergency
1. Check power connected
2. Restart: `sudo systemctl restart tap-station`
3. Manual log if system down
4. Call Clancy

---
**Keep this laminated near each station** 📋

# Deployment Checklist
## Pre-Event Prep & Day-Of Operations

---

## 📅 One Week Before Event

### Hardware Check
- [ ] Test both Pis boot successfully
- [ ] PN532 readers detected (`sudo i2cdetect -y 1`)
- [ ] Buzzers working
- [ ] Power banks fully charged
- [ ] Have spare power banks
- [ ] USB cables in good condition
- [ ] MicroSD cards backed up

### Software Check
- [ ] Services start on boot (`sudo systemctl enable tap-station`)
- [ ] Latest code deployed
- [ ] Config files set correctly (device_id, stage, session_id)
- [ ] Database cleared or archived from last event
- [ ] Logs rotated/cleared

### Cards
- [ ] All 100 cards initialized
- [ ] Card mapping CSV saved (`data/card_mapping.csv`)
- [ ] Cards numbered visually (optional but helpful)
- [ ] Cards stored safely

### Supplies
- [ ] Tape/velcro for mounting readers
- [ ] "TAP HERE" signs printed
- [ ] Ziplock bags (weatherproofing)
- [ ] Printed peer guide
- [ ] Printed troubleshooting flowchart
- [ ] Sharpies (for manual backup)
- [ ] Paper log sheets (if tech fails)

---

## 🌅 Morning of Event (30 min setup)

### 1. Station 1 Setup (Queue/Registration) - 10 min
- [ ] Power on Pi, wait for boot (~30 sec)
- [ ] Verify green LED (Pi is on)
- [ ] Check service running: `sudo systemctl status tap-station`
- [ ] Test tap: grab a card → tap → hear beep ✓
- [ ] Mount reader on desk/clipboard
- [ ] Place "TAP HERE" sign
- [ ] Brief peer on workflow

### 2. Station 2 Setup (Exit) - 10 min
- [ ] Same as Station 1
- [ ] Position at exit point (after service complete)

### 3. Final Test - 5 min
- [ ] Take one card
- [ ] Tap at Station 1 → BEEP ✓
- [ ] Tap at Station 2 → BEEP ✓
- [ ] Check database: `python -m tap_station.main --stats`
  - Should show 2 events (1 at each stage)

### 4. Peer Brief - 5 min
**Give peers the laminated guide, explain:**
- Hand out cards when people join queue
- Point to tap zone
- Listen for beep (success) or double-beep (already tapped)
- If no beep after 2 tries, write it down manually
- Come get you if problems

---

## 🎪 During Event (Monitoring)

### Hourly Check (2 min)
- [ ] Walk by each station - is it beeping when tapped?
- [ ] Ask peers: "Any issues?"
- [ ] Visual check: Pi lights on

### If Available: Remote Check (30 sec)
```bash
# SSH into each station
ssh pi@station1.local

# Quick health check
python -m tap_station.main --stats
# Shows total events, recent taps

# Check battery
vcgencmd get_throttled
# Should be 0x0 (no undervoltage)
```

### Mid-Event Backup (5 min, optional)
```bash
# Export data so far
python scripts/export_data.py

# Copy to laptop
scp pi@station1.local:~/nfc-tap-logger/export*.csv ~/Desktop/
```

---

## 🌙 End of Event (15 min)

### 1. Data Export - 5 min
**Station 1:**
```bash
ssh pi@station1.local
cd nfc-tap-logger
source venv/bin/activate
python scripts/export_data.py
# Creates: export_YYYYMMDD_HHMMSS.csv
```

**Station 2:**
```bash
ssh pi@station2.local
cd nfc-tap-logger
source venv/bin/activate
python scripts/export_data.py
```

### 2. Copy Data to Laptop - 2 min
```bash
# From your laptop
scp pi@station1.local:~/nfc-tap-logger/export*.csv ~/Desktop/festival-data/
scp pi@station2.local:~/nfc-tap-logger/export*.csv ~/Desktop/festival-data/
```

### 3. Backup Databases - 3 min
```bash
# Station 1
ssh pi@station1.local
cp data/events.db backups/events_station1_YYYYMMDD.db

# Station 2
ssh pi@station2.local
cp data/events.db backups/events_station2_YYYYMMDD.db
```

### 4. Shutdown - 2 min
```bash
# Both stations
sudo systemctl stop tap-station
sudo shutdown now
```

### 5. Pack Up - 3 min
- [ ] Disconnect power
- [ ] Coil cables neatly
- [ ] Pack Pis in protective case
- [ ] Collect cards (or let participants keep)
- [ ] Pack buzzers, power banks, cables

---

## 📊 Post-Event Analysis (30 min)

### 1. Merge Data
```r
library(tidyverse)

# Load both stations
station1 <- read_csv("export_station1.csv")
station2 <- read_csv("export_station2.csv")

# Combine
events <- bind_rows(station1, station2)

# Save merged
write_csv(events, "festival_YYYYMMDD_merged.csv")
```

### 2. Calculate Metrics
```r
# Wait times
flow <- events %>%
  pivot_wider(names_from = stage, values_from = timestamp) %>%
  mutate(
    wait_time = difftime(EXIT, QUEUE_JOIN, units = "mins"),
    total_time = as.numeric(wait_time)
  )

# Key metrics
median_wait <- median(flow$total_time, na.rm = TRUE)
p90_wait <- quantile(flow$total_time, 0.9, na.rm = TRUE)
total_served <- sum(!is.na(flow$EXIT))
abandonment <- sum(is.na(flow$EXIT) & !is.na(flow$QUEUE_JOIN))

# Report
cat(sprintf("
Festival Report
===============
Total participants: %d
Completed service: %d
Abandoned queue: %d
Median wait time: %.1f minutes
90th percentile: %.1f minutes
",
nrow(flow),
total_served,
abandonment,
median_wait,
p90_wait
))
```

### 3. Visualize
```r
# Wait time distribution
ggplot(flow, aes(x = total_time)) +
  geom_histogram(bins = 30) +
  labs(
    title = "Wait Time Distribution",
    x = "Wait Time (minutes)",
    y = "Count"
  )

# Throughput over time
events %>%
  filter(stage == "EXIT") %>%
  mutate(hour = floor_date(timestamp, "hour")) %>%
  count(hour) %>%
  ggplot(aes(x = hour, y = n)) +
  geom_col() +
  labs(
    title = "Throughput by Hour",
    x = "Time",
    y = "People Served"
  )
```

### 4. Share Results
- [ ] Create summary report
- [ ] Share with team
- [ ] Share with funders (if needed)
- [ ] Identify improvements for next event

---

## 🔄 Between Events

### Maintenance
- [ ] Charge power banks
- [ ] Update software if needed (`git pull`)
- [ ] Clear old databases (keep backups)
- [ ] Test both Pis still work
- [ ] Replace any worn cables/hardware

### Planning
- [ ] Review what went well
- [ ] Note any problems encountered
- [ ] Plan improvements
- [ ] Update documentation if needed

---

## 🆘 Emergency Backup Plan

### If Station Fails During Event

**Option 1: Manual Logging**
- Paper sheet with columns: Token ID | Time | Stage
- Peer writes down each tap
- Enter data later

**Option 2: Phone Backup** (if you built this)
- Use NFC Tools app
- Scan card UID
- Log in spreadsheet

**Option 3: Swap Hardware**
- Keep spare Pi configured
- Swap in < 5 minutes
- Resume operation

**Remember:** Missing some data is OK. Better to serve people than fix tech.

---

## ✅ Success Criteria

After event, you should be able to say:

- [ ] System ran for full event duration
- [ ] >90% of cards have complete journey (queue → exit)
- [ ] Can calculate median wait time
- [ ] Peers found it easy to use
- [ ] Would deploy again at next event

---

## 📝 Notes Section

**Event:** _____________________
**Date:** _____________________
**Location:** _____________________

**What worked well:**


**What could improve:**


**Technical issues:**


**Next time:**


---

**Print this, laminate it, keep it with your hardware kit.** 📋

# User Workflows

## Who Uses This System

**Primary Users:** Peer workers at festivals

- Handing out cards at registration
- Operating tap stations
- NOT responsible for troubleshooting tech

**Secondary Users:** Clancy + data team

- Setting up system before event
- Exporting/analyzing data after event
- Maintaining hardware between events

## Key Workflows

### 1. Pre-Event Setup (Clancy)

**Timeline:** Morning of event, ~30 minutes

1. **Initialize cards (if not done):**
   - Run card init script
   - Tap 100 cards in sequence
   - Script writes token_id (001-100) to each
2. **Boot Pis:**

   - Connect power banks
   - Wait 30 seconds for boot
   - Verify: LEDs blink or beep on startup (shows ready)

3. **Quick test:**

   - Tap one card at Station 1 → should beep
   - Tap same card at Station 2 → should beep
   - Check log: `sqlite3 data/events.db "SELECT COUNT(*) FROM events;"`
   - Should see 2 events

4. **Position stations:**

   - Station 1: Registration desk (visible "TAP HERE" sign)
   - Station 2: Exit point (after service complete)

5. **Brief peers:**
   - "Give people a card when they join"
   - "Tell them to tap at each station"
   - "Beep = success, double beep = already tapped here"
   - "If no beep and they swear they tapped, come get me"

---

### 2. During Event - Peer at Registration

**Workflow:**

1. Participant arrives
2. Peer hands them card: "This helps us track wait times - tap it at each station"
3. Person taps card to Station 1 reader
4. **BEEP** (or green LED flash)
5. Peer: "You're checked in, current wait is about X minutes" (estimate from crowd)
6. Person joins queue

**If problems:**

- No beep → "Try tapping again, hold it flat"
- Still no beep → "No worries, we'll track it manually" (peer notes time on paper)
- Double beep → "Looks like you already tapped - you're good"

**Peer does NOT:**

- Troubleshoot hardware
- Reset the Pi
- Check logs

---

### 3. During Event - Participant Journey

**From participant perspective:**

1. Get card from peer (looks like a plastic card/token)
2. Tap at Station 1 → hear beep → know they're checked in
3. Wait for service (do whatever while waiting)
4. Complete service (consult, get results, etc.)
5. Tap at Station 2 (exit) → hear beep → done
6. Return card to peer OR keep it (we don't care, card is cheap)

**Simple, minimal friction, doesn't interfere with actual service.**

---

### 4. During Event - Monitoring (Optional)

**If Clancy is onsite and wants to check system:**

```bash
# SSH into Pi (if on same network)
ssh pi@raspberrypi.local

# Check service status
sudo systemctl status tap-station

# Check recent activity
tail -f /home/pi/tap-logger/logs/tap-station.log

# Check event count
sqlite3 /home/pi/tap-logger/data/events.db "SELECT COUNT(*) FROM events;"

# Check battery
vcgencmd get_throttled
```

**But ideally: system just works, no monitoring needed.**

---

### 5. Post-Event - Data Export (Clancy)

**Timeline:** Right after event, ~5 minutes

1. **Stop services (if still running):**

   ```bash
      sudo systemctl stop tap-station
   ```

2. **Export data:**

   ```bash
      python3 export_data.py
      # Creates: export_20250615_143022.csv
   ```

3. **Backup database:**

   ```bash
      cp data/events.db backups/events_festival-2025-summer.db
   ```

4. **Copy to laptop:**

   ```bash
      scp pi@192.168.x.x:tap-logger/export*.csv ~/Desktop/
   ```

5. **Shutdown Pis:**

   ```bash
      sudo shutdown now
   ```

6. **Pack hardware**

---

### 6. Data Analysis (Clancy)

**Timeline:** After event, whenever

1. **Load CSV into R:**

   ```r
      library(tidyverse)
      events <- read_csv("export.csv")
   ```

2. **Calculate wait times:**

   ```r
      flow <- events %>%
      pivot_wider(names_from = stage, values_from = timestamp) %>%
      mutate(
         wait_time = difftime(EXIT, QUEUE_JOIN, units = "mins"),
         total_time = as.numeric(wait_time)
      )

      median(flow$total_time, na.rm = TRUE)
      quantile(flow$total_time, 0.9, na.rm = TRUE)
   ```

3. **Identify bottlenecks, abandonment rate, throughput, etc.**

4. **Generate report for team/funders**

5. **Make flow improvements for next event (PDSA cycle)**

---

## Error Scenarios & Recovery

### Card Read Fails (Common)

**Symptom:** No beep when card tapped

**Peer action:**

- "Try again, hold it flat"
- If still fails: "No worries, we've got you covered" (manual log)

**What system does:**

- Retry read 3×
- If all fail: log error, give error beep, move on
- System doesn't crash, just skips this tap

---

### Pi Crashes (Rare)

**Symptom:** No response to taps, LEDs off

**Peer action:**

- Come get Clancy

**Clancy action:**

- Check power bank (swap if needed)
- Reboot Pi (unplug/replug power)
- System auto-starts on boot (systemd)
- Check logs to see what crashed

**Data safety:**

- SQLite in WAL mode = all previous taps are safe
- System resumes from where it left off

---

### Person Loses Card (Uncommon)

**Symptom:** Person at exit, no card

**Peer action:**

- "What number was on your card?" (if visual number printed)
- Or: "No worries, we can track manually"

**System:**

- If we know token_id, we can check if they tapped at queue join
- If not: just missing data point, not a crisis

---

### Duplicate Tap (Edge Case)

**Symptom:** Person accidentally taps at same station twice

**System:**

- Detects stage lock (this token already logged at QUEUE_JOIN)
- Gives double-beep pattern
- Does NOT log duplicate

**Peer:**

- "You already tapped here, you're good!"

---

## Design Philosophy

**For peers:**

- Simple, clear, forgiving
- Errors don't stop the system
- Fallback to manual if needed
- No technical knowledge required

**For system:**

- Fail gracefully
- Log errors but keep running
- Data integrity over perfect capture
- Post-event export is simple

**For Clancy:**

- Easy to setup/maintain
- Clear logs for debugging
- Can SSH in if needed, but shouldn't need to
- Data export is trivial

---

## Success Criteria (User Perspective)

**Peer says:**

- "That was easy, way better than manual tracking"
- "I didn't have to think about it"
- "A few people had trouble tapping, but it wasn't a big deal"

**Participant says:**

- "Quick and easy, barely noticed it"
- "Felt professional and organized"

**Clancy says:**

- "Setup took 20 minutes, ran for 8 hours, no issues"
- "Data export worked first try"
- "Can clearly see median wait time was 18 minutes"
- "Ready to deploy at next festival"

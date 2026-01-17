# 3-Stage Service Tracking Guide

**Version:** 2.2  
**Date:** January 18, 2026  
**Feature:** Enhanced service flow tracking

---

## Overview

The 3-stage tracking system separates **queue wait time** from **actual service time**, providing much deeper operational insights.

### Traditional 2-Stage System

```
QUEUE_JOIN ─────────────────────► EXIT
     └─────── Total Time ──────────┘
```

**Problem:** Can't tell if delays are from long queue or slow service

### New 3-Stage System

```
QUEUE_JOIN ──────► SERVICE_START ──────► EXIT
     └── Queue Wait ──┘  └── Service Time ──┘
```

**Benefit:** Know exactly where time is spent

---

## How It Works

### The Three Stages

**1. QUEUE_JOIN** - Person enters queue

- Participant taps card at entry station
- Joins waiting queue
- Clock starts

**2. SERVICE_START** - Staff begins helping (NEW!)

- Participant reaches front of queue
- Staff taps card when beginning service
- Marks transition from waiting to active service

**3. EXIT** - Service complete

- Participant taps card when leaving
- Journey complete
- Full metrics available

---

## Setup Instructions

### Option A: Add a Third Station (Recommended)

**Best for:** Larger operations with dedicated staff

```
Station 1 (Entry):    config.yaml → stage: "QUEUE_JOIN"
Station 2 (Service):  config.yaml → stage: "SERVICE_START"
Station 3 (Exit):     config.yaml → stage: "EXIT"
```

**Physical Setup:**

```
[Entry Point]                    [Service Area]                [Exit Point]
     ↓                                ↓                              ↓
Station 1: QUEUE_JOIN          Station 2: SERVICE_START       Station 3: EXIT
(Participants tap              (Staff taps when               (Participants tap
 when joining queue)            beginning service)             when leaving)
```

### Option B: Staff-Only Station 2 (Budget Option)

**Best for:** Smaller operations, reusing existing hardware

```
Station 1: QUEUE_JOIN (participants tap)
Station 2: SERVICE_START (staff taps) ← Can be mobile phone!
Station 2 (alt): EXIT (participants tap when done)
```

**Use mobile app for SERVICE_START:**

- Cheaper than third Raspberry Pi
- Staff carries phone
- Taps participant's card when beginning service
- See [Mobile App Guide](MOBILE.md)

### Option C: Hybrid (Most Flexible)

```
Station 1: QUEUE_JOIN (Raspberry Pi at entry)
Phone: SERVICE_START (Staff member's phone)
Station 2: EXIT (Raspberry Pi at exit)
```

---

## Configuration

### For Raspberry Pi Stations

Edit `config.yaml` on each station:

**Station 1 (Entry):**

```yaml
station:
  device_id: "station1"
  stage: "QUEUE_JOIN" # Unchanged
  session_id: "festival-2026-01"
```

**Station 2 (Service Start):**

```yaml
station:
  device_id: "station2"
  stage: "SERVICE_START" # NEW!
  session_id: "festival-2026-01"
```

**Station 3 (Exit):**

```yaml
station:
  device_id: "station3"
  stage: "EXIT"
  session_id: "festival-2026-01"
```

### For Mobile App

In mobile app settings:

- Set Stage: `SERVICE_START`
- Set Device ID: `phone-1` (or staff member name)
- Set same Session ID as Pi stations

---

## What You Get

### New Dashboard Metrics

When 3-stage data is detected, dashboard automatically shows:

#### **In Queue vs In Service**

- **In Queue:** People waiting (QUEUE_JOIN → not yet SERVICE_START)
- **Being Served:** People actively being helped (SERVICE_START → not yet EXIT)

#### **Separate Time Metrics**

- **Avg Queue Wait:** Time waiting (QUEUE_JOIN → SERVICE_START)
- **Avg Service Time:** Time being helped (SERVICE_START → EXIT)
- **Avg Total Time:** Complete journey (QUEUE_JOIN → EXIT)

### Example Data

```
Traditional View:
Avg Wait Time: 25 minutes
└─ What does this include? 🤷

3-Stage View:
Avg Queue Wait: 18 minutes  ← Time spent waiting
Avg Service Time: 7 minutes  ← Time staff spent helping
Avg Total Time: 25 minutes   ← Matches old metric
```

**Insight:** Most time is queue, not service! Add more capacity.

---

## Operational Benefits

### 1. Identify Bottlenecks

**Scenario A: Long Queue Wait, Short Service**

```
Queue Wait: 30 min 🔴
Service Time: 5 min ✓
→ Problem: Not enough staff
→ Solution: Add testing lanes
```

**Scenario B: Short Queue Wait, Long Service**

```
Queue Wait: 5 min ✓
Service Time: 25 min 🔴
→ Problem: Service is slow/complex
→ Solution: Streamline process or train staff
```

### 2. Measure Service Quality

Track service time trends:

```
Early event: 8 min avg → Staff fresh
Peak time:  12 min avg → Rush causes delays
Late event:  7 min avg → Tired but experienced
```

### 3. Optimize Resources

**Before 3-stage:**

- "Wait times are long, add more staff?"
- No data on what's actually slow

**After 3-stage:**

- "Queue wait is 20 min, service is 8 min"
- Data shows need more lanes, not faster service

### 4. Funder Reporting

**Old metric:**

- "Average wait: 25 minutes"

**New metrics:**

- "Participants waited 18 minutes in queue"
- "Service delivered in 7 minutes per person"
- "94% throughput efficiency"

---

## Staff Workflow

### For Staff at Service Area

**When participant reaches front of queue:**

1. Participant hands you their card
2. **Tap card on SERVICE_START station** (or your phone)
3. Begin drug checking service
4. Complete service
5. Send participant to exit station

**Key:** Tap card BEFORE starting service, not after!

### Training Points

- "Tap when you START, not when you finish"
- Card tap = "I'm beginning to help this person now"
- Takes 1 second, don't skip it!
- This data helps improve service for everyone

---

## Backwards Compatibility

### Using 3-Stage with Existing 2-Stage Data

**Good news:** Old data still works!

- System detects if SERVICE_START exists
- If no SERVICE_START: Uses old 2-stage calculation
- If SERVICE_START present: Uses new 3-stage calculation
- Dashboard auto-adapts

**Migration Path:**

```
Day 1-3: Run 2-stage (QUEUE_JOIN → EXIT)
         ↓ (collect baseline data)
Day 4+:  Add SERVICE_START station
         ↓ (3-stage kicks in automatically)
         Dashboard shows new metrics immediately
```

### Mixed Data

What if some journeys have SERVICE_START and some don't?

- **2-stage journeys:** Counted in "Avg Total Time" only
- **3-stage journeys:** Counted in all metrics
- Dashboard shows: "X% using 3-stage tracking"

---

## Troubleshooting

### Dashboard not showing 3-stage metrics

**Check:**

1. Do any journeys have SERVICE_START events?

   ```bash
   sqlite3 data/events.db "SELECT COUNT(*) FROM events WHERE stage='SERVICE_START'"
   ```

   If returns 0, no 3-stage data yet

2. Is Station 2 configured correctly?

   ```yaml
   stage: "SERVICE_START" # Must be exactly this
   ```

3. Are all stations using same `session_id`?

### Service time shows 0 or weird values

**Possible causes:**

- Staff tapping SERVICE_START AFTER service (should be before)
- Clock sync issues between stations
- Card tapped at SERVICE_START and EXIT in wrong order

**Fix:** Remind staff to tap when STARTING service

### Some people "stuck" in SERVICE_START

**Symptom:** "Being Served" count keeps growing

**Cause:** Staff forgetting to send people to exit station

**Fix:**

- Remind staff: "Make sure everyone exits!"
- Use "Mark as Exited" tool in control panel

---

## Data Examples

### Sample Journey (3-Stage)

```
Token 042:
├─ QUEUE_JOIN:     14:30:00 (entered queue)
├─ SERVICE_START:  14:48:00 (began service, waited 18 min)
└─ EXIT:           14:55:00 (completed, service took 7 min)

Analysis:
• Queue Wait: 18 minutes
• Service Time: 7 minutes
• Total Time: 25 minutes
```

### Sample Journey (2-Stage - Old Style)

```
Token 067:
├─ QUEUE_JOIN:  15:00:00
└─ EXIT:        15:23:00

Analysis:
• Total Time: 23 minutes
• Cannot determine queue vs service split
```

---

## Best Practices

### DO

✅ Tap card when STARTING service (not finishing)  
✅ Keep SERVICE_START station near service area  
✅ Train all staff on workflow  
✅ Monitor "Being Served" count for stuck cards  
✅ Use same session_id across all stations

### DON'T

❌ Don't tap SERVICE_START after completing service  
❌ Don't skip SERVICE_START taps to "save time"  
❌ Don't use different session_ids  
❌ Don't leave SERVICE_START station unattended

---

## FAQ

**Q: Do I need three Raspberry Pis?**  
A: No! Use mobile phone for SERVICE_START station.

**Q: What if staff forget to tap SERVICE_START?**  
A: Those journeys fall back to 2-stage (QUEUE_JOIN → EXIT). You still get total time, just not the split.

**Q: Can I add SERVICE_START mid-event?**  
A: Yes! Dashboard auto-detects and shows new metrics immediately.

**Q: Does this affect my existing data?**  
A: No! Old 2-stage data is preserved and still usable.

**Q: What if someone taps stations out of order?**  
A: System is resilient. Uses latest tap per stage. Unusual patterns flagged in logs.

**Q: Can I have multiple SERVICE_START stations?**  
A: Yes! If you have 3 testing lanes, use 3 phones/stations all set to SERVICE_START.

---

## Next Steps

1. **Test locally:** Set up three stages on test system
2. **Train staff:** Quick 5-minute workflow training
3. **Deploy gradually:** Add SERVICE_START after first day if unsure
4. **Monitor dashboard:** Watch for new metrics to appear
5. **Analyze data:** Use insights to optimize operations

---

## Technical Details

### Database Schema

No changes needed! Existing `events` table handles all three stages:

```sql
events (
  token_id TEXT,    -- Card identifier
  stage TEXT,       -- QUEUE_JOIN, SERVICE_START, or EXIT
  timestamp TEXT,   -- When tap occurred
  session_id TEXT,  -- Event identifier
  device_id TEXT    -- Which station
)
```

### Query Logic

System automatically detects 3-stage journeys:

```sql
-- 3-stage journey
SELECT
  QUEUE_JOIN.timestamp as queue_time,
  SERVICE_START.timestamp as service_start,
  EXIT.timestamp as exit_time
FROM events
WHERE token_id = '042'
```

If SERVICE_START is NULL → 2-stage calculation  
If SERVICE_START exists → 3-stage calculation

---

## Support

Questions?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Check [NEW_FEATURES.md](NEW_FEATURES.md)
- Open GitHub issue
- Contact development team

---

**Transform your data - separate waiting from service! 📊**

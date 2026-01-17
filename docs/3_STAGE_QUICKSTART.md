# 3-Stage Tracking - Quick Start

## TL;DR

Add a third stage (`SERVICE_START`) to separate **queue wait** from **service time**.

```
Before: QUEUE_JOIN ────────────► EXIT (25 min total - but why?)
After:  QUEUE_JOIN ──► SERVICE_START ──► EXIT (18 min queue + 7 min service)
```

---

## Quick Setup (3 Options)

### Option 1: Three Raspberry Pis

```
Station 1: QUEUE_JOIN      (entry)
Station 2: SERVICE_START   (service area)
Station 3: EXIT            (exit)
```

### Option 2: Two Pis + Phone (Cheapest!)

```
Station 1 (Pi):   QUEUE_JOIN      (entry)
Phone:            SERVICE_START   (staff carries)
Station 2 (Pi):   EXIT            (exit)
```

### Option 3: Gradual Migration

```
Day 1-3:  2-stage (collect baseline)
Day 4+:   Add SERVICE_START station
          (dashboard auto-shows new metrics)
```

---

## Configuration

### Edit config.yaml on Station 2

```yaml
station:
  device_id: "station2"
  stage: "SERVICE_START" # Change this line!
  session_id: "festival-2026-01" # Same as other stations
```

### Mobile App Setup

```
Settings → Stage → SERVICE_START
         → Device ID → phone-1
         → Session ID → (same as stations)
```

---

## Staff Workflow

**When participant reaches front of queue:**

1. Take their card
2. **Tap card on SERVICE_START station** ⭐
3. Begin service
4. Complete service
5. Send to exit

**Key:** Tap when STARTING, not finishing!

---

## What You See

### Dashboard Shows (when 3-stage detected)

```
┌──────────────────────────────────┐
│ 📊 3-Stage Tracking Active       │
└──────────────────────────────────┘

In Queue: 8          In Service: 3
Avg Queue Wait: 18 min   Avg Service Time: 7 min
Avg Total Time: 25 min
```

### Without 3-Stage Data

```
In Queue: 8
Avg Wait Time: 25 min
(Old style - no split)
```

---

## Benefits

✅ Know where delays happen (queue vs service)  
✅ Optimize staffing decisions  
✅ Better funder reporting  
✅ Identify bottlenecks  
✅ Measure service efficiency

---

## Troubleshooting

**Not seeing 3-stage metrics?**

- Check Station 2: `stage: "SERVICE_START"` (exact spelling!)
- Verify same `session_id` on all stations
- Need at least one complete journey with SERVICE_START

**Service count keeps growing?**

- Staff forgetting to send people to exit
- Use "Mark as Exited" in control panel

---

## Full Documentation

See [3_STAGE_TRACKING.md](3_STAGE_TRACKING.md) for complete guide.

---

**Get deeper insights in 10 minutes! 🚀**

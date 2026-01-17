# New Features Guide - Drug Checking Operations

**Version:** 2.1  
**Date:** January 18, 2026  
**Focus:** Enhanced real-time monitoring and public-facing displays

---

## Overview

Three new features have been added to improve drug checking operations:

1. **Public Queue Display** - Simple display for participants
2. **Enhanced Staff Alerts** - Proactive operational monitoring
3. **Shift Summary** - Quick handoff information

---

## 1. Public Queue Display

### Purpose

Provide participants with real-time queue information without asking staff.

### Access

```
http://<station-ip>:5000/public
```

### Features

- **Large queue length display** (easy to read from distance)
- **Estimated wait time** for new arrivals
- **Service status indicator** (open/closed)
- **Completed today count**
- **Average service time**
- **Auto-refresh every 5 seconds**

### Setup Instructions

**Option A: Dedicated Tablet**

1. Get a cheap Android tablet or iPad
2. Open browser to `http://station1.local:5000/public`
3. Enable full-screen mode (browser settings)
4. Mount tablet at entry point where participants can see it
5. Leave it running - it will auto-update

**Option B: Large Monitor**

1. Connect HDMI monitor to Raspberry Pi (if using station1 as main)
2. Open Chromium in kiosk mode:

   ```bash
   chromium-browser --kiosk http://localhost:5000/public
   ```

3. Display will auto-refresh

**Option C: Staff Phone**

- Any staff member can open the page on their phone
- Share URL via QR code for easy access

### Benefits

- ✅ Reduces "how long is the wait?" questions to staff
- ✅ Manages participant expectations
- ✅ Shows service is active/operational
- ✅ Professional appearance for public-facing operations

### Customization

To modify appearance, edit: `tap_station/templates/public.html`

---

## 2. Enhanced Staff Dashboard Alerts

### Purpose

Proactive monitoring to detect operational issues before they become critical.

### Access

Existing dashboard (now with enhanced alerts):

```
http://<station-ip>:5000/dashboard
```

### New Alert Types

#### 🚨 Critical Alerts (Red)

- **Queue >20 people** - "Queue critical - consider additional resources"
- **Wait time >90 minutes** - "Critical wait time"
- **No activity >10 min** - "Station may be down"

#### ⚠️ Warning Alerts (Yellow)

- **Queue >10 people** - "Queue is long"
- **Wait time >45 minutes** - "Longest wait: X min"
- **No taps in 5+ minutes** - "Check stations"
- **People in queue >2 hours** - "Possible abandonments or missed exits"

#### ℹ️ Info Alerts (Blue)

- **Capacity >90%** - "Operating near capacity"
- **Service time variance** - "Longest service: X min" (indicates complex cases)

### Activity Monitoring

The system now automatically detects:

1. **Station Failures**
   - No activity in 10 minutes → Critical alert
   - No activity in 5 minutes → Warning

2. **Service Time Anomalies**
   - If someone takes 3× longer than average
   - May indicate complex sample or issue

3. **Stuck Cards**
   - People in queue >2 hours without exit
   - Likely abandonments or missed exit taps

4. **Capacity Issues**
   - Near-capacity warnings
   - Queue length trends

### Dashboard Enhancements

**Visual Queue Health**

- 🟢 Green: Queue <5, wait <30 min (good)
- 🔵 Blue: Queue 5-10, wait 30-45 min (moderate)
- 🟡 Yellow: Queue 10-20, wait 45-90 min (warning)
- 🔴 Red: Queue >20, wait >90 min (critical)

The queue card background color changes based on health status.

---

## 3. Shift Summary

### Purpose

Quick handoff information when shifts change.

### Access

```
http://<station-ip>:5000/shift
```

### What It Shows

**Current State:**

- Number of people currently in queue
- Completed services (last 4 hours)
- Average wait time (this shift)
- Total service hours today

**Shift Insights:**

- Busiest hour (and how many people)
- Longest current wait
- Current time

**Printable Format:**

- Print-friendly layout
- Can be added to shift handoff notes

### Usage

**At Shift Change:**

1. Outgoing staff opens `/shift` page
2. Reviews numbers with incoming staff
3. Optional: Print copy for records
4. Incoming staff can see at-a-glance status

**Quick Check:**

- Coordinators can check shift summary remotely
- No need to disturb staff on duty

---

## Quick Reference - All Endpoints

| Endpoint     | Purpose                  | Audience     | Refresh |
| ------------ | ------------------------ | ------------ | ------- |
| `/public`    | Queue status display     | Participants | 5 sec   |
| `/dashboard` | Full operational metrics | Staff        | 5 sec   |
| `/monitor`   | Simple large view        | Staff        | 5 sec   |
| `/shift`     | Shift handoff summary    | Staff        | Manual  |
| `/control`   | System administration    | Coordinators | Manual  |

---

## API Endpoints

### `/api/public`

Returns public-safe statistics:

```json
{
  "queue_length": 8,
  "estimated_wait_minutes": 25,
  "completed_today": 42,
  "avg_service_minutes": 15,
  "service_active": true,
  "session_id": "festival-2026-01",
  "timestamp": "2026-01-18T14:30:00Z"
}
```

### `/api/shift-summary`

Returns shift handoff data:

```json
{
  "current_queue": 8,
  "completed_this_shift": 23,
  "avg_wait_minutes_shift": 18,
  "busiest_hour": "14:00",
  "busiest_hour_count": 12,
  "service_hours_today": 6.5,
  "longest_current_wait_minutes": 35,
  "timestamp": "2026-01-18T14:30:00Z",
  "session_id": "festival-2026-01"
}
```

---

## Recommended Setup for Events

### Small Event (1-2 staff)

```
[Entry Station] ← Station 1 (Raspberry Pi)
        ↓
[Testing Area]
        ↓
[Exit Station] ← Station 2 (Raspberry Pi)

Staff phone: /dashboard (for monitoring)
```

### Medium Event (3-5 staff)

```
Tablet at entry: /public (for participants)
Coordinator laptop: /dashboard (for monitoring)
Entry station: Station 1
Exit station: Station 2
```

### Large Event (6+ staff)

```
Large monitor at entry: /public
Coordinator station: /dashboard (main monitor)
Staff tablets: /monitor (simplified view)
Shift leads: /shift (for handoffs)
Multiple stations: Station 1, 2, 3...
```

---

## Troubleshooting

### Public display not updating

1. Check network connection
2. Verify web server is running: `sudo systemctl status tap-station`
3. Check browser console for errors
4. Try refreshing page

### Alerts not showing

1. Ensure dashboard has recent data (auto-refresh every 5 seconds)
2. Check `/api/dashboard` endpoint directly
3. Clear browser cache

### Shift summary shows "--"

1. May be no data yet (service just started)
2. Check database has events: `sqlite3 data/events.db "SELECT COUNT(*) FROM events"`
3. Verify session_id in config matches events

---

## Tips for Staff

**For Entry Staff:**

- Set up `/public` display before event starts
- Point participants to display: "Check the screen for wait times"
- Reduces repetitive questions

**For Coordinators:**

- Keep `/dashboard` open on laptop/tablet
- Watch for critical alerts (red)
- Plan breaks during slow periods (green/blue health)

**For Shift Changes:**

- Open `/shift` 5 minutes before handoff
- Walk through key numbers
- Highlight any alerts or issues

---

## Future Enhancements (Under Consideration)

Based on field use, we may add:

- Battery level monitoring (if detectable)
- SMS/email alerts for critical issues
- Service time tracking (add SERVICE_START stage)
- Export shift reports to PDF
- Historical comparison ("busier than usual?")

---

## Feedback

Using these features at your event? We'd love to hear:

- What worked well?
- What could be improved?
- Additional metrics needed?

Open an issue on GitHub or contact the development team.

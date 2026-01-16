# Development Roadmap

## Overview

This document outlines potential enhancements to the NFC Tap Logger system. Each section is rated by complexity and value.

## Quick Wins (Low Effort, High Value)

### 1. NFC Tools App Integration ⭐⭐⭐

**What:** Write NDEF records to cards that can be read by NFC Tools app (iOS/Android)
**Why:**

- Participants can tap their own phone to check their status
- Fallback if station is down (peer uses their phone)
- QR code alternative for older phones

**Implementation:**

```python
# Add to nfc_reader.py
def write_ndef_record(self, token_id: str, url: str):
    """Write NDEF URL record to card"""
    # Format: https://yoursite.com/check?token=001
    # Participant taps phone → sees "Token 001 checked in at 2:15pm"
```

**Effort:** 2-3 days
**Value:** High - gives participants visibility, reduces "did it work?" questions

---

### 2. Quick-Start Cards (Laminated Cheat Sheets) ⭐⭐⭐

**What:** One-page visual guides for peers
**Why:** Faster training, reference during event

**Cards to create:**

- Station Setup (15 min version)
- Troubleshooting Flowchart
- Peer Workflow Card
- Emergency Recovery Steps

**Effort:** 1 day
**Value:** High - reduces training time, empowers peers

---

### 3. Health Check Endpoint ⭐⭐

**What:** Simple HTTP endpoint for monitoring
**Why:** Check if station is alive without SSH

**Implementation:**

```python
# Add to main.py
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
```

**Usage:**

```bash
curl http://station1.local:8080/health
# Returns "OK" if service running
```

**Effort:** 1 day
**Value:** Medium - easier monitoring without SSH

---

## Medium Enhancements (3-5 days each)

### 4. Smartphone Fallback Mode ⭐⭐⭐

**What:** Android app that does same job as Pi station
**Why:**

- Backup if Pi fails
- Lower cost deployment
- Easier setup for small events

**Options:**

- **NFC Tools App** (existing app) - just read UID, manual logging
- **Custom Android app** - full featured, syncs to Pi database
- **PWA (Progressive Web App)** - works on iOS too, uses Web NFC API

**Recommendation:** Start with PWA

```javascript
// Example: Web NFC API
const ndef = new NDEFReader();
await ndef.scan();
ndef.addEventListener("reading", ({ serialNumber }) => {
  fetch("/api/log-event", {
    method: "POST",
    body: JSON.stringify({ uid: serialNumber }),
  });
});
```

**Effort:** 5 days for basic PWA
**Value:** High - great backup option

---

### 5. Real-Time Dashboard (Flask Web UI) ⭐⭐

**What:** Simple web page showing live stats
**Why:** Clancy can monitor from laptop/phone

**Features:**

- Current event count
- Last 10 taps
- Battery status
- Error log
- Live wait time estimate

**Implementation:**

```python
# Add to tap_station/
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/stats')
def stats():
    return jsonify({
        'total_events': db.get_event_count(),
        'recent': db.get_recent_events(10),
        'uptime': get_uptime()
    })
```

**Effort:** 3-4 days
**Value:** Medium - nice to have, not critical for v1.0

---

### 6. QR Code Alternative ⭐⭐

**What:** Print QR codes on cards, scan with phone camera
**Why:**

- Backup if NFC fails
- Works with any smartphone
- Cheaper than NFC cards

**Implementation:**

- Generate QR codes: `https://yoursite.com/tap?token=001&stage=queue`
- Peer scans with phone camera
- Logs to same database

**Effort:** 2-3 days
**Value:** Medium - good fallback, but adds peer friction

---

## Advanced Features (1-2 weeks each)

### 7. Multi-Station Network Sync ⭐

**What:** Stations sync data in real-time (if WiFi available)
**Why:**

- See wait times during event
- Detect bottlenecks live
- Dashboard shows all stations

**Implementation:**

- Add Redis/MQTT for pub/sub
- Stations publish events to central broker
- Dashboard subscribes to all events

**Effort:** 1-2 weeks
**Value:** Medium - nice for larger deployments

---

### 8. Participant-Facing Features ⭐

**What:** Participants can check their status via web/app
**Why:** Transparency, reduces questions

**Features:**

- "Where am I in queue?" → scan card/QR
- Estimated wait time
- SMS notifications when service ready

**Effort:** 2 weeks
**Value:** Low for v1.0 - adds complexity, requires internet

---

### 9. Multi-Event Tracking ⭐

**What:** Same card works across multiple festivals
**Why:**

- Longitudinal data
- Participant loyalty/tracking
- Less waste (reuse cards)

**Implementation:**

- Add `event_id` to database schema
- Card stores participant ID, not token ID
- Privacy considerations (anonymization)

**Effort:** 1 week
**Value:** Low for v1.0 - adds privacy concerns

---

### 10. Docker Deployment 🐳

**What:** Package system as Docker container
**Why:** Easier deployment, reproducible builds

**Implementation:**

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-m", "tap_station.main"]
```

**Effort:** 2-3 days
**Value:** Low for Pi deployment, high for server deployment

---

## Documentation Improvements

### 11. Visual Setup Guide ⭐⭐⭐

**What:** Photos/diagrams of hardware setup
**Why:** Easier than text-only instructions

**Content:**

- Wiring diagram (color-coded)
- Photos of correct PN532 placement
- LED/buzzer connection photos
- Common mistakes (what NOT to do)

**Effort:** 1 day (with photos)
**Value:** High - prevents setup errors

---

### 12. Video Tutorials ⭐⭐

**What:** 5-10 min videos for key tasks
**Why:** Some people learn better visually

**Videos:**

1. Hardware setup (5 min)
2. Software installation (3 min)
3. Card initialization (3 min)
4. Troubleshooting common issues (5 min)

**Effort:** 2-3 days
**Value:** Medium - time investment but helpful

---

### 13. Troubleshooting Flowchart ⭐⭐⭐

**What:** Decision tree for common problems
**Why:** Faster problem resolution

**Example:**

```
Card won't read?
├─ Is PN532 detected? (i2cdetect)
│  ├─ No → Check wiring
│  └─ Yes → Is card NTAG215?
│     ├─ No → Get correct cards
│     └─ Yes → Check antenna placement
```

**Effort:** 1 day
**Value:** High - reduces support burden

---

## Recommended Priorities

### Phase 1 (Next 2 weeks)

1. ✅ **Quick-Start Cards** - Immediate value for deployment
2. ✅ **NFC Tools App Integration** - Gives participants visibility
3. ✅ **Visual Setup Guide** - Prevents setup errors

### Phase 2 (Month 2)

1. **Smartphone Fallback (PWA)** - Backup option
2. **Real-Time Dashboard** - Live monitoring
3. **Health Check Endpoint** - Easier ops

### Phase 3 (Month 3+)

1. **QR Code Alternative** - Additional resilience
2. **Multi-Station Sync** - For larger deployments
3. **Video Tutorials** - Training materials

### Maybe Never

- Participant-facing features (privacy concerns, adds complexity)
- Multi-event tracking (privacy, scope creep)
- Docker (Pi doesn't need it)

---

## Alternative Deployment Options

### Option A: Pi-Only (Current)

- **Pros:** Reliable, offline, tested
- **Cons:** Hardware cost, setup complexity
- **Best for:** Main deployment

### Option B: Smartphone-Only

- **Pros:** No hardware, instant setup
- **Cons:** Requires internet, battery drain, less reliable
- **Best for:** Small events, backup

### Option C: Hybrid (Pi + Phone Backup)

- **Pros:** Best of both worlds
- **Cons:** More complexity
- **Best for:** Critical deployments

### Option D: Cloud-Based with Phone Readers

- **Pros:** Centralized data, real-time analytics
- **Cons:** Requires internet, single point of failure
- **Best for:** Multi-site deployments

---

## Tech Stack Alternatives

### Current: Python + SQLite + PN532

**Good for:** Offline, simple, maintainable

### Alternative 1: Web-Based

- **Stack:** Flask + PostgreSQL + Web NFC API
- **Pros:** Web dashboard, phone readers
- **Cons:** Requires server, internet dependency

### Alternative 2: Native Mobile

- **Stack:** React Native + Firebase
- **Pros:** Professional UX, cloud sync
- **Cons:** Development time, cost

### Alternative 3: Hybrid

- **Stack:** Current (Pi) + REST API + React dashboard
- **Pros:** Keeps offline core, adds visibility
- **Cons:** More moving parts

---

## Cost-Benefit Analysis

| Enhancement          | Effort | Value | Recommendation |
| -------------------- | ------ | ----- | -------------- |
| Quick-Start Cards    | 1d     | High  | **Do Now**     |
| NFC Tools App        | 2-3d   | High  | **Do Now**     |
| Visual Setup Guide   | 1d     | High  | **Do Now**     |
| Smartphone Fallback  | 5d     | High  | **Phase 2**    |
| Real-Time Dashboard  | 4d     | Med   | **Phase 2**    |
| Health Check API     | 1d     | Med   | **Phase 2**    |
| QR Code Alternative  | 3d     | Med   | **Phase 3**    |
| Multi-Station Sync   | 10d    | Med   | **Phase 3**    |
| Video Tutorials      | 3d     | Med   | **Later**      |
| Participant Features | 14d    | Low   | **Skip v1**    |
| Multi-Event Tracking | 7d     | Low   | **Skip v1**    |
| Docker Packaging     | 3d     | Low   | **Skip**       |

---

## Next Steps

1. **Test current system** at a small event (10-50 people)
2. **Gather feedback** from peers and participants
3. **Prioritize enhancements** based on real pain points
4. **Iterate quickly** - release often, get feedback

---

## Questions to Answer Before Expanding

1. **What's the biggest pain point with current system?**

   - Setup complexity?
   - Peer training?
   - Hardware reliability?
   - Data export/analysis?

2. **What's the deployment environment?**

   - Always have WiFi?
   - Multiple simultaneous events?
   - Indoor vs outdoor?

3. **What's the scale?**

   - 50 people or 500?
   - 2 stations or 10?
   - 1 event/month or 1/week?

4. **Who's the bottleneck?**
   - Clancy's time (setup/maintenance)?
   - Peer training?
   - Hardware procurement?
   - Data analysis?

Answer these → guides what to build next.

---

## Conclusion

**For v1.0:** Focus on documentation and ease of use

- Quick-start cards
- Visual guides
- Better troubleshooting

**For v1.1:** Add visibility and resilience

- NFC Tools app integration
- Smartphone fallback
- Health check API

**For v2.0:** Consider real-time features

- Dashboard
- Multi-station sync
- Live wait time estimates

**Keep it simple.** Every feature adds complexity. Only add what solves real problems.

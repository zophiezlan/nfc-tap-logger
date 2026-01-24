# 🎪 Festival Scenarios - Visual Guide

## Quick Start: Pick a Scenario

```bash
# Scenario 1: HTID (Baseline Success) ✅
python demo_server.py --scenario htid

# Scenario 2: Lost Paradise (Crisis) 🔴
python demo_server.py --scenario lost_paradise_actual

# Scenario 3: Lost Paradise (Ideal) ⭐
python demo_server.py --scenario lost_paradise_ideal
```

Then visit: **http://localhost:8080**

---

## Visual Comparison

### Scenario 1: HTID ✅

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         HTID - SINGLE DAY FESTIVAL
         ✅ MANAGEABLE & SUCCESSFUL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 STAFFING:  6 peers + 6 chemists
⏱️  DURATION:  6 hours
📊 SERVED:     70 groups (110 samples)

📈 QUEUE DYNAMICS:
Hour 1  ▁▁▁       (2-3 people)    - Quiet start
Hour 2  ▃▃▃▃      (8 people)      - Building
Hour 3  ▅▅▅▅▅▅    (15 people)     - Peak
Hour 4  ▃▃▃       (8 people)      - Dropping
Hour 5  ▂▂        (4 people)      - Winding down
Hour 6  ▁         (1-2 people)    - Almost done

⏰ WAIT TIMES:
Average:  15 minutes
Peak:     30 minutes
Abandon:  2% (very low)

✅ OUTCOME: Everyone served, quality conversations,
            sustainable for staff
```

### Scenario 2: Lost Paradise (Actual) 🔴

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    LOST PARADISE - MULTI-DAY FESTIVAL
       🔴 CRITICAL CAPACITY CRISIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 STAFFING:  6 peers + 6 chemists (SAME AS HTID!)
⏱️  DURATION:  12 hours (2 days × 6hr)
📊 SERVED:     150 groups (300 samples)

📈 QUEUE DYNAMICS:
Hour 1  ▇▇▇▇▇▇▇▇▇▇▇▇      (35 people)  - Line before opening
Hour 2  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇    (45 people)  - Constant overload
Hour 3  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇   (60+ people) - Out the door!
Hour 4  ▇▇▇▇▇▇▇▇▇▇▇▇▇▇    (55 people)  - Still overwhelmed
Hour 5  ▇▇▇▇▇▇▇▇▇▇▇       (40 people)  - People giving up
Hour 6  ▇▇▇▇▇▇▇            (25 people)  - Many left

⏰ WAIT TIMES:
Average:  120 minutes (2 hours!)
Peak:     180 minutes (3 HOURS!)
Abandon:  25% (many turned away)

❌ OUTCOME: Severe understaffing, staff burnout,
            many participants couldn't access service

🚨 ALERTS FIRING:
   • Queue critical (60+ vs threshold of 50)
   • Wait time critical (180+ vs threshold of 150)
   • High abandonment rate
   • Staff overwhelmed
```

### Scenario 3: Lost Paradise (Ideal) ⭐

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    LOST PARADISE - MULTI-DAY FESTIVAL
      ⭐ PROPER RESOURCING SOLUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👥 STAFFING:  12 peers + 12 chemists (DOUBLED!)
⏱️  DURATION:  12 hours (2 days × 6hr)
📊 CAPACITY:   250+ groups (500+ samples)

📈 QUEUE DYNAMICS:
Hour 1  ▄▄▄▄        (12 people)   - Steady start
Hour 2  ▅▅▅▅▅       (18 people)   - Building
Hour 3  ▅▅▅▅▅▅      (20 people)   - Peak (manageable!)
Hour 4  ▅▅▅▅▅       (17 people)   - Consistent
Hour 5  ▃▃▃         (10 people)   - Dropping
Hour 6  ▂▂          (5 people)    - Winding down

⏰ WAIT TIMES:
Average:  25 minutes
Peak:     45 minutes
Abandon:  3% (minimal)

✅ OUTCOME: Demand met, quality harm reduction,
            sustainable staffing, happy participants

✅ METRICS:
   • All queue thresholds green
   • Double throughput vs 6+6 staffing
   • Everyone gets served
   • Staff can take proper time with results
```

---

## Side-by-Side Comparison

| Metric | HTID ✅ | LP Actual 🔴 | LP Ideal ⭐ |
|--------|---------|--------------|-------------|
| **Staffing** | 6 + 6 | 6 + 6 | **12 + 12** |
| **Duration** | 6 hrs | 12 hrs | 12 hrs |
| **Demand Level** | Moderate | **VERY HIGH** | Very High |
| | | | |
| **Peak Queue** | ~15 | **60+** 😱 | ~20 |
| **Avg Wait** | 15 min | **120 min** | 25 min |
| **Max Wait** | 30 min | **180 min** | 45 min |
| **Abandoned** | 2% | **25%** | 3% |
| | | | |
| **Groups Served** | 70 | 150 | 250+ |
| **Staff Experience** | Good | **Burnout** | Sustainable |
| **Participant Exp** | Excellent | **Terrible** | Excellent |
| | | | |
| **Result** | ✅ Success | ❌ **Crisis** | ✅ Success |

---

## The Story

### Act 1: HTID - "We Can Do This"
- Single day festival
- Moderate demand
- 6+6 staff handle it well
- Everyone happy

### Act 2: Lost Paradise Actual - "We're Drowning"
- Multi-day festival
- Try to use SAME 6+6 staff
- Queue explodes
- 3 hour waits
- 1 in 4 people leave without service
- Staff completely burned out

### Act 3: Lost Paradise Ideal - "Here's the Solution"
- Same festival
- DOUBLE the staff (12+12)
- Queue stays manageable
- Everyone served
- <45 min waits
- Quality harm reduction conversations
- Sustainable model

---

## For NSW Health Pitch

### Opening
"Let me show you three scenarios based on our actual NSW deployments..."

### The Hook
"Here's HTID - single day, works great with 6 peers and 6 chemists."

### The Problem
"Now here's Lost Paradise with the SAME staffing... watch what happens.
Queue hits 60 people. 3 hour waits. 25% of participants left."

### The Solution
"Now here's the same festival with proper resourcing - 12 and 12.
Queue never goes above 20. 45 minute max wait. Everyone served."

### The Ask
"The difference between crisis and success is doubling the staffing.
That's the investment we're proposing for multi-day festivals."

---

## Technical Notes

- Each scenario has its own database
- Live simulation starts immediately
- Takes 2-3 minutes to see realistic patterns
- Runs continuously for as long as server is up
- All based on actual NSW deployment data

---

## Deploy Options

**For demos/presentations:**
- Deploy all 3 to Render.com (free)
- Give NSW Health all 3 URLs
- They can explore independently

**For workshops:**
- Run locally, switch between scenarios
- Show live how queue dynamics change
- Restart with different --scenario flag

See `DEPLOY_ALL_SCENARIOS.md` for deployment guide.

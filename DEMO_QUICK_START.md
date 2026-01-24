# NSW Health Drug Checking Demo - Quick Start

## 🎯 Three Live Scenarios (Pick One to Explore)

### Option 1: HTID - Success Story ✅
**What works for single-day festivals**

```bash
python demo_server.py --scenario htid
```

Then visit: http://localhost:8080

**What you'll see:**
- Moderate queue (peaks at ~15)
- ~30 min max wait
- Everyone gets served
- 6 peers + 6 chemists handling it well

---

### Option 2: Lost Paradise Actual - The Crisis 🔴
**What happens when you're understaffed**

```bash
python demo_server.py --scenario lost_paradise_actual
```

Then visit: http://localhost:8080

**What you'll see:**
- Queue explodes to 60+ people
- 3 HOUR waits
- 25% abandonment (people leaving)
- Same 6+6 staff completely overwhelmed

---

### Option 3: Lost Paradise Ideal - The Solution ⭐
**What proper resourcing achieves**

```bash
python demo_server.py --scenario lost_paradise_ideal
```

Then visit: http://localhost:8080

**What you'll see:**
- Queue stays manageable (~20)
- <45 min waits
- Everyone served well
- 12 peers + 12 chemists handling it

---

## 🚀 For NSW Health Demo/Presentation

### Deploy All Three (Recommended)

1. **Deploy to Render.com** (free) - Do this 3 times:

   **Deployment 1: HTID**
   - Name: `nfc-demo-htid`
   - Environment Variable: `DEMO_SCENARIO=htid`
   - URL: `https://nfc-demo-htid.onrender.com`

   **Deployment 2: Lost Paradise Actual**
   - Name: `nfc-demo-lost-paradise-actual`
   - Environment Variable: `DEMO_SCENARIO=lost_paradise_actual`
   - URL: `https://nfc-demo-lost-paradise-actual.onrender.com`

   **Deployment 3: Lost Paradise Ideal**
   - Name: `nfc-demo-lost-paradise-ideal`
   - Environment Variable: `DEMO_SCENARIO=lost_paradise_ideal`
   - URL: `https://nfc-demo-lost-paradise-ideal.onrender.com`

2. **Share all three URLs** with NSW Health so they can compare side-by-side!

---

## 💡 Quick Comparison for Your Pitch

Open three browser tabs:

| Tab 1: HTID ✅ | Tab 2: Actual 🔴 | Tab 3: Ideal ⭐ |
|----------------|------------------|-----------------|
| Queue: ~15 | Queue: **60+** | Queue: ~20 |
| Wait: 30min | Wait: **3 HOURS** | Wait: 45min |
| Staff: 6+6 | Staff: 6+6 **(same!)** | Staff: 12+12 |
| Outcome: ✅ Success | Outcome: ❌ **Crisis** | Outcome: ✅ Success |

**The story writes itself!**

---

## 📊 What Each Demo Shows

**HTID Dashboard:**
- Nice steady queue
- Good throughput
- Green alerts
- Happy metrics

**Lost Paradise Actual Dashboard:**
- Queue growing constantly
- Red critical alerts everywhere
- Wait time climbing to 180+ min
- Abandonment alerts firing

**Lost Paradise Ideal Dashboard:**
- Queue managed well
- Double the throughput
- Green metrics
- Everyone served

---

## 🎭 For Workshop Sessions

Run locally and **restart** between scenarios:

```bash
# Show baseline
python demo_server.py --scenario htid

# (Let them explore for 5 min)

# Stop (Ctrl+C), then show the crisis
python demo_server.py --scenario lost_paradise_actual

# (Let them see the queue explode)

# Stop (Ctrl+C), then show the solution
python demo_server.py --scenario lost_paradise_ideal

# (Watch the difference!)
```

Each scenario has its own database so data doesn't mix.

---

## 🔧 Technical Notes

- Each scenario runs independently
- Separate databases: `data/demo_htid.db`, `data/demo_lost_paradise_actual.db`, etc.
- Live simulation starts immediately
- Takes ~2-3 minutes to see realistic queue patterns develop

---

## 📱 Share With Stakeholders

Send them:

> "We've set up three live demos showing different festival scenarios:
>
> 1️⃣ **HTID (Success)**: https://nfc-demo-htid.onrender.com
> What works for single-day festivals
>
> 2️⃣ **Lost Paradise (Crisis)**: https://nfc-demo-lost-paradise-actual.onrender.com
> What happened with same staff but multi-day demand - 3hr waits!
>
> 3️⃣ **Lost Paradise (Ideal)**: https://nfc-demo-lost-paradise-ideal.onrender.com
> What doubling staff achieves - everyone served, <45min waits
>
> Each demo runs live - you'll see real-time queue dynamics. Open all three in separate tabs to compare side-by-side!"

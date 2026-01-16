# Project Context

## The Problem

Festival drug checking services currently have no systematic way to measure wait times or identify bottlenecks. We need data to:

- Optimize staffing and flow
- Report to funders and health authorities
- Improve participant experience
- Run PDSA improvement cycles between events

Current approach is manual observation or rough estimates ("wait time seemed long today").

## The Solution

Two tap stations (Raspberry Pi + NFC reader) at key checkpoints:

- Station 1: Queue join (registration desk)
- Station 2: Exit (after service complete)

Participants tap an NFC card at each station. System logs timestamps. Post-event analysis shows:

- Median wait time
- 90th percentile wait time (captures festival reality)
- Throughput (people/hour)
- Abandonment rate (joined queue but didn't complete)

## The Users

**Primary:** Peer workers at festivals

- Comfortable with basic tech (phones, tablets)
- NOT developers
- Working in chaotic, loud, distracting environments
- Need dead simple workflows

**Secondary:** Clancy (me) + NUAA data team

- Will analyze data post-event
- Need clean CSV exports
- Want to iterate system between festivals

## The Environment

**Festivals:**

- Outdoor, potentially muddy/wet
- Unreliable or no WiFi
- Loud (buzzers helpful for feedback)
- Busy (people asking questions while peers operate system)

**Constraints:**

- Battery powered (can't rely on mains)
- No network for core operation (standalone)
- Must survive being jostled, briefly rained on, etc.

## Success Looks Like

**During event:**

- Peer hands out card: "Tap at each station"
- Person taps at queue → beep (confirmation)
- Person taps at exit → beep
- System just works, no troubleshooting needed

**After event:**

- Export data in 2 minutes
- Load into R → see median wait time, identify bottlenecks
- Make flow improvements for next festival
- Show funders/stakeholders real data

**Not success:**

- Peers spending time debugging tech instead of supporting people
- Data quality so poor we can't calculate wait times
- System crashes halfway through event
- Battery dies after 4 hours

## Why These Choices

**PN532 NFC:** Already owned, proven tech, fast reads  
**NTAG215:** Rewritable, cheap, can track multi-event if needed later  
**SQLite:** Lightweight, no server, perfect for offline  
**Standalone vs networked:** Reliability > real-time features for v1.0  
**Python:** Fast development, good libraries, easy to maintain  
**Raspberry Pi:** Clancy already comfortable with Pi ecosystem

## What Comes After v1.0

If this works well:

- Add more stations (consult start, sample registered, etc.) for detailed bottleneck analysis
- Real-time dashboard (Flask web UI)
- Network sync between stations
- Participant-facing features ("scan QR to check your wait time")
- Multi-event tracking (same card across festivals)

But for now: **nail the basics, prove the concept.**

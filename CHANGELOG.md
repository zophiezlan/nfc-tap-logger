# Changelog

## [2.2.1] - 2025-01-19

### Added - Force-Exit Tool

- **Control Panel Stuck Cards Section** - New UI section showing cards stuck in queue >2 hours
- **Bulk Force-Exit Operations** - Select individual or all stuck cards to mark as exited
- **API: `GET /api/control/stuck-cards`** - Returns list of stuck cards with hours stuck
- **API: `POST /api/control/force-exit`** - Batch marks cards as exited
- **Auto-Refresh** - Stuck cards list updates every 30 seconds
- **Visual Feedback** - Color-coded stuck duration (orange >2h, red >4h)
- **Confirmation Dialogs** - Prevent accidental bulk operations

**Why:** Solves end-of-event cleanup when participants forget to tap out

### Added - Real-Time Export

- **Dashboard Export Buttons** - Three one-click export options in dashboard header
  - "Export Last Hour" - Recent activity
  - "Export Today" - Full day's data
  - "Export All" - Complete session history
- **API: `GET /api/export`** - CSV generation with time-based filtering
- **Auto-Download** - CSV files download automatically with descriptive names
- **Responsive Layout** - Updated dashboard header with flex layout

**Why:** Non-technical staff can export data without SSH access

### Changed

- **Control Panel (`control.html`)** - Added stuck cards management section (+145 lines)
- **Dashboard (`dashboard.html`)** - Updated header layout with export buttons (+30 lines)
- **Web Server (`web_server.py`)** - Added export and force-exit endpoints (+95 lines)

### Technical Details

- Force-exit events marked with `device_id = "manual_force_exit"`
- Forced UIDs use format `"FORCED_{token_id}"` for filtering in analysis
- CSV exports include all 7 columns: id, token_id, uid, stage, timestamp, device_id, session_id
- Export filenames: `nfc_data_{filter}_{session_id}.csv`

### Documentation

- Added `docs/FORCE_EXIT_AND_EXPORT.md` - Complete feature guide
- Added `docs/FORCE_EXIT_QUICKSTART.md` - 2-minute quick start
- Added `IMPLEMENTATION_v2.2.1.md` - Implementation details
- Added `VISUAL_SUMMARY_v2.2.1.md` - Visual feature summary
- Updated `README.md` - Added v2.2.1 to "What's New"

### Performance

- Stuck cards query: <50ms typical
- Force-exit insert: ~10ms per card
- Export hour: <100ms
- Export today: <500ms
- Export all: <2 seconds typical

### Impact

- **Time Savings:** ~8 minutes per event (force-exit + export)
- **Accessibility:** Non-technical staff can now export data
- **Data Quality:** Cleaner analytics without stuck cards
- **Operations:** Mid-event data access enables better decisions

---

## [2.2] - 2025-01-18

### Added - 3-Stage Tracking

- **3-Stage Journey Tracking** - QUEUE_JOIN → SERVICE_START → EXIT
- **Separate Metrics** - Queue wait time vs actual service time
- **Auto-Detection** - System detects 3-stage vs 2-stage mode automatically
- **Dashboard Updates** - New metric cards for in-service count, queue wait, service time
- **Backwards Compatible** - Works with 2-stage (enter/exit) or 3-stage setups

**Why:** Separate queue bottlenecks from service bottlenecks

### Documentation

- Added `docs/3_STAGE_TRACKING.md` - Complete 3-stage guide
- Added `docs/3_STAGE_QUICKSTART.md` - Quick start guide

---

## [2.1] - 2025-01-17

### Added - Operational Intelligence

- **Public Display (`/public`)** - Large-format queue status for participants
- **Enhanced Staff Alerts** - 8 alert types for proactive monitoring
- **Shift Summary (`/shift`)** - Quick handoff information
- **Activity Monitoring** - Detects station failures, long waits, service anomalies
- **Auto-Refresh Dashboards** - 5-second updates for live data

**Why:** Real-time operational intelligence for drug checking staff

### Added Alerts

1. Queue length alerts (>10 warning, >20 critical)
2. Long wait alerts (>20 min)
3. Service time variance detection
4. Throughput drops
5. Capacity utilization monitoring
6. Station failure detection (no activity)
7. Stuck cards detection (>2 hours)
8. Service start distribution (3-stage mode)

### Documentation

- Added `docs/NEW_FEATURES.md` - Complete v2.1 guide
- Added `docs/CONTROL_PANEL.md` - Control panel documentation
- Added `docs/OPERATIONS.md` - Operational workflows
- Updated `README.md` - v2.1 feature summary

---

## [2.0] - 2025-01-15

### Changed - Architecture Improvements

- **WAL Mode** - Enabled Write-Ahead Logging for concurrent reads
- **Database Optimization** - Added indexes for common queries
- **Error Handling** - Improved error messages and recovery
- **Logging** - Enhanced logging for troubleshooting

---

## [1.5] - 2025-01-10

### Added - Mobile PWA

- **Mobile App** - Progressive Web App for Android phones
- **Offline Support** - Service worker for offline operation
- **Batch Sync** - Background sync when network available
- **Installation** - Add to home screen capability

**Why:** Backup option when Raspberry Pi hardware unavailable

---

## [1.0] - 2025-01-01

### Initial Release

- **Core Functionality** - 2-stage tracking (enter/exit)
- **Hardware Support** - Raspberry Pi + PN532 NFC readers
- **Web Dashboard** - Real-time monitoring
- **Data Export** - CSV export scripts
- **Documentation** - Setup and operations guides

---

## Version Numbering

- **Major (X.0.0)**: Breaking changes, major feature additions
- **Minor (0.X.0)**: New features, backwards compatible
- **Patch (0.0.X)**: Bug fixes, small improvements

---

## Upcoming Features (Roadmap)

See [ROADMAP.md](docs/ROADMAP.md) for planned features:

- Multi-event session management
- Advanced analytics dashboard
- SMS/email alerts (optional)
- RFID wristband support
- Database replication for redundancy

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## Support

- **Issues:** GitHub Issues
- **Questions:** See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Documentation:** [docs/](docs/)

---

**Latest Version:** 2.2.1  
**Release Date:** 2025-01-19  
**Status:** Production Ready ✅

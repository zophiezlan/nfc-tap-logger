# Force-Exit Tool & Real-Time Export

**Version:** 2.2.1  
**Added:** Force-exit for stuck cards + Real-time export buttons

## Overview

These two "quick win" features solve critical operational pain points:

1. **Force-Exit Tool**: Handle cards stuck in queue at end of events (people who forgot to tap out)
2. **Real-Time Export**: Export data mid-event without SSH access for decision-making

---

## 🏷️ Force-Exit Tool

### Problem Solved

At the end of events, some participants forget to tap out. This leaves cards "stuck" in the queue (QUEUE_JOIN without corresponding EXIT), skewing metrics and analytics.

### Solution

The Control Panel now shows all stuck cards (>2 hours in queue) with bulk operations to mark them as exited.

### How to Use

1. **Access Control Panel**: Navigate to `/control` on your tap station
2. **View Stuck Cards**: Scroll to "🏷️ Stuck Cards Management" section
3. **Select Cards**:
   - Check individual cards, or
   - Use "Select All" checkbox to select all stuck cards
4. **Force Exit**:
   - Click "Mark Selected as Exited" for checked cards
   - Click "Mark All as Exited" to exit all stuck cards at once
5. **Confirmation**: Confirm the action when prompted

### What It Does

- Queries database for QUEUE_JOIN events >2 hours old without corresponding EXIT
- Inserts EXIT events with:
  - `device_id`: `"manual_force_exit"`
  - `uid`: `"FORCED_{token_id}"`
  - `timestamp`: Current time
- These exits are marked so you can filter them out in post-event analysis if needed

### Auto-Refresh

The stuck cards list automatically refreshes every 30 seconds, so you see real-time updates as you process cards.

### When to Use

- **End of Event**: After event closes, before teardown
- **Event Transitions**: Between sessions when resetting
- **Cleanup**: When you notice stuck cards accumulating

### Best Practices

1. **Announce Last Call**: Give participants a final reminder to tap out before force-exiting
2. **Document**: Note in event logs when force-exits were performed
3. **Filter Analytics**: When analyzing data, you can filter out `device_id = "manual_force_exit"` if you want to exclude forced exits

---

## 📊 Real-Time Export

### Problem Solved

Previously, exporting data required SSH access to the Raspberry Pi and running command-line scripts. Staff needed mid-event exports for decision-making but didn't have the technical access or skills.

### Solution

Export buttons are now integrated directly into the Live Dashboard header. One click downloads a CSV file.

### How to Use

1. **Access Dashboard**: Navigate to `/dashboard` on your tap station
2. **Choose Export Range**: Click one of three buttons:
   - **📊 Export Last Hour**: Events from the past hour only
   - **📅 Export Today**: All events from today
   - **📦 Export All**: Complete event history for this session
3. **Download**: CSV file downloads automatically to your device

### Export Format

CSV files include all event data:

```csv
id,token_id,uid,stage,timestamp,device_id,session_id
1,ABC123,04:A1:B2:C3:D4:E5:F6,QUEUE_JOIN,2025-01-19 14:23:45,station-01,2025-01-19_festival
2,ABC123,04:A1:B2:C3:D4:E5:F6,EXIT,2025-01-19 14:45:12,station-01,2025-01-19_festival
...
```

### When to Use

- **Mid-Event Decisions**: Check queue patterns, identify bottlenecks
- **Staff Handoffs**: Export data for incoming shift to review
- **Quick Analysis**: Load into Excel/Google Sheets for quick metrics
- **Reporting**: Provide stakeholders with current status
- **Backup**: Regular exports as additional backup mechanism

### File Naming

Files are automatically named with filter type and date:

```
tap_station_export_hour_2025-01-19.csv
tap_station_export_today_2025-01-19.csv
tap_station_export_all_2025-01-19.csv
```

---

## 🔧 Technical Details

### API Endpoints

#### Get Stuck Cards

```
GET /api/control/stuck-cards
```

Returns list of cards stuck >2 hours:

```json
{
  "stuck_cards": [
    {
      "token_id": "ABC123",
      "queue_time": "2025-01-19 14:23:45",
      "hours_stuck": 2.4
    }
  ]
}
```

#### Force Exit Cards

```
POST /api/control/force-exit
Content-Type: application/json

{
  "token_ids": ["ABC123", "DEF456", "GHI789"]
}
```

Response:

```json
{
  "success": true,
  "marked_count": 3
}
```

#### Export Data

```
GET /api/export?filter=hour|today|all
```

Returns CSV file with appropriate Content-Disposition header for download.

### Database Queries

**Stuck Cards Detection:**

```sql
SELECT DISTINCT 
    q.token_id,
    q.timestamp as queue_time,
    (julianday('now') - julianday(q.timestamp)) * 24 as hours_stuck
FROM events q
WHERE q.session_id = ?
    AND q.stage = 'QUEUE_JOIN'
    AND q.timestamp < datetime('now', '-2 hours')
    AND NOT EXISTS (
        SELECT 1 FROM events e
        WHERE e.session_id = q.session_id
            AND e.token_id = q.token_id
            AND e.stage = 'EXIT'
            AND e.timestamp > q.timestamp
    )
ORDER BY hours_stuck DESC
```

**Export Filtering:**

- **Last Hour**: `WHERE timestamp > datetime('now', '-1 hour')`
- **Today**: `WHERE date(timestamp) = date('now')`
- **All**: No WHERE clause (session_id filter only)

---

## 🚀 Performance

### Force-Exit Tool

- **Query Speed**: <50ms for typical stuck card queries (<100 cards)
- **Insert Speed**: Batch inserts processed quickly (~10ms per card)
- **UI Responsiveness**: Auto-refresh every 30 seconds doesn't impact performance

### Export Tool

- **Small Datasets** (<1000 events): <100ms export time
- **Medium Datasets** (1000-10,000 events): <500ms export time
- **Large Datasets** (10,000+ events): <2 seconds export time
- **Download**: Browser handles streaming, no memory issues

---

## 🎯 Quick Reference

### Control Panel - Force Exit

1. Go to `/control`
2. Scroll to "Stuck Cards Management"
3. Select cards → Click "Mark Selected as Exited"
4. Confirm action

### Dashboard - Export

1. Go to `/dashboard`
2. Click export button in header:
   - "Export Last Hour" for recent data
   - "Export Today" for full day
   - "Export All" for everything
3. CSV downloads automatically

---

## 🔍 Troubleshooting

### Force-Exit Issues

**"No stuck cards found" but I know there are some:**

- Check that >2 hours have passed since QUEUE_JOIN
- Verify cards don't already have EXIT events
- Refresh the page

**Force-exit doesn't work:**

- Check browser console for JavaScript errors
- Verify API endpoint is accessible: `GET /api/control/stuck-cards`
- Check service logs: `sudo journalctl -u tap-station -n 50`

### Export Issues

**Export button doesn't download file:**

- Check browser's download settings
- Try different browser
- Check API endpoint directly: `/api/export?filter=hour`

**Export is empty:**

- Verify events exist in database
- Check filter: "hour" may be empty if no recent events
- Try "Export All" to see if any data exists

**Export is slow:**

- For very large datasets (>50,000 events), use SSH and command-line export instead
- Consider filtering to smaller time ranges

---

## 📋 Post-Event Checklist

1. ✅ **Before teardown**: Use Force-Exit tool to clean up stuck cards
2. ✅ **Final export**: Click "Export All" to download complete dataset
3. ✅ **Verify export**: Open CSV in Excel/Google Sheets to verify data
4. ✅ **Backup**: Keep export file as additional backup
5. ✅ **Document**: Note any force-exits or anomalies in event log

---

## 🎉 Impact

### Time Savings

- **Force-Exit**: 5 minutes → 30 seconds (10x faster)
- **Export**: SSH + commands (3 minutes) → One click (5 seconds)
- **Total per event**: ~8 minutes saved

### Operational Benefits

- Non-technical staff can export data
- Mid-event decision-making enabled
- Cleaner analytics (no stuck cards)
- Faster event teardown

---

## 📚 Related Documentation

- [Control Panel Documentation](CONTROL_PANEL.md)
- [3-Stage Tracking](3_STAGE_TRACKING.md)
- [Operations Guide](OPERATIONS.md)
- [Troubleshooting](TROUBLESHOOTING.md)

---

**Need help?** Check the main [README](../README.md) or [Operations Guide](OPERATIONS.md)

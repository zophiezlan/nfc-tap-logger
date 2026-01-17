# Quick Start: Force-Exit & Export

**2-Minute Guide to New v2.2.1 Features**

---

## 🏷️ Force-Exit Stuck Cards

**When:** End of event, when people forgot to tap out

**Where:** Control Panel (`/control`)

**Steps:**

1. Go to `http://<your-pi-ip>:5000/control`
2. Scroll to "🏷️ Stuck Cards Management"
3. Review list of stuck cards (>2 hours in queue)
4. Options:
   - **Select specific cards** → Check boxes → Click "Mark Selected as Exited"
   - **Exit all at once** → Click "Mark All as Exited"
5. Confirm when prompted
6. Done! Cards now marked as exited

**Why it matters:** Cleans up your data, prevents skewed metrics

---

## 📊 Export Data

**When:** Mid-event for decisions, or end-of-event for analysis

**Where:** Live Dashboard (`/dashboard`)

**Steps:**

1. Go to `http://<your-pi-ip>:5000/dashboard`
2. Look at top-right header
3. Click one button:
   - **📊 Export Last Hour** - Recent activity only
   - **📅 Export Today** - Full day's data
   - **📦 Export All** - Complete history
4. CSV downloads automatically
5. Open in Excel/Google Sheets

**Why it matters:** No SSH needed, non-technical staff can export

---

## 💡 Pro Tips

### Force-Exit Tool

- **Announce last call** before using force-exit
- **Check the list** - if >10 stuck cards, something may be wrong with exit station
- **Document it** - note in event log that force-exits were used
- **Filter later** - In analytics, filter out `device_id = "manual_force_exit"` if needed

### Export Tool

- **Export hourly** during event to monitor patterns
- **Use "Last Hour"** for quick checks
- **Use "Today"** for shift handoffs
- **Use "Export All"** for final backup at end
- **Keep the files** as additional backup

---

## 🎯 Common Scenarios

### End-of-Event Cleanup

1. Go to `/control`
2. Use force-exit to clean stuck cards
3. Go to `/dashboard`
4. Click "Export All"
5. Done!

### Mid-Event Check

1. Go to `/dashboard`
2. Click "Export Last Hour"
3. Open CSV in Google Sheets
4. Check for patterns/issues
5. Adjust operations if needed

### Shift Handoff

1. Go to `/shift` (shift summary)
2. Review quick stats
3. Go to `/dashboard`
4. Click "Export Today"
5. Hand off CSV to next shift

---

## 📱 Mobile Access

Both features work great on phones/tablets:

- Control panel responsive design
- Export buttons accessible
- Downloads work on mobile browsers

---

## ⚠️ Important Notes

- **Force-exit is permanent** - Can't undo, so confirm before clicking "Mark All"
- **Exports include all data** - Be mindful of privacy/security when sharing CSVs
- **Auto-refresh** - Stuck cards list updates every 30 seconds

---

## 🚑 Quick Troubleshooting

**"No stuck cards found" but there should be:**

- Check >2 hours have passed
- Verify cards don't have EXIT events already

**Export button doesn't download:**

- Check browser download settings
- Try different browser

**Force-exit doesn't work:**

- Check service is running: `sudo systemctl status tap-station`
- Check logs: `sudo journalctl -u tap-station -n 20`

---

## 📚 More Info

- [Full Documentation](FORCE_EXIT_AND_EXPORT.md)
- [Control Panel Guide](CONTROL_PANEL.md)
- [Operations Guide](OPERATIONS.md)

---

**That's it!** Two simple tools to make event operations smoother. 🎉

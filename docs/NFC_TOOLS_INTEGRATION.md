# NFC Tools App Integration

## Overview

Integrate with the [NFC Tools](https://www.wakdev.com/en/apps/nfc-tools.html) app (free, iOS/Android) to give participants visibility into their status using their own phones.

## Why This is Useful

1. **Participant visibility** - "Did my tap work?"
2. **Backup reader** - Peer can use their phone if Pi fails
3. **Self-service** - Participants check their own status
4. **No custom app needed** - Uses existing, trusted app

## Implementation Options

### Option 1: Static NDEF URL (Simplest)

Write a URL to each card that encodes the token ID.

**On card initialization:**

```python
def write_static_url(self, token_id: str) -> bool:
    """Write static URL to card"""
    from ndef import TextRecord, UriRecord, Message

    # URL format: https://yoursite.com/check?token=001
    url = f"https://your-festival-site.com/check?token={token_id}"

    record = UriRecord(url)
    message = Message(record)

    # Write to card
    # ... NDEF writing code ...

    return True
```

**When participant taps phone:**

- Phone reads URL
- Opens browser to `https://your-festival-site.com/check?token=001`
- Simple web page shows: "Token 001 - Checked in at 2:15pm ✓"

**Pros:**

- Simple
- Works with any NFC-enabled phone
- No app required (uses browser)

**Cons:**

- Requires web server
- Requires internet on participant's phone

---

### Option 2: NDEF Text Record (Offline)

Write status directly to card each time it's tapped.

**On each tap:**

```python
def update_card_status(self, token_id: str, stage: str) -> bool:
    """Update card with latest status"""
    from ndef import TextRecord, Message
    from datetime import datetime

    # Text to write
    status = f"Token {token_id} - {stage} at {datetime.now().strftime('%I:%M%p')}"

    record = TextRecord(status)
    message = Message(record)

    # Write to card
    # ... NDEF writing code ...

    return True
```

**When participant taps phone:**

- Phone reads text
- NFC Tools app displays: "Token 001 - EXIT at 3:45pm"
- No internet needed

**Pros:**

- Works offline
- Instant feedback
- Simple

**Cons:**

- Slower (write on each tap, not just read)
- Wears out card faster (NTAG215 good for 100,000 writes though)

---

### Option 3: Hybrid (Best of Both)

**During initialization:**

- Write static URL with token ID

**During taps:**

- Only read UID (fast)
- Optional: Update NDEF if time permits

**When participant checks with phone:**

- Reads URL
- Web page queries database: "Where is token 001?"
- Shows journey: "Queue 2:15pm → Exit 3:45pm (wait: 90 min)"

---

## Implementation Example

### Enhanced Card Initialization

```python
#!/usr/bin/env python3
"""
Enhanced card initialization with NDEF support
"""

import ndef

class NFCCardInitializer:
    def __init__(self, base_url: str = "https://your-site.com"):
        self.base_url = base_url

    def write_card(self, token_id: str, uid: str):
        """Write token ID and URL to card"""

        # Create NDEF message
        records = [
            # Text record (backup)
            ndef.TextRecord(f"Token {token_id}"),

            # URL record (primary)
            ndef.UriRecord(f"{self.base_url}/check?token={token_id}")
        ]

        message = ndef.Message(records)

        # Write to card
        # Note: Requires enhanced pn532pi with NDEF support
        # Or use a different library like nfcpy

        print(f"✓ Wrote Token {token_id} with URL")
```

### Simple Status Web Page

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Check Your Status</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      body {
        font-family: Arial;
        max-width: 400px;
        margin: 50px auto;
        padding: 20px;
        text-align: center;
      }
      .status {
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
      }
      .checked-in {
        background: #d4edda;
        color: #155724;
      }
      .waiting {
        background: #fff3cd;
        color: #856404;
      }
      .complete {
        background: #cce5ff;
        color: #004085;
      }
    </style>
  </head>
  <body>
    <h1>🎪 Festival Check-In</h1>

    <div id="status" class="status">Loading...</div>

    <script>
      // Get token from URL
      const params = new URLSearchParams(window.location.search);
      const token = params.get("token");

      // Fetch status (would query your database)
      fetch(`/api/status/${token}`)
        .then((r) => r.json())
        .then((data) => {
          const statusDiv = document.getElementById("status");

          if (data.exit) {
            statusDiv.className = "status complete";
            statusDiv.innerHTML = `
                        <h2>✅ Complete!</h2>
                        <p>Token ${token}</p>
                        <p>Joined: ${data.queue_join}</p>
                        <p>Completed: ${data.exit}</p>
                        <p><strong>Wait time: ${data.wait_time} minutes</strong></p>
                    `;
          } else if (data.queue_join) {
            statusDiv.className = "status waiting";
            statusDiv.innerHTML = `
                        <h2>⏱️ In Queue</h2>
                        <p>Token ${token}</p>
                        <p>Joined: ${data.queue_join}</p>
                        <p>Estimated wait: ~${data.estimated_wait} minutes</p>
                    `;
          } else {
            statusDiv.className = "status checked-in";
            statusDiv.innerHTML = `
                        <h2>👋 Welcome!</h2>
                        <p>Token ${token}</p>
                        <p>Tap your card at the queue station</p>
                    `;
          }
        })
        .catch((err) => {
          document.getElementById(
            "status"
          ).innerHTML = `<p>Error loading status. Please ask a volunteer.</p>`;
        });
    </script>
  </body>
</html>
```

### Simple API Backend (Flask)

```python
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/status/<token_id>')
def get_status(token_id):
    """Get status for a token"""

    # Query database
    conn = sqlite3.connect('data/events.db')
    conn.row_factory = sqlite3.Row

    cursor = conn.execute("""
        SELECT stage, timestamp
        FROM events
        WHERE token_id = ?
        ORDER BY timestamp
    """, (token_id,))

    events = cursor.fetchall()
    conn.close()

    # Parse events
    result = {
        'token_id': token_id,
        'queue_join': None,
        'exit': None,
        'wait_time': None,
        'estimated_wait': 20  # Simple estimate
    }

    for event in events:
        if event['stage'] == 'QUEUE_JOIN':
            result['queue_join'] = event['timestamp']
        elif event['stage'] == 'EXIT':
            result['exit'] = event['timestamp']

    # Calculate wait time if complete
    if result['queue_join'] and result['exit']:
        from datetime import datetime
        queue_time = datetime.fromisoformat(result['queue_join'])
        exit_time = datetime.fromisoformat(result['exit'])
        result['wait_time'] = int((exit_time - queue_time).total_seconds() / 60)

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Deployment Options

### Option A: Local Only (No Internet)

- Write NDEF text records to cards
- Participant taps phone → sees text
- No server needed
- Works offline

### Option B: Pi as Web Server

- Run Flask app on one Pi
- Creates local WiFi hotspot
- Participants connect to WiFi
- Tap card → opens local web page
- No internet needed

### Option C: Cloud Server

- Deploy Flask app to Heroku/Vercel/etc
- Sync data from Pi to cloud (after event or via WiFi)
- Participant taps → opens cloud URL
- Works anywhere with internet

---

## Recommended Approach

**For v1.0:** Skip it. Keep it simple.

**For v1.1 (if participants ask):**

1. Write static NDEF URL during card init
2. URL points to simple status page
3. Status page shows "Token 001 - tap at stations"
4. After event, you can update it with results

**For v2.0 (if you want real-time):**

1. Pi runs Flask app
2. Creates WiFi hotspot
3. Participant taps → sees live status
4. No cloud dependency

---

## NDEF Writing Code Example

```python
"""
Add NDEF writing to nfc_reader.py
"""

def write_ndef_url(self, url: str) -> bool:
    """
    Write NDEF URL record to card

    Args:
        url: URL to write (e.g., "https://example.com/check?token=001")

    Returns:
        True if successful
    """
    try:
        # This is pseudocode - actual implementation depends on library
        # pn532pi doesn't support NDEF writing out of the box
        # You'd need to use nfcpy or implement NDEF formatting manually

        # NDEF URL record format (simplified):
        # TNF: 0x01 (Well-known)
        # Type: "U" (URI)
        # Payload: URL with prefix byte

        # For full implementation, see:
        # https://github.com/nfcpy/nfcpy
        # or
        # https://github.com/Don/phonegap-nfc

        logger.info(f"NDEF URL written: {url}")
        return True

    except Exception as e:
        logger.error(f"Failed to write NDEF: {e}")
        return False
```

---

## Testing with NFC Tools App

1. **Install NFC Tools** on your phone (free)
2. **Write a test card:**

   ```python
   python scripts/write_ndef_test.py --token 001
   ```

3. **Tap card with phone**
4. **App should show:**
   - URL: <https://your-site.com/check?token=001>
   - Text: "Token 001"
5. **Tap URL** → opens browser

---

## Pros & Cons

### Pros

✅ Participants get instant feedback
✅ Uses existing app (no custom app needed)
✅ Backup if Pi fails (peer uses phone)
✅ Self-service status checking
✅ Professional feel

### Cons

❌ Adds complexity to card init
❌ Requires web server for best experience
❌ Slower if writing on each tap
❌ NDEF libraries can be finicky

---

## Recommendation

**Start without NFC Tools integration.** Get the basics working first.

**Add it later if:**

- Participants frequently ask "did it work?"
- You want to offer self-service status checking
- You have time to build the web interface
- You're comfortable debugging NDEF issues

**The current system is already great.** This is a nice-to-have, not a must-have.

---

## Next Steps If You Decide to Build It

1. Research NDEF libraries (nfcpy vs pn532pi)
2. Test NDEF writing on a few cards
3. Build simple status web page
4. Deploy Flask app (Pi or cloud)
5. Update card init script
6. Test with participants
7. Iterate based on feedback

---

**Keep it simple first. Add features based on real feedback.** 🚀

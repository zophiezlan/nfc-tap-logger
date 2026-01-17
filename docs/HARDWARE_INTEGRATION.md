# Hardware Integration Guide

## Overview

The NFC Tap Logger system integrates several hardware components to provide real-time operational feedback and monitoring capabilities. This guide explains how each component is utilized and monitored.

## Hardware Components

### 1. **Green LED (GPIO 27)** ✅

- **Purpose**: Visual success indicator
- **Triggers**:
  - Successful NFC tap logged
  - Card processed and recorded in database
- **Pattern**: Quick flash (0.1s on, 0.1s off)
- **Configuration**: `config.yaml` → `feedback.gpio.led_green`

### 2. **Red LED (GPIO 22)** ⚠️

- **Purpose**: Visual error/duplicate indicator
- **Triggers**:
  - Duplicate card tap (within debounce window)
  - System errors or warnings
  - Critical hardware failures
- **Pattern**: Slower flash (0.2s on, 0.2s off)
- **Configuration**: `config.yaml` → `feedback.gpio.led_red`

### 3. **Buzzer (GPIO 17)** 🔊

- **Purpose**: Audio feedback for card taps
- **Patterns**:
  - **Success**: 1 short beep (0.1s)
  - **Duplicate**: 2 quick beeps (0.05s on, 0.05s off, 0.05s on)
  - **Error**: 3 rapid beeps (0.05s on, 0.03s off pattern)
  - **Startup**: Ascending tone pattern
- **Configuration**: `config.yaml` → `feedback.gpio.buzzer`

### 4. **RTC (Real-Time Clock)** ⏰

- **Purpose**: Maintain accurate time across power cycles
- **Benefits**:
  - Accurate timestamps even without network
  - Event logs maintain chronological integrity
  - System clock synchronization
- **Detection**: Automatically detected at `/dev/rtc0` or `/dev/rtc1`
- **Status**: Monitored in hardware status dashboard

### 5. **PN532 NFC Reader (I2C)** 📡

- **Interface**: I2C bus (default address: 0x24)
- **Purpose**: Read NTAG213/215 NFC tags
- **Features**:
  - Automatic retry on failed reads
  - Debounce protection
  - UID and NDEF text record reading
- **Configuration**: `config.yaml` → `nfc` section

## Hardware Verification

### Automated Testing

Use the enhanced hardware verification script:

```powershell
python scripts/verify_hardware.py
```

This script tests:

- ✅ I2C bus availability
- ✅ PN532 NFC reader communication
- ✅ Green LED (GPIO 27) - individual test
- ✅ Red LED (GPIO 22) - individual test
- ✅ Buzzer (GPIO 17) - user confirmation prompt
- ✅ RTC hardware clock (if present)
- ✅ Database connectivity
- ✅ Power supply status (under-voltage detection)

### Manual Testing

**Test Green LED:**

```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.output(27, GPIO.HIGH)  # LED on
time.sleep(1)
GPIO.output(27, GPIO.LOW)   # LED off
GPIO.cleanup()
```

**Test Red LED:**

```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.OUT)
GPIO.output(22, GPIO.HIGH)  # LED on
time.sleep(1)
GPIO.output(22, GPIO.LOW)   # LED off
GPIO.cleanup()
```

**Test Buzzer:**

```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
pwm = GPIO.PWM(17, 2000)  # 2kHz tone
pwm.start(50)  # 50% duty cycle
time.sleep(0.5)
pwm.stop()
GPIO.cleanup()
```

## Real-Time Monitoring

### Control Panel Dashboard

Access the hardware status dashboard at: `http://<device-ip>:5000/control`

**Features:**

- ✅ Real-time component status
- 🌡️ CPU temperature monitoring
- ⚡ Power supply status (under-voltage alerts)
- 💾 Disk space monitoring
- 🔌 I2C bus status
- 💡 GPIO/LED configuration display
- ⏰ RTC clock status and time
- 🔄 Auto-refresh every 30 seconds

**Status Indicators:**

- **OK** (Green): Component functioning normally
- **WARNING** (Yellow): Non-critical issue detected
- **ERROR** (Red): Critical failure requiring attention
- **INFO** (Blue): Informational status
- **UNKNOWN** (Gray): Cannot determine status

### Hardware Status API

Query hardware status programmatically:

```bash
curl http://localhost:5000/api/control/hardware-status
```

**Response Example:**

```json
{
  "timestamp": "2026-01-15T12:34:56.789Z",
  "components": {
    "i2c": {
      "status": "ok",
      "message": "I2C bus available",
      "critical": true
    },
    "gpio": {
      "status": "ok",
      "message": "GPIO available",
      "details": {
        "buzzer": "GPIO 17",
        "green_led": "GPIO 27",
        "red_led": "GPIO 22"
      },
      "critical": false
    },
    "temperature": {
      "status": "ok",
      "message": "58.3°C",
      "value": 58.3,
      "critical": false
    },
    "power": {
      "status": "ok",
      "message": "Power OK",
      "throttled_hex": "0x0",
      "critical": false
    },
    "disk": {
      "status": "ok",
      "message": "12.3 GB free of 14.5 GB",
      "percent_used": 15.2,
      "free_gb": 12.3,
      "critical": false
    },
    "rtc": {
      "status": "ok",
      "message": "RTC available",
      "time": "2026-01-15 12:34:56",
      "critical": false
    }
  }
}
```

## Operational Integration

### Event Flow with Hardware Feedback

1. **Card Tap Detected**
   - NFC reader detects card via I2C
   - System reads UID and token ID

2. **Database Logging**
   - Event logged to SQLite database
   - Timestamp recorded (RTC time if available)

3. **Hardware Feedback**
   - **Success**: Green LED flashes + 1 beep
   - **Duplicate**: Red LED flashes + 2 beeps

4. **Monitoring Update**
   - Real-time stats updated
   - Hardware status refreshed (30s interval)

### Error Handling

**I2C Communication Failure:**

- Red LED activates
- Error logged to `/logs/`
- Hardware status shows critical error
- System attempts retry (configurable)

**Under-Voltage Detection:**

- Critical warning in control panel
- Power status shows ERROR state
- Logged for diagnostics
- May cause system instability

**Temperature Threshold:**

- **70-80°C**: Warning status (yellow)
- **80°C+**: Error status (red)
- Automatic CPU throttling by Raspberry Pi OS
- Consider improved cooling

## Hardware Configuration

### GPIO Pin Assignments (BCM Mode)

```yaml
feedback:
  gpio:
    buzzer: 17      # PWM-capable pin for audio
    led_green: 27   # Success indicator
    led_red: 22     # Error/duplicate indicator
```

### I2C Configuration

```yaml
nfc:
  i2c_bus: 1        # I2C bus number (usually 1 on Pi Zero 2)
  address: 0x24     # PN532 default address
```

### Enable/Disable Hardware

```yaml
feedback:
  buzzer_enabled: true   # Set to false to disable buzzer
  led_enabled: true      # Set to false to disable LEDs
```

## Wiring Schematic

See [wiring_schematic.md](../wiring_schematic.md) for complete GPIO wiring diagram.

**Quick Reference:**

- Green LED: GPIO 27 → 330Ω resistor → LED → GND
- Red LED: GPIO 22 → 330Ω resistor → LED → GND
- Buzzer: GPIO 17 → Buzzer (+) | GND → Buzzer (-)
- PN532: SCL → GPIO 3 (I2C1 SCL) | SDA → GPIO 2 (I2C1 SDA)

## Troubleshooting

### LEDs Not Working

1. Check GPIO connections
2. Verify resistor values (330Ω recommended)
3. Test LED polarity (longer leg = anode/+)
4. Run `verify_hardware.py` for diagnostics
5. Check `led_enabled: true` in config

### Buzzer Not Working

1. Verify GPIO 17 connection
2. Check buzzer polarity
3. Test with manual GPIO script
4. Ensure `buzzer_enabled: true` in config
5. Check for PWM conflicts

### RTC Not Detected

1. Verify RTC module I2C connection
2. Check I2C address: `i2cdetect -y 1`
3. Install RTC kernel module (if needed)
4. RTC is **optional** - system works without it

### I2C Communication Issues

1. Enable I2C: `sudo raspi-config` → Interface Options
2. Check connections: `i2cdetect -y 1`
3. Expected address: 0x24 (PN532)
4. Verify power supply (5V 2.5A minimum)

## Best Practices

1. **Always test hardware before deployment**
   - Run `verify_hardware.py` after setup
   - Test all LEDs and buzzer individually
   - Verify NFC reads with test cards

2. **Monitor power supply quality**
   - Use official Raspberry Pi power supply
   - Check for under-voltage warnings
   - Consider UPS/battery backup for events

3. **Temperature management**
   - Ensure adequate ventilation
   - Monitor CPU temperature in control panel
   - Keep system below 70°C under load

4. **Regular status checks**
   - Check hardware dashboard periodically
   - Monitor for critical warnings
   - Review logs for hardware errors

5. **Backup hardware status logs**
   - Export hardware status data
   - Track trends over time
   - Identify failing components early

## Future Enhancements

- **LCD Display**: Real-time queue status display
- **Battery Status**: UPS/battery level monitoring
- **Network Status**: WiFi signal strength indicator
- **Camera Integration**: Event photo capture
- **Multi-Color LED**: RGB status indication
- **Haptic Feedback**: Vibration motor for tactile feedback

## References

- [FeedbackController Source](../tap_station/feedback.py)
- [Hardware Verification Script](../scripts/verify_hardware.py)
- [Main System Integration](../tap_station/main.py)
- [Control Panel UI](../tap_station/templates/control.html)
- [Wiring Schematic](../wiring_schematic.md)

---

**Last Updated**: January 2026  
**Hardware Version**: v2.0 (Raspberry Pi Zero 2 W + PN532)

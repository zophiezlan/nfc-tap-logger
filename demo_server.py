#!/usr/bin/env python3
"""
Demo Server for NSW Health Presentation
Runs the tap station in demo mode with simulated live data
"""

import os
import sys
import yaml
import threading
import time
from pathlib import Path

# Add tap_station to path
sys.path.insert(0, str(Path(__file__).parent))

from tap_station.web_server import StatusWebServer
from tap_station.database import Database
from demo_data_generator import DemoDataGenerator


class DemoConfig:
    """Simple config object for demo mode"""
    def __init__(self, config_dict):
        self.device_id = config_dict['station']['device_id']
        self.stage = config_dict['station']['stage']
        self.session_id = config_dict['station']['session_id']
        self.database_path = config_dict['database']['path']
        self.wal_mode = config_dict['database'].get('wal_mode', True)
        self._raw = config_dict


def load_demo_config():
    """Load demo-specific configuration"""
    config = {
        'station': {
            'device_id': 'demo-web-station',
            'stage': 'QUEUE_JOIN',
            'session_id': 'demo-festival-2026'
        },
        'database': {
            'path': 'data/demo_events.db',
            'wal_mode': True
        },
        'nfc': {
            'auto_init_cards': True,
            'auto_init_start_id': 1,
            'debounce_seconds': 1
        },
        'feedback': {
            'buzzer_enabled': False,
            'led_enabled': False
        },
        'web_server': {
            'enabled': True,
            'host': '0.0.0.0',
            'port': int(os.environ.get('PORT', 8080))
        },
        'logging': {
            'level': 'INFO',
            'path': 'logs/demo.log'
        }
    }
    return config


def load_demo_service_config():
    """Load demo service configuration for drug checking"""
    return {
        'service': {
            'name': 'NSW Festival Drug Checking Service',
            'organization': 'NSW Health - Harm Reduction',
            'description': 'Free, confidential substance testing service',
            'type': 'festival'
        },
        'workflow': {
            'stages': [
                {
                    'id': 'QUEUE_JOIN',
                    'label': 'Join Queue',
                    'description': 'Participant enters the queue',
                    'order': 1,
                    'required': True,
                    'visible_to_public': True,
                    'duration_estimate': 2,
                    'icon': '👋'
                },
                {
                    'id': 'SERVICE_START',
                    'label': 'Testing Started',
                    'description': 'Peer intake (5min) + Chemist testing (8min)',
                    'order': 2,
                    'required': True,
                    'visible_to_public': False,
                    'duration_estimate': 13,  # 5 min peer chat + 8 min testing
                    'icon': '🔬'
                },
                {
                    'id': 'SUBSTANCE_RETURNED',
                    'label': 'Results Discussion',
                    'description': 'Results chat with peer (avg 10min, range 5-30min)',
                    'order': 3,
                    'required': False,
                    'visible_to_public': False,
                    'duration_estimate': 10,  # Average, but high variance
                    'icon': '✅'
                },
                {
                    'id': 'EXIT',
                    'label': 'Service Complete',
                    'description': 'Participant exits the service',
                    'order': 4,
                    'required': True,
                    'visible_to_public': True,
                    'duration_estimate': 0,
                    'icon': '🚪'
                }
            ]
        },
        'capacity': {
            # Real HTID data: ~70 groups over 6 hours with 6 peers + 6 chemists
            'expected_throughput_per_hour': 12,  # 70 groups / 6 hours
            'average_service_time_minutes': 23,  # 5 min intake + 8 min test + 10 min results
            'max_queue_length': 50,
            'staff_count': 6  # 6 peer workers handling intake/results
        },
        'alerts': {
            'queue_length_warning': 10,  # NSW realistic: getting busy
            'queue_length_critical': 15,  # NSW realistic: peak queue at HTID was ~15 groups
            'wait_time_warning_minutes': 30,
            'wait_time_critical_minutes': 60,
            'inactivity_warning_minutes': 10,  # Quiet periods are normal (first/last hour)
            'stuck_card_threshold_minutes': 45  # Results chat can go 30+ mins legitimately
        },
        'display': {
            'show_token_ids': True,
            'show_timestamps': True,
            'recent_events_limit': 20,
            'timezone': 'Australia/Sydney'
        }
    }


def setup_demo_data(db: Database, config: dict):
    """Initialize database with some baseline demo data"""
    print("🎭 Setting up demo festivals...")

    # Create demo data directory if needed
    Path('data').mkdir(exist_ok=True)

    # The database will auto-create tables
    print("✅ Database initialized")


def run_background_simulator(db: Database, config: dict, service_config: dict):
    """Run continuous background simulation of festival activity"""
    print("🎪 Starting live demo data simulator...")

    generator = DemoDataGenerator(db, config, service_config)

    # Start with some initial participants
    generator.seed_initial_data(num_participants=10)

    # Run continuous simulation
    while True:
        try:
            generator.simulate_activity_cycle()
            time.sleep(5)  # Run simulation every 5 seconds
        except Exception as e:
            print(f"⚠️  Simulator error: {e}")
            time.sleep(10)


def main():
    """Main entry point for demo server"""
    print("=" * 60)
    print("🎪 NFC TAP LOGGER - NSW HEALTH DEMO")
    print("=" * 60)

    # Load configurations
    config_dict = load_demo_config()
    service_config = load_demo_service_config()

    # Create config object
    config = DemoConfig(config_dict)

    # Initialize database
    db = Database(config.database_path, wal_mode=config.wal_mode)
    setup_demo_data(db, config_dict)

    # Start background simulator in separate thread
    simulator_thread = threading.Thread(
        target=run_background_simulator,
        args=(db, config_dict, service_config),
        daemon=True
    )
    simulator_thread.start()
    print("✅ Background simulator started")

    # Write service config to file so it can be loaded
    import yaml
    service_config_path = Path('service_config.yaml')
    with open(service_config_path, 'w') as f:
        yaml.dump(service_config, f, default_flow_style=False)

    # Create web server using standard initialization
    web_server = StatusWebServer(config, db)

    # Override index route to use demo template
    from flask import render_template

    @web_server.app.route("/")
    def demo_index():
        """Demo landing page for NSW Health"""
        return render_template("demo_index.html")

    app = web_server.app

    port = config_dict['web_server']['port']
    host = config_dict['web_server']['host']

    print("\n" + "=" * 60)
    print(f"🌐 Demo server running at http://{host}:{port}")
    print("=" * 60)
    print("\n📱 AVAILABLE PAGES:")
    print(f"  • Home/Landing:     http://localhost:{port}/")
    print(f"  • Public Display:   http://localhost:{port}/public")
    print(f"  • Staff Dashboard:  http://localhost:{port}/dashboard")
    print(f"  • Control Panel:    http://localhost:{port}/control")
    print(f"  • Queue Monitor:    http://localhost:{port}/monitor")
    print("\n🎭 Live data simulation is running in the background")
    print("=" * 60 + "\n")

    # Run Flask app
    app.run(
        host=host,
        port=port,
        debug=False,
        threaded=True
    )


if __name__ == '__main__':
    main()

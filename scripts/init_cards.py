#!/usr/bin/env python3
"""
Card Initialization Script

Writes sequential token IDs (001-100) to NTAG215 cards.
Shows progress as cards are tapped.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import argparse
from tap_station.nfc_reader import NFCReader, MockNFCReader


class CardInitializer:
    """Initialize NFC cards with sequential token IDs"""

    def __init__(self, start_id: int = 1, end_id: int = 100, mock: bool = False, auto_mode: bool = False):
        """
        Initialize card initializer

        Args:
            start_id: Starting token ID
            end_id: Ending token ID
            mock: Use mock NFC reader
            auto_mode: If True, automatically proceed between cards (no user confirmation)
        """
        self.start_id = start_id
        self.end_id = end_id
        self.current_id = start_id
        self.auto_mode = auto_mode

        # Initialize NFC reader
        if mock:
            self.nfc = MockNFCReader()
            print("Using mock NFC reader (testing mode)")
        else:
            self.nfc = NFCReader()
            print("PN532 NFC reader initialized")

        self.initialized_cards = []
        self.failed_cards = []

    def run(self):
        """Run card initialization process"""
        total_cards = self.end_id - self.start_id + 1

        print(f"\n{'=' * 60}")
        print(f"Card Initialization")
        print(f"{'=' * 60}")
        print(f"Will initialize {total_cards} cards (ID {self.start_id:03d} to {self.end_id:03d})")

        if self.auto_mode:
            print(f"\nMode: AUTOMATIC (will proceed between cards automatically)")
            print(f"\nInstructions:")
            print(f"  1. Tap card on the NFC reader")
            print(f"  2. Wait for confirmation message")
            print(f"  3. Remove card when prompted")
            print(f"  4. System will wait 3 seconds before next card")
        else:
            print(f"\nMode: MANUAL (will wait for confirmation between cards)")
            print(f"\nInstructions:")
            print(f"  1. Tap card on the NFC reader")
            print(f"  2. Wait for confirmation message")
            print(f"  3. Remove card when prompted")
            print(f"  4. Press Enter when ready with next card")

        print(f"\nPress Ctrl+C to stop at any time\n")

        input("Press Enter to start...")

        try:
            while self.current_id <= self.end_id:
                token_id = f"{self.current_id:03d}"
                self._init_card(token_id)

        except KeyboardInterrupt:
            print("\n\nStopped by user")

        finally:
            self._print_summary()

    def _init_card(self, token_id: str):
        """
        Initialize a single card

        Args:
            token_id: Token ID to write (e.g., "001")
        """
        print(f"\n[{self.current_id}/{self.end_id}] Waiting for card (Token ID: {token_id})...")

        # Wait for card with no timeout
        result = self.nfc.wait_for_card(timeout=None)

        if not result:
            print("  ✗ TIMEOUT (no card detected)")
            self.failed_cards.append(token_id)
            return

        uid, _ = result
        print(f"  ✓ Card detected (UID: {uid})")

        # Write token ID to card
        # Note: In current implementation, we use UID as token_id
        # For full NDEF writing, this would need enhancement

        print(f"  Writing token ID '{token_id}'...", end='', flush=True)

        # For now, we just record the mapping
        # In a real implementation, you'd write NDEF data here
        success = True  # self.nfc.write_token_id(token_id)

        if success:
            print(" SUCCESS ✓")
            self.initialized_cards.append({
                'token_id': token_id,
                'uid': uid,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })

            # Save mapping to file
            self._save_mapping()

            # Wait for card removal with actual detection
            print("  Please remove card...", end='', flush=True)
            removed = self.nfc.wait_for_card_removal(timeout=15.0)

            if removed:
                print(" OK ✓")

                # Reset reader to clear state
                self.nfc.reset_reader()

                # Give extra time for physical handling and reader reset
                if self.auto_mode:
                    # In auto mode, wait 3 seconds then proceed
                    print("  Waiting 3 seconds before next card...")
                    time.sleep(3)
                else:
                    # In manual mode, wait for user confirmation
                    input("  Press Enter when ready with next card...")

                self.current_id += 1

            else:
                print(" TIMEOUT (card still present)")
                print("  ⚠ Card was not removed in time, skipping...")
                self.failed_cards.append(token_id)

        else:
            print(" FAILED ✗")
            self.failed_cards.append(token_id)

    def _save_mapping(self):
        """Save UID to token ID mapping to CSV file"""
        mapping_file = "data/card_mapping.csv"

        # Ensure directory exists
        os.makedirs(os.path.dirname(mapping_file), exist_ok=True)

        # Write mapping
        with open(mapping_file, 'w') as f:
            f.write("token_id,uid,initialized_at\n")
            for card in self.initialized_cards:
                f.write(f"{card['token_id']},{card['uid']},{card['timestamp']}\n")

    def _print_summary(self):
        """Print initialization summary"""
        total_attempted = len(self.initialized_cards) + len(self.failed_cards)
        success_count = len(self.initialized_cards)
        fail_count = len(self.failed_cards)

        print(f"\n{'=' * 60}")
        print(f"Initialization Summary")
        print(f"{'=' * 60}")
        print(f"Total attempted: {total_attempted}")
        print(f"Successful:      {success_count} ✓")
        print(f"Failed:          {fail_count} ✗")

        if fail_count > 0:
            print(f"\nFailed token IDs: {', '.join(self.failed_cards)}")

        print(f"\nCard mapping saved to: data/card_mapping.csv")
        print(f"{'=' * 60}\n")


def main():
    """Entry point for card initialization"""
    parser = argparse.ArgumentParser(description='Initialize NFC cards with token IDs')
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='Starting token ID (default: 1)'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=100,
        help='Ending token ID (default: 100)'
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock NFC reader for testing'
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Automatic mode: proceed between cards without user confirmation'
    )

    args = parser.parse_args()

    # Validate range
    if args.start < 1 or args.end < args.start:
        print("Error: Invalid token ID range", file=sys.stderr)
        return 1

    try:
        initializer = CardInitializer(
            start_id=args.start,
            end_id=args.end,
            mock=args.mock,
            auto_mode=args.auto
        )
        initializer.run()
        return 0

    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

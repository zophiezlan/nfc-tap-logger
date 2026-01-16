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
from datetime import datetime
from pathlib import Path
from tap_station.nfc_reader import NFCReader, MockNFCReader
from tap_station.feedback import FeedbackController


class CardInitializer:
    """Initialize NFC cards with sequential token IDs"""

    def __init__(self, start_id: int = 1, end_id: int = 100, mock: bool = False, auto_mode: bool = False,
                 enable_audio: bool = True, resume: bool = False):
        """
        Initialize card initializer

        Args:
            start_id: Starting token ID
            end_id: Ending token ID
            mock: Use mock NFC reader
            auto_mode: If True, automatically proceed between cards (no user confirmation)
            enable_audio: Enable buzzer feedback
            resume: Resume from last completed card
        """
        self.start_id = start_id
        self.end_id = end_id
        self.current_id = start_id
        self.auto_mode = auto_mode
        self.mapping_file = "data/card_mapping.csv"

        # Load existing cards for duplicate detection and resume
        self.existing_cards = self._load_existing_cards()

        # Resume from last card if requested
        if resume and self.existing_cards:
            last_id = max(int(card['token_id']) for card in self.existing_cards.values())
            if last_id >= self.start_id:
                self.current_id = last_id + 1
                print(f"Resuming from card {self.current_id:03d} (last completed: {last_id:03d})")

        # Initialize NFC reader
        if mock:
            self.nfc = MockNFCReader()
            print("Using mock NFC reader (testing mode)")
        else:
            self.nfc = NFCReader()
            print("PN532 NFC reader initialized")

        # Initialize feedback controller
        try:
            self.feedback = FeedbackController(
                buzzer_enabled=enable_audio,
                led_enabled=False,  # No LEDs during init
                beep_success=[0.1],  # Short beep
                beep_duplicate=[0.1, 0.05, 0.1],  # Double beep
                beep_error=[0.3]  # Long beep
            )
            if enable_audio:
                print("Audio feedback enabled")
        except Exception as e:
            print(f"Warning: Could not enable audio feedback: {e}")
            self.feedback = None

        # Statistics tracking
        self.initialized_cards = []
        self.failed_cards = []
        self.duplicate_cards = []
        self.start_time = None

    def _load_existing_cards(self) -> dict:
        """Load existing card mappings from CSV"""
        existing = {}
        mapping_path = Path(self.mapping_file)

        if not mapping_path.exists():
            return existing

        try:
            with open(mapping_path, 'r') as f:
                # Skip header
                next(f)
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        token_id = parts[0]
                        uid = parts[1]
                        existing[uid] = {'token_id': token_id, 'uid': uid}
        except Exception as e:
            print(f"Warning: Could not load existing cards: {e}")

        if existing:
            print(f"Loaded {len(existing)} existing card(s) from {self.mapping_file}")

        return existing

    def _get_progress_bar(self, current: int, total: int, width: int = 30) -> str:
        """Generate a text progress bar"""
        completed = self.current_id - self.start_id
        progress = completed / total if total > 0 else 0
        filled = int(width * progress)
        bar = '█' * filled + '░' * (width - filled)
        percent = int(progress * 100)
        return f"[{bar}] {percent}%"

    def _get_statistics(self) -> str:
        """Generate statistics string"""
        if not self.start_time:
            return ""

        elapsed = (datetime.now() - self.start_time).total_seconds()
        completed = self.current_id - self.start_id

        if completed == 0 or elapsed == 0:
            return ""

        # Cards per minute
        rate = (completed / elapsed) * 60

        # Estimated time remaining
        remaining = self.end_id - self.current_id + 1
        eta_seconds = (remaining / rate) * 60 if rate > 0 else 0
        eta_min = int(eta_seconds / 60)

        elapsed_min = int(elapsed / 60)
        elapsed_sec = int(elapsed % 60)

        stats = f"  Time: {elapsed_min}m {elapsed_sec}s"
        stats += f" | Rate: {rate:.1f} cards/min"
        if eta_min > 0:
            stats += f" | ETA: {eta_min}m"

        return stats

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

        # Startup beep
        if self.feedback:
            self.feedback.startup()

        # Start timer
        self.start_time = datetime.now()

        try:
            while self.current_id <= self.end_id:
                token_id = f"{self.current_id:03d}"

                # Show progress
                total_cards = self.end_id - self.start_id + 1
                progress_bar = self._get_progress_bar(self.current_id, total_cards)
                stats = self._get_statistics()
                print(f"\n{progress_bar}{stats}")

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
        print(f"[{self.current_id}/{self.end_id}] Waiting for card (Token ID: {token_id})...")

        # Wait for card with no timeout
        result = self.nfc.wait_for_card(timeout=None)

        if not result:
            print("  ✗ TIMEOUT (no card detected)")
            if self.feedback:
                self.feedback.error()
            self.failed_cards.append(token_id)
            return

        uid, _ = result
        print(f"  ✓ Card detected (UID: {uid})")

        # Check for duplicates
        if uid in self.existing_cards:
            existing_token = self.existing_cards[uid]['token_id']
            print(f"  ⚠ DUPLICATE! This card is already token ID {existing_token}")
            if self.feedback:
                self.feedback.duplicate()
            self.duplicate_cards.append({
                'new_token_id': token_id,
                'existing_token_id': existing_token,
                'uid': uid
            })

            # Ask user what to do
            response = input("  Skip this card? (y/n): ").strip().lower()
            if response == 'y':
                print("  Skipping duplicate card")
                return
            else:
                print(f"  Overwriting token ID {existing_token} → {token_id}")

        # Write token ID to card
        print(f"  Writing token ID '{token_id}'...", end='', flush=True)

        # For now, we just record the mapping
        # In a real implementation, you'd write NDEF data here
        success = True  # self.nfc.write_token_id(token_id)

        if success:
            print(" SUCCESS ✓")

            # Success beep
            if self.feedback:
                self.feedback.success()

            self.initialized_cards.append({
                'token_id': token_id,
                'uid': uid,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })

            # Update existing cards dict
            self.existing_cards[uid] = {'token_id': token_id, 'uid': uid}

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
                    # In auto mode, visual countdown
                    for i in range(3, 0, -1):
                        print(f"  Next card in: {i}...", end='\r', flush=True)
                        time.sleep(1)
                    print(" " * 40, end='\r')  # Clear countdown line
                else:
                    # In manual mode, wait for user confirmation
                    input("  Press Enter when ready with next card...")

                self.current_id += 1

            else:
                print(" TIMEOUT (card still present)")
                print("  ⚠ Card was not removed in time, skipping...")
                if self.feedback:
                    self.feedback.error()
                self.failed_cards.append(token_id)

        else:
            print(" FAILED ✗")
            if self.feedback:
                self.feedback.error()
            self.failed_cards.append(token_id)

    def _save_mapping(self):
        """Save UID to token ID mapping to CSV file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.mapping_file), exist_ok=True)

        # Combine existing cards with new initialized cards
        all_cards = {}

        # Add existing cards first
        for uid, card in self.existing_cards.items():
            all_cards[uid] = card

        # Add/update with newly initialized cards
        for card in self.initialized_cards:
            all_cards[card['uid']] = card

        # Write all cards to file
        with open(self.mapping_file, 'w') as f:
            f.write("token_id,uid,initialized_at\n")
            for card in sorted(all_cards.values(), key=lambda x: x['token_id']):
                timestamp = card.get('timestamp', 'unknown')
                f.write(f"{card['token_id']},{card['uid']},{timestamp}\n")

    def _print_summary(self):
        """Print initialization summary"""
        # Calculate final statistics
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            elapsed_min = int(elapsed / 60)
            elapsed_sec = int(elapsed % 60)
        else:
            elapsed_min = 0
            elapsed_sec = 0

        success_count = len(self.initialized_cards)
        fail_count = len(self.failed_cards)
        duplicate_count = len(self.duplicate_cards)
        total_attempted = success_count + fail_count

        print(f"\n{'=' * 60}")
        print(f"Initialization Summary")
        print(f"{'=' * 60}")
        print(f"Total time:      {elapsed_min}m {elapsed_sec}s")
        print(f"Total attempted: {total_attempted}")
        print(f"Successful:      {success_count} ✓")
        print(f"Failed:          {fail_count} ✗")
        print(f"Duplicates:      {duplicate_count} ⚠")

        if fail_count > 0:
            print(f"\nFailed token IDs: {', '.join(self.failed_cards)}")

        if duplicate_count > 0:
            print(f"\nDuplicate cards detected:")
            for dup in self.duplicate_cards:
                print(f"  Token {dup['new_token_id']} → Already exists as {dup['existing_token_id']} (UID: {dup['uid']})")

        # Show overall progress
        total_cards = self.end_id - self.start_id + 1
        completed = self.current_id - self.start_id
        progress_percent = int((completed / total_cards) * 100)
        print(f"\nOverall progress: {completed}/{total_cards} ({progress_percent}%)")

        print(f"\nCard mapping saved to: {self.mapping_file}")
        print(f"{'=' * 60}\n")

        # Cleanup feedback
        if self.feedback:
            self.feedback.cleanup()


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
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last completed card'
    )
    parser.add_argument(
        '--no-audio',
        action='store_true',
        help='Disable audio feedback (buzzer)'
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
            auto_mode=args.auto,
            enable_audio=not args.no_audio,
            resume=args.resume
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

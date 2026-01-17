"""
Test to verify the fix for NFC card initialization write error.

The issue was that mifareultralight_ReadPage returns a tuple (success, data),
but the code was treating it as if it returned just the data.
"""

from unittest.mock import patch, MagicMock
from tap_station.nfc_reader import NFCReader


def test_read_page_returns_tuple():
    """Test that ReadPage method properly handles tuple return value"""
    
    class MockPn532:
        """Mock PN532 that mimics the real library behavior"""
        
        def begin(self):
            pass
        
        def getFirmwareVersion(self):
            return 0x01020000
        
        def SAMConfig(self):
            pass
        
        def readPassiveTargetID(self, cardbaudrate):
            # Return tuple as the real library does
            return True, bytearray([0x04, 0x31, 0x6B, 0xD1, 0x2D, 0x02, 0x89])
        
        def mifareultralight_ReadPage(self, page):
            """
            This is the key method that returns a tuple (success, data).
            The bug was that code was not unpacking this tuple.
            """
            if page == 4:
                # Return token ID "001" as written to the card
                return True, bytearray([0x30, 0x30, 0x31, 0x00])  # b'001\x00'
            else:
                return True, bytearray([0x00, 0x00, 0x00, 0x00])
        
        def mifareultralight_WritePage(self, page, buffer):
            return True
    
    # Create reader with mock PN532
    with patch.object(NFCReader, "_setup_reader", lambda self: None):
        reader = NFCReader()
    
    reader.pn532 = MockPn532()
    
    # Test _read_token_id - this was failing before the fix
    uid_bytes = bytearray([0x04, 0x31, 0x6B, 0xD1, 0x2D, 0x02, 0x89])
    token = reader._read_token_id(uid_bytes)
    
    # Should successfully read the token ID
    assert token == "001", f"Expected token '001', got '{token}'"


def test_write_token_id_with_verification():
    """Test that write_token_id with readback verification works"""
    
    class MockPn532:
        """Mock PN532 that mimics the real library behavior"""
        
        def begin(self):
            pass
        
        def getFirmwareVersion(self):
            return 0x01020000
        
        def SAMConfig(self):
            pass
        
        def readPassiveTargetID(self, cardbaudrate):
            return True, bytearray([0x04, 0x31, 0x6B, 0xD1, 0x2D, 0x02, 0x89])
        
        def mifareultralight_ReadPage(self, page):
            """Returns tuple (success, data)"""
            if page == 4:
                return True, bytearray([0x30, 0x30, 0x31, 0x00])  # Token "001"
            else:
                return True, bytearray([0x00, 0x00, 0x00, 0x00])
        
        def mifareultralight_WritePage(self, page, buffer):
            return True
    
    # Create reader with mock PN532
    with patch.object(NFCReader, "_setup_reader", lambda self: None):
        reader = NFCReader()
    
    reader.pn532 = MockPn532()
    
    # This was failing with: 'bytearray' object cannot be interpreted as an integer
    # The error occurred in the verification readback when bytes(raw) was called
    # on a tuple (True, bytearray([...])) instead of just the bytearray
    result = reader.write_token_id("001")
    
    # Should successfully write and verify
    assert result is True, "write_token_id should succeed"


def test_bytes_on_tuple_raises_error():
    """
    Demonstrate the original error that was happening.
    
    This shows what was happening before the fix.
    """
    # Simulate the old behavior where read_page result wasn't unpacked
    raw = (True, bytearray([0x30, 0x30, 0x31, 0x00]))  # What read_page returns
    
    # This is what the old code was doing: bytes(raw) where raw is a tuple
    try:
        _ = bytes(raw)
        assert False, "Should have raised TypeError"
    except TypeError as e:
        # This is the exact error message from the bug report
        assert "'bytearray' object cannot be interpreted as an integer" in str(e)


def test_bytes_on_unpacked_data_works():
    """
    Demonstrate the fix: unpacking the tuple before calling bytes().
    """
    # Simulate correct behavior where we unpack the tuple
    success, raw = (True, bytearray([0x30, 0x30, 0x31, 0x00]))
    
    # Now bytes(raw) works because raw is just the bytearray
    result = bytes(raw)
    assert result == b'001\x00'

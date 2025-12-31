import unittest
import os
import sys
from datetime import datetime

# Add project root to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.types import ChatMetadata
from analyzers.group import GroupAnalyzer
from core.loader import stream_messages

class TestAnalyzerSmoke(unittest.TestCase):
    def setUp(self):
        # Updated: Fixtures are now a sibling folder to this test file
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.json_path = os.path.join(self.fixtures_dir, 'basic_chat.json')
        
        # Setup mock metadata
        self.meta = ChatMetadata(chat_id=123, name="Test", chat_type="group")
        
        # Initialize Analyzer (Group strategy)
        self.analyzer = GroupAnalyzer(stop_words=set(), profanity_words=set())
        self.analyzer.result.metadata = self.meta

    def test_basic_stats(self):
        """Checks if total messages and participants are counted correctly."""
        # Using list signature as per new loader
        messages = stream_messages([self.json_path])
        
        for msg in messages:
            self.analyzer.process_message(msg)
        self.analyzer.finalize()
        
        res = self.analyzer.result
        
        # Check Global Stats
        self.assertEqual(res.global_stats.total_messages, 3, "Should count 3 regular messages")
        self.assertEqual(res.global_stats.photos, 1, "Should detect 1 photo")
        self.assertEqual(res.global_stats.replies, 1, "Should detect 1 reply")
        
        # Check Participants
        self.assertIn("Alice", res.users_stats)
        self.assertIn("Bob", res.users_stats)
        self.assertEqual(res.users_stats["Alice"].total_messages, 2)
        self.assertEqual(res.users_stats["Bob"].total_messages, 1)

if __name__ == '__main__':
    unittest.main()
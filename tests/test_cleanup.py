import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

from kalamanch import cleanup as cl

ACCEPTED = datetime(2026, 10, 1, tzinfo=timezone.utc)


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "voices.json")

    def tearDown(self):
        self.tmp.cleanup()

    def write_state(self, state):
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(state, fh)

    def read_state(self):
        with open(self.path, encoding="utf-8") as fh:
            return json.load(fh)

    def test_record_final_stores_profile_once_with_first_accept_time(self):
        with mock.patch.object(cl, "resolve_profile_id", return_value="id-1"):
            cl.record_final(["narrator"], now=ACCEPTED, path=self.path)
            cl.record_final(["narrator"], now=ACCEPTED + timedelta(days=3), path=self.path)
        entry = self.read_state()["id-1"]
        self.assertEqual(entry["name"], "narrator")
        self.assertEqual(entry["accepted_at"], ACCEPTED.isoformat())

    def test_nothing_deleted_before_grace_period(self):
        self.write_state({"id-1": {"name": "narrator", "accepted_at": ACCEPTED.isoformat()}})
        with mock.patch.object(cl.requests, "delete") as delete:
            due = cl.cleanup(now=ACCEPTED + timedelta(days=9), path=self.path)
        self.assertEqual(due, [])
        delete.assert_not_called()

    def test_deletes_recorded_profile_after_grace_period(self):
        self.write_state({"id-1": {"name": "narrator", "accepted_at": ACCEPTED.isoformat()}})
        response = mock.Mock(status_code=200, text="")
        with mock.patch.object(cl.requests, "delete", return_value=response) as delete:
            due = cl.cleanup(now=ACCEPTED + timedelta(days=10), path=self.path)
        self.assertEqual(due, ["narrator"])
        delete.assert_called_once()
        self.assertIn("/profiles/id-1", delete.call_args[0][0])
        self.assertIn("deleted_at", self.read_state()["id-1"])

    def test_dry_run_lists_due_profiles_and_deletes_nothing(self):
        self.write_state({"id-1": {"name": "narrator", "accepted_at": ACCEPTED.isoformat()}})
        with mock.patch.object(cl.requests, "delete") as delete:
            due = cl.cleanup(now=ACCEPTED + timedelta(days=11), dry_run=True, path=self.path)
        self.assertEqual(due, ["narrator"])
        delete.assert_not_called()
        self.assertNotIn("deleted_at", self.read_state()["id-1"])

    def test_profiles_not_recorded_are_never_deleted(self):
        self.write_state({})
        with mock.patch.object(cl.requests, "delete") as delete:
            due = cl.cleanup(now=ACCEPTED + timedelta(days=365), path=self.path)
        self.assertEqual(due, [])
        delete.assert_not_called()

    def test_already_deleted_profile_is_skipped(self):
        self.write_state({"id-1": {"name": "narrator", "accepted_at": ACCEPTED.isoformat(),
                                   "deleted_at": ACCEPTED.isoformat()}})
        with mock.patch.object(cl.requests, "delete") as delete:
            due = cl.cleanup(now=ACCEPTED + timedelta(days=30), path=self.path)
        self.assertEqual(due, [])
        delete.assert_not_called()

    def test_failed_delete_raises_and_keeps_record_pending(self):
        self.write_state({"id-1": {"name": "narrator", "accepted_at": ACCEPTED.isoformat()}})
        response = mock.Mock(status_code=500, text="boom")
        with mock.patch.object(cl.requests, "delete", return_value=response):
            with self.assertRaises(RuntimeError):
                cl.cleanup(now=ACCEPTED + timedelta(days=10), path=self.path)
        self.assertNotIn("deleted_at", self.read_state()["id-1"])


if __name__ == "__main__":
    unittest.main()

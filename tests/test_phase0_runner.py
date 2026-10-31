"""External 2WCF runner preflight tests; never execute third-party upstream code."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / "Python_code"
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("phase0_external_runner", ROOT / "run_2wcf_external.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerPreflightTests(unittest.TestCase):
    def test_missing_source_fails(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                runner.validate_upstream(Path(d))

    def test_pinned_sha_and_blob_required(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            (folder / runner.UPSTREAM_FILE).write_text("placeholder")
            with patch.object(runner, "_git", side_effect=["wrong", runner.UPSTREAM_BLOB]):
                with self.assertRaisesRegex(ValueError, "Wrong upstream commit"):
                    runner.validate_upstream(folder)
            with patch.object(runner, "_git", side_effect=[runner.UPSTREAM_SHA, "wrong"]):
                with self.assertRaisesRegex(ValueError, "differs from audited blob"):
                    runner.validate_upstream(folder)

    def test_valid_pinned_sha_and_blob(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            source = folder / runner.UPSTREAM_FILE
            source.write_text("placeholder")
            with patch.object(runner, "_git", side_effect=[runner.UPSTREAM_SHA, runner.UPSTREAM_BLOB]):
                self.assertEqual(runner.validate_upstream(folder), source)

    def test_snapshot_only_serializable_params(self):
        class FakeOFV:
            ArrowDensityStep = 7
            VelocityInversion = -1
            USE_SVD = False
            KillIDs = [0, 2]
            Other = object()
            ImageFolder = Path("somewhere")
        params = runner.collect_parameter_snapshot(FakeOFV)
        self.assertEqual(params["ArrowDensityStep"], 7)
        self.assertEqual(params["KillIDs"], [0, 2])
        self.assertNotIn("Other", params)
        self.assertNotIn("ImageFolder", params)


if __name__ == "__main__":
    unittest.main()

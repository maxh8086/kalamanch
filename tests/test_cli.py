import os
import unittest
from unittest import mock

from kalamanch import cli
from kalamanch.upscale import upscale
from kalamanch.video import animate


class BuildParserTests(unittest.TestCase):
    def test_subcommands_registered(self):
        parser = cli.build_parser()
        subparsers = next(
            action for action in parser._actions if action.dest == "command"
        )
        self.assertEqual(
            set(subparsers.choices),
            {"assemble", "upscale", "voice", "animate", "accept", "cleanup"},
        )

    def test_assemble_arguments_parse(self):
        args = cli.build_parser().parse_args(["assemble", "v.mp4", "a.wav", "o.mp4"])
        self.assertEqual(args.command, "assemble")
        self.assertEqual(args.video_path, "v.mp4")
        self.assertEqual(args.audio_path, "a.wav")
        self.assertEqual(args.out_path, "o.mp4")

    def test_upscale_default_scale(self):
        args = cli.build_parser().parse_args(["upscale", "in.mp4", "out.mp4"])
        self.assertEqual(args.scale, 2)


class AnimateTests(unittest.TestCase):
    def test_raises_when_wan_cmd_unset(self):
        with mock.patch.dict(os.environ, clear=False):
            os.environ.pop("WAN_CMD", None)
            with self.assertRaises(RuntimeError) as ctx:
                animate("portrait.png", 5, "out.mp4")
        self.assertIn("WAN_CMD", str(ctx.exception))


class UpscaleTests(unittest.TestCase):
    def test_builds_expected_argv(self):
        with mock.patch("kalamanch.upscale.subprocess.run") as run:
            result = upscale("in.mp4", "out.mp4", scale=2)
        self.assertEqual(result, "out.mp4")
        run.assert_called_once_with(
            ["video2x", "-i", "in.mp4", "-o", "out.mp4", "-p", "realesrgan", "-s", "2"],
            check=True,
        )


if __name__ == "__main__":
    unittest.main()

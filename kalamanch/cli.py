"""Command line entry point for the KalaManch stages."""

import argparse
import sys

from kalamanch.assemble import assemble
from kalamanch.upscale import upscale
from kalamanch.video import animate
from kalamanch.voice import synthesize


def build_parser():
    parser = argparse.ArgumentParser(prog="kalamanch", description="KalaManch video pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("assemble", help="Stage 4: combine video and audio into an MP4")
    p.add_argument("video_path")
    p.add_argument("audio_path")
    p.add_argument("out_path")

    p = sub.add_parser("upscale", help="Stage 5: upscale with Video2X and Real-ESRGAN")
    p.add_argument("in_path")
    p.add_argument("out_path")
    p.add_argument("--scale", type=int, default=2)

    p = sub.add_parser("voice", help="Stage 2: synthesize narration via Voicebox")
    p.add_argument("text")
    p.add_argument("profile")
    p.add_argument("out_path")

    p = sub.add_parser("animate", help="Stage 3: image-to-video via the Wan command")
    p.add_argument("portrait")
    p.add_argument("seconds", type=float)
    p.add_argument("out_path")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "assemble":
            out = assemble(args.video_path, args.audio_path, args.out_path)
        elif args.command == "upscale":
            out = upscale(args.in_path, args.out_path, scale=args.scale)
        elif args.command == "voice":
            out = synthesize(args.text, args.profile, args.out_path)
        elif args.command == "animate":
            out = animate(args.portrait, args.seconds, args.out_path)
        else:  # pragma: no cover - argparse enforces the choices
            raise ValueError(f"unknown command: {args.command}")
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

---
name: voice-reply
description: Use when the user explicitly asks for a spoken reply — turning an answer into a short voice clip (free TTS), always attaching the text, transcribing inbound voice notes before processing, and degrading to plain text when synthesis fails.
metadata:
  version: 1.0.0
  author: aidog
compatibility: Knowledge-first skill; wire the helper commands shown to your project's own scripts and tooling.
---

# voice-reply — free voice replies

## When a voice clip is appropriate

- **Only on an explicit request** ("reply by voice / send it as voice / say it
  out loud"). Default is always plain text; never add voice unprompted —
  voice is the user's "cannot look at the screen right now" option, not a
  style flourish.
- Long reports and multi-option menus are **never** voiced (they cannot be
  clicked and cannot be read out completely). Voice carries the
  **conclusion, ≤60 seconds**; details stay in text.
- When asked for voice: write the text first (as normal), then convert
  **the same content** into the clip. Strip markdown, emoji and code blocks
  from the spoken text — it must read as speech (short sentences, no
  "✅" or "# heading" read out loud).

## Generation

```bash
T=/tmp/voice_$$.ogg
edge-tts --voice zh-CN-XiaoxiaoNeural --text "what to say" --write-media /tmp/v$$.mp3 \
  && ffmpeg -y -loglevel error -i /tmp/v$$.mp3 -c:a libopus -b:a 32k "$T" && echo "$T"
```

- Pick **one** default voice for the product and keep it (a calm female voice
  is a sane default; alternatives: a livelier voice, two male registers, a
  broadcast register) — voice choice is a product decision, not a per-message
  improvisation.
- Listen tuning: `--rate=+5%` to speed up, `--pitch=-2Hz` to sound more
  natural.
- One clip per message; if it would run past 60 seconds, voice the conclusion
  only.

## Sending

**Iron rule: a voice clip always carries its text.** The user may not be able
to listen right now, so the content must be readable. Two shapes by length:

- text ≤ 900 characters: put it in the attachment caption (clip + text in one
  message);
- longer: send the clip first, then the full text in the same reply.

**Never send a bare clip.** Delete the temporary files after sending.

## Inbound voice (user sends an audio note → transcribe, then treat as text)

Messaging platforms hand the agent a **file path**, not text — so a turn
carrying an audio attachment is transcribed first:

```bash
stt.py <attachment-path> --language zh     # Chinese; use --model base if weak
stt.py <attachment-path> --json            # JSON with segments + language
stt_selftest.py                            # self-check loop (TTS -> STT round trip)
```

- **Zero external dependency, zero key**: a local whisper-class model in a
  project venv (the script re-execs itself into it, never touching the
  machine interpreter); model sizes are cached after first use.
- Exit codes are specific: missing dependency → install guidance (rc 3),
  missing file (rc 2), model/transcription failure (rc 4).
- mp3 / ogg / opus / wav / m4a all accepted (platform inbound voice is opus
  in practice). The transcript **becomes** the turn's input and is handled
  exactly like typed text.
- Only the user's inbound voice is transcribed; never do the reverse
  automatically — outbound voice stays request-only per the section above.

## Failure fallback

If any link in the chain fails, **retry at most once, then give up on voice**:

1. `edge-tts` non-zero / timeout / missing or zero-byte output (rate limiting,
   broken package);
2. `ffmpeg` transcode failure (missing codec, corrupt file);
3. the attachment arrives as a generic file instead of a playable clip (a
   known platform-side failure mode).

Fallback action: **send the normal text reply** (content complete as usual)
with one closing line — "voice generation failed, here is the text version".
No technical explanation, no retry storm, never keep the user waiting.
Text is the floor; voice is the add-on.

## Notes

- edge-tts-style synthesis and ffmpeg cost nothing; total voice cost = 0.
- Temporary files live outside the project and are removed after each send.

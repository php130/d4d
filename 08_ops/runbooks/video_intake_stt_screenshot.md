# Video Intake: Caption, STT, Screenshot Runbook

Use this runbook for YouTube/webinar/tutorial materials related to D4D platforms.

## Recommendation

Prefer this order:

1. Official captions/transcripts
2. Auto-generated YouTube captions
3. Screenshot/key-frame notes for UI-heavy demos
4. STT from audio only when captions are missing or poor

Do not store full transcripts by default. Store summary cards, timestamps, concepts, product workflow notes, and screenshots where needed.

## Why Captions First

- Faster than STT.
- Usually enough for platform education.
- Avoids unnecessary audio/video download.
- Easier to align with timestamps.

## When Screenshots Matter

Use screenshots when the video shows:

- search/filter UI
- graph/canvas workflow
- dashboard or map output
- API configuration
- report/export flow
- Palantir Workshop/Ontology setup screens

Transcript alone is weak for these because the important information is visual.

## When STT Matters

Use STT when:

- no captions are available
- captions are missing major sections
- the speaker uses domain terms that captions mistranscribe
- the video is uploaded outside YouTube and has no transcript

## Output Template

Create one summary card per video:

```markdown
# Video Summary: <title>

- Source:
- Date reviewed:
- Duration:
- Caption source: official / auto / STT / none
- Visual capture needed: yes/no

## 5-line Summary

1.
2.
3.
4.
5.

## Platform Features Mentioned

- 

## Workflow Pattern

1.
2.
3.

## D4D Relevance

- Related track:
- Possible demo use:
- Data needed:

## Timestamps To Revisit

| Time | Reason |
| --- | --- |
|  |  |

## Terms To Add To Glossary

- 
```

## Storage Layout

Recommended:

```text
04_platforms/
  stealthmole/
    youtube_video_index.md
    video_summaries/
      <date>_<video_id>_<slug>.md
    screenshots/
      <video_id>/
        0001.png
        0002.png
```

Avoid by default:

```text
full_transcripts/
raw_video_downloads/
raw_audio_downloads/
```

## D4D Safety Rule

Even if a video shows sensitive examples, do not reproduce raw credentials, personal information, exploit instructions, or dark web source text in project notes. Summarize the workflow and keep indicators masked unless they are clearly safe public examples.


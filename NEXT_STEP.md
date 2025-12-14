## Goal

Add an optional step `--link-original-media` that:

1. Scans WhatsApp-export media files (low-res) referenced in `_chat.txt` / generated HTML
2. Scans a user-provided folder of original media (copied from iPhone)
3. Builds a mapping `exported_file -> original_file` using robust matching
4. Rewrites HTML (and/or internal message model) to point to originals (preferably copying/hardlinking into the output bundle for portability)

If no match is confident, keep existing exported media.

---

## CLI / Config

Add parameters:

* `--export-media-dir <path>` (folder containing WhatsApp-exported images/videos)
* `--original-media-dir <path>` (folder with iPhone originals)
* `--output-media-dir <path>` (e.g. `output/original_media/`)
* `--match-window-seconds <int>` default `600` (±10 minutes)
* `--phash-threshold <int>` default `10` (Hamming distance; tune)
* `--confidence-mode {strict,balanced,loose}` (controls thresholds)
* `--copy-mode {copy,hardlink,symlink}` default `copy` (symlink if staying local, copy if USB gift)
* `--write-mapping-json <path>` (debugging / reproducibility)

---

## High-level matching strategy

### Images (primary)

Use **timestamp + perceptual hash**:

1. For each exported image `E`:

   * Get a timestamp from filename if present (WhatsApp names often embed datetime), else filesystem mtime.
   * Compute perceptual hash `pHash(E)` (on normalized pixel data).
2. Pre-index originals `O`:

   * Extract creation timestamp from EXIF `DateTimeOriginal` (fallback to file mtime)
   * Compute `pHash(O)` (same normalization)
3. Candidate set: originals with timestamp within `±match_window_seconds`.
4. Pick best candidate by smallest Hamming distance.
5. Accept match if:

   * `dist <= phash_threshold`
   * and best candidate is sufficiently better than runner-up (e.g., `dist2 - dist1 >= 3`) to avoid collisions.

### Videos

Use **metadata timestamp + duration** (hashing video frames is expensive):

1. For each exported video:

   * Get timestamp from filename if possible; else mtime.
   * Get duration via `ffprobe`.
2. Originals:

   * Extract creation time from QuickTime tag `creation_time` (ffprobe) or fallback mtime.
   * Extract duration via ffprobe.
3. Candidate set: within time window.
4. Rank by:

   * absolute duration diff (primary)
   * timestamp closeness (secondary)
   * filesize similarity (optional)
5. Accept if duration diff is small (e.g., ≤0.5s) and time diff within window.

---

## Recommended Python libraries

### Images

* `Pillow` for loading and normalization
* `imagehash` for perceptual hashes
* `exifread` or `Pillow.ExifTags` for EXIF `DateTimeOriginal`

Install:

```bash
pip install pillow imagehash exifread
```

### Videos

* Use `ffprobe` from FFmpeg (system dependency).

  * On macOS: `brew install ffmpeg`
  * On Ubuntu: `apt-get install ffmpeg`
  * On Windows: ship ffmpeg or document install

In Python, call `ffprobe` via `subprocess` and parse JSON:

```bash
ffprobe -v quiet -print_format json -show_format -show_streams <file>
```

---

## Data structures

Create two indexes.

### Original index

`original_index_images: dict[int_bucket -> list[OriginalImage]]`

Where `int_bucket = creation_ts // bucket_size` (e.g. 60s) to speed up lookups.

`OriginalImage`:

* `path`
* `creation_ts` (int unix)
* `phash` (64-bit as int or imagehash obj)
* optional: `width`, `height`

Similarly for videos:

* `creation_ts`, `duration`, etc.

### Export list

A list of exported media items referenced in the chat model:
`ExportMedia`:

* `export_path`
* `type` (image/video)
* `msg_ts` (if you have it from parsed `_chat.txt`)
* fallback timestamp candidates
* computed features (phash/duration)

---

## Timestamp extraction rules (important)

### Prefer these in order

For exported media:

1. If your parsed `_chat.txt` contains the message timestamp for that media, use it.
2. Else parse from filename if it embeds datetime:

   * example: `...PHOTO-2024-12-22-20-36-00.jpg` → local time
3. Else filesystem mtime

For originals:

1. Images: EXIF `DateTimeOriginal`
2. Videos: QuickTime `creation_time` (ffprobe usually shows it in format tags)
3. Else filesystem mtime

### Timezone / DST robustness

Implement a fallback “offset sweep” if matching fails:

* try offsets in `[-7200, -3600, 0, +3600, +7200]` seconds between exported timestamps and originals.
* Pick the offset that yields the most confident matches globally.
* Apply that offset during matching.

(Engineers love this because it avoids support tickets.)

---

## Image normalization for hashing

Before pHash:

1. Load with Pillow
2. Apply EXIF rotation (Pillow has `ImageOps.exif_transpose`)
3. Convert to RGB
4. Optionally downscale to max width ~512 px for speed
5. Compute pHash

Example (sketch):

```python
from PIL import Image, ImageOps
import imagehash

def compute_phash(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img.thumbnail((512, 512))
    return imagehash.phash(img)  # 64-bit hash
```

---

## Matching algorithm (images)

Pseudo:

1. Build original image index by time bucket.
2. For each exported image:

   * `t = exported_ts` (from message, filename, or mtime)
   * candidate originals = gather buckets covering `[t-window, t+window]`
   * compute `dist = (export_phash - orig_phash)` using `hash1 - hash2` (imagehash returns Hamming)
   * sort by dist then by abs(time diff)
   * accept if:

     * `dist <= threshold` AND
     * (runner-up dist - best dist) >= margin
3. Store mapping.

Parameters (balanced defaults):

* `window = 600s`
* `phash_threshold = 10`
* `margin = 3`

Strict mode:

* threshold 8, margin 4

Loose mode:

* threshold 14, margin 2

---

## Matching algorithm (videos)

Pseudo:

1. For each original video: extract `creation_ts`, `duration`.
2. For each exported video: `t`, `duration`.
3. Candidates within time window.
4. Choose candidate minimizing:

   * `duration_diff` first
   * then `time_diff`
5. Accept if `duration_diff <= 0.5s` (tune) and `time_diff <= window`.

---

## Output bundling / HTML rewrite

### Best practice for portability

Even if originals live elsewhere, for the gift use-case you probably want everything self-contained.

Implement:

* For each matched original file, copy/hardlink into `output/original_media/`
* Name it deterministically to avoid collisions, e.g.:

  * `original_media/<sha1_of_full_path>_<basename>`
* Then rewrite HTML to reference that file.

### Rewrite points

Depending on your architecture, do one of:

* Modify your internal message/media model before rendering HTML
* Or do a post-pass over produced HTML:

  * replace `src="media/<exported>"` with `src="original_media/<newname>"`

Also consider `href` if you link to media files.

---

## Debugging & QA requirements

1. Produce `mapping.json` with:

   * exported path
   * original matched path
   * match score: hash distance, time diff, decision threshold, mode
   * reason for rejection (no candidates / ambiguous / too high distance)

2. Provide a small report at the end:

   * total exported media
   * matched images/videos counts + %
   * unmatched counts
   * “ambiguous” counts

3. Add a `--dry-run` to avoid copying, just report.

---

## Acceptance criteria

* On a typical chat export, images should match at high rates (>80% is common) when originals exist.
* No silent wrong matches in strict mode:

  * If ambiguous, keep exported image.
* The tool remains backward compatible when `--original-media-dir` isn’t provided.


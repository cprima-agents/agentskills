# patches/

Patch files in this directory are **local-only** (gitignored). They capture the
adaptations applied to upstream skill content after each sync.

## Setup

Each `sync-*` justfile recipe expects a corresponding `.patch` file here.
Generate it once after the initial sync, then keep it as long as it applies cleanly.

### Steps

1. Set the env vars for the skill you want to patch (see the `# skill sync` section
   in the justfile for the expected variable names). Store them in a local `.env`
   file or your shell profile — both are gitignored.

2. Register the upstream remote (one-time per machine):
   ```
   just setup-upstream-remote
   ```

3. Run the sync recipe to pull upstream content into the skill folder:
   ```
   just sync-<skillname>
   ```
   This overwrites the skill's `SKILL.md` with the upstream version.

3. Generate the patch from the resulting diff:
   ```
   git diff -R HEAD -- skills/<skillname>/SKILL.md > patches/<skillname>-SKILL.md.patch
   ```

4. Restore the committed (adapted) version:
   ```
   git checkout HEAD -- skills/<skillname>/SKILL.md
   ```

5. Verify the patch applies cleanly:
   ```
   just sync-<skillname>
   ```

## Maintenance

If `git apply` fails during a sync, the upstream `SKILL.md` changed in a way that
conflicts with the local adaptation. Resolve manually:

1. Inspect the conflict: `git diff -- skills/<skillname>/SKILL.md`
2. Edit `skills/<skillname>/SKILL.md` to re-apply the intended adaptations
3. Regenerate the patch (steps 2–4 above)

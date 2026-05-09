# Document Not Available

> **{{ artefact_label or "This document" }}** has not been created for project **{{ process_name or "[unknown]" }}**.

## What to do

1. Create the document by copying the template:

   ```
   {{ template_file or "{artefact_id}-template.md" }}
   ```

2. Fill in the required sections.

3. Re-run the renderer once the document exists.

---

| Field | Value |
| --- | --- |
| Expected file pattern | `{{ file_glob or "[unknown]" }}` |
| Artefact | {{ artefact_id or "[unknown]" }} |
| Generated | {{ generated_at or "[unknown]" }} |

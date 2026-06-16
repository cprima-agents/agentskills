| Item | Value |
| --- | --- |
| Production environment | {{ production_environment or 'UiPath Orchestrator — cg371p / Shared (Production tenant)' }} |
| Trigger / Schedule | {{ trigger_schedule or 'Daily 06:00 CET Mon–Fri via Orchestrator time trigger' }} |
| Process input | {{ process_input or 'Orchestrator queue InvoicePosting — items enqueued by Dispatcher' }} |
| Expected output | {{ expected_output or 'SAP MIRO FI document posted; queue item set to Succeeded' }} |
| Orchestrator queues | {{ orchestrator_queues or 'InvoicePosting (Performer), InvoicePosting_Dispatcher (Dispatcher)' }} |
| Orchestrator asset names | {{ orchestrator_asset_names or 'cg371p/cred_SAP_Prod, cg371p/cred_SMTP' }} |
| Credentials storage | {{ credentials_storage or 'Orchestrator Assets (Credential type) — never hardcoded' }} |
| Multiple resolutions supported | {{ multiple_resolutions_supported or 'No — tested on 1920×1080' }} |
| Recommended resolution | {{ recommended_resolution or '1920×1080' }} |

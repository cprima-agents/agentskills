{%- set known = {
  'UiPath.System.Activities':              'Core workflow activities',
  'UiPath.System.Activities.Runtime':      'Core runtime (auto-added)',
  'UiPath.CodedWorkflows':                 'C# coded workflow support (auto-added)',
  'UiPath.UIAutomation.Activities':        'UI automation — desktop and web',
  'UiPath.Excel.Activities':               'Excel read/write',
  'UiPath.Mail.Activities':                'Email via SMTP / IMAP / Exchange',
  'UiPath.MicrosoftOffice365.Activities':  'Microsoft 365 — Mail, Teams, SharePoint',
  'UiPath.PDF.Activities':                 'PDF text extraction',
  'UiPath.Testing.Activities':             'Test automation framework',
  'UiPath.WebAPI.Activities':              'REST / SOAP web service calls',
  'UiPath.FTP.Activities':                 'FTP / SFTP file transfer',
  'UiPath.Database.Activities':            'Database connectivity (ADO.NET)',
  'UiPath.IntelligentOCR.Activities':      'Document Understanding — OCR pipeline',
  'UiPath.DocumentUnderstanding.ML.Activities': 'Document Understanding — ML extraction',
} -%}
{%- if project and project.dependencies %}
| Package | Version | Rule | Purpose |
| --- | --- | --- | --- |
{%- for name, version in project.dependencies.items() %}
{%- if name.startswith('UiPath.') %}
| `{{ name }}` | {{ version }} | {{ 'Strict' if version.startswith('[') and version.endswith(']') else 'Lowest Applicable' }} | {{ known.get(name, '') }} |
{%- endif %}
{%- endfor %}
{%- else %}
| Package | Version | Rule | Purpose |
| --- | --- | --- | --- |
| `UiPath.Excel.Activities` | [2.24.3] | Strict | Excel read/write |
| `UiPath.Mail.Activities` | [2.2.10] | Strict | Email via SMTP / IMAP / Exchange |
| `UiPath.MicrosoftOffice365.Activities` | [2.7.24] | Strict | Microsoft 365 — Mail, Teams, SharePoint |
| `UiPath.System.Activities` | [24.10.4] | Strict | Core workflow activities |
| `UiPath.Testing.Activities` | [24.10.4] | Strict | Test automation framework |
| `UiPath.UIAutomation.Activities` | [25.10.12] | Strict | UI automation — desktop and web |
{%- endif %}

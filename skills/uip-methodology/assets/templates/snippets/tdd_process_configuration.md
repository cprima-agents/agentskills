{%- if config_sections %}
{%- for section in config_sections %}
#### {{ section.name }}

| Property | Type |{% for env in config_envs %} {{ env | upper }} |{% endfor %}
| --- | --- |{% for env in config_envs %} --- |{% endfor %}
{%- for prop in section.properties %}
| `{{ prop.name }}` | `{{ prop.type }}` |{% for env in config_envs %} {{ prop.get(env, '—') }} |{% endfor %}
{%- endfor %}

{%- endfor %}
{%- else %}
#### Settings

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| `OrchestratorQueueName` | `string` | InvoicePosting_Dev | InvoicePosting_Test | InvoicePosting |
| `OrchestratorQueueFolder` | `string` | Shared | Shared | Shared |
| `LogFBusinessProcessName` | `string` | InvoicePosting | InvoicePosting | InvoicePosting |
| `SapAdapter` | `string` | mock | live | live |
| `OrchestratorDeadLetterQueue` | `string` | Shared/dead-letter | Shared/dead-letter | Shared/dead-letter |

#### Constants

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| `MaxRetryNumber` | `int` | 1 | 1 | 0 |
| `MaxConsecutiveSystemExceptions` | `int` | 3 | 3 | 3 |
| `ShouldMarkJobAsFaulted` | `bool` | false | false | true |
| `RetryNumberGetTransactionItem` | `int` | 2 | 2 | 2 |
| `RetryNumberSetTransactionStatus` | `int` | 2 | 2 | 2 |
| `ExScreenshotsFolderPath` | `string` | Exceptions_Screenshots | Exceptions_Screenshots | Exceptions_Screenshots |

#### Assets

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| `SapCredential` | `string` | cg371p/cred_SAP_Dev | cg371p/cred_SAP_Test | cg371p/cred_SAP_Prod |
| `SmtpCredential` | `string` | cg371p/cred_SMTP | cg371p/cred_SMTP | cg371p/cred_SMTP |

#### SAP

| Property | Type | DEV | TEST | PROD |
| --- | --- | --- | --- | --- |
| `SystemId` | `string` | DEV | TST | PRD |
| `Client` | `string` | 100 | 200 | 300 |
| `Language` | `string` | DE | DE | DE |
| `NavigateOnEntry` | `bool` | true | true | true |
| `DrainPopups` | `bool` | true | true | true |
| `ForceRestart` | `bool` | false | false | true |
| `SapLogonDescription` | `string` | SAP Dev | SAP Test | SAP Production |
| `CredentialAsset` | `string` | cg371p/cred_SAP_Dev | cg371p/cred_SAP_Test | cg371p/cred_SAP_Prod |
{%- endif %}

| Scenario | Volume | Runtimes Required | Notes |
| --- | --- | --- | --- |
| Standard load | {{ daily_volume or "[TBD]" }} | {{ runtimes_standard or "[TBD]" }} | |
| Peak load | {{ peak_volume or "[TBD]" }} | {{ runtimes_peak or "[TBD]" }} | Peak utilisation: {{ peak_utilisation_pct or "[TBD]" }}% |
| Scaling trigger | — | — | {{ scaling_trigger or "[TBD — queue depth / time threshold]" }} |

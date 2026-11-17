# Test cases

| Test | Expected result |
|---|---|
| Four seeded discrepancy types | Timing, duplicate, aggregate rounding, and unmatched refund are detected |
| Unmatched refund | Not double-counted as a missing settlement |
| Duplicate bank record | Raw total includes duplicate; adjusted total excludes it |
| Next-month settlement | Classified as timing difference, not missing settlement |
| Invalid platform schema | DataValidationError |
| Invalid bank schema | DataValidationError |
| Empty datasets | Reconciled with zero discrepancies |
| Missing settlement | Missing settlement category |
| Bank-only transaction | Unmatched bank entry category |

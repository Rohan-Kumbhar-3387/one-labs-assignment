# Architecture

```mermaid
flowchart TD
    A[Platform CSV] --> C[Validation and normalization]
    B[Bank CSV] --> C
    C --> D[Reconciliation engine]
    D --> E[Matching and duplicate handling]
    D --> F[Discrepancy classification]
    E --> G[Summary and transaction report]
    F --> G
    G --> H[Streamlit dashboard]
    G --> I[CSV exports]
```

The Streamlit layer handles uploads, presentation, filtering, and downloads. Validation and reconciliation are implemented in independent Python modules so they can be tested without running the UI. Decimal values are retained for all financial comparisons and totals.

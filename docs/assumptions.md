# Phase 1 — Data assumptions

- Reporting period: October 1–31, 2026, using calendar dates and no timezone conversion.
- Currency: INR only; multi-currency conversion is out of scope for this synthetic dataset.
- Payments are positive amounts; refunds are negative amounts.
- The platform records successful payment and refund events at transaction time.
- Ordinary bank settlements occur 1–2 calendar days after the platform event.
- A settlement dated November 1 for an October 31 payment is intentionally included to demonstrate a next-month timing difference.
- Five transactions contain a platform amount of INR 100.004 and a bank amount of INR 100.000. Each residual is INR 0.004, below the proposed per-transaction tolerance of INR 0.005; their aggregate residual is INR 0.020. These sub-paise values are synthetic allocation/conversion residuals used to demonstrate aggregate rounding analysis, not a claim that ordinary INR cash settlement occurs in fractions of a paise.
- One bank settlement is duplicated with a new settlement ID but the same transaction ID and amount.
- One platform refund references a deliberately nonexistent original payment ID and has no bank settlement.
- Five other refunds are valid and have matching bank entries, so the dataset includes normal refund examples.
- Random generation uses seed 20261017 for reproducibility.
- The data is synthetic and must not be treated as real payment or banking information.

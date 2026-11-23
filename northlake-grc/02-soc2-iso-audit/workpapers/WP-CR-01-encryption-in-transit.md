# Workpaper WP-CR-01 — Encryption in Transit

| | |
|---|---|
| **Control ID** | CR-01 — Encryption in transit |
| **Frameworks** | SOC 2 CC6.7 · ISO 27001 A.8.24 · NIST SC-8, SC-8(1) |
| **Control owner** | Security Engineering |
| **Tester** | GRC (internal control testing) |
| **Period tested** | FY2026, point-in-time validation 2026-09-12 |
| **Test methods** | Inspection, Reperformance |

## 1. Control description

Data transmitted over public/untrusted networks to NorthLake's external endpoints is protected using TLS 1.2 or higher with strong cipher suites. Weak protocols (SSLv3, TLS 1.0/1.1) and weak ciphers are disabled. HSTS is enabled on web endpoints.

## 2. Test objective

Confirm that all in-scope external endpoints enforce TLS 1.2+ with strong ciphers and reject deprecated protocols, consistent with the stated configuration.

## 3. Population

All externally reachable in-scope endpoints: the PayRails API gateway, the LendLens API gateway, the Console web application, and the public marketing site (informational — not in the data boundary but tested for completeness). **4 endpoints.**

## 4. Test steps performed

1. **Inspected** the load-balancer / ingress TLS policy configuration (Terraform state + console) for each endpoint.
2. **Reperformed** an independent external scan of each endpoint (TLS version and cipher enumeration) and compared results to policy.
3. **Inspected** HSTS response headers on the web endpoints.
4. **Attempted** a negotiated handshake at TLS 1.0 and 1.1 to confirm rejection.

## 5. Results

| Endpoint | TLS 1.2+ enforced | Weak protocols rejected | Strong ciphers only | HSTS |
|---|---|---|---|---|
| PayRails API | Yes | Yes (1.0/1.1 refused) | Yes | n/a (API) |
| LendLens API | Yes | Yes | Yes | n/a (API) |
| Console web | Yes | Yes | Yes | Yes (max-age 1yr) |
| Marketing site | Yes | Yes | Yes | Yes |

Scan results reconciled to the configured policy with no discrepancies.

## 6. Exceptions noted

None.

## 7. Conclusion

**Control CR-01: Effective.** All in-scope external endpoints enforced TLS 1.2+ with strong ciphers and rejected deprecated protocols at the time of testing. Recommend this validation be run continuously rather than point-in-time (see Project 3), so drift is caught between audits.

## 8. Cross-references

- Evidence: PBC-009 (`evidence-tracker.csv`)
- No finding (control effective).

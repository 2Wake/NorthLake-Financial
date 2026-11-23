# Vendor Risk Assessment — source

`vendor-risk-assessment.html` is the source of the interactive vendor-risk tool that is also published at [`/docs`](../../docs/) for the live site.

**What it does.** Rates a vendor's inherent exposure (data sensitivity × access × criticality), scores its controls across eight domains (governance, access, data protection, infrastructure, incident response, resilience, compliance, subprocessors) with weighted questions, and derives a **residual-risk** rating via an inherent × control-effectiveness matrix — plus flagged gaps, remediations, and an onboarding recommendation. Loads with a sample vendor.

Self-contained HTML; no dependencies beyond Google Fonts. Feeds control **VN-01** in the audit project.

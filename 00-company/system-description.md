# Empire City Taxi Co. — System Description (SOC 2)

*Abbreviated, SOC 2-style system description for the fictional ECT platform. In a real engagement this is management's assertion and forms Section III of the SOC 2 report. Synthetic.*

## 1. Overview of services

Empire City Taxi Co. operates a NYC taxi and for-hire mobility platform: the *ECT Rider* and *ECT Driver* apps, a Dispatch & Matching service, a Payments service, and an internal Console. The services are delivered as a multi-tenant SaaS platform hosted on Google Cloud.

## 2. Principal service commitments and system requirements

ECT commits to riders, drivers, and partners through its terms, privacy policy, and published documentation that it will:

- Protect rider, driver, and cardholder data through encryption in transit and at rest and least-privilege access.
- Maintain availability consistent with a 99.5% monthly uptime commitment for the rider and driver apps.
- Notify affected parties of confirmed security incidents within 72 hours.
- Handle cardholder data in accordance with PCI DSS.
- Restrict access to personal and cardholder data to authorized personnel with a business need.

These commitments drive the system requirements implemented as controls (see the Control Matrix, Project 2).

## 3. Components of the system

**Infrastructure.** GKE clusters, Cloud Run services, Cloud SQL (Postgres), BigQuery, and Cloud Storage within Google Cloud, provisioned via Terraform.

**Software.** ECT-developed services (Rider app, Driver app, Dispatch & Matching, Payments) and the Console; third-party and open-source components tracked in a software inventory.

**People.** Engineering, Platform/SRE, Security & GRC, IT, Driver Operations, Support, Finance, People Ops, and corporate functions. Access governed by role.

**Data.** Rider PII, payment tokens and card last 4 digits (card numbers stay with the payments processor; DOC-01 v2.0), driver PII, employee data, trip/operational data, and financials. Classified per the Data Classification Standard.

**Processes.** Change management, access management, incident response, vulnerability management, vendor risk management, and the control-monitoring process operated by the GRC function.

## 4. Boundaries of the system

The system boundary includes the production GCP environment serving the Rider app, Driver app, Dispatch & Matching, Payments, and Console, and the supporting corporate systems used to administer them (Okta, GitHub, the GRC and ticketing platforms). Google Cloud is treated as a **carved-out** sub-service organization; complementary controls expected of GCP are listed in Section 6. Card processing is performed by a PCI DSS-compliant payments processor (also carved out).

## 5. Complementary user-entity controls (CUECs)

Riders and drivers are responsible for, among others:

- Safeguarding their own app credentials.
- Keeping their contact and payout information accurate.
- Reporting suspected account compromise promptly.

## 6. Complementary sub-service-organization controls

*(Google Cloud)* ECT's controls assume Google Cloud maintains physical and environmental security of data centers, hardware decommissioning, and underlying network infrastructure security — evidenced by GCP's own SOC 2 / ISO reports reviewed annually. The payments processor is assumed to maintain PCI DSS compliance for the card-processing environment, evidenced by its Attestation of Compliance (AOC) reviewed annually.

## 7. Significant changes during the period

*(Example for a report period.)* During the examination period ECT migrated Console authentication to phishing-resistant MFA and implemented continuous configuration monitoring across its GCP projects. Both changes were managed through the change-management process and are reflected in the relevant controls.

# NorthLake Financial — System Description (SOC 2)

*Abbreviated, SOC 2-style system description for the fictional NorthLake platform. In a real engagement this is management's assertion and forms Section III of the SOC 2 report. Synthetic.*

## 1. Overview of services

NorthLake Financial provides embedded payments (PayRails) and lending-analytics (LendLens) APIs and an administrative dashboard (Console) to banking institutions. The services are delivered as a multi-tenant SaaS platform hosted on Google Cloud.

## 2. Principal service commitments and system requirements

NorthLake commits to its customers through master service agreements, security addenda, and published documentation that it will:

- Protect customer data confidentiality through encryption in transit and at rest and least-privilege access.
- Maintain availability consistent with a 99.9% monthly uptime commitment.
- Notify customers of confirmed security incidents affecting their data within 72 hours.
- Restrict access to customer data to authorized personnel with a business need.

These commitments drive the system requirements implemented as controls (see the Control Matrix, Project 2).

## 3. Components of the system

**Infrastructure.** GKE clusters, Cloud Run services, Cloud SQL (Postgres), BigQuery, and Cloud Storage within Google Cloud, provisioned via Terraform.

**Software.** NorthLake-developed API services and the Console web application; third-party and open-source components tracked in a software inventory.

**People.** Engineering, Platform/SRE, Security & GRC, IT, Product, Customer Success, and corporate functions. Access governed by role.

**Data.** Customer PII and financial data processed on behalf of bank clients; operational data (logs, metrics); configuration data. Classified per the Data Classification Standard.

**Processes.** Change management, access management, incident response, vulnerability management, vendor risk management, and the control-monitoring process operated by the GRC function.

## 4. Boundaries of the system

The system boundary includes the production GCP environment serving PayRails, LendLens, and Console, and the supporting corporate systems used to administer them (Okta, GitHub, the GRC and ticketing platforms). Google Cloud is treated as a **carved-out** sub-service organization; complementary controls expected of GCP are listed in Section 6.

## 5. Complementary user-entity controls (CUECs)

Customers (banks) are responsible for, among others:

- Managing their own Console users and promptly removing access for departed staff.
- Protecting API keys issued to them.
- Configuring product settings in line with their own risk appetite.

## 6. Complementary sub-service-organization controls (Google Cloud)

NorthLake's controls assume Google Cloud maintains, among others, physical and environmental security of data centers, hardware decommissioning, and underlying network infrastructure security — evidenced by GCP's own SOC 2 / ISO reports reviewed annually.

## 7. Significant changes during the period

*(Example for a report period.)* During the examination period NorthLake migrated Console authentication to phishing-resistant MFA and implemented continuous configuration monitoring across its GCP projects. Both changes were managed through the change-management process and are reflected in the relevant controls.

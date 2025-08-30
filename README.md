# TikTok TeckJam 2025

## Team: Don Don Donki

### Our Product: GeoGovLite

## Repository Information

### Development tools used to build the project

-   **VSCode**: A popular code editor used for writing and managing code.
-   **Docker**: A platform for developing, shipping, and running applications in containers.

## APIs used in the project

-   **OpenAI API**: Provides access to advanced AI models for natural language processing and understanding.
-   **Congress API**: Provides access to legislative data and information about members of Congress.

### Assets used in the project

-   **TikTok Dataset:** Sample dataset given below.

---

## Problem Statement 3:

### From Guesswork to Governance: Automating Geo-Regulation with LLM

### Assets used in the project

-   **React:** A JavaScript library for building user interfaces.
-   **FastAPI:** A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
-   **OpenAI:** Provides access to advanced AI models for natural language processing and understanding.
-   **CrewAI:** Multi-modal AI platform for building and deploying AI applications.

## Problem Statement

Build a prototype system that **utilizes LLM capabilities to flag features that require geo-specific compliance logic**; turning regulatory detection from a blind spot into a traceable, auditable output.

### Our Solution Empowers TikTok To

1. Proactively implement legal guardrails before features launch
2. Generate auditable evidence proving features were screened for regional compliance needs
3. Confidently respond to regulatory inquiries with automated traceability

### Projects Goals / Questions Tackling

1.  **Boosting LLM Precision:** How can LLMs be fine-tuned, or augmented with domain-specific knowledge to overcome misinterpretations and improve accuracy in identifying related scenarios? How to fill the context gap, e.g. some internal jargon (like feature codenames or ambiguous abbreviations) to avoid misclassification?

2.  **Full automation:** How to build the overall system to be as automated as possible, e.g. Self-evolving multi-agent system that can automatically iterate through human feedback with human intervention.

3.  **Alternative Detection Mechanisms:** Beyond feature artifacts analysis, what other innovative techniques can be employed to detect existing geo-compliance logics (e.g., static code analysis, runtime analysis, data flow tracing)?

### System Inputs

-   Feature artifacts, e.g. Title, description, related documents (PRD, TRD, etc.)
    Examples:
-   ✅ "Feature reads user location to enforce France's copyright rules (download blocking)"
-   ✅ "Requires age gates specific to Indonesia's Child Protection Law"
-   ❌ "Geofences feature rollout in US for market testing" (Business-driven ≠ legal requirement)
-   ❓ "A video filter feature is available globally except KR" (didn't specify the intention, need human evaluation)

### The Expected Output of the System:

-   (required) Flag whether this feature needs geo-specific compliance logic
-   (required) Clear Reasoning
-   (optional) the related regulations

### Task Requirements

-   **Reduce Compliance Governance Costs**: By lowering manual effort in identifying and managing geo-compliance requirements

-   **Mitigate Regulatory Exposure**: By minimizing legal and financial risks from undetected compliance gaps.

-   **Enable Audit-Ready Transparency**: By generating automated evidence trails to streamline regulatory inquiries and audits.

### Deliverables

1. Build or update a working solution that addresses this problem statement

2. Include a text description that should explain the features and functionality of the project, and also include:

    - Development tools used to build the project

    - APIs used in the project

    - Assets used in the project

    - Libraries used in the project

    - The relevant problem statement

    - Any additional dataset(s) that you have used and is not provided in the problem statement

3. Include a link to the team's public Github repository with Readme. Preferably, the repo can be easily set-up for a locally runable demo.

4. Include a demonstration video of the project. The video portion of the submission:

    - should be less than three (3) minutes
    - should include footage that shows the project functioning on the device for which it was built
    - must be uploaded to and made publicly visible on YouTube, and a link to the video must be provided in the text description; and
    - must not include third party trademarks, or copyrighted music or other material unless the Entrant has permission to use such material.

5. Include a csv file containing your system's outputs regarding the test dataset.

### Data Set

> This dataset is a synthetic dataset. No real business data is used.

**Terminology Table**

| Term       | Definition                                                                               |
| ---------- | ---------------------------------------------------------------------------------------- |
| NR         | Not recommended                                                                          |
| PF         | Personalized feed                                                                        |
| GH         | Geo-handler; a module responsible for routing features based on user region              |
| CDS        | Compliance Detection System                                                              |
| DRT        | Data retention threshold; duration for which logs can be stored                          |
| LCP        | Local compliance policy                                                                  |
| Redline    | Flag for legal review (different from its traditional business use for 'financial loss') |
| Softblock  | A user-level limitation applied silently without notifications                           |
| Spanner    | A synthetic name for a rule engine (not to be confused with Google Spanner)              |
| ShadowMode | Deploy feature in non-user-impact way to collect analytics only                          |
| T5         | Tier 5 sensitivity data; more critical than T1‚ÄìT4 in this internal taxonomy            |
| ASL        | Age-sensitive logic                                                                      |
| Glow       | A compliance-flagging status, internally used to indicate geo-based alerts               |
| NSP        | Non-shareable policy (content should not be shared externally)                           |
| Jellybean  | Feature name for internal parental control system                                        |
| EchoTrace  | Log tracing mode to verify compliance routing                                            |
| BB         | Baseline Behavior; standard user behavior used for anomaly detection                     |
| Snowcap    | A synthetic codename for the child safety policy framework                               |
| FR         | Feature rollout status                                                                   |
| IMT        | Internal monitoring trigger                                                              |

**Sample Data**

| feature_name                                                  | feature_description                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Curfew login blocker with ASL and GH for Utah minors          | To comply with the Utah Social Media Regulation Act, we are implementing a curfew-based login restriction for users under 18. The system uses ASL to detect minor accounts and routes enforcement through GH to apply only within Utah boundaries. The feature activates during restricted night hours and logs activity using EchoTrace for auditability. This allows parental control to be enacted without user-facing alerts, operating in ShadowMode during initial rollout. |
| PF default toggle with NR enforcement for California teens    | As part of compliance with California’s SB976, the app will disable PF by default for users under 18 located in California. This default setting is considered NR to override, unless explicit parental opt-in is provided. Geo-detection is handled via GH, and rollout is monitored with FR logs. The design ensures minimal disruption while meeting the strict personalization requirements imposed by the law.                                                               |
| Child abuse content scanner using T5 and CDS triggers         | In line with the US federal law requiring providers to report child sexual abuse content to NCMEC, this feature scans uploads and flags suspected materials tagged as T5. Once flagged, the CDS auto-generates reports and routes them via secure channel APIs. The logic runs in real-time, supports human validation, and logs detection metadata for internal audits. Regional thresholds are governed by LCP parameters in the backend.                                       |
| Content visibility lock with NSP for EU DSAS                  | To meet the transparency expectations of the EU Digital Services Act, we are introducing a visibility lock for flagged user-generated content labeled under NSP. When such content is detected, a soft Softblock is applied and GH ensures enforcement is restricted to the EU region only. EchoTrace supports traceability, and Redline status can be triggered for legal review. This feature enhances accountability and complies with Article 16’s removal mechanisms.        |
| Jellybean-based parental notifications for Florida regulation | To support Florida's Online Protections for Minors law, this feature extends the Jellybean parental control framework. Notifications are dispatched to verified parent accounts when a minor attempts to access restricted features. Using IMT, the system checks behavioral anomalies against BB models. If violations are detected, restrictions are applied in ShadowMode with full audit logging through CDS. Glow flags ensure compliance visibility during rollout phases.  |
| Unified retention control via DRT & CDS                       | Introduce a data retention feature using DRT thresholds, ensuring automatic log deletion across all regions. CDS will continuously audit retention violations, triggering EchoTrace as necessary. Spanner logic ensures all platform modules comply uniformly.                                                                                                                                                                                                                    |
| NSP auto-flagging                                             | This feature will automatically detect and tag content that violates NSP policy. Once flagged, Softblock is applied and a Redline alert is generated if downstream sharing is attempted.                                                                                                                                                                                                                                                                                          |
| T5 tagging for sensitive reports                              | When users report content containing high-risk information, it is tagged as T5 for internal routing. CDS then enforces escalation. The system is universal and does not rely on regional toggles or GH routes.                                                                                                                                                                                                                                                                    |
| Underage protection via Snowcap trigger                       | Snowcap is activated for all underage users platform-wide, applying ASL to segment accounts. Actions taken under this logic are routed to CDS and monitored using BB to identify deviations in usage.                                                                                                                                                                                                                                                                             |
| Universal PF deactivation on guest mode                       | By default, PF will be turned off for all uses browsing in guest mode.                                                                                                                                                                                                                                                                                                                                                                                                            |
| Story resharing with content expiry                           | Enable users to reshare stories from others, with auto-expiry after 48 hours. This feature logs resharing attempts with EchoTrace and stores activity under BB.                                                                                                                                                                                                                                                                                                                   |
| Leaderboard system for weekly creators                        | Introduce a creator leaderboard updated weekly using internal analytics. Points and rankings are stored in FR metadata and tracked using IMT.                                                                                                                                                                                                                                                                                                                                     |
| Mood-based PF enhancements                                    | Adjust PF recommendations based on inferred mood signals from emoji usage. This logic is soft-tuned using BB and undergoes quiet testing in ShadowMode.                                                                                                                                                                                                                                                                                                                           |
| New user rewards via NR profile suggestions                   | At onboarding, users will receive NR-curated profiles to follow for faster network building. A/B testing will use Spanner.                                                                                                                                                                                                                                                                                                                                                        |
| Creator fund payout tracking in CDS                           | Monetization events will be tracked through CDS to detect anomalies in creator payouts. DRT rules apply for log trimming.                                                                                                                                                                                                                                                                                                                                                         |
| Trial run of video replies in EU                              | Roll out video reply functionality to users in EEA only. GH will manage exposure control, and BB is used to baseline feedback.                                                                                                                                                                                                                                                                                                                                                    |
| Canada-first PF variant test                                  | Launch a PF variant in CA as part of early experimentation. Spanner will isolate affected cohorts and Glow flags will monitor feature health.                                                                                                                                                                                                                                                                                                                                     |
| Chat UI overhaul                                              | A synthetic codename for the child safety policy framework                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Regional trial of autoplay behavior                           | Enable video autoplay only for users in US. GH filters users, while Spanner logs click-through deltas.                                                                                                                                                                                                                                                                                                                                                                            |
| South Korea dark theme A/B experiment                         | A/B test dark theme accessibility for users in South Korea. Rollout is limited via GH and monitored with FR flags.                                                                                                                                                                                                                                                                                                                                                                |
| Age-specific notification controls with ASL                   | Notifications will be tailored by age using ASL, allowing us to throttle or suppress push alerts for minors. EchoTrace will log adjustments, and CDS will verify enforcement across rollout waves.                                                                                                                                                                                                                                                                                |
| Chat content restrictions via LCP                             | Enforce message content constraints by injecting LCP rules on delivery. ShadowMode will initially deploy the logic for safe validation. No explicit mention of legal requirements, but privacy context is implied.                                                                                                                                                                                                                                                                |
| Video upload limits for new users                             | Introduce limits on video uploads from new accounts. IMT will trigger thresholds based on BB patterns. These limitations are partly for platform safety but without direct legal mapping.                                                                                                                                                                                                                                                                                         |
| Flag escalation flow for sensitive comments                   | A flow that detects high-risk comment content and routes it via CDS with Redline markers. The logic applies generally and is monitored through EchoTrace, with no mention of regional policies.                                                                                                                                                                                                                                                                                   |
| User behavior scoring for policy gating                       | Behavioral scoring via Spanner will be used to gate access to certain tools. The feature tracks usage and adjusts gating based on BB divergence.                                                                                                                                                                                                                                                                                                                                  |
| Minor-safe chat expansion via Jellybean                       | We’re expanding chat features, but for users flagged by Jellybean, certain functions (e.g., media sharing) will be limited. BB and ASL will monitor compliance posture.                                                                                                                                                                                                                                                                                                           |
| Friend suggestions with underage safeguards                   | New suggestion logic uses PF to recommend friends, but minors are excluded from adult pools using ASL and CDS logic. EchoTrace logs interactions in case future policy gates are needed.                                                                                                                                                                                                                                                                                          |
| Reaction GIFs with embedded filtering                         | Enable GIFs in comments, while filtering content deemed inappropriate for minor accounts. Softblock will apply if a flagged GIF is used by ASL-flagged profiles.                                                                                                                                                                                                                                                                                                                  |
| Longform posts with age-based moderation                      | Longform post creation is now open to all. However, moderation for underage authors is stricter via Snowcap.                                                                                                                                                                                                                                                                                                                                                                      |
| Custom avatar system with identity checks                     | Users can now design custom avatars. For safety, T5 triggers block adult-themed assets from use by underage profiles. Age detection uses ASL and logs flow through GH.                                                                                                                                                                                                                                                                                                            |

### Additional Information

Due to time constraints, participants may focus on identifying the following regulations:

1. EU Digital Service Act [DSA](https://en.wikipedia.org/wiki/Digital_Services_Act)
2. California state law - [Protecting Our Kids from Social Media Addiction Act](https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202320240SB976)
3. Florida state law - [Online Protections for Minors](https://www.flsenate.gov/Session/Bill/2024/3)
4. Utah state law - [Utah Social Media Regulation Act](https://en.wikipedia.org/wiki/Utah_Social_Media_Regulation_Act)
5. US law on reporting child sexual abuse content to NCMEC - [Reporting requirements of providers](https://www.law.cornell.edu/uscode/text/18/2258A)

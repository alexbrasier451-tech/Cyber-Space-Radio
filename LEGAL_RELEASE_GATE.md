# UK pre-release legal gate

**Status revised 17 August 2026:** local-only Phase 1 development and bounded
source evaluation may proceed. Public marketplace distribution remains subject
to the local-client checklist below. Hosted collection, content-bearing sync,
remote reporting, and federation remain **NO-GO** pending their separate gate.

This is an engineering review, not legal advice or approval. It assumes a UK
operator. Monitoring sources or people in other countries can trigger their
laws as well, so “across the web” needs jurisdiction-specific advice before it
can be a release claim.

Releasing a local application and operating a hosted monitoring service are
different. Phase 1 is the former: the app connects from the user's device
directly to a public source, processes locally, and sends no listening data to
Cyber Space Radio infrastructure. On those stated facts, the publisher is not
expected to act as controller or processor for the user's listening corpus. The
local operator determines the purpose and controls the records; purely personal
or household activity may be outside UK GDPR, while professional use may make
that user or organisation the controller.

The publisher remains responsible for any separate information it actually
receives, such as support correspondence, store transactions, website logs, or
diagnostics. This allocation must be re-evaluated if the real implementation
adds telemetry, accounts, cloud backup under publisher control, remote push,
sync, a proxy, hosted reports, or federation. Controller status depends on the
actual purposes and means, not product labels or encryption alone.

Primary guidance:

- [ICO: controllers and processors](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/controllers-and-processors/controllers-and-processors/what-are-controllers-and-processors/)
- [ICO: domestic-purposes exemption](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/exemptions/a-guide-to-the-data-protection-exemptions/)
- [ICO: privacy in the product design lifecycle](https://ico.org.uk/privacy-design)

## 0. Local-only Phase 1 boundary

The legal assessment relies on all of these facts remaining true:

- there is no Cyber Space Radio account, ingestion server, proxy, cloud
  database, listening telemetry, hosted alert, or remote reporting service;
- messages travel directly from the public source to the installed station;
- source selection, classification, matching, notification, encryption,
  retention, reporting, deletion, and STOP happen locally;
- project infrastructure never receives message content, event identifiers,
  author evidence, watch phrases, matches, reports, source history, or listening
  state;
- unmatched content expires from bounded memory and matched content is retained
  only as authenticated ciphertext on that device;
- crash reports and support bundles are structurally incapable of including
  listening data;
- any Windows localhost UI binds only to loopback and accepts no LAN or Internet
  connection; and
- Android notifications are generated locally without a content-bearing remote
  push service.

An encrypted payload routed through a project server would still be a new data
flow and is not permitted by this boundary. Generic software updates may use a
distribution service only when update traffic is separated from listening data
and cannot reveal sources, watches, matches, or history.

### Local-client distribution checklist

- [ ] Network tests prove that listening data has no project-operated egress
      path during normal use, errors, crashes, notifications, export, backup,
      STOP, purge, update, or uninstall.
- [ ] The app's privacy notice says what remains local and separately identifies
      any support, store, website, update, or optional diagnostic data.
- [ ] Diagnostics are off by default or content-free by construction; message
      text, event IDs, watch terms, source history, and decrypted records cannot
      enter them.
- [ ] Device and OS backup behaviour is documented; any included app records are
      already encrypted and remain subject to deletion limitations.
- [ ] Local expiry, exact deletion, complete purge, passphrase-loss reset, STOP,
      and uninstall behaviour pass end-to-end tests.
- [ ] Ordinary seven-day expiry, explicit message/topic Keep, Unkeep, the
      100 MiB default hard per-device capacity, protected-item behaviour, and
      storage-full refusal are accurately disclosed and pass boundary tests.
- [ ] Enabled sources use their public supported interface, stay within recorded
      limits, back off on failure, and stop on denial or operator request.
- [ ] User documentation distinguishes private household use from professional
      or organisational use and does not promise universal legal clearance.
- [ ] App-store privacy and data-safety declarations match the tested binary and
      included SDKs.
- [ ] Inspecting a Nostr signal is entirely local. Any external viewer is an
      operator-configured HTTPS destination, requires explicit confirmation,
      receives only an encoded event reference, and is described as a separate
      third-party disclosure.

Sections 1-5 below describe the wider risks and become directly applicable to
the publisher wherever it actually receives or controls personal information.
They are also guidance for professional station operators. They do not convert
the publisher into controller of a corpus it never receives merely because the
software is capable of local processing.

## 1. Personal information and profiling

An entry URL, title, author name, online identifier, or a report connecting a
person with an idea can be personal information. Filtering posts by ideas may
also infer opinions or interests. Topics involving politics, religion, health,
sexuality, ethnicity, trade-union membership, genetics, or biometrics can
involve special-category information with additional legal requirements.

The fact that a post is publicly available does not remove data-protection
obligations or imply agreement to unrelated collection and profiling. The ICO
specifically warns that blanket collection from public online sources can be
unfair, non-transparent, and contrary to data minimisation.

Before operation, the named controller must:

- write a specific, legitimate purpose that excludes identity inference,
  individual scoring, targeting, eligibility decisions, and harassment;
- identify and document an Article 6 lawful basis for every processing purpose;
- if relying on legitimate interests, complete the purpose, necessity, and
  balancing tests in a Legitimate Interests Assessment;
- prevent special-category and children's information from entering the system
  unless counsel confirms a valid additional condition and safeguards;
- complete a Data Protection Impact Assessment before large-scale, systematic,
  invisible, or profiling-related monitoring;
- publish privacy information explaining sources, purposes, lawful basis,
  recipients, retention, rights, contact details, and complaint routes;
- provide that information within the applicable period. ICO guidance says the
  latest point for indirectly obtained information is generally one month,
  subject to the circumstances and any valid exception;
- provide working access, objection, correction, restriction, and erasure
  procedures, including deletion across replicas and backups where applicable;
- document a short, justified retention period and verify automatic deletion;
- perform the ICO data-protection-fee self-assessment and pay if required; and
- keep processing records, security responsibilities, incident procedures, and
  any controller/processor or international-transfer arrangements.

Primary guidance:

- [ICO: personal information](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/personal-information-what-is-it/what-is-personal-data/what-is-personal-data/)
- [ICO: public-source transparency](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/individual-rights/the-right-to-be-informed/what-common-issues-might-come-up-in-practice/)
- [ICO: lawful basis](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/a-guide-to-lawful-basis/)
- [ICO: legitimate interests](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/legitimate-interests/what-is-the-legitimate-interests-basis/)
- [ICO: DPIAs](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/accountability-and-governance/guide-to-accountability-and-governance/data-protection-impact-assessments/)
- [ICO: data minimisation](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/)
- [ICO: storage limitation](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/storage-limitation/)
- [ICO: data protection fee](https://ico.org.uk/for-organisations/data-protection-fee/data-protection-fee/)

## 2. Copyright, licences, and database rights

Public access does not mean unrestricted reuse. Web writing and databases may
be protected automatically. The UK's text-and-data-mining exception described
by the Intellectual Property Office is limited to computational analysis for
non-commercial research where the researcher already has lawful access. It is
not a general commercial-product permission. Database rights and source terms
need separate consideration, including the risk from repeated or systematic
extraction.

Before operation:

- maintain an approved-source register containing the feed/API URL, owner,
  applicable licence and terms, permitted purpose, attribution requirement,
  polling limit, review date, and opt-out contact;
- use an official feed or supported API rather than scraping ordinary pages;
- obtain a licence or written permission when the intended use is not clearly
  covered, especially for commercial operation;
- do not bypass logins, paywalls, rate limits, technical controls, exclusions,
  or access revocation;
- store digests and source references instead of copied post bodies wherever
  possible; and
- remove a source promptly when permission is withdrawn or terms change.

Primary guidance:

- [GOV.UK: copyright overview](https://www.gov.uk/copyright)
- [Intellectual Property Office: copyright exceptions](https://www.gov.uk/guidance/exceptions-to-copyright)
- [GOV.UK: sui generis database rights](https://www.gov.uk/guidance/sui-generis-database-rights)

## 3. Authorised access and network conduct

The Computer Misuse Act 1990 makes unauthorised access and certain
unauthorised acts criminal offences. This project must stay within documented,
operator-approved public feeds and APIs. It must never evade access controls,
probe unrelated systems, follow peer-supplied URLs, spread software, overload a
service, or continue after access is expressly withdrawn.

The current local prototype performs no crawling, discovery, installation, or
peer federation. Continuous polling is limited to one request per configured
feed every 15 minutes or slower, requires an operator contact in its User-Agent,
and should be reduced further whenever a source specifies a stricter policy.

Primary legislation:

- [Computer Misuse Act 1990](https://www.legislation.gov.uk/ukpga/1990/18/contents)

## 4. Contacting people and PECR

The prototype must not automatically contact, advertise to, recruit, rank, or
target people whose posts match. If a future product sends promotional email,
texts, direct messages, or similar electronic communications, PECR and data
protection rules can apply. A public address is not permission to market to it.

Primary guidance:

- [ICO: electronic and telephone marketing](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/electronic-and-telephone-marketing/)

## 5. Security and encryption

Encryption is an appropriate security control in many deployments, but it does
not provide a lawful basis or anonymise information when the operator holds the
key. Security must be proportionate to the actual data and risk and include
minimisation, access control, key management, availability, incident response,
and regular testing—not merely “more encryption.”

The proposed federation remains disabled until mutual TLS, per-node identity,
replay protection, bounded queues, certificate rotation and revocation, the
fail-closed operating lease, and emergency-stop tests pass in the intended
hosting environment.

Primary guidance:

- [ICO: data security](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/security/a-guide-to-data-security/)
- [ICO: encryption and data protection](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/security/encryption/encryption-and-data-protection/)

## 6. Hosted and federated release checklist

This checklist applies only if the product adds a backend, publisher-controlled
collection, content-bearing sync, hosted reporting, multi-tenancy, or
federation. Every applicable item requires named evidence and an owner. A blank
or unsupported “not applicable” blocks that operating mode.

- [ ] Product purpose, prohibited uses, controller, processors, and supported
      jurisdictions are named.
- [ ] A UK solicitor with data-protection and IP experience has reviewed the
      real operating model, not only this source code.
- [ ] The Article 6 basis and any Article 9 condition are documented.
- [ ] The LIA and DPIA are complete and approved.
- [ ] The privacy notice and rights-request contact are live and tested.
- [ ] Exact-source deletion and full deletion work across logs, replicas,
      queues, backups, and federation nodes.
- [ ] The retention schedule has evidence supporting each period.
- [ ] The ICO fee self-assessment is complete.
- [ ] Every enabled source has a current approved-source record and licence or
      other documented permission.
- [ ] No source requires bypassing access controls, terms, or rate limits.
- [ ] Automated outreach and decisions about people are technically disabled.
- [ ] Special-category and children's information controls are tested.
- [ ] Hosting, processor contracts, international transfers, and breach
      procedures are approved.
- [ ] The encryption, identity, lease, emergency-stop, abuse, partition,
      deletion, and resource-bound tests in `FEDERATION_DESIGN.md` all pass.
- [ ] The user-facing documentation describes limitations, opt-out, deletion,
      security contact, and the fact that a match is not proof about a person.

Until all applicable items pass, keep the no-backend boundary, do not enable the
new hosted/federated operating mode, and do not present the product as
universally legally cleared.

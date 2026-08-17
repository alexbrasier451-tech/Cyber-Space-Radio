# Cyber Space Radio contact

Project operator contact: **[cyberspaceradio@proton.me](mailto:cyberspaceradio@proton.me)**

Display name: **Cyber Space Radio**
Recorded: **2026-08-17**

## Purpose

This mailbox is the public contact route intended for source operators,
platform operators, security reporters, and people raising an access,
deletion, or courtesy concern about Cyber Space Radio. It is not a destination
for listened-to messages, telemetry, watch phrases, event identifiers, or
station history.

The project operator contact is different from a source owner's contact. For
example, `support@bsky.app` belongs to Bluesky; it does not identify or reach
the Cyber Space Radio operator. Source-owner and project-operator contacts are
therefore stored in separate fields in the approved-source register.

## Publication state

**Published, anonymously reachable, mailbox-verified, and client-exposed.**
The initial Phase 0 package was pushed to the public repository in commit
`1bfa0ff` on 2026-08-17.

The intended public page is:

<https://github.com/alexbrasier451-tech/Cyber-Space-Radio/blob/main/CONTACT.md>

On 2026-08-17 the raw file was fetched without a signed-in session and returned
successfully with the exact `mailto:cyberspaceradio@proton.me` route. A local,
synthetic WebSocket upgrade also confirmed that the bounded client emits the
exact `X-Cyber-Space-Radio-Operator-Contact` header once without logging or
persisting the address. On the same date, the project operator confirmed that
a message sent from an independent mailbox arrived successfully and that a
reply was sent from this Proton mailbox. Message content, addresses other than
the public project contact, and credentials were not recorded.

The composite contact state is now `published-and-client-exposed`. This clears
the contact prerequisite for an explicitly authorised, bounded Jetstream
comparison invoked with
`--operator-contact mailto:cyberspaceradio@proton.me`; it does not enable
continuous listening or change any source row from `approved-disabled`.

## Handling

- Do not publish mailbox credentials, recovery information, or personal
  addresses in this repository.
- Review incoming operational requests before changing source access or local
  data. Stop a source promptly on a credible operator refusal or access denial.
- Do not ask correspondents to send private messages, user station data, or
  copies of collected content to this mailbox.
- If the address changes, update this file, every approved-source row, the
  bounded client configuration, and the public page together.

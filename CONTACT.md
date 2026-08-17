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

**Recorded locally; not yet evidenced as publicly published.** This file is in
the current local, untracked repository. Its existence here does not establish
that Bluesky, a relay operator, or the public can find it.

The intended public page is:

<https://github.com/alexbrasier451-tech/Cyber-Space-Radio/blob/main/CONTACT.md>

The public repository exists but was empty when this contact was recorded. The
URL above is therefore a publication target, not evidence that this file is
already online.

Before a live Jetstream trial, the project must:

1. push this file to the public repository's `main` branch;
2. fetch
   `https://raw.githubusercontent.com/alexbrasier451-tech/Cyber-Space-Radio/main/CONTACT.md`
   without a signed-in session, require an HTTP success response, and confirm
   it contains the exact `mailto:cyberspaceradio@proton.me` route;
3. send a test message from an independent mailbox, confirm it arrives in this
   mailbox, and send a reply so receive and reply capability are both checked;
4. run the bounded client's synthetic handshake test and confirm it emits the
   exact `X-Cyber-Space-Radio-Operator-Contact` header without logging or
   persisting the address; and
5. invoke the authorised Jetstream comparison with
   `--operator-contact mailto:cyberspaceradio@proton.me`.

After the push, re-check the public page through an unauthenticated route rather
than treating a successful Git operation as publication evidence. Until all
checks above are recorded, source rows use the contact status
`recorded-not-published` and remain `approved-disabled`. No external
publication or live source access is performed by this document update.

## Handling

- Do not publish mailbox credentials, recovery information, or personal
  addresses in this repository.
- Review incoming operational requests before changing source access or local
  data. Stop a source promptly on a credible operator refusal or access denial.
- Do not ask correspondents to send private messages, user station data, or
  copies of collected content to this mailbox.
- If the address changes, update this file, every approved-source row, the
  bounded client configuration, and the public page together.

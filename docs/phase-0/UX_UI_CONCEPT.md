# UX and UI concept

## Experience statement

The interface should feel like a quiet listening desk: focused, legible, and
calm enough that a rare signal matters. The radio metaphor supplies names and
atmosphere, but the interface always explains that it is observing approved
public Internet sources.
The first tuned channel is standalone public relay messages: events with no
recipient, group, reply, quote, or repost target.

Provide the complete station experience on Windows 11 and Android. The proposed
.NET MAUI foundation uses shared native navigation/view models with
platform-appropriate controls and explicit Windows/Android lifecycle and
security integrations. There is no localhost browser server or WebView store.
Each installation has its own sources, passphrase, encrypted store, and STOP
state; the phone is not a remote control for the desktop. This UI foundation
remains provisional until the physical Phase 0B gate passes.

## Navigation

| Area | Purpose |
|---|---|
| Now | Listening state, active stream connections, last event, source health, new-signal count, and separate non-identifying `Noise blocked` and `Oversized` counts. |
| Signals | Review source-attributed matches, explanations, and deletion actions. |
| Watches | Create ideas, alternative phrasings, exclusions, and thresholds; preview against fixtures. |
| Sources | Manage the explicit allowlist, permissions, courtesy policy, and health. |
| Data & deletion | Inspect retained fields, expiry, exact delete, source delete, and purge. |
| Settings | Operator contact, local paths, limits, diagnostics, and export. |
| Network | Hidden until Phase 3; later shows observer-specific node reachability. |

On phone, expose the primary areas through a compact bottom navigation or an
equally accessible native pattern. `Now`, `Signals`, and `STOP LISTENING` must
remain reachable without desktop-sized hover menus or precision pointing.

## First-run topic screen

After local passphrase setup and before the first Start, show a full-screen
question: **What would you like to listen for?** This is a friendly starting
point, not a mandatory profiling questionnaire.

Present large, multi-select topic cards in small labelled groups. The initial
starter set is:

- **People & relationships:** `Relationships & dating`, `Gossip & drama`, and
  `Friendship & family`;
- **Everyday life:** `Work & workplace`, `Money & cost of living`, and `Local
  happenings`;
- **Culture:** `Technology & internet culture` and `Games, media &
  entertainment`; and
- **Your own:** `Create a custom topic`.

Starter topics are local, editable watch templates rather than fixed editorial
categories. A card opens a short review sheet showing example concepts,
alternative phrasings, exclusions, breadth, and validation status. The operator
may remove concepts, add their own language, split a broad card into watches,
or rename it before continuing. `Keep future matches` remains off.

The bottom of the screen offers two equally understandable routes:

- **Review selected topics** creates local draft watches and then shows the
  exact watches that will be enabled when the operator deliberately starts
  listening; and
- **Skip and explore** enters Discovery with no active topic watch, so the
  operator can inspect the bounded volatile waterfall and create a watch later.

No topic is preselected. Opening or selecting a card makes no source request,
starts no listener, and creates no matched-message record. Watch configuration
stays on the device and never becomes telemetry. A template version that has
not passed the accepted precision/recall corpus gate is labelled `Preview only`
and cannot automatically persist or notify until validated.

### Create-your-own tutorial

Choosing `Create a custom topic` opens a skippable four-step tutorial. It is
also available later from `Watches` -> `Add topic` -> `Create your own`, and can
be replayed from Help.

1. **Describe the idea.** Ask for a plain-language sentence such as `People
   talking about difficult long-distance relationships`, not a person, account,
   or network address.
2. **Add ways people might say it.** Explain alternative phrasings with short
   editable examples such as `living apart`, `long-distance partner`, and
   `relationship across countries`.
3. **Say what should not count.** Explain exclusions as likely false matches,
   for example `long-distance running` or `business relationship`.
4. **Preview and tune.** Test locally against bundled synthetic examples and,
   when available, the current in-memory waterfall without saving it. Show
   which phrases contributed, which exclusion rejected an item, the threshold,
   and a simple breadth label: `Focused`, `Balanced`, or `Broad`.

The final review shows the watch name, included ideas, exclusions, threshold,
validation state, seven-day ordinary retention, and `Keep future matches: Off`.
`Save draft` never starts listening. `Enable when I start listening` is a
separate explicit choice. A custom watch can filter/highlight the volatile
Discovery view immediately, but automatic persistence and notification remain
locked until its matcher version satisfies the accepted evidence gate.

A `Validate for automatic saving` action opens a separate local promotion
wizard. It explains the 200-example/50-positive minimum, collects only
deliberately authored or labelled encrypted examples, freezes the watch and
development/held-out split before scoring, and shows precision and recall.
Passing promotes only that exact version; any later phrase, exclusion,
threshold, label, corpus, or matcher change visibly returns it to `Preview
only`. Bundled starter cards display their shipped evaluation version and the
same metrics instead of asking the operator to reproduce the product team's
corpus work.

Use inline explanations and a small `Why?` link rather than forcing the whole
tutorial on repeat users. All typed topic text, examples, exclusions, fixture
labels, and previews remain local and are cleared by watch deletion or station
reset according to their normal scope.

## Main screen: Listening desk

The default screen answers three questions immediately:

1. Is the station listening?
2. What is it listening for?
3. Did anything meaningful arrive?

It also makes the operating mode explicit:

- **Discovery:** a bounded live waterfall helps the operator understand what
  exists; unmatched content is volatile unless the operator explicitly keeps
  one valid item.
- **Tuned:** the waterfall remains available; topic matches enter the signal
  inbox or reports automatically, while another valid item enters only through
  an explicit local `Keep`.
- **Stopped:** source connections are closed, reconnect is disabled, and the
  volatile waterfall is cleared.

### Header

- Product name: `Cyber Space Radio`.
- Factual subtitle: `Public-source listening console`.
- The active-channel description remains precise, for example `Standalone
  public messages from approved relay streams`.
- Current state: Listening, Background limited, Paused, Stopped, Offline, or
  Degraded, using only states applicable to the current platform. After
  execution resumes, an unclosed session plus stale last-activity evidence may
  show `Coverage gap / previously suspended`; the app never claims it reported
  live while its process was not running.
- Separate encryption state: Locked or Unlocked. Listening cannot coexist with
  Locked.
- One persistent **STOP LISTENING** action.
- The stop action requires confirmation but no complex navigation.
- Stop never deletes records. It closes stream connections and schedules,
  prevents reconnects and outbound reports, clears volatile previews, locks
  persisted content, and leaves an obvious stopped state.
- A phone never says `Listening` merely because listening was requested. It
  shows the latest OS-permitted execution state and the last proven source
  activity time.
- After an explicit Start, Android may continue off-screen through a visible
  ongoing foreground-service notification. The notification shows the real
  state, last proven activity, and a prominent STOP action without exposing
  message text.

### Watch control

- One primary watch selector; hide it if only one watch exists.
- `Add from topics` reopens the same starter-topic catalogue without changing
  existing watches or starting listening.
- `Create your own` opens the manual-topic tutorial; experienced operators may
  skip directly to the editable watch form.
- A plain-language idea field.
- Alternative phrasing and exclusion editing behind a compact edit action.
- A threshold shown as both percentage and label, such as `72% - precision
  first`.
- The evaluation panel shows the accepted corpus gate explicitly: `Precision
  >= 85%` and `Recall >= 60%`, with per-source results and fixture counts.
- Prevent enabling durable reports for a matcher version that has not passed
  the precision and recall gate; discovery mode remains available.
- Preview shows known positive and negative fixtures before saving.

### Signal inbox

Signals is one unified inbox across all watches. Every new unlocked session
opens at `All topics`, newest first by the signal's first `observed_at` time,
with stable signal ID as the deterministic tie-breaker. A later relay duplicate,
additional topic match, or retention change updates the row without moving it
as though it were a newly observed signal.

Topic chips and a local multi-select filter let the operator narrow the view
without creating separate inboxes. Selected topic filters use `match any`
semantics by default, with source, retention state, and new/reviewed filters
available in the same local filter sheet. Clearing filters always returns to
the complete inbox.

Active filters, sort position, and scroll position may survive navigation only
within the current unlocked session. Lock, STOP, application restart, or station
reset clears that view state, so the next unlock returns to `All topics, newest
first`. Do not persist it in the database, browser storage, files, backups,
telemetry, or crash reports.

One deduplicated shout is one inbox row even when it matches several watches.
Show every matching topic as a compact chip, place overflow topics behind an
accessible `+N` control, and expose each topic's score and explanation in the
inspector. The unique signal count and local notification increment once per
shout, not once per topic. Filtering, sorting, and expanding chips perform no
network request and create no extra durable message copy.

A newly persisted signal starts as `New`. Opening the row marks it `Reviewed`
only after the station is unlocked and the local inspector has rendered
successfully. Merely displaying the row, receiving or tapping a locked
notification, previewing a deletion, or filtering the inbox does not mark it
reviewed. Because topics share one signal, review state applies to the whole
signal rather than to each topic chip.

`Mark as new` is available from the row menu and inspector and clears the local
review timestamp. It does not issue another notification, increment counts,
change a match, alter Keep/expiry, reorder the signal, or contact a source.
Review state survives ordinary restart as local signal metadata, remains
independent on Windows and Android, and disappears whenever the signal itself
is deleted.

The inbox also offers `Mark visible as reviewed`. Here, `visible` means every
currently `New` signal in the complete filtered result—not merely rows rendered
in the viewport or current pagination window. Before confirmation, show the
active filters and exact unique-signal count. Confirmation applies to the
previewed signal-ID snapshot only; a signal arriving or entering the filter
later remains `New`. The action is disabled at zero, never opens or decrypts
message bodies, and has no notification, matching, order, Keep, expiry, or
network effect.

Each row contains only:

- source title or a deliberately retained display excerpt, subject to the data
  decision;
- protocol and a compact provenance badge showing the relay/stream set; the
  initial Nostr values are `Damus`, `nos.lol`, and `Both`;
- stable event reference and public permalink when one exists;
- observed time;
- the strongest match percentage when one or more topics matched;
- topic chips plus a one-line strongest-match explanation, or `Kept manually`;
  and
- review state: `New` or `Reviewed`, plus a separate `Kept` or expiry badge.

`Keep` adds a manual protection reason to one signal. Every keep-enabled topic
that matched it contributes its own topic protection reason. The single signal
remains protected and non-expiring while at least one reason remains. A `Kept`
badge is visible in both the row and inspector; STOP and restart do not remove
it.

The inspector lists the reasons, for example `Kept manually`, `Relationships &
dating keeps future matches`, and `Gossip & drama keeps future matches`.
Removing one reason leaves the signal protected by the others. Removing the
final reason, after confirmation, starts a fresh seven-day expiry from that
time. Switching `Keep future matches` off on a topic affects later matches only;
removing that topic's reason from existing signals is a separate action with an
item/byte preview.

Selecting a row opens a signal inspector with the original link, retained
fields, retention mode, expiry, and delete action. Topic matches also show
matching concepts, score, explanation, and matcher version separately for every
matched watch; manually kept non-matches do not invent those fields. Do not show
inferred personality, belief, affiliation, or identity.

The inspector renders the retained Nostr message and provenance entirely from
local data. It performs no profile lookup, link preview, media fetch, relay
query, or external viewer request. A separate `Open externally` action appears
only when the operator has configured a Nostr viewer. The confirmation names
that viewer and explains that it will receive the event reference and ordinary
browser connection metadata. Cancelling leaves the device-local view unchanged.
New installations and reset stations have no viewer configured, so the action
is absent rather than disabled or promoted during onboarding.

Persisted signal text is decrypted only for an unlocked local session. Locked
records show source, time, expiry, and an `Unlock to view message` state without
placing plaintext in browser storage or URL parameters. Protocol public keys,
when required for verification, stay in technical detail and are never
presented as a resolved identity.

### Live waterfall

- Visually separate volatile shouts from the durable signal inbox.
- Show `Not saved` beside every waterfall item and explain its expiry.
- Show at most 280 user-perceived Unicode characters in the collapsed card,
  ending at a grapheme boundary so emoji and combined characters are not split.
  `Expand` reveals the complete accepted message in place from local memory;
  `Collapse` returns to the preview. Neither action contacts a relay, link,
  media host, profile service, or external viewer.
- Show a compact `Damus`, `nos.lol`, or `Both` provenance badge. If the same
  verified event later arrives through the other relay, update the existing
  item to `Both` without adding a row or incrementing the activity count.
- Retain the most recent 100 items or ten minutes, whichever limit removes an
  unkept item first. Display both limits in the waterfall help text.
- Provide `Clear waterfall` without a destructive-data warning because no
  durable record is affected.
- Provide `Keep` on each valid waterfall item. It encrypts and moves that exact
  item to Signals even when no topic matched, subject to the local capacity.
  Move it only after the durable write succeeds. Failure shows
  `Not saved - storage full` and leaves the item volatile under the ordinary
  100-item/ten-minute limits.
- Topic matches leave the waterfall through the privacy projection and appear
  in the signal inbox as durable records.
- Mode changes affect future events only; they do not save older previews.
- Obvious spam/flood events do not enter the waterfall. `Noise blocked` shows
  an aggregate count and opens the volatile Junk drawer.
- A complete event envelope over 65,536 UTF-8 bytes or decoded body over 16,384
  UTF-8 bytes does not enter the waterfall. `Oversized` shows a separate
  aggregate count, may break it down only as `Envelope` or `Body`, and opens a
  short explanation of the safety limits; it exposes no message, identity,
  source, or folder.

### Volatile Junk drawer

- Open it from the `Noise blocked` count; it is not a durable inbox or primary
  navigation destination.
- Show no more than 50 items and no item older than five minutes.
- Label every item `Not saved` and show its spam-rule explanation plus
  `Damus`, `nos.lol`, or `Both` provenance.
- `Restore once` returns a valid item to the live waterfall and normal matcher
  for the current session. Explain that this does not trust an author, relay, or
  future message.
- Malformed events, invalid signatures, structurally excluded conversations,
  and `Oversized` inputs never appear and cannot be restored. Oversized content
  is not spam and does not increment `Noise blocked`.
- Provide `Clear Junk`; STOP and restart also clear it without confirmation
  because it contains no durable records.

### Source health

Show health as operational evidence, for example:

- `Nostr / Relay A: connected; last event 2 seconds ago`
- `AT Jetstream: reconnecting in 30 seconds`
- `RSS / Example Lab: rate limited until 14:30`

Avoid a global `healthy/unhealthy` claim when individual sources differ.

## Secondary screens

### Watches

- List enabled and paused watches.
- Show last evaluation date and precision/recall fixture result.
- Editing a watch creates a new evaluation version; existing signals retain the
  version that produced them.
- Topic definitions persist until deleted; Pause changes activity, not
  retention. `Keep future matches` defaults off and applies only to later
  matches. A separate `Apply to existing matches` flow previews item/byte counts
  before changing existing records to kept.
- Switching `Keep future matches` off also affects only later matches. Offer a
  separate `Remove this topic's keep from existing signals` action with
  protected-item and byte counts. Signals that retain another manual or topic
  reason remain non-expiring; only the final reason removal starts a fresh
  seven-day expiry.
- `Delete topic` opens a preview grouped as `Remains under other topics`,
  `Remains because manually kept`, `Ordinary signals deleted`, and `Protected
  signals deleted`, with item and estimated-byte counts. The confirmation names
  the topic and separately acknowledges protected deletions. Survivors lose
  only that topic's chip, match decision, and keep reason. Cancellation changes
  nothing.
- Disallow saving a watch with no meaningful terms or no labelled positive
  examples once the evaluation gate is enabled.

### Sources

- Rows come from the approved-source register, never from network discovery.
- Show source, protocol, event filter, replay window, rate ceiling,
  owner/contact, terms review date, last success, and enabled state.
- `Remove source` stops that connection and future replay while retaining
  historical provenance. It then offers the separate action
  `Delete this source's data`.
- Received content can never create a source row.

### Data & deletion

- Show exactly which fields are stored and why.
- Show encryption/unlock state, key version, seven-day ordinary expiry, kept
  item count, and topic retention modes without displaying key material.
- Show current retention, next expiry run, and the per-device capacity meter:
  used/configured bytes, ordinary and kept shares, warnings at 80% and 95%, and
  `Storage full` state.
- Default capacity is 100 MiB. Increasing it requires available-space preflight;
  lowering it previews expired/oldest-unkept pruning and is rejected when kept
  data plus transaction headroom cannot fit.
- At capacity, the UI states that expired and oldest unkept signals may be
  removed, kept items are protected, and volatile listening can continue even
  though new durable saves are paused.
- Exact deletion uses the public entry URL or signal ID.
- By-source deletion previews counts for signals that will be deleted and
  multi-source signals that will remain with the selected provenance removed.
  For example, deleting Damus data changes `Both` to `nos.lol` and deletes only
  Damus-only signals.
- The preview separately counts ordinary Damus-only deletions, Kept Damus-only
  deletions, and `Both` records that will survive. If Kept items are affected,
  require a confirmation naming Damus and the protected-item count. A surviving
  Kept `Both` item remains Kept as `nos.lol`.
- Exact signal deletion removes the complete signal regardless of whether its
  badge is `Damus`, `nos.lol`, or `Both`.
- Explicit deletion previews and names any `Kept` records affected; Keep protects
  against automatic expiry/eviction, not a confirmed exact delete, source-data
  delete, reset, or purge.
- Purge requires the operator to type `PURGE`; it deletes local content but not
  source configuration unless separately selected.
- `Forgot passphrase` never offers recovery. It explains that existing saved
  messages cannot be recovered and offers only `Cancel` or the separate
  `PURGE AND RESET KEY` flow.
- Key reset previews affected encrypted records, requires the exact confirmation
  phrase, deletes ciphertext and the wrapped key, and returns to first-run key
  creation. It cannot claim to delete offline backup media.

### Future network view

- Show direct observation: `London cannot reach Leeds since 14:02`.
- Never display `Leeds is dead` based on a timeout.
- Separate local stop from future **STOP NETWORK**.
- The emergency network action explains the maximum lease-expiry delay and does
  not delete evidence.

## Key flows

### First run

1. Explain public-source-only operation in one screen.
2. Capture the operator contact and explain what connection metadata an
   approved relay may observe.
3. Import or create approved source rows.
4. Create and confirm the manual passphrase without storing it.
5. Show **What would you like to listen for?** with no selection, then either
   review editable local draft watches or choose `Skip and explore`.
6. Arrive at the listening desk with all connections off; the chosen route sets
   Tuned or Discovery as the requested mode but does not start it.
7. Unlock locally and run a bounded, explicitly started session.
8. Preview and tune draft watches against synthetic fixtures and current
   in-memory items; only a separately validated watch can auto-save or notify.
9. Continue in Discovery or Tuned mode, or stop entirely.

### Review a signal

1. Open a new signal.
2. Read why it matched.
3. Open the public source in a new browser tab if desired.
4. Keep, dismiss, or delete it.
5. Optionally add an exclusion from selected terms; preview the effect before
   applying it to the watch.

### Stop

1. Press STOP LISTENING.
2. Confirm `Close source connections, stop polling, and prevent reconnects?`.
3. UI immediately changes to Stopped.
4. The scheduler and outbound gates prove they are closed.
5. The volatile waterfall is cleared; persisted topic matches remain.
6. Saved message text locks and usable in-memory content keys are discarded.
7. Resume requires a fresh manual passphrase unlock and separate start action.
8. On Android, STOP also terminates the foreground service, removes its ongoing
   notification, and prevents automatic restart by alarms, boot receivers, or
   schedulers.

## States that must be designed

- First run with no sources or watches.
- Listening with no signals.
- Discovery mode with an empty waterfall and with active ephemeral shouts.
- Tuned mode with activity but no topic matches.
- Listening with new signals.
- Paused by the operator.
- Stopped by the emergency action.
- Degraded because one or more sources failed.
- Entirely offline.
- Locked after launch, wrong passphrase, unlock throttled, and key unavailable.
- Lost passphrase, reset preview, reset cancelled, reset complete, and reset
  failed before new-key creation.
- Source rate-limited or credentials missing.
- Phone background work permitted, restricted, expired, or retrospectively
  identified as a coverage gap after suspension/process removal.
- Phone resumed after a background gap, with the gap visible and bounded catch-
  up policy explained.
- Lock-screen and app-switcher snapshot with message text redacted.
- Empty result after filters.
- Record expired between list and detail views.
- Delete complete, delete failed, and purge preview.

## Visual direction

- Modern field instrument, not a neon hacker dashboard.
- Deep graphite or warm paper surfaces with a restrained cyan signal accent,
  amber caution, and red reserved exclusively for stop/destructive actions.
- High-information density with generous reading space; avoid decorative gauges.
- Use a monospaced face only for IDs and timestamps, never entire paragraphs.
- Motion is limited to state transitions; nothing pulses continuously.
- The original source remains a normal, visible link rather than a hidden icon.
- Collapsed waterfall text is a 280-character local preview, not a separately
  retained excerpt. Expansion remains inside the app and uses the same volatile
  item.
- Nostr event references remain locally viewable. `Open externally` is a
  clearly labelled user action, never an automatic redirect, preview, or
  requirement for reading a retained message.

## Accessibility and trust

- Meet WCAG 2.2 AA for contrast, keyboard access, focus, names, errors, and
  reduced motion.
- Do not encode match or health state by colour alone.
- Every icon action has a visible or accessible text label.
- Scores always include an explanation and matcher version.
- Times show timezone and offer an exact timestamp.
- The UI says `matched text`, `source reported`, or `station observed`, never
  `this person believes`.
- All destructive actions state their exact scope and recovery implications.
- Notifications and lock-screen previews contain counts or a generic signal
  notice, never matched message text. The accepted match alert is `New signal
  found`; it omits source, author, score, explanation, and event reference.
- Tapping a match alert opens the locked Signals screen and requires the manual
  passphrase before any retained plaintext or source evidence is shown.
- App-switcher snapshots redact the waterfall, saved message text, and source
  evidence while the station is locked or leaving the foreground.

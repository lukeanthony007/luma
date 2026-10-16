---
name: luma-inbox
description: Create structured messages and worksheets for the user, integrate responses, and clear handled inbox items.
---

# Use the inbox

Use when a conversation needs a richer written interface, an authorized background task needs the person's attention, or the user returns to pending interactions. Follow the owning workspace's working agreement. The default location is `inbox/`, a temporary human-facing queue; durable understanding belongs in the wiki.

## Prepare an interaction

A fresh Luma workspace has no `inbox/`. Create it when there is an actual interaction to write. When checking for pending items, an absent directory means there is no queue to inspect; do not create one just to check it. Do not add placeholders or usage READMEs.

Write one Markdown file per interaction with a distinct filename. Include the sender, date, relevant topic, purpose and requested response. Link to current knowledge rather than copying whole pages. Fit the structure to the conversation: current understanding, assumptions to examine, alternatives, questions and space for observations. Explain why questions matter and distinguish suggested answers from actual responses.

The person may answer in the file, in chat or both. Inspect the current item and reconcile those responses together. Preserve existing user edits instead of regenerating over them.

## Resume and clear

1. Inspect the relevant items and current responses when the user returns. A session starting does not resolve every message. Informational messages may be acknowledged; unanswered questions remain pending unless dismissed or superseded.
2. Develop any needed clarification. Use [luma-wiki](../luma-wiki/SKILL.md) to integrate useful understanding, decisions, corrections and ongoing obligations into the wiki. Preserve attribution and evidence where needed; an exchange with no lasting significance need not produce a knowledge entry.
3. Verify durable updates were saved. Move necessary supporting material to an appropriate durable source location and repair links before deleting its temporary inbox copy.
4. Reread the item before cleanup. Clear only the handled item and exclusively temporary attachments. Preserve new edits, unresolved parts, shared sources and other messages. If interrupted, check what was already integrated before resuming so it is not duplicated.

Dismissed or superseded items can be cleared after preserving anything still needed. Never clear the whole inbox simply because the person returned. Live items and attachments are excluded from this public foundation repository. Do not force-stage them.

## Background handoffs

An already authorized background agent or cron job may leave a review or worksheet for the next conversation. Identify the originating task or run and avoid repeating an unresolved request. Other agents still need scoped authority to write to this workspace's inbox.

This skill defines a file-based practice. It does not install a scheduler, watcher, notification service, form renderer or transactional queue. Concurrent delivery, retry identifiers and richer interface behavior remain implementation choices; the folder's presence does not activate background work.

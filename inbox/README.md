# Inbox

The inbox is a temporary, human-facing interaction queue. An agent can leave a message, a set of questions or a structured worksheet here when a richer interface would help the person and agent develop understanding together. The person can work through it in Obsidian or another editor, then continue the conversation with their agent.

Durable understanding belongs in the [wiki](../wiki/index.md). Inbox items exist to support an interaction and are cleared once that interaction has been handled. This README documents the queue and is not itself a message to clear.

## Writing an item

Use one Markdown file per interaction with a distinct filename, so separate agents or runs do not overwrite each other's messages. Include the sender, creation date, relevant project or topic, the reason for the message and what response would be useful. Link to existing knowledge or source material rather than copying whole pages into the queue.

Choose the structure to fit the conversation. A worksheet might present the current understanding, questions about assumptions, alternatives to compare, and space for the person's observations or corrections. Explain why the questions matter. Distinguish the agent's suggested answers from the person's actual responses. Structured interaction should help clarify meaning, not impose a form for every conversation.

The person may answer in the file, in chat, or through both. When resuming, inspect the current item and reconcile the responses together; do not assume a response in one place invalidates an edit in the other.

## Handling and clearing

1. When the person returns, review pending items relevant to the conversation. A session starting does not by itself resolve every item.
2. Read their response and develop any needed clarification together. An informational message may be acknowledged without requiring a worksheet response. A question awaiting an answer remains pending unless the person dismisses it or it is explicitly superseded.
3. Integrate useful understanding, decisions, corrections and ongoing obligations into the appropriate wiki pages. Retain attribution and supporting evidence where needed. Do not copy the entire exchange into the wiki merely to preserve a transcript, and do not fabricate a knowledge update for an item with no lasting significance.
4. Check that the durable changes were saved and that no retained explanation depends on a soon-to-be-deleted inbox path. Preserve necessary supporting material in an appropriate durable source location before clearing its temporary copy.
5. Remove only the handled item and its exclusively temporary attachments. Inspect the current contents again before cleanup; new user edits, unresolved parts or an interrupted save keep the item pending. If interrupted after saving, check what was already integrated before resuming so it is not duplicated. Never clear the whole inbox merely because the user returned.

A dismissed or superseded item can also be cleared after preserving anything still needed. Do not delete shared source files, other pending messages or this README. Clearing the interface is separate from erasing the durable understanding developed through it.

## Scheduled and background work

An already authorized background agent or cron job could leave a review, question or worksheet here for the person's next session. The inbox is the handoff point between that work and the conversation. A producer should identify its run or originating task, avoid repeating an unresolved request, and preserve user edits rather than regenerating over them. Parent and child agents still need their own scoped authority to write to a workspace's inbox.

This foundation defines a file-based practice. It does not install cron jobs, run a watcher, send notifications, render custom forms or provide transactional queue processing. Concurrent delivery, retry identifiers and richer interface behavior remain implementation decisions. Adding an inbox does not activate background work.

## Repository convention

Live items and attachments in this repository's `inbox/` are excluded from Git; only this guide is tracked. There are no seeded messages or sample user responses. The [workspace model](../wiki/workspace-model.md) explains how the inbox fits alongside user material, the wiki and agent resources.

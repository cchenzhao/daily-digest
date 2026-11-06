# Daily Class Prep Digest

Run this once daily at the user's selected local time.

1. Read `config.json`. Run `python3 fetch_canvas_snapshot.py`. If it fails, email the authenticated user a short failure alert and stop.
2. Compare `state/current.json` with `state/previous.json`; identify only new or materially changed assignments, due dates, submission states, and modules.
3. Read the next seven days from the authenticated user's Google Calendar. Include course meetings and other commitments only when they affect preparation time.
4. Read recent Gmail only for high-signal, time-sensitive academic or meeting actions. Omit newsletters, promotions, receipts, and bulk mail.
5. Send one compact, mobile-friendly HTML email to the authenticated user. Use the subject `📚 Class Prep — <Day, Mon D>`.

The email should contain:

- **Today first:** at most three urgent/unsubmitted actions with course, deadline, and source link.
- **Upcoming:** a chronological seven-day list of Canvas deadlines.
- **Calendar:** only relevant upcoming class and preparation commitments.
- **Inbox actions:** only verified, time-sensitive items.
- **Changes since last digest:** only material changes found from the two snapshots.
- **Source check:** Canvas snapshot timestamp and timezone.

Never expose credentials, private calendar details, raw email body text, or raw API payloads. Do not modify Canvas, Calendar, or Drive. Before sending, check `state/last-successful-send-date`; if it equals today's date in the configured timezone, do not send. After Gmail confirms success, write today's date to that file.

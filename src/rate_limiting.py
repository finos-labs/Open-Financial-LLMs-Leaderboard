from datetime import datetime, timezone, timedelta


def user_submission_permission(submission_name, users_to_submission_dates, rate_limit_period):
    org_or_user, _ = submission_name.split("/")
    if org_or_user not in users_to_submission_dates:
        return 0
    submission_dates = sorted(users_to_submission_dates[org_or_user])

    time_limit = (datetime.now(timezone.utc) - timedelta(days=rate_limit_period)).strftime("%Y-%m-%dT%H:%M:%SZ")
    submissions_after_timelimit = [d for d in submission_dates if d > time_limit]

    return len(submissions_after_timelimit)

import datetime
# ============================================================
# Time
# ============================================================

def speak_time_text():

    now = datetime.datetime.now()

    hour = now.hour

    minute = now.minute

    period = "morning"

    if now.hour >= 12:

        period = "afternoon"

    if now.hour >= 17:

        period = "evening"

    if now.hour >= 20:

        period = "night"

    if hour == 0:

        hour = 12

    elif hour > 12:

        hour -= 12

    if minute == 0:

        return f"It's {hour} o'clock in the {period}"

    if minute < 10:

        return f"It's {hour} oh {minute} in the {period}"

    return f"It's {hour} {minute} in the {period}"

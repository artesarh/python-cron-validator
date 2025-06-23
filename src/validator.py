import re
from typing import Dict, Optional, TypedDict


def safe_parse_int(value: str) -> float:
    if re.match(r"^\d+$", value):
        return float(value)
    return float("nan")


def is_wildcard(value: str) -> bool:
    return value == "*"


def is_question_mark(value: str) -> bool:
    return value == "?"


def is_in_range(value: float, start: int, stop: int) -> bool:
    return value >= start and value <= stop


def is_valid_range(value: str, start: int, stop: int) -> bool:
    sides = value.split("-")
    if len(sides) == 1:
        return is_wildcard(value) or is_in_range(safe_parse_int(value), start, stop)
    elif len(sides) == 2:
        small, big = map(safe_parse_int, sides)
        return (
            small <= big
            and is_in_range(small, start, stop)
            and is_in_range(big, start, stop)
        )
    return False


def is_valid_step(value: Optional[str]) -> bool:
    return value is None or (
        re.search(r"[^\d]", value) is None and safe_parse_int(value) > 0
    )


def validate_for_range(value: str, start: int, stop: int) -> bool:
    if re.search(r"[^\d,/*-]", value) is not None:
        return False

    conditions = value.split(",")
    for condition in conditions:
        splits = condition.split("/")
        if condition.strip().endswith("/"):
            return False
        if len(splits) > 2:
            return False
        left, right = splits[0], splits[1] if len(splits) == 2 else None
        if not (is_valid_range(left, start, stop) and is_valid_step(right)):
            return False
    return True


def has_valid_seconds(seconds: str) -> bool:
    return validate_for_range(seconds, 0, 59)


def has_valid_minutes(minutes: str) -> bool:
    return validate_for_range(minutes, 0, 59)


def has_valid_hours(hours: str) -> bool:
    return validate_for_range(hours, 0, 23)


def has_valid_days(days: str, allow_blank_day: bool = False) -> bool:
    return (allow_blank_day and is_question_mark(days)) or validate_for_range(
        days, 1, 31
    )


month_alias: Dict[str, str] = {
    "jan": "1",
    "feb": "2",
    "mar": "3",
    "apr": "4",
    "may": "5",
    "jun": "6",
    "jul": "7",
    "aug": "8",
    "sep": "9",
    "oct": "10",
    "nov": "11",
    "dec": "12",
}


def has_valid_months(months: str, alias: bool = False) -> bool:
    if re.search(r"\/[a-zA-Z]", months) is not None:
        return False

    if alias:

        def replace_alias(match: re.Match) -> str:
            return month_alias.get(match.group(0).lower(), match.group(0))

        remapped_months = re.sub(r"[a-z]{3}", replace_alias, months.lower())
        return validate_for_range(remapped_months, 1, 12)

    return validate_for_range(months, 1, 12)


weekdays_alias: Dict[str, str] = {
    "sun": "0",
    "mon": "1",
    "tue": "2",
    "wed": "3",
    "thu": "4",
    "fri": "5",
    "sat": "6",
}


class WeekdayOptions(TypedDict):
    alias: bool
    allowBlankDay: bool
    allowSevenAsSunday: bool
    allowNthWeekdayOfMonth: bool


def has_valid_weekdays(weekdays: str, options: WeekdayOptions) -> bool:
    allow_blank_day = options["allowBlankDay"]
    alias = options["alias"]
    allow_seven_as_sunday = options["allowSevenAsSunday"]
    allow_nth_weekday_of_month = options["allowNthWeekdayOfMonth"]

    if allow_blank_day and is_question_mark(weekdays):
        return True
    elif not allow_blank_day and is_question_mark(weekdays):
        return False

    if re.search(r"\/[a-zA-Z]", weekdays) is not None:
        return False

    if alias:

        def replace_alias(match: re.Match) -> str:
            return weekdays_alias.get(match.group(0).lower(), match.group(0))

        remapped_weekdays = re.sub(
            r"[a-z]{3}", replace_alias, weekdays.lower())
    else:
        remapped_weekdays = weekdays

    max_weekday_num = 7 if allow_seven_as_sunday else 6

    split_by_hash = remapped_weekdays.split("#")
    if allow_nth_weekday_of_month and len(split_by_hash) >= 2:
        if len(split_by_hash) > 2:
            return False
        weekday, occurrence = split_by_hash[:2]
        return is_in_range(safe_parse_int(occurrence), 1, 5) and is_in_range(
            safe_parse_int(weekday), 0, max_weekday_num
        )

    return validate_for_range(remapped_weekdays, 0, max_weekday_num)


def has_compatible_day_format(
    days: str, weekdays: str, allow_blank_day: bool = False
) -> bool:
    return not (
        allow_blank_day and is_question_mark(
            days) and is_question_mark(weekdays)
    )


def split_cron(cron: str) -> list[str]:
    return cron.strip().split()


class Options(TypedDict):
    """Options for configuring cron expression validation."""

    alias: bool
    """If True, allows month and weekday aliases (e.g., 'jan', 'sun')."""
    seconds: bool
    """If True, allows six-field cron expressions with a seconds field (0-59)."""
    allowBlankDay: bool
    """If True, allows '?' in day-of-month or day-of-week fields to indicate no specific value."""
    allowSevenAsSunday: bool
    """If True, allows '7' as an alias for Sunday in the day-of-week field (in addition to '0')."""
    allowNthWeekdayOfMonth: bool
    """If True, allows 'weekday#n' format in day-of-week field (e.g., 'mon#2' for second Monday)."""


default_options: Options = {
    "alias": False,
    "seconds": False,
    "allowBlankDay": False,
    "allowSevenAsSunday": False,
    "allowNthWeekdayOfMonth": False,
}


def is_valid_cron(cron: str, partial_options: Optional[dict] = None) -> bool:
    """
    Validates a cron expression for correctness.

    Args:
        cron (str): The cron expression to validate (e.g., '* * * * *' or '0 59 23 * * 6').
        partial_options (Optional[dict]): Optional configuration to override default options.
            Available options:
            - alias (bool): If True, allows month (e.g., 'jan', 'feb') and weekday (e.g., 'mon', 'sun')
              aliases. Default: False.
            - seconds (bool): If True, allows a six-field cron expression with a seconds field (0-59).
              If False, expects a five-field expression (minutes, hours, day-of-month, month,
              day-of-week). Default: False.
            - allowBlankDay (bool): If True, allows '?' in day-of-month or day-of-week fields to
              indicate no specific value (but not both). Default: False.
            - allowSevenAsSunday (bool): If True, allows '7' as an alias for Sunday in the day-of-week
              field (in addition to '0'). Default: False.
            - allowNthWeekdayOfMonth (bool): If True, allows 'weekday#n' format in the day-of-week
              field (e.g., 'mon#2' for the second Monday of the month). Default: False.

    Returns:
        bool: True if the cron expression is valid according to the specified options, False otherwise.

    Examples:
        >>> is_valid_cron('* * * * *')
        True
        >>> is_valid_cron('59 23 * * 6')
        True
        >>> is_valid_cron('0 59 23 * * 6', {'seconds': True})
        True
        >>> is_valid_cron('* * * jan *', {'alias': True})
        True
        >>> is_valid_cron('* * ? * *', {'allowBlankDay': True})
        True
    """
    options = {**default_options, **(partial_options or {})}
    splits = split_cron(cron)
    if len(splits) > (6 if options["seconds"] else 5) or len(splits) < 5:
        return False
    checks = []
    if len(splits) == 6:
        seconds = splits.pop(0)
        checks.append(has_valid_seconds(seconds))
    try:
        minutes, hours, days, months, weekdays = splits
    except ValueError:
        return False
    checks.append(has_valid_minutes(minutes))
    checks.append(has_valid_hours(hours))
    checks.append(has_valid_days(days, options["allowBlankDay"]))
    checks.append(has_valid_months(months, options["alias"]))
    checks.append(has_valid_weekdays(weekdays, options))
    checks.append(has_compatible_day_format(
        days, weekdays, options["allowBlankDay"]))
    return all(checks)

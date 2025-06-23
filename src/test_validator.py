import pytest

# Assuming the main module is named cron.py
from .validator import is_valid_cron


def test_not_accept_less_than_5_symbols():
    valid = is_valid_cron("* * * *")
    assert not valid


def test_not_accept_more_than_6_symbols():
    valid = is_valid_cron("* * * * * * *")
    assert not valid


def test_accept_6_symbols_with_seconds_option():
    valid = is_valid_cron("* * * * * *", {"seconds": True})
    assert valid


def test_accept_5_symbols_without_seconds():
    valid = is_valid_cron("* * * * *")
    assert valid


def test_accept_whitespaces_on_each_side():
    valid = is_valid_cron(" * * * * * ")
    assert valid


def test_not_accept_scalar_ending_with_wildcard():
    assert not is_valid_cron("1* * * * *")
    assert not is_valid_cron("* 1* * * *")
    assert not is_valid_cron("*1 * * * *")
    assert not is_valid_cron("* *1 * * *")


def test_not_accept_seconds_outside_0_59():
    assert is_valid_cron("0 * * * * *", {"seconds": True})
    assert is_valid_cron("59 * * * * *", {"seconds": True})
    assert not is_valid_cron("60 * * * * *", {"seconds": True})


def test_not_accept_minutes_outside_0_59():
    assert is_valid_cron("* 0 * * * *", {"seconds": True})
    assert is_valid_cron("* 59 * * * *", {"seconds": True})
    assert not is_valid_cron("* 60 * * * *", {"seconds": True})
    assert is_valid_cron("59 * * * *")
    assert not is_valid_cron("60 * * * *")


def test_not_accept_hours_outside_0_23():
    assert is_valid_cron("* 0 * * *")
    assert is_valid_cron("* 23 * * *")
    assert not is_valid_cron("* 24 * * *")


def test_not_accept_days_outside_1_31():
    assert is_valid_cron("* * 1 * *")
    assert not is_valid_cron("* * 0 * *")
    assert is_valid_cron("* * 31 * *")
    assert not is_valid_cron("* * 32 * *")


def test_not_accept_months_outside_1_12():
    assert is_valid_cron("* * * 1 *")
    assert not is_valid_cron("* * * 0 *")
    assert is_valid_cron("* * * 12 *")
    assert not is_valid_cron("* * * 13 *")


def test_accept_month_alias_with_alias_flag():
    assert is_valid_cron("* * * jan,JAN *", {"alias": True})
    assert is_valid_cron("* * * feb,FEB *", {"alias": True})
    assert is_valid_cron("* * * mar,MAR *", {"alias": True})
    assert is_valid_cron("* * * apr,APR *", {"alias": True})
    assert is_valid_cron("* * * may,MAY *", {"alias": True})
    assert is_valid_cron("* * * jun,JUN *", {"alias": True})
    assert is_valid_cron("* * * jul,JUL *", {"alias": True})
    assert is_valid_cron("* * * aug,AUG *", {"alias": True})
    assert is_valid_cron("* * * sep,SEP *", {"alias": True})
    assert is_valid_cron("* * * oct,OCT *", {"alias": True})
    assert is_valid_cron("* * * nov,NOV *", {"alias": True})
    assert is_valid_cron("* * * dec,DEC *", {"alias": True})


def test_not_accept_month_alias_without_alias_flag():
    assert not is_valid_cron("* * * jan *")


def test_not_accept_invalid_month_alias():
    assert not is_valid_cron("* * * january *", {"alias": True})


def test_not_accept_month_alias_as_steps():
    assert not is_valid_cron("* * * */jan *", {"alias": True})


def test_not_accept_days_of_week_outside_0_6():
    assert is_valid_cron("* * * * 0")
    assert is_valid_cron("* * * * 6")
    assert not is_valid_cron("* * * * 7")


def test_accept_7_days_of_week_with_allow_seven_as_sunday_flag():
    assert is_valid_cron("* * * * 7", {"allowSevenAsSunday": True})


def test_accept_weekdays_alias_with_alias_flag():
    assert is_valid_cron("* * * * sun,SUN", {"alias": True})
    assert is_valid_cron("* * * * mon,MON", {"alias": True})
    assert is_valid_cron("* * * * tue,TUE", {"alias": True})
    assert is_valid_cron("* * * * wed,WED", {"alias": True})
    assert is_valid_cron("* * * * thu,THU", {"alias": True})
    assert is_valid_cron("* * * * fri,FRI", {"alias": True})
    assert is_valid_cron("* * * * sat,SAT", {"alias": True})


def test_not_accept_weekdays_alias_without_flag():
    assert not is_valid_cron("* * * * sun")


def test_not_accept_invalid_weekdays_alias():
    assert not is_valid_cron("* * * * sunday", {"alias": True})


def test_not_accept_weekdays_alias_as_steps():
    assert not is_valid_cron("* * * * */sun", {"alias": True})


def test_accept_ranges():
    assert is_valid_cron("1-10 * * * * *", {"seconds": True})
    assert is_valid_cron("1-10 * * * *")
    assert is_valid_cron("* 1-10 * * *")
    assert is_valid_cron("* * 1-31 * *")
    assert is_valid_cron("* * * 1-12 *")
    assert is_valid_cron("* * * * 0-6")


def test_accept_ranges_with_allow_nth_weekday_flag():
    assert is_valid_cron("* * * * 0-6", {"allowNthWeekdayOfMonth": True})


def test_accept_list_of_ranges():
    assert is_valid_cron("1-10,11-20,21-30 * * * * *", {"seconds": True})
    assert is_valid_cron("1-10,11-20,21-30 * * * *")
    assert is_valid_cron("* 1-10,11-20,21-23 * * *")
    assert is_valid_cron("* * 1-10,11-20,21-31 * *")
    assert is_valid_cron("* * * 1-2,3-4,5-6 *")
    assert is_valid_cron("* * * * 0-2,3-4,5-6")


def test_not_accept_inverted_ranges():
    assert not is_valid_cron("10-1,20-11,30-21 * * * * *", {"seconds": True})
    assert not is_valid_cron("10-1,20-11,30-21 * * * *")
    assert not is_valid_cron("* 10-1,20-11,23-21 * * *")
    assert not is_valid_cron("* * 10-1,20-11,31-21 * *")
    assert not is_valid_cron("* * * 2-1,4-3,6-5 *")
    assert not is_valid_cron("* * * * 2-0,4-3,6-5")


def test_accept_steps_in_ranges():
    assert is_valid_cron("1-10/2,21-30/2 * * * * *", {"seconds": True})
    assert is_valid_cron("1-10/2,11-20/2 * * * *")
    assert is_valid_cron("* 1-10/2,11-20/2 * * *")
    assert is_valid_cron("* * 1-10/2,11-20/2 * *")
    assert is_valid_cron("* * * 1-2/2,3-4/2 *")
    assert is_valid_cron("* * * * 0-2/2,3-4/2")


def test_accept_wildcards_over_steps_in_ranges():
    assert is_valid_cron("1-10,*/2 * * * * *", {"seconds": True})
    assert is_valid_cron("1-10,*/2 * * * *")
    assert is_valid_cron("* 1-10,*/2 * * *")
    assert is_valid_cron("* * 1-10,*/2 * *")
    assert is_valid_cron("* * * 1-2,*/2 *")
    assert is_valid_cron("* * * * 0-2,*/2")


def test_not_accept_steps_below_1():
    assert not is_valid_cron("1-10,*/0 * * * * *", {"seconds": True})
    assert not is_valid_cron("1-10,*/0 * * * *")
    assert not is_valid_cron("* 1-10,*/0 * * *")
    assert not is_valid_cron("* * 1-10,*/0 * *")
    assert not is_valid_cron("* * * 1-2,*/0 *")
    assert not is_valid_cron("* * * * 0-2,*/-1")


def test_not_accept_invalid_range():
    assert not is_valid_cron("1-10-20 * * * * *")
    assert not is_valid_cron("1-10-20 * * * *", {"seconds": True})
    assert not is_valid_cron("* 1-10-20 * * *")
    assert not is_valid_cron("* * 1-10-20 * *")
    assert not is_valid_cron("* * * 1-2-10 *")
    assert not is_valid_cron("* * * * 0-2-6")


def test_not_accept_invalid_step():
    assert not is_valid_cron("1/10/20 * * * * *", {"seconds": True})
    assert not is_valid_cron("1/10/20 * * * *")
    assert not is_valid_cron("* 1/10/20 * * *")
    assert not is_valid_cron("* * 1/10/20 * *")
    assert not is_valid_cron("* * * 1/2/10 *")
    assert not is_valid_cron("* * * * 0/2/6")


def test_not_accept_incomplete_step():
    assert not is_valid_cron("*/ * * * * *", {"seconds": True})
    assert not is_valid_cron("*/ * * * *")
    assert not is_valid_cron("* */ * * *")
    assert not is_valid_cron("* * */ * *")
    assert not is_valid_cron("* * * /* *")
    assert not is_valid_cron("* * * * */")


def test_not_accept_wildcards_as_range_value():
    assert not is_valid_cron("1-* * * * * *", {"seconds": True})
    assert not is_valid_cron("1-* * * * *")
    assert not is_valid_cron("* 1-* * * *")
    assert not is_valid_cron("* * 1-* * *")
    assert not is_valid_cron("* * * 1-* *")
    assert not is_valid_cron("* * * * 0-*")


def test_not_accept_invalid_range_format():
    assert not is_valid_cron("1- * * * * *", {"seconds": True, "alias": True})
    assert not is_valid_cron("1- * * * *")
    assert not is_valid_cron("* - * * *")
    assert not is_valid_cron("* * 1- * *")
    assert not is_valid_cron("* * * -1 *")
    assert not is_valid_cron("* * * * 0-")


def test_accept_everything_combined():
    valid = is_valid_cron(
        "10,*/15,12-14,15-30/5 10,*/15,12-14,15-30/5 10,*/12,12-14,5-10/2 10,*/7,12-15,15-30/5 1,*/3,4-5,jun-oct/2 0,*/3,2-4,mon-fri/2",
        {"seconds": True, "alias": True},
    )
    assert valid


def test_accept_number_prefixed_with_0():
    assert is_valid_cron("05 05 * * *")


def test_not_accept_question_marks_in_days_if_allow_blank_day_not_set():
    assert not is_valid_cron("* * ? * *")
    assert not is_valid_cron("* * * * ?")
    assert not is_valid_cron("* * ? * ?")


def test_accept_question_marks_in_days_if_allow_blank_day_set():
    assert is_valid_cron("* * ? * *", {"allowBlankDay": True})


def test_accept_question_marks_in_weekdays():
    assert is_valid_cron("* * * * ?", {"allowBlankDay": True})
    assert is_valid_cron("* * * * ?", {"alias": True, "allowBlankDay": True})


def test_not_accept_question_marks_in_both_if_allow_blank_day_set():
    assert not is_valid_cron("* * ? * ?", {"allowBlankDay": True})
    assert not is_valid_cron("* * ? * ?", {"alias": True})


@pytest.mark.parametrize("weekday", ["1#2", "2", "WED#5"])
def test_accept_nth_weekday_of_month(weekday):
    assert is_valid_cron(
        f"* * * * {weekday}", {"allowNthWeekdayOfMonth": True, "alias": True}
    )


@pytest.mark.parametrize("weekday", ["mon-fri#2", "mon#2-fri#2", "WED#6"])
def test_not_accept_nth_weekday_of_month(weekday):
    assert not is_valid_cron(
        f"* * * * * {weekday}",
        {"allowNthWeekdayOfMonth": True, "allowBlankDay": True, "alias": True},
    )


def test_nth_weekday_not_accept_alias_without_flag():
    assert not is_valid_cron("* * * * mon#2", {"allowNthWeekdayOfMonth": True})


def test_accept_every_minute():
    assert is_valid_cron("1 * * * *")


def test_accept_every_second_day():
    assert is_valid_cron("1 * 2 * *")


def test_assert_every_week_saturday_midnight():
    assert is_valid_cron("59 23 * * 6")
    assert is_valid_cron("59 23 * * sat", {"alias": True})  # Five-field, alias
    assert is_valid_cron("59 23 * * SAT", {"alias": True})  # Five-field, alias


def test_assert_every_working_day_at_7am():
    assert is_valid_cron("0 7 * * 1-5")


def test_random_difficult_cron():
    assert is_valid_cron("0 0,12 1 */2 *")

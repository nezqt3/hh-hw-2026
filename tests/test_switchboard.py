import pytest

from app.switchboard import Switchboard
from app.users import ForeignUser, LocalUser


LOCAL_1 = "1,Ivan Ivanov,+79990000000"
LOCAL_2 = "4,Petr Petrov,+78880000000"

FOREIGN_1 = "2,John Smith,+15551234567"
FOREIGN_2 = "3,Jane Doe,+33123456789"
FOREIGN_3 = "5,Alex Doe,+442012345678"
FOREIGN_4 = "6,John Doe,+33123456780"


def make_call(caller: str, receiver: str) -> str:
    return f"{caller},{receiver}"


LOCAL_TO_FOREIGN_CALL = make_call(LOCAL_1, FOREIGN_1)
FOREIGN_TO_LOCAL_CALL = make_call(FOREIGN_1, LOCAL_1)
LOCAL_TO_LOCAL_CALL = make_call(LOCAL_1, LOCAL_2)
FOREIGN_TO_FOREIGN_CALL = make_call(FOREIGN_1, FOREIGN_2)


@pytest.fixture
def switchboard() -> Switchboard:
    return Switchboard()


@pytest.mark.parametrize(
    ("raw_call", "expected_error"),
    [
        ("1,Ivan Ivanov,+79990000000,2,John Smith", ValueError),
        ("1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567,extra", ValueError),
        ("abc,Ivan Ivanov,+79990000000,2,John Smith,+15551234567", ValueError),
        ("1,Ivan Ivanov,+79990000000,xyz,John Smith,+15551234567", ValueError),
        ("1,   ,+79990000000,2,John Smith,+15551234567", ValueError),
        ("1,Ivan Ivanov,+79990000000,2,   ,+15551234567", ValueError),
        ("1,Ivan Ivanov,   ,2,John Smith,+15551234567", ValueError),
        ("1,Ivan Ivanov,+79990000000,2,John Smith,   ", ValueError),
        ("", ValueError),
        (",,,,,", ValueError),
        (None, TypeError),
    ],
)
def test_register_call_raises_error_for_invalid_input(
    switchboard: Switchboard,
    raw_call: str | None,
    expected_error: type[Exception],
) -> None:
    with pytest.raises(expected_error):
        switchboard.register_call(raw_call)


def test_register_call_creates_local_and_foreign_users(
    switchboard: Switchboard,
) -> None:
    active_call = switchboard.register_call(LOCAL_TO_FOREIGN_CALL)

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.is_cross_border is True
    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2


def test_register_call_creates_foreign_and_local_users(
    switchboard: Switchboard,
) -> None:
    active_call = switchboard.register_call(FOREIGN_TO_LOCAL_CALL)

    assert isinstance(active_call.caller, ForeignUser)
    assert isinstance(active_call.receiver, LocalUser)
    assert active_call.is_cross_border is True
    assert active_call.caller.id == 2
    assert active_call.receiver.id == 1


def test_register_call_does_not_add_invalid_call(
    switchboard: Switchboard,
) -> None:
    with pytest.raises(ValueError):
        switchboard.register_call(
            "abc,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
        )

    assert switchboard.get_active_calls_count() == 0
    assert switchboard.get_cross_border_calls_count() == 0


def test_local_to_local_call_is_not_cross_border(
    switchboard: Switchboard,
) -> None:
    active_call = switchboard.register_call(LOCAL_TO_LOCAL_CALL)

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, LocalUser)
    assert active_call.is_cross_border is False
    assert switchboard.get_cross_border_calls_count() == 0


def test_foreign_to_foreign_call_is_not_cross_border(
    switchboard: Switchboard,
) -> None:
    active_call = switchboard.register_call(FOREIGN_TO_FOREIGN_CALL)

    assert isinstance(active_call.caller, ForeignUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.is_cross_border is False
    assert switchboard.get_cross_border_calls_count() == 0


def test_register_call_counts_active_calls(
    switchboard: Switchboard,
) -> None:
    switchboard.register_call(LOCAL_TO_LOCAL_CALL)
    switchboard.register_call(FOREIGN_TO_FOREIGN_CALL)

    assert switchboard.get_active_calls_count() == 2


def test_register_call_counts_calls_between_local_and_foreign_users(
    switchboard: Switchboard,
) -> None:
    switchboard.register_call(LOCAL_TO_FOREIGN_CALL)
    switchboard.register_call(make_call("3,Petr Petrov,+78880000000", "4,Maria Petrova,+79991112233"))
    switchboard.register_call(make_call("5,Jane Doe,+33123456789", "6,Alex Doe,+442012345678"))

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1


def test_cross_border_calls_count_increases_for_each_cross_border_call(
    switchboard: Switchboard,
) -> None:
    switchboard.register_call(make_call(LOCAL_1, FOREIGN_1))
    switchboard.register_call(make_call(FOREIGN_2, LOCAL_2))
    switchboard.register_call(make_call(FOREIGN_3, FOREIGN_4))

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 2
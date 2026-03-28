import pytest

from app.switchboard import Switchboard
from app.users import ForeignUser, LocalUser


LOCAL_1 = "1,Ivan Ivanov,+79990000000"
LOCAL_2 = "4,Petr Petrov,+78880000000"
LOCAL_3 = "7,Maria Petrova,+79991112233"

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
SECOND_LOCAL_TO_LOCAL_CALL = make_call(LOCAL_2, LOCAL_3)
SECOND_FOREIGN_TO_FOREIGN_CALL = make_call(FOREIGN_3, FOREIGN_4)


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


@pytest.mark.parametrize(
    ("raw_call", "caller_type", "receiver_type", "is_cross_border", "caller_id", "receiver_id"),
    [
        (LOCAL_TO_FOREIGN_CALL, LocalUser, ForeignUser, True, 1, 2),
        (FOREIGN_TO_LOCAL_CALL, ForeignUser, LocalUser, True, 2, 1),
        (LOCAL_TO_LOCAL_CALL, LocalUser, LocalUser, False, 1, 4),
        (FOREIGN_TO_FOREIGN_CALL, ForeignUser, ForeignUser, False, 2, 3),
    ],
)
def test_register_call_creates_expected_users(
    switchboard: Switchboard,
    raw_call: str,
    caller_type: type[LocalUser | ForeignUser],
    receiver_type: type[LocalUser | ForeignUser],
    is_cross_border: bool,
    caller_id: int,
    receiver_id: int,
) -> None:
    active_call = switchboard.register_call(raw_call)

    assert isinstance(active_call.caller, caller_type)
    assert isinstance(active_call.receiver, receiver_type)
    assert active_call.is_cross_border is is_cross_border
    assert active_call.caller.id == caller_id
    assert active_call.receiver.id == receiver_id


def test_register_call_does_not_add_invalid_call(
    switchboard: Switchboard,
) -> None:
    with pytest.raises(ValueError):
        switchboard.register_call(
            "abc,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
        )

    assert switchboard.get_active_calls_count() == 0
    assert switchboard.get_cross_border_calls_count() == 0


def test_register_call_counts_active_calls(
    switchboard: Switchboard,
) -> None:
    switchboard.register_call(LOCAL_TO_LOCAL_CALL)
    switchboard.register_call(SECOND_FOREIGN_TO_FOREIGN_CALL)

    assert switchboard.get_active_calls_count() == 2


def test_register_call_counts_cross_border_calls(
    switchboard: Switchboard,
) -> None:
    switchboard.register_call(LOCAL_TO_FOREIGN_CALL)
    switchboard.register_call(SECOND_LOCAL_TO_LOCAL_CALL)
    switchboard.register_call(SECOND_FOREIGN_TO_FOREIGN_CALL)

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1


def test_cross_border_calls_count_increases_for_each_cross_border_call(
    switchboard: Switchboard,
) -> None:
    switchboard.register_call(LOCAL_TO_FOREIGN_CALL)
    switchboard.register_call(make_call(FOREIGN_2, LOCAL_2))
    switchboard.register_call(SECOND_FOREIGN_TO_FOREIGN_CALL)

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 2
from __future__ import annotations

from dataclasses import dataclass

from app.users import User, LocalUser, ForeignUser


LOCAL_PHONE_PREFIX = "+7"


@dataclass(slots=True)
class ActiveCall:
    caller: User
    receiver: User

    @property
    def is_cross_border(self) -> bool:
        return type(self.caller) is not type(self.receiver)


def _validate_raw_call_type(raw_call: str) -> None:
    if not isinstance(raw_call, str):
        raise TypeError("raw_call must be str")


def _validate_raw_call_not_empty(raw_call: str) -> None:
    if not raw_call.strip():
        raise ValueError("raw_call cannot be empty")


def _split_raw_call(raw_call: str) -> list[str]:
    data = [item.strip() for item in raw_call.split(",")]

    if len(data) != 6:
        raise ValueError("invalid format of str")

    return data


def _validate_fields_not_empty(fields: list[str]) -> None:
    if any(not field for field in fields):
        raise ValueError("Fields cannot be empty")


def _parse_user_id(raw_user_id: str, field_name: str) -> int:
    try:
        return int(raw_user_id)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be integer") from exc


def _create_user(user_id: int, name: str, phone: str) -> User:
    if phone.startswith(LOCAL_PHONE_PREFIX):
        return LocalUser(user_id, name, phone)
    return ForeignUser(user_id, name, phone)


def _parse_call_data(raw_call: str) -> tuple[User, User]:
    _validate_raw_call_type(raw_call)
    _validate_raw_call_not_empty(raw_call)

    data = _split_raw_call(raw_call)
    _validate_fields_not_empty(data)

    caller_id_raw, caller_name, caller_phone, receiver_id_raw, receiver_name, receiver_phone = data

    caller_id = _parse_user_id(caller_id_raw, "caller_id")
    receiver_id = _parse_user_id(receiver_id_raw, "receiver_id")

    caller = _create_user(caller_id, caller_name, caller_phone)
    receiver = _create_user(receiver_id, receiver_name, receiver_phone)

    return caller, receiver


class Switchboard:
    def __init__(self) -> None:
        self._active_calls: list[ActiveCall] = []
        self._cross_border_calls: int = 0

    def register_call(self, raw_call: str) -> ActiveCall:
        """
        Метод принимает строку формата:
        "caller_id,caller_name,caller_phone,receiver_id,receiver_name,receiver_phone"

        Например:
        "1001,Иван Петров,+71234567890,1085,Адам Яковлев,+71255556666"
        """
        caller, receiver = _parse_call_data(raw_call)

        active_call = ActiveCall(caller, receiver)
        self._active_calls.append(active_call)

        if active_call.is_cross_border:
            self._cross_border_calls += 1

        return active_call

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_calls
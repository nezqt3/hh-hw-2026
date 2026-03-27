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


class Switchboard:
    def __init__(self) -> None:
        self._active_calls: list[ActiveCall] = []
        self._cross_border_calls: int = 0

    def register_call(self, raw_call: str) -> ActiveCall:
        '''
        Метод должен принимать только 1 строку и возвращать класс ActiveCall.
        На входе строка должна быть вида "caller_id,caller_name,caller_phone,reciever_id,reciever_name,reciever_phone"

        Например: "1001,Иван Петров,+71234567890,1085,Адам Яковлев,+71255556666"
        '''
        if not isinstance(raw_call, str):
            raise TypeError("raw_call must be str")
        
        if not raw_call.strip():
            raise ValueError("raw_call cannot be empty")
        
        data = [item.strip() for item in raw_call.split(",")]
        
        if len(data) != 6:
            raise ValueError("invalid format of str")
        
        if any(not field for field in data):
            raise ValueError("Fields cannot be empty")
        
        caller_id, caller_name, caller_phone, receiver_id, receiver_name, receiver_phone = data
        try:
            caller_id = int(caller_id)
        except ValueError:
            raise ValueError("caller_id must be integer")

        try:
            receiver_id = int(receiver_id)
        except ValueError:
            raise ValueError("receiver_id must be integer")
        
        if caller_phone.startswith(LOCAL_PHONE_PREFIX):
            caller = LocalUser(caller_id, caller_name, caller_phone)
        else:
            caller = ForeignUser(caller_id, caller_name, caller_phone)

        if receiver_phone.startswith(LOCAL_PHONE_PREFIX):
            receiver = LocalUser(receiver_id, receiver_name, receiver_phone)
        else:
            receiver = ForeignUser(receiver_id, receiver_name, receiver_phone)
        
        active_call = ActiveCall(caller, receiver)
        self._active_calls.append(active_call)
        
        if active_call.is_cross_border:
            self._cross_border_calls += 1
        
        return active_call

    def get_active_calls_count(self) -> int:
        return len(self._active_calls)

    def get_cross_border_calls_count(self) -> int:
        return self._cross_border_calls

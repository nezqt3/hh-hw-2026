import pytest

from app.switchboard import Switchboard
from app.users import ForeignUser, LocalUser


def test_register_call_raises_error_when_not_enough_fields() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,2,John Smith"
        )
        
def test_register_call_raises_type_error_when_raw_call_is_not_string() -> None:
    switchboard = Switchboard()

    with pytest.raises(TypeError):
        switchboard.register_call(None) 
        
def test_register_call_raises_error_when_too_many_fields() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567,extra"
        )
        
def test_register_call_raises_error_when_caller_id_is_not_integer() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(
            "abc,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
        )
        
def test_register_call_raises_error_when_receiver_id_is_not_integer() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,xyz,John Smith,+15551234567"
        )
        
def test_register_call_raises_error_when_caller_name_is_empty() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(
            "1,   ,+79990000000,2,John Smith,+15551234567"
        )
        
def test_register_call_raises_error_when_receiver_name_is_empty() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,2,   ,+15551234567"
        )
        
def test_register_call_raises_error_when_caller_phone_is_empty() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(
            "1,Ivan Ivanov,   ,2,John Smith,+15551234567"
        )
        
def test_register_call_raises_error_when_receiver_phone_is_empty() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(
            "1,Ivan Ivanov,+79990000000,2,John Smith,   "
        )
        
def test_register_call_raises_error_when_raw_call_is_empty() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call("")   
        
def test_register_call_raises_error_when_all_fields_are_empty() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(",,,,,") 

def test_register_call_creates_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.is_cross_border is True
    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2

def test_register_call_creates_foreign_and_local_users() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,John Smith,+15551234567,2,Ivan Ivanov,+79990000000"
    )

    assert isinstance(active_call.caller, ForeignUser)
    assert isinstance(active_call.receiver, LocalUser)
    assert active_call.is_cross_border is True
    assert active_call.caller.id == 1
    assert active_call.receiver.id == 2
    
def test_register_call_does_not_add_invalid_call() -> None:
    switchboard = Switchboard()

    with pytest.raises(ValueError):
        switchboard.register_call(
            "abc,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
        )

    assert switchboard.get_active_calls_count() == 0
    assert switchboard.get_cross_border_calls_count() == 0

def test_local_to_local_call_is_not_cross_border() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000"
    )

    assert isinstance(active_call.caller, LocalUser)
    assert isinstance(active_call.receiver, LocalUser)
    assert active_call.is_cross_border is False
    assert switchboard.get_cross_border_calls_count() == 0
    
def test_foreign_to_foreign_call_is_not_cross_border() -> None:
    switchboard = Switchboard()

    active_call = switchboard.register_call(
        "1,John Smith,+15551234567,2,Jane Doe,+33123456789"
    )

    assert isinstance(active_call.caller, ForeignUser)
    assert isinstance(active_call.receiver, ForeignUser)
    assert active_call.is_cross_border is False
    assert switchboard.get_cross_border_calls_count() == 0

def test_register_call_counts_active_calls() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,Petr Petrov,+78880000000"
    )
    switchboard.register_call(
        "3,John Smith,+15551234567,4,Jane Doe,+33123456789"
    )

    assert switchboard.get_active_calls_count() == 2


def test_register_call_counts_calls_between_local_and_foreign_users() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )
    switchboard.register_call(
        "3,Petr Petrov,+78880000000,4,Maria Petrova,+79991112233"
    )
    switchboard.register_call(
        "5,Jane Doe,+33123456789,6,Alex Doe,+442012345678"
    )

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 1

def test_cross_border_calls_count_increases_for_each_cross_border_call() -> None:
    switchboard = Switchboard()

    switchboard.register_call(
        "1,Ivan Ivanov,+79990000000,2,John Smith,+15551234567"
    )
    switchboard.register_call(
        "3,Jane Doe,+33123456789,4,Petr Petrov,+78880000000"
    )
    switchboard.register_call(
        "5,Alex Doe,+442012345678,6,John Doe,+33123456780"
    )

    assert switchboard.get_active_calls_count() == 3
    assert switchboard.get_cross_border_calls_count() == 2
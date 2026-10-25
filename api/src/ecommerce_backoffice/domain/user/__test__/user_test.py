from datetime import datetime, date

from ecommerce_backoffice.domain.user.entity.user import User
from ecommerce_backoffice.domain.user.user_value_object import Email

def test_create_user_entity():
    user = User(
        email = Email("user@example.com"),
        date_of_birth= date(1996, 6, 24), 
        firstname= "Nico",
        lastname="Polo",
    )
    
    assert isinstance(user.create_date,  datetime)
    assert isinstance(user.age,  int)
    assert isinstance(user.email,  Email)
    assert isinstance(user.firstname,  str)
    assert isinstance(user.lastname,  str)
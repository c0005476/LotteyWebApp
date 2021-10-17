import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, ValidationError, Length, EqualTo
from werkzeug.security import generate_password_hash


def character_check(form, field):
    excluded_chars="*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Char {char} is not allowed."
            )


class RegisterForm(FlaskForm):
    email = StringField(validators=[Required(), Email()])
    firstname = StringField(validators=[Required(), character_check])
    lastname = StringField(validators=[Required(), character_check])
    phone = StringField(validators=[Required()])
    password = PasswordField(validators=[Required(), Length(min=6, max=12,
                                                            message="Password must be between 6 "
                                                                    "and 12 characters in length.")])
    confirm_password = PasswordField(validators=[Required(),
                                                 EqualTo('password', message='Both password fields must be equal.')])
    pin_key = StringField(validators=[Required(), Length(min=32, max=32, message='Pin Key must be 32 characters long.')])

    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[]\[*?!%&/()=}{$@<>])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit,"
                                  " 1 lowercase letter, 1 upper case letter and 1 special character.")

    def validate_phone(self, phone):
        p = re.compile(r'\d\d\d\d-\d\d\d-\d\d\d\d')
        if not p.fullmatch(self.phone.data):
            raise ValidationError("Phone number must follow the pattern of XXXX-XXX-XXXX")

    submit = SubmitField()


class LoginForm(FlaskForm):
    email = StringField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])
    pin = StringField(validators=[Required(), Length(min=6, max=6, message='PIN must be 6 characters long')])

    def validate_pin(self, pin):
        # TODO write pin validation
        pin_copy = pin
        return ValidationError("Invalid Pin entered, please try again")

    submit = SubmitField()

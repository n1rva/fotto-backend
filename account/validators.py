import re
from django.forms import ValidationError


def validate_password(password):

   if len(password) < 8:
       raise ValidationError("Şifre en az 8 karakter olmalıdır")

   if password.isdigit():
       raise ValidationError("Şifre sadece rakamdan oluşamaz")

   if password.isalpha():
       raise ValidationError("Şifre sadece harften oluşamaz")
       
   try:
       validate_password_strength(password)
   except Exception as e:
       raise ValidationError(str(e))

   # diğer kontroller

   return True

def validate_password_strength(password):

    if len(password) < 8:
        raise Exception("Şifre en az 8 karakter olmalı")

    if password.isdigit() or password.isalpha():
        raise Exception("Şifre alfa-nümerik olmalı")
    
    if not re.search("[a-z]", password):
        raise Exception("Şifre küçük harf içermeli")

    # Diğer kontroller

    # # Entropy hesaplama
    # entropy = calculate_entropy(password) 
    # if entropy < 4:
    #     raise Exception("Şifre daha karmaşık olmalı")

    return True
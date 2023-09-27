from django import forms
   
# creating a form 
class LoginForm(forms.Form):
   
    username = forms.CharField(max_length = 200, 
                     help_text = "At least 3 charachters"
                     )
    password = forms.CharField(widget = forms.PasswordInput(), help_text="Use numbers and words")
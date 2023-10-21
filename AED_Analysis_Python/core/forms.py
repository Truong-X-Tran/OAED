from django import forms
  
# creating a form 
class ScoreForm(forms.Form):
    lowest_score = forms.IntegerField(label="Lowest Score")
    highest_score = forms.IntegerField(label="Highest Score")
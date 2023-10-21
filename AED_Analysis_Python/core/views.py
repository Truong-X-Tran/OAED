from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from AED_Analysis_Python.core.analysis.entrypoint import EntryPoint

from .forms import ScoreForm
class Home(TemplateView):
    template_name = 'home.html'

def upload(request):

    context = {}

    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        
        
        form = ScoreForm(request.POST)
        if form.is_valid():
            lowest_score = form.cleaned_data["lowest_score"]
            highest_score = form.cleaned_data["highest_score"]

        entrypoint = EntryPoint()
        output_file_name = entrypoint.computeAED(uploaded_file.name, lowest_score, highest_score)

        context['url'] = fs.url(output_file_name)
    return render(request, 'upload.html', context)
 